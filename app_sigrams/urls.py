from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),

    # Futuras URLs para CRUD
    #path('productores/', views.lista_productores, name='lista_productores'),
    #path('productores/nuevo/', views.nuevo_productor, name='nuevo_productor'),
    #path('productores/<int:pk>/', views.detalle_productor, name='detalle_productor'),
    #path('productores/<int:pk>/editar/', views.editar_productor, name='editar_productor'),
    
    #path('marcas/', views.lista_marcas, name='lista_marcas'),
    #path('marcas/nueva/', views.nueva_marca, name='nueva_marca'),
    #path('marcas/<int:pk>/', views.detalle_marca, name='detalle_marca'),
    
    #path('solicitudes/', views.lista_solicitudes, name='lista_solicitudes'),
    #path('solicitudes/nueva/', views.nueva_solicitud, name='nueva_solicitud'),


]
