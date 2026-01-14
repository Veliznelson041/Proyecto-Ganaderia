from datetime import timezone
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from app_registros.models import UserProfile, Productor, MarcaSenal, Solicitud, Campo, TipoSenal, ImagenMarcaPredefinida
from app_registros.forms import ProductorForm, MarcaSenalForm, SolicitudForm
from django.http import JsonResponse
from django.views.generic import ListView, CreateView, UpdateView, DetailView
from django.urls import reverse_lazy
from django.conf import settings

from django.views.generic import ListView, CreateView, UpdateView, DetailView, DeleteView, TemplateView
from django.views import View
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from app_registros.models import Productor, Campo, MarcaSenal


from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from django.http import HttpResponse
# Create your views here.


# app_sigrams/views.py - Agregar estas funciones al inicio
from django.http import JsonResponse
import json

def get_campos_por_productor(request, productor_id):
    """Obtener campos de un productor específico (para AJAX)"""
    try:
        # Verificar si el productor existe
        from app_registros.models import Productor, Campo
        productor = Productor.objects.get(id=productor_id)
        
        # Obtener campos del productor
        campos = Campo.objects.filter(productor_id=productor_id)
        
        if not campos.exists():
            # Si no hay campos, crear uno automáticamente basado en los datos del productor
            campo = Campo.objects.create(
                nombre=productor.campo or f"Campo de {productor.nombre} {productor.apellido}",
                productor=productor,
                distrito=productor.localidad or "Sin especificar",
                departamento=productor.departamento or "Sin especificar",
                area_hectareas=productor.area_hectareas or 0,
                latitud=productor.latitud,
                longitud=productor.longitud
            )
            campos = Campo.objects.filter(productor_id=productor_id)
        
        # Preparar datos para JSON
        data = []
        for campo in campos:
            data.append({
                'id': campo.id,
                'nombre': campo.nombre,
                'distrito': campo.distrito or '',
                'departamento': campo.departamento or ''
            })
        
        return JsonResponse(data, safe=False)
        
    except Productor.DoesNotExist:
        return JsonResponse([], safe=False)
    except Exception as e:
        print(f"Error en get_campos_por_productor: {str(e)}")
        return JsonResponse([{'error': str(e)}], safe=False, status=500)
    
def get_imagenes_marcas(request):
    """Obtener imágenes predefinidas de marcas (para AJAX)"""
    try:
        imagenes = ImagenMarcaPredefinida.objects.filter(activa=True)
        data = []
        for imagen in imagenes:
            data.append({
                'id': imagen.id,
                'nombre': imagen.nombre,
                'tipo_marca': imagen.get_tipo_marca_display(),
                'imagen': imagen.imagen.url if imagen.imagen else '',
                'imagen_url': request.build_absolute_uri(imagen.imagen.url) if imagen.imagen else ''
            })
        return JsonResponse(data, safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)



