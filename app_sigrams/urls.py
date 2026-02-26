from django.urls import path
from . import views
from .views import (
    ListaMarcasView,
    NuevaMarcaView,
    EditarMarcaView,
    DetalleMarcaView,
    cargar_campos,
    get_marcas_por_productor,
    get_campos_por_productor,
)

urlpatterns = [

    # =========================
    # AUTENTICACIÓN
    # =========================
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),

    # =========================
    # PRODUCTORES
    # =========================
    path('productores/', views.lista_productores, name='lista_productores'),
    path('productores/nuevo/', views.nuevo_productor, name='nuevo_productor'),
    path('productores/<int:pk>/', views.detalle_productor, name='detalle_productor'),
    path('productores/<int:pk>/editar/', views.editar_productor, name='editar_productor'),
    path('productores/<int:pk>/eliminar/', views.eliminar_productor, name='eliminar_productor'),

    # =========================
    # MARCAS Y SEÑALES
    # =========================
    path('marcas/', ListaMarcasView.as_view(), name='lista_marcas'),
    path('marcas/nueva/', NuevaMarcaView.as_view(), name='nueva_marca'),
    path('marcas/<int:pk>/editar/', EditarMarcaView.as_view(), name='editar_marca'),
    path('marcas/<int:pk>/', DetalleMarcaView.as_view(), name='detalle_marca'),

    # =========================
    # SOLICITUDES
    # =========================
    path('solicitudes/', views.lista_solicitudes, name='lista_solicitudes'),
    path('solicitudes/nueva/', views.nueva_solicitud, name='nueva_solicitud'),
    path('solicitudes/<int:pk>/', views.detalle_solicitud, name='detalle_solicitud'),
    path('solicitudes/<int:pk>/editar/', views.editar_solicitud, name='editar_solicitud'),
    path('solicitudes/<int:pk>/revision/', views.revision_solicitud, name='revision_solicitud'),
    path('solicitudes/<int:pk>/<str:accion>/', views.cambiar_estado_solicitud, name='cambiar_estado_solicitud'),
    path('mis-solicitudes/', views.mis_solicitudes, name='mis_solicitudes'),
    path('dashboard-solicitudes/', views.dashboard_solicitudes, name='dashboard_solicitudes'),

    # =========================
    # AJAX (IMPORTANTE: agrupado)
    # =========================
    path('ajax/marcas/<int:productor_id>/', get_marcas_por_productor, name='ajax_marcas'),
    path('ajax/campos/<int:productor_id>/', get_campos_por_productor, name='ajax_campos'),
    path('ajax/imagenes-marcas/', views.get_imagenes_marcas, name='ajax_imagenes_marcas'),

    # =========================
    # OTRAS VISTAS
    # =========================
    path('cargar-campos/', cargar_campos, name='cargar_campos'),

    # =========================
    # API
    # =========================
    path('api/productores/geojson/', views.api_productores_geojson, name='api_productores_geojson'),

    # =========================
    # REPORTES
    # =========================
    path('reportes/ingresos/', views.reporte_ingresos, name='reporte_ingresos'),


    # URL temporal para verificar que las vistas funcionan
    path('test/marcas/', views.test_marcas_view, name='test_marcas'),


    path('documentos/<int:documento_id>/eliminar/', views.eliminar_documento, name='eliminar_documento'),

    # Rutas para reportes PDF y Excel
    path('reportes/productores/pdf/', views.reporte_productores_pdf, name='reporte_productores_pdf'),
    path('reportes/marcas/pdf/', views.reporte_marcas_pdf, name='reporte_marcas_pdf'),
    path('reportes/solicitudes/pdf/', views.reporte_solicitudes_pdf, name='reporte_solicitudes_pdf'),
    path('reportes/productores/excel/', views.reporte_productores_excel, name='reporte_productores_excel'),
    path('reportes/marcas/excel/', views.reporte_marcas_excel, name='reporte_marcas_excel'),
    path('reportes/solicitudes/excel/', views.reporte_solicitudes_excel, name='reporte_solicitudes_excel'),

    # Ruta para el dashboard del administrador
    path('admin-dashboard/', views.dashboard_admin, name='dashboard_admin'),
    
    # Rutas para reportes de usuarios (solo para admin)
    path('reporte/usuarios/pdf/', views.reporte_usuarios_pdf, name='reporte_usuarios_pdf'),
    path('reporte/usuarios/excel/', views.reporte_usuarios_excel, name='reporte_usuarios_excel'),

]
