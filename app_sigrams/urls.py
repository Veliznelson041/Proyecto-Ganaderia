from django.urls import path
from . import views
from .views import ListaMarcasView, NuevaMarcaView, EditarMarcaView, DetalleMarcaView, cargar_campos


urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),

    # URLs para Productores
    path('productores/', views.lista_productores, name='lista_productores'),
    path('productores/nuevo/', views.nuevo_productor, name='nuevo_productor'),
    path('productores/<int:pk>/', views.detalle_productor, name='detalle_productor'),
    path('productores/<int:pk>/editar/', views.editar_productor, name='editar_productor'),
    path('productores/<int:pk>/eliminar/', views.eliminar_productor, name='eliminar_productor'),
    
    # URLs para Marcas y Señales
    path('marcas/', ListaMarcasView.as_view(), name='lista_marcas'),
    path('marcas/nueva/', NuevaMarcaView.as_view(), name='nueva_marca'),
    path('marcas/<int:pk>/editar/', EditarMarcaView.as_view(), name='editar_marca'),
    path('marcas/<int:pk>/', DetalleMarcaView.as_view(), name='detalle_marca'),
    path('cargar-campos/', cargar_campos, name='cargar_campos'),
        
    # URLs para Solicitudes
    path('solicitudes/', views.lista_solicitudes, name='lista_solicitudes'),
    path('solicitudes/nueva/', views.nueva_solicitud, name='nueva_solicitud'),
    path('solicitudes/<int:pk>/<str:estado>/', views.cambiar_estado_solicitud, name='cambiar_estado_solicitud'),
    
    # API
    path('api/productores/geojson/', views.api_productores_geojson, name='api_productores_geojson'),

    # URLs para AJAX
    path('ajax/campos/<int:productor_id>/', views.get_campos_por_productor, name='ajax_campos'),
    path('ajax/imagenes-marcas/', views.get_imagenes_marcas, name='ajax_imagenes_marcas'),

]