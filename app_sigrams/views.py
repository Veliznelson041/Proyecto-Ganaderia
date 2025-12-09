from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator

from app_registros.models import (
    UserProfile, Productor, MarcaSenal, Solicitud,
    Campo, TipoSenal, ImagenMarcaPredefinida
)
from app_registros.forms import ProductorForm, MarcaSenalForm, SolicitudForm

# ===================================================================
# HOME
# ===================================================================

@login_required
def home(request):
    from django.utils import timezone
    
    total_productores = Productor.objects.count()
    total_marcas = MarcaSenal.objects.filter(estado='VIGENTE').count()
    solicitudes_pendientes = Solicitud.objects.filter(estado='PENDIENTE').count()
    
    mes_actual = timezone.now().month
    tramites_mes = Solicitud.objects.filter(
        fecha_solicitud__month=mes_actual
    ).count()
    
    ultimas_solicitudes = Solicitud.objects.select_related('productor').order_by('-fecha_solicitud')[:5]
    
    return render(request, 'app_sigrams/index.html', {
        'total_productores': total_productores,
        'total_marcas': total_marcas,
        'solicitudes_pendientes': solicitudes_pendientes,
        'tramites_mes': tramites_mes,
        'ultimas_solicitudes': ultimas_solicitudes,
    })

# ===================================================================
# LOGIN / LOGOUT / REGISTER
# ===================================================================

def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        
        if user:
            login(request, user)
            messages.success(request, f'¡Bienvenido/a {user.username}!')
            return redirect('home')
        else:
            messages.error(request, 'Usuario o contraseña incorrectos.')
    
    return render(request, 'app_sigrams/login.html')


@login_required
def logout_view(request):
    logout(request)
    messages.info(request, 'Has cerrado sesión correctamente.')
    return redirect('login')


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

        if password != password2:
            messages.error(request, 'Las contraseñas no coinciden.')
            return render(request, 'app_sigrams/register.html')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'El nombre de usuario ya existe.')
            return render(request, 'app_sigrams/register.html')
            
        if User.objects.filter(email=email).exists():
            messages.error(request, 'El email ya está registrado.')
            return render(request, 'app_sigrams/register.html')

        user = User.objects.create_user(
            username=username, 
            email=email, 
            password=password,
            first_name=first_name,
            last_name=last_name
        )
        
        UserProfile.objects.create(user=user, rol='inspector')
        
        messages.success(request, 'Cuenta creada correctamente.')
        return redirect('login')

    return render(request, 'app_sigrams/register.html')


# ===================================================================
# PRODUCTORES
# ===================================================================

@login_required
def lista_productores(request):
    productores = Productor.objects.all()

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

    return render(request, 'app_sigrams/productores/lista.html', {
        'productores': productores,
        'query': query,
        'estado_filtro': estado,
        'localidad_filtro': localidad,
        'departamento_filtro': departamento,
    })


@login_required
def detalle_productor(request, pk):
    productor = get_object_or_404(Productor, pk=pk)
    marcas = productor.marcas_senales.all()
    solicitudes = productor.solicitudes.all()
    campos = productor.campos.all()
    
    return render(request, 'app_sigrams/productores/detalle.html', {
        'productor': productor,
        'marcas': marcas,
        'solicitudes': solicitudes,
        'campos': campos,
    })


@login_required
def nuevo_productor(request):
    if request.method == 'POST':
        form = ProductorForm(request.POST)
        if form.is_valid():
            productor = form.save()
            messages.success(request, f'Productor {productor.nombre_completo} creado correctamente.')
            return redirect('detalle_productor', pk=productor.pk)
    else:
        form = ProductorForm()

    return render(request, 'app_sigrams/productores/form.html', {
        'form': form,
        'titulo': 'Nuevo Productor'
    })


@login_required
def editar_productor(request, pk):
    productor = get_object_or_404(Productor, pk=pk)

    if request.method == 'POST':
        form = ProductorForm(request.POST, instance=productor)
        if form.is_valid():
            productor = form.save()
            messages.success(request, 'Productor actualizado.')
            return redirect('detalle_productor', pk=productor.pk)
    else:
        form = ProductorForm(instance=productor)

    return render(request, 'app_sigrams/productores/form.html', {
        'form': form,
        'titulo': 'Editar Productor'
    })


