from django.urls import path
from . import views

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
    path('marcas/', views.lista_marcas, name='lista_marcas'),
    path('marcas/nueva/', views.nueva_marca, name='nueva_marca'),
    path('marcas/<int:pk>/', views.detalle_marca, name='detalle_marca'),
    path('marcas/<int:pk>/editar/', views.editar_marca, name='editar_marca'),
    
    # URLs para Solicitudes
    path('solicitudes/', views.lista_solicitudes, name='lista_solicitudes'),
    path('solicitudes/nueva/', views.nueva_solicitud, name='nueva_solicitud'),
    path('solicitudes/<int:pk>/<str:estado>/', views.cambiar_estado_solicitud, name='cambiar_estado_solicitud'),
]