from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from app_registros.models import UserProfile, Productor, MarcaSenal, Solicitud, Campo, TipoSenal
from app_registros.forms import ProductorForm, MarcaSenalForm, SolicitudForm

# Create your views here.

@login_required
def home(request):
    """Vista principal del dashboard"""
    from app_registros.models import Productor, MarcaSenal, Solicitud  # Asegúrate que sea MarcaSenal
    from django.utils import timezone
    
    # Estadísticas para el dashboard
    total_productores = Productor.objects.count()
    total_marcas = MarcaSenal.objects.filter(estado='VIGENTE').count()
    solicitudes_pendientes = Solicitud.objects.filter(estado='PENDIENTE').count()
    
    # Trámites del mes actual
    mes_actual = timezone.now().month
    tramites_mes = Solicitud.objects.filter(
        fecha_solicitud__month=mes_actual
    ).count()
    
    # Últimas solicitudes
    ultimas_solicitudes = Solicitud.objects.select_related('productor').order_by('-fecha_solicitud')[:5]
    
    context = {
        'total_productores': total_productores,
        'total_marcas': total_marcas,
        'solicitudes_pendientes': solicitudes_pendientes,
        'tramites_mes': tramites_mes,
        'ultimas_solicitudes': ultimas_solicitudes,
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
def register_view(request):
    if request.user.is_authenticated:
        return redirect('home')
        
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        password2 = request.POST['password2']
        first_name = request.POST.get('first_name', '')
        last_name = request.POST.get('last_name', '')

        # Validaciones
        if password != password2:
            messages.error(request, 'Las contraseñas no coinciden.')
            return render(request, 'app_sigrams/register.html')
            
        if User.objects.filter(username=username).exists():
            messages.error(request, 'El nombre de usuario ya existe.')
            return render(request, 'app_sigrams/register.html')
            
        if User.objects.filter(email=email).exists():
            messages.error(request, 'El email ya está registrado.')
            return render(request, 'app_sigrams/register.html')

        # Crear usuario
        user = User.objects.create_user(
            username=username, 
            email=email, 
            password=password,
            first_name=first_name,
            last_name=last_name
        )
        
        # Crear perfil por defecto (inspector)
        UserProfile.objects.create(
            user=user,
            rol='inspector'
        )
        
        messages.success(request, 'Cuenta creada correctamente. Ahora podés iniciar sesión.')
        return redirect('login')

    return render(request, 'app_sigrams/register.html')




# ... (tus vistas existentes de login, logout, register, home)

# ============================================================================
# VISTAS PARA PRODUCTORES
# ============================================================================

@login_required
def lista_productores(request):
    """Lista todos los productores con filtros"""
    productores = Productor.objects.all()
    
    # Filtros
    query = request.GET.get('q', '')
    estado = request.GET.get('estado', '')
    distrito = request.GET.get('distrito', '')
    
    if query:
        productores = productores.filter(
            Q(nombre__icontains=query) | 
            Q(apellido__icontains=query) |
            Q(dni__icontains=query)
        )
    
    if estado:
        productores = productores.filter(estado=estado)
    
    if distrito:
        productores = productores.filter(distrito__icontains=distrito)
    
    context = {
        'productores': productores,
        'query': query,
        'estado_filtro': estado,
        'distrito_filtro': distrito,
    }
    return render(request, 'app_sigrams/productores/lista.html', context)

@login_required
def detalle_productor(request, pk):
    """Detalle de un productor específico"""
    productor = get_object_or_404(Productor, pk=pk)
    marcas = productor.marcas_senales.all()
    solicitudes = productor.solicitudes.all()
    
    context = {
        'productor': productor,
        'marcas': marcas,
        'solicitudes': solicitudes,
    }
    return render(request, 'app_sigrams/productores/detalle.html', context)

@login_required
def nuevo_productor(request):
    """Crear nuevo productor"""
    if request.method == 'POST':
        form = ProductorForm(request.POST)
        if form.is_valid():
            productor = form.save()
            messages.success(request, f'Productor {productor.nombre_completo} creado exitosamente.')
            return redirect('detalle_productor', pk=productor.pk)
    else:
        form = ProductorForm()
    
    context = {'form': form, 'titulo': 'Nuevo Productor'}
    return render(request, 'app_sigrams/productores/form.html', context)

@login_required
def editar_productor(request, pk):
    """Editar productor existente"""
    productor = get_object_or_404(Productor, pk=pk)
    
    if request.method == 'POST':
        form = ProductorForm(request.POST, instance=productor)
        if form.is_valid():
            productor = form.save()
            messages.success(request, f'Productor {productor.nombre_completo} actualizado exitosamente.')
            return redirect('detalle_productor', pk=productor.pk)
    else:
        form = ProductorForm(instance=productor)
    
    context = {'form': form, 'titulo': 'Editar Productor', 'productor': productor}
    return render(request, 'app_sigrams/productores/form.html', context)

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

# ============================================================================
# VISTAS PARA MARCAS Y SEÑALES
# ============================================================================

@login_required
def lista_marcas(request):
    """Lista todas las marcas y señales"""
    marcas = MarcaSenal.objects.all()
    
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
    marca = get_object_or_404(MarcaSenal, pk=pk)
    
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
            marca = form.save()
            messages.success(request, f'Marca #{marca.numero_orden} creada exitosamente.')
            return redirect('detalle_marca', pk=marca.pk)
    else:
        form = MarcaSenalForm()
    
    context = {'form': form, 'titulo': 'Nueva Marca y Señal'}
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
        form = MarcaSenalForm(instance=marca)
    
    context = {'form': form, 'titulo': 'Editar Marca y Señal', 'marca': marca}
    return render(request, 'app_sigrams/marcas/form.html', context)

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