# app_sigrams/views.py - Actualizar función home
@login_required
def home(request):
    """Vista principal del dashboard"""
    from app_registros.models import Productor, MarcaSenal, Solicitud, Campo
    from django.db.models import Count, Q, Sum
    from django.utils import timezone
    import datetime
    import json
    
    hoy = timezone.now()
    
    # ========== ESTADÍSTICAS BÁSICAS ==========
    total_productores = Productor.objects.count()
    total_marcas = MarcaSenal.objects.filter(estado='VIGENTE').count()
    solicitudes_pendientes = Solicitud.objects.filter(estado='PENDIENTE').count()
    total_campos = Campo.objects.count()
    
    # ========== ESTADÍSTICAS AVANZADAS ==========
    # Ingresos por sellados (último mes)
    primer_dia_mes = hoy.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    ingresos_mes = MarcaSenal.objects.filter(
        fecha_creacion__gte=primer_dia_mes,
        valor_sellado__isnull=False
    ).aggregate(total=Sum('valor_sellado'))['total'] or 0
    
    # Trámites del mes actual
    tramites_mes = Solicitud.objects.filter(
        fecha_solicitud__gte=primer_dia_mes
    ).count()
    
    # ========== DISTRIBUCIONES ==========
    # Productores por estado
    productores_por_estado = list(Productor.objects.values('estado').annotate(
        total=Count('id')
    ).order_by('estado'))
    
    # Marcas por tipo de trámite
    marcas_por_tipo = list(MarcaSenal.objects.values('tipo_tramite').annotate(
        total=Count('id')
    ).order_by('tipo_tramite'))
    
    # Solicitudes por estado
    solicitudes_por_estado = list(Solicitud.objects.values('estado').annotate(
        total=Count('id')
    ).order_by('estado'))
    
    # ========== DATOS RECIENTES ==========
    # Últimas solicitudes (10)
    ultimas_solicitudes = Solicitud.objects.select_related('productor').order_by('-fecha_solicitud')[:10]
    
    # Productores recientes (últimos 7 días)
    fecha_limite = hoy - datetime.timedelta(days=7)
    productores_recientes = Productor.objects.filter(
        fecha_registro__gte=fecha_limite
    ).order_by('-fecha_registro')[:5]
    
    # Marcas próximas a vencer (próximos 30 días)
    fecha_vencimiento = hoy + datetime.timedelta(days=30)
    marcas_por_vencer = MarcaSenal.objects.filter(
        fecha_vencimiento__gte=hoy,
        fecha_vencimiento__lte=fecha_vencimiento,
        estado='VIGENTE'
    ).select_related('productor').order_by('fecha_vencimiento')[:5]
    
    # Marcas recientemente inscritas
    marcas_recientes = MarcaSenal.objects.select_related('productor').order_by('-fecha_inscripcion')[:5]
    
    # ========== ACTIVIDAD DEL MES ==========
    # Gráfico de actividad mensual
    meses_actividad = []
    for i in range(6):
        fecha = hoy - datetime.timedelta(days=30*i)
        mes_str = fecha.strftime('%Y-%m')
        nombre_mes = fecha.strftime('%b')
        
        # Solicitudes del mes
        solicitudes_mes = Solicitud.objects.filter(
            fecha_solicitud__year=fecha.year,
            fecha_solicitud__month=fecha.month
        ).count()
        
        # Marcas del mes
        marcas_mes = MarcaSenal.objects.filter(
            fecha_inscripcion__year=fecha.year,
            fecha_inscripcion__month=fecha.month
        ).count()
        
        meses_actividad.append({
            'mes': mes_str,
            'nombre': nombre_mes,
            'solicitudes': solicitudes_mes,
            'marcas': marcas_mes
        })
    
    meses_actividad.reverse()  # Para mostrar del más antiguo al más reciente
    
    # ========== TOP 5 PRODUCTORES CON MÁS MARCAS ==========
    top_productores = Productor.objects.annotate(
        total_marcas=Count('marcas_senales')
    ).order_by('-total_marcas')[:5]
    
    # ========== CONTEXT ==========
    context = {
        # Estadísticas básicas
        'total_productores': total_productores,
        'total_marcas': total_marcas,
        'solicitudes_pendientes': solicitudes_pendientes,
        'total_campos': total_campos,
        'ingresos_mes': ingresos_mes,
        'tramites_mes': tramites_mes,
        
        # Distribuciones
        'productores_por_estado': json.dumps(productores_por_estado),
        'marcas_por_tipo': json.dumps(marcas_por_tipo),
        'solicitudes_por_estado': json.dumps(solicitudes_por_estado),
        
        # Datos recientes
        'ultimas_solicitudes': ultimas_solicitudes,
        'productores_recientes': productores_recientes,
        'marcas_por_vencer': marcas_por_vencer,
        'marcas_recientes': marcas_recientes,
        
        # Actividad
        'meses_actividad': json.dumps(meses_actividad),
        
        # Top productores
        'top_productores': top_productores,
        
        # Para badges
        'productores_estados_list': productores_por_estado,
        'marcas_tipos_list': marcas_por_tipo,
    }
    
    return render(request, 'app_sigrams/index.html', context)



