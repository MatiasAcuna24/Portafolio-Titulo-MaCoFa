from django.urls import path
from .views import  *
from . import views
from django.views.generic import TemplateView

urlpatterns = [
    path('',index, name='index'),
    path('contacto/', contacto, name='contacto'),

    #usuarios_admin
    path("admin/usuarios/", views.listar_usuarios, name="listar_usuarios"),
    path("admin/usuarios/<int:user_id>/cambiar-rol/", views.cambiar_rol_usuario, name="cambiar_rol_usuario"),

    #perfil
    path('perfil/', perfil_usuario, name='perfil_usuario'),
    path("perfil/admin/", perfil_admin, name="perfil_admin"),
    path('perfil/editar/', editar_perfil, name='editar_perfil'),
    path('perfil/cambiar-contrasena/', cambiar_contrasena, name='cambiar_contrasena'),

    #productos
    path('productos',productos, name='productos'),
    path("productos/<int:producto_id>/", detalle_producto, name="detalle_producto"),
    #producto admin
    path("producto/crear/", crear_producto, name="crear_producto"),
    path("producto/<int:producto_id>/eliminar/", eliminar_producto, name="eliminar_producto"),
    path("producto/<int:producto_id>/actualizar/", actualizar_producto, name="actualizar_producto"),

    #carrito
    path('agregar/<int:producto_id>/', agregar_al_carrito, name='agregar_al_carrito'),
    path('carrito/', ver_carrito, name='ver_carrito'),
    path('carrito/modificar/<int:item_id>/<str:accion>/', modificar_cantidad, name='modificar_cantidad'),
    path('carrito/eliminar/<int:item_id>/', eliminar_item, name='eliminar_item'),
    path('carrito/vaciar/', vaciar_carrito, name='vaciar_carrito'),
    
    #Pedidos
    path('checkout/', checkout, name='checkout'),
    path('ajax/cargar_provincias/', cargar_provincias, name='cargar_provincias'),
    path('ajax/cargar_comunas/', cargar_comunas, name='cargar_comunas'),
    path("checkout/<int:pedido_id>/", pedido_confirmado, name="pedido_confirmado"),
    path("mis-pedidos/", ver_pedidos, name="ver_pedidos"),
    
    #Pedidos personalizados
    path("pedidos/<int:pedido_id>/personalizado/", pedido_personalizado, name="personalizado_editar"),

    #PedidosAdmin
    path("pedido/<int:pedido_id>/actualizar/", actualizar_estado_pedido, name="actualizar_estado_pedido"),
    path("pedido/<int:pedido_id>/eliminar/", eliminar_pedido, name="eliminar_pedido"),
    path('admin/reporte_pedidos_excel/', exportar_pedidos_excel, name='reporte_pedidos_excel'),
    path('admin/reporte_pedidos_pdf/', exportar_pedidos_pdf, name='reporte_pedidos_pdf'),

    #Registro y login
    path('registro/', registro, name='registro'),
    path("login/", login_view, name="login"),
    path("logout/", logout_view, name="logout"),
]




   
    