@login_required
def eliminar_productor(request, pk):
    productor = get_object_or_404(Productor, pk=pk)
    
    if request.method == 'POST':
        nombre = productor.nombre_completo
        productor.delete()
        messages.success(request, f'Productor {nombre} eliminado.')
        return redirect('lista_productores')

    return render(request, 'app_sigrams/productores/confirmar_eliminar.html', {
        'productor': productor
    })


# ===================================================================
# MARCAS Y SEÑALES
# ===================================================================

@login_required
def lista_marcas(request):
    marcas = MarcaSenal.objects.select_related('productor', 'campo').all()

    query = request.GET.get('q', '')
    estado = request.GET.get('estado', '')
    tipo_tramite = request.GET.get('tipo_tramite', '')

    # Filtros
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

    # PAGINACIÓN (corregida)
    paginator = Paginator(marcas, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'app_sigrams/marcas/lista.html', {
        'marcas': page_obj,
        'query': query,
        'estado_filtro': estado,
        'tipo_tramite_filtro': tipo_tramite,
    })


@login_required
def detalle_marca(request, pk):
    marca = get_object_or_404(
        MarcaSenal.objects.select_related('productor', 'campo', 'tipo_senal'),
        pk=pk
    )
    return render(request, 'app_sigrams/marcas/detalle.html', {'marca': marca})


@login_required
def nueva_marca(request):
    if request.method == 'POST':
        form = MarcaSenalForm(request.POST, request.FILES)
        if form.is_valid():
            marca = form.save()
            messages.success(request, 'Marca creada.')
            return redirect('detalle_marca', pk=marca.pk)
    else:
        form = MarcaSenalForm()

    return render(request, 'app_sigrams/marcas/form.html', {
        'form': form,
        'titulo': 'Nueva Marca y Señal'
    })


@login_required
def editar_marca(request, pk):
    marca = get_object_or_404(MarcaSenal, pk=pk)

    if request.method == 'POST':
        form = MarcaSenalForm(request.POST, request.FILES, instance=marca)
        if form.is_valid():
            form.save()
            messages.success(request, 'Marca actualizada.')
            return redirect('detalle_marca', pk=marca.pk)
    else:
        form = MarcaSenalForm(instance=marca)

    return render(request, 'app_sigrams/marcas/form.html', {
        'form': form,
        'titulo': 'Editar Marca',
        'marca': marca
    })


# ===================================================================
# SOLICITUDES
# ===================================================================

@login_required
def lista_solicitudes(request):
    solicitudes = Solicitud.objects.all()

    estado = request.GET.get('estado', '')
    tipo_tramite = request.GET.get('tipo_tramite', '')

    if estado:
        solicitudes = solicitudes.filter(estado=estado)

    if tipo_tramite:
        solicitudes = solicitudes.filter(tipo_tramite=tipo_tramite)

    return render(request, 'app_sigrams/solicitudes/lista.html', {
        'solicitudes': solicitudes,
        'estado_filtro': estado,
        'tipo_tramite_filtro': tipo_tramite
    })


@login_required
def nueva_solicitud(request):
    if request.method == 'POST':
        form = SolicitudForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Solicitud creada.')
            return redirect('lista_solicitudes')
    else:
        form = SolicitudForm()

    return render(request, 'app_sigrams/solicitudes/form.html', {'form': form})


@login_required
def cambiar_estado_solicitud(request, pk, estado):
    solicitud = get_object_or_404(Solicitud, pk=pk)

    if estado in ['APROBADO', 'RECHAZADO']:
        solicitud.estado = estado
        solicitud.save()

    return redirect('lista_solicitudes')


# ===================================================================
# API GEOJSON
# ===================================================================

@login_required
def api_productores_geojson(request):
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
                "area_hectareas": float(productor.area_hectareas or 0),
                "detalle_url": f"/productores/{productor.id}/"
            }
        })

    return JsonResponse({"type": "FeatureCollection", "features": features})