# LOGIN
def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
        
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'¡Bienvenido/a {user.username}!')
            
            # Redirigir según el rol del usuario
            try:
                profile = UserProfile.objects.get(user=user)
                if profile.rol == 'admin':
                    return redirect('home')
                elif profile.rol == 'inspector':
                    return redirect('home')
                else:
                    return redirect('home')
            except UserProfile.DoesNotExist:
                return redirect('home')
                
        else:
            messages.error(request, 'Usuario o contraseña incorrectos.')
    
    return render(request, 'app_sigrams/login.html')


# LOGOUT
@login_required
def logout_view(request):
    logout(request)
    messages.info(request, 'Has cerrado sesión correctamente.')
    return redirect('login')


# REGISTRO
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User

from app_sigrams.forms import CustomUserCreationForm

def register_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)

        if form.is_valid():
            user = form.save()

            # Crear perfil por defecto (inspector)
            UserProfile.objects.create(
                user=user,
                rol='inspector'
            )

            messages.success(
                request,
                'Cuenta creada correctamente. Ahora podés iniciar sesión.'
            )
            return redirect('login')

        else:
            # Mostrar errores campo por campo como mensajes
            for field, errors in form.errors.items():
                label = (
                    form.fields[field].label
                    if field in form.fields
                    else field
                )
                for error in errors:
                    messages.error(request, f"{label}: {error}")

    else:
        form = CustomUserCreationForm()

    return render(
        request,
        'app_sigrams/register.html',
        {'form': form}
    )



class EsEmpleadoOMas(UserPassesTestMixin):
    def test_func(self):
        user_profile = UserProfile.objects.get(user=self.request.user)
        return user_profile.rol in ['admin', 'empleado']



# ... (tus vistas existentes de login, logout, register, home)

# ============================================================================
# VISTAS PARA PRODUCTORES
# ============================================================================

@login_required
def lista_productores(request):
    """Lista todos los productores con filtros"""
    productores = Productor.objects.all()
    
    # Filtros - ELIMINAMOS DISTRITO
    query = request.GET.get('q', '')
    estado = request.GET.get('estado', '')
    localidad = request.GET.get('localidad', '')
    departamento = request.GET.get('departamento', '')
    
    if query:
        productores = productores.filter(
            Q(nombre__icontains=query) | 
            Q(apellido__icontains=query) |
            Q(dni__icontains=query) |
            Q(campo__icontains=query)
        )
    
    if estado:
        productores = productores.filter(estado=estado)
    
    if localidad:
        productores = productores.filter(localidad__icontains=localidad)
    
    if departamento:
        productores = productores.filter(departamento__icontains=departamento)
    
    context = {
        'productores': productores,
        'query': query,
        'estado_filtro': estado,
        'localidad_filtro': localidad,
        'departamento_filtro': departamento,
    }
    return render(request, 'app_sigrams/productores/lista.html', context)

@login_required
def detalle_productor(request, pk):
    """Detalle de un productor específico"""
    productor = get_object_or_404(Productor, pk=pk)
    marcas = productor.marcas_senales.all()
    solicitudes = productor.solicitudes.all()
    campos = productor.campos.all()
    
    context = {
        'productor': productor,
        'marcas': marcas,
        'solicitudes': solicitudes,
        'campos': campos,
    }
    return render(request, 'app_sigrams/productores/detalle.html', context)

@login_required
def nuevo_productor(request):
    """Crear nuevo productor"""
    try:
        if request.method == 'POST':
            form = ProductorForm(request.POST)
            if form.is_valid():
                productor = form.save()
                messages.success(request, f'Productor {productor.nombre_completo} creado exitosamente.')
                return redirect('detalle_productor', pk=productor.pk)
            else:
                # Obtener todos los errores para mostrarlos
                error_list = []
                for field, errors in form.errors.items():
                    for error in errors:
                        if field != '__all__':
                            field_label = form.fields[field].label or field
                            error_list.append(f"{field_label}: {error}")
                        else:
                            error_list.append(str(error))
                
                if error_list:
                    messages.error(request, "Errores en el formulario:")
                    for error in error_list:
                        messages.error(request, f"- {error}")
                else:
                    messages.error(request, 'Por favor, corrija los errores en el formulario.')
                
                # Mantener los datos ingresados
                context = {'form': form, 'titulo': 'Nuevo Productor'}
                return render(request, 'app_sigrams/productores/form.html', context)
        else:
            form = ProductorForm()
        
        context = {'form': form, 'titulo': 'Nuevo Productor'}
        return render(request, 'app_sigrams/productores/form.html', context)
    
    except Exception as e:
        messages.error(request, f'Error al crear el productor: {str(e)}')
        return redirect('lista_productores')



@login_required
def editar_productor(request, pk):
    """Editar productor existente"""
    try:
        productor = get_object_or_404(Productor, pk=pk)
        
        if request.method == 'POST':
            form = ProductorForm(request.POST, instance=productor)
            if form.is_valid():
                productor = form.save()
                messages.success(request, f'Productor {productor.nombre_completo} actualizado exitosamente.')
                return redirect('detalle_productor', pk=productor.pk)
            else:
                messages.error(request, 'Por favor, corrija los errores en el formulario.')
        else:
            form = ProductorForm(instance=productor)
        
        context = {'form': form, 'titulo': 'Editar Productor', 'productor': productor}
        return render(request, 'app_sigrams/productores/form.html', context)
    
    except Exception as e:
        messages.error(request, f'Error al editar el productor: {str(e)}')
        return redirect('lista_productores')



@login_required
def eliminar_productor(request, pk):
    """Eliminar productor"""
    productor = get_object_or_404(Productor, pk=pk)
    
    if request.method == 'POST':
        nombre = productor.nombre_completo
        productor.delete()
        messages.success(request, f'Productor {nombre} eliminado exitosamente.')
        return redirect('lista_productores')
    
    context = {'productor': productor}
    return render(request, 'app_sigrams/productores/confirmar_eliminar.html', context)

# Vistas para Productores
class ListaProductoresView(LoginRequiredMixin, ListView):
    model = Productor
    template_name = 'productores/lista.html'
    context_object_name = 'productores'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = super().get_queryset()
        # Filtros
        nombre = self.request.GET.get('nombre')
        dni = self.request.GET.get('dni')
        localidad = self.request.GET.get('localidad')
        estado = self.request.GET.get('estado')
        
        if nombre:
            queryset = queryset.filter(Q(nombre__icontains=nombre) | Q(apellido__icontains=nombre))
        if dni:
            queryset = queryset.filter(dni__icontains=dni)
        if localidad:
            queryset = queryset.filter(localidad__icontains=localidad)
        if estado:
            queryset = queryset.filter(estado=estado)
        
        return queryset.order_by('apellido', 'nombre')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_productores'] = Productor.objects.count()
        context['estados'] = Productor.ESTADO_CHOICES
        return context

class NuevoProductorView(LoginRequiredMixin, EsEmpleadoOMas, CreateView):
    model = Productor
    template_name = 'productores/form.html'
    fields = ['nombre', 'apellido', 'dni', 'cuit', 'domicilio', 'distrito', 
              'localidad', 'telefono', 'email', 'latitud', 'longitud', 
              'estado', 'observaciones']
    success_url = reverse_lazy('lista_productores')
    
    def form_valid(self, form):
        form.instance.usuario_registro = self.request.user
        return super().form_valid(form)

class EditarProductorView(LoginRequiredMixin, EsEmpleadoOMas, UpdateView):
    model = Productor
    template_name = 'productores/form.html'
    fields = ['nombre', 'apellido', 'dni', 'cuit', 'domicilio', 'distrito', 
              'localidad', 'telefono', 'email', 'latitud', 'longitud', 
              'estado', 'observaciones']
    success_url = reverse_lazy('lista_productores')

class DetalleProductorView(LoginRequiredMixin, DetailView):
    model = Productor
    template_name = 'productores/detalle.html'
    context_object_name = 'productor'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['campos'] = self.object.campos.all()
        context['marcas'] = self.object.marcas_senales.all()
        context['solicitudes'] = self.object.solicitudes.all()
        return context

class EliminarProductorView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Productor
    template_name = 'productores/confirmar_eliminar.html'
    success_url = reverse_lazy('lista_productores')
    
    def test_func(self):
        user_profile = UserProfile.objects.get(user=self.request.user)
        return user_profile.rol == 'admin'


class ReporteProductoresPDFView(LoginRequiredMixin, View):
    def get(self, request):
        # Crear respuesta HTTP con contenido PDF
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="reporte_productores.pdf"'
        
        # Crear documento PDF
        doc = SimpleDocTemplate(response, pagesize=letter)
        elements = []
        
        # Estilos
        styles = getSampleStyleSheet()
        
        # Título
        title = Paragraph("Reporte de Productores - SIGRAMS", styles['Title'])
        elements.append(title)
        
        # Fecha
        fecha = Paragraph(f"Generado: {timezone.now().strftime('%d/%m/%Y %H:%M')}", styles['Normal'])
        elements.append(fecha)
        
        elements.append(Paragraph("<br/><br/>", styles['Normal']))
        
        # Datos
        productores = Productor.objects.all().order_by('apellido', 'nombre')
        
        # Tabla
        data = [['Nombre', 'DNI', 'Localidad', 'Estado', 'Fecha Registro']]
        
        for p in productores:
            data.append([
                f"{p.apellido}, {p.nombre}",
                p.dni,
                p.localidad,
                p.get_estado_display(),
                p.fecha_registro.strftime('%d/%m/%Y')
            ])
        
        table = Table(data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0A2E5A')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        
        elements.append(table)
        
        # Generar PDF
        doc.build(elements)
        
        return response

# ============================================================================
# VISTAS PARA MARCAS Y SEÑALES
# ============================================================================

# Vistas para Marcas y Señales
@login_required
def lista_marcas(request):
    """Lista todas las marcas y señales"""
    marcas = MarcaSenal.objects.select_related('productor', 'campo').all()
    
    # Filtros
    query = request.GET.get('q', '')
    estado = request.GET.get('estado', '')
    tipo_tramite = request.GET.get('tipo_tramite', '')
    
    if query:
        marcas = marcas.filter(
            Q(productor__nombre__icontains=query) | 
            Q(productor__apellido__icontains=query) |
            Q(numero_orden__icontains=query)
        )
    
    if estado:
        marcas = marcas.filter(estado=estado)
    
    if tipo_tramite:
        marcas = marcas.filter(tipo_tramite=tipo_tramite)
    
    context = {
        'marcas': marcas,
        'query': query,
        'estado_filtro': estado,
        'tipo_tramite_filtro': tipo_tramite,
    }
    return render(request, 'app_sigrams/marcas/lista.html', context)



@login_required
def detalle_marca(request, pk):
    """Detalle de una marca específica"""
    marca = get_object_or_404(MarcaSenal.objects.select_related('productor', 'campo', 'tipo_senal'), pk=pk)
    
    context = {
        'marca': marca,
    }
    return render(request, 'app_sigrams/marcas/detalle.html', context)



@login_required
def nueva_marca(request):
    """Crear nueva marca y señal"""
    if request.method == 'POST':
        form = MarcaSenalForm(request.POST, request.FILES)
        if form.is_valid():
            marca = form.save(commit=False)
            
            # Si se seleccionó una imagen predefinida, copiar la imagen
            if marca.imagen_predefinida and not marca.imagen_marca:
                imagen_predefinida = marca.imagen_predefinida
                # Copiar la imagen predefinida al campo imagen_marca
                if imagen_predefinida.imagen:
                    # Esta es una forma simple de copiar el archivo
                    marca.imagen_marca.save(
                        f"predefinida_{imagen_predefinida.id}_{imagen_predefinida.imagen.name}",
                        imagen_predefinida.imagen.file,
                        save=False
                    )
            
            marca.save()
            messages.success(request, f'Marca #{marca.numero_orden} creada exitosamente.')
            return redirect('detalle_marca', pk=marca.pk)
        else:
            messages.error(request, 'Por favor, corrija los errores en el formulario.')
    else:
        form = MarcaSenalForm()
    
    context = {
        'form': form, 
        'titulo': 'Nueva Marca y Señal',
        'imagenes_predefinidas': ImagenMarcaPredefinida.objects.filter(activa=True)
    }
    return render(request, 'app_sigrams/marcas/form.html', context)



@login_required
def editar_marca(request, pk):
    """Editar marca existente"""
    marca = get_object_or_404(MarcaSenal, pk=pk)
    
    if request.method == 'POST':
        form = MarcaSenalForm(request.POST, request.FILES, instance=marca)
        if form.is_valid():
            marca = form.save()
            messages.success(request, f'Marca #{marca.numero_orden} actualizada exitosamente.')
            return redirect('detalle_marca', pk=marca.pk)
        else:
            messages.error(request, 'Por favor, corrija los errores en el formulario.')
    else:
        form = MarcaSenalForm(instance=marca)
    
    context = {'form': form, 'titulo': 'Editar Marca y Señal', 'marca': marca}
    return render(request, 'app_sigrams/marcas/form.html', context)


class ListaMarcasView(ListView):
    model = MarcaSenal
    template_name = 'app_sigrams/marcas/lista.html'
    context_object_name = 'marcas'
    paginate_by = 20

class NuevaMarcaView(CreateView):
    model = MarcaSenal
    form_class = MarcaSenalForm
    template_name = 'app_sigrams/marcas/form.html'
    success_url = reverse_lazy('lista_marcas')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Nueva Marca y Señal'
        context['imagenes_predefinidas'] = ImagenMarcaPredefinida.objects.filter(activa=True)
        return context

class EditarMarcaView(UpdateView):
    model = MarcaSenal
    form_class = MarcaSenalForm
    template_name = 'app_sigrams/marcas/form.html'
    success_url = reverse_lazy('lista_marcas')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = f'Editar Marca y Señal #{self.object.numero_orden}'
        context['imagenes_predefinidas'] = ImagenMarcaPredefinida.objects.filter(activa=True)
        return context

class DetalleMarcaView(DetailView):
    model = MarcaSenal
    template_name = 'app_sigrams/marcas/detalle.html'
    context_object_name = 'marca'

# Vista para cargar campos según el productor seleccionado (AJAX)
def cargar_campos(request):
    productor_id = request.GET.get('productor_id')
    campos = Campo.objects.filter(productor_id=productor_id).order_by('nombre')
    return render(request, 'marcas/campo_dropdown_options.html', {'campos': campos})





# ============================================================================
# VISTAS PARA SOLICITUDES
# ============================================================================

@login_required
def lista_solicitudes(request):
    """Lista todas las solicitudes"""
    solicitudes = Solicitud.objects.all()
    
    # Filtros
    estado = request.GET.get('estado', '')
    tipo_tramite = request.GET.get('tipo_tramite', '')
    
    if estado:
        solicitudes = solicitudes.filter(estado=estado)
    
    if tipo_tramite:
        solicitudes = solicitudes.filter(tipo_tramite=tipo_tramite)
    
    context = {
        'solicitudes': solicitudes,
        'estado_filtro': estado,
        'tipo_tramite_filtro': tipo_tramite,
    }
    return render(request, 'app_sigrams/solicitudes/lista.html', context)

@login_required
def nueva_solicitud(request):
    """Crear nueva solicitud"""
    if request.method == 'POST':
        form = SolicitudForm(request.POST, request.FILES)
        if form.is_valid():
            solicitud = form.save()
            messages.success(request, f'Solicitud #{solicitud.id} creada exitosamente.')
            return redirect('lista_solicitudes')
    else:
        form = SolicitudForm()
    
    context = {'form': form, 'titulo': 'Nueva Solicitud'}
    return render(request, 'app_sigrams/solicitudes/form.html', context)

@login_required
def cambiar_estado_solicitud(request, pk, estado):
    """Cambiar estado de una solicitud"""
    solicitud = get_object_or_404(Solicitud, pk=pk)
    
    if estado in ['APROBADO', 'RECHAZADO']:
        solicitud.estado = estado
        solicitud.save()
        
        if estado == 'APROBADO':
            messages.success(request, f'Solicitud #{solicitud.id} aprobada.')
        else:
            messages.warning(request, f'Solicitud #{solicitud.id} rechazada.')
    
    return redirect('lista_solicitudes')



@login_required
def api_productores_geojson(request):
    """API para obtener productores en formato GeoJSON"""
    productores = Productor.objects.exclude(latitud__isnull=True).exclude(longitud__isnull=True)
    
    features = []
    for productor in productores:
        features.append({
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [float(productor.longitud), float(productor.latitud)]
            },
            "properties": {
                "id": productor.id,
                "nombre": productor.nombre_completo,
                "dni": productor.dni,
                "estado": productor.estado,
                "area_hectareas": float(productor.area_hectareas) if productor.area_hectareas else 0,
                "detalle_url": f"/productores/{productor.id}/"
            }
        })
    
    geojson = {
        "type": "FeatureCollection",
        "features": features
    }
    
    return JsonResponse(geojson)


# app_sigrams/views.py
class MapaProductoresView(LoginRequiredMixin, TemplateView):
    template_name = 'mapa/mapa.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Obtener productores con coordenadas
        productores = Productor.objects.exclude(latitud__isnull=True).exclude(longitud__isnull=True)
        
        # Preparar datos para el mapa
        puntos_mapa = []
        for p in productores:
            if p.latitud and p.longitud:
                puntos_mapa.append({
                    'id': p.id,
                    'nombre': p.nombre_completo,
                    'dni': p.dni,
                    'localidad': p.localidad,
                    'estado': p.get_estado_display(),
                    'lat': float(p.latitud),
                    'lng': float(p.longitud),
                    'color': 'green' if p.estado == 'REGISTRADO' else 'orange'
                })
        
        context['puntos_mapa'] = puntos_mapa
        context['total_puntos'] = len(puntos_mapa)
        
        return context

def get_puntos_mapa_json(request):
    """API para obtener puntos del mapa en formato GeoJSON"""
    productores = Productor.objects.exclude(latitud__isnull=True).exclude(longitud__isnull=True)
    
    features = []
    for p in productores:
        if p.latitud and p.longitud:
            feature = {
                'type': 'Feature',
                'geometry': {
                    'type': 'Point',
                    'coordinates': [float(p.longitud), float(p.latitud)]
                },
                'properties': {
                    'id': p.id,
                    'nombre': p.nombre_completo,
                    'dni': p.dni,
                    'localidad': p.localidad,
                    'estado': p.estado,
                    'estado_display': p.get_estado_display(),
                    'color': 'green' if p.estado == 'REGISTRADO' else 'orange'
                }
            }
            features.append(feature)
    
    geojson = {
        'type': 'FeatureCollection',
        'features': features
    }
    
    return JsonResponse(geojson)