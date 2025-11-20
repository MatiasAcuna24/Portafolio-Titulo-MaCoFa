from django.contrib import admin
from .models import *

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ("nombre","descripcion")

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ("nombre", "categoria", "precio", "stock")
    list_filter = ("categoria","nombre")
    search_fields = ("nombre",)
   

@admin.register(Promocion)
class PromocionAdmin(admin.ModelAdmin):
    list_display = ("nombre", "tipo", "valor", "activo", "fecha_inicio", "fecha_fin")
    list_filter = ("activo", "tipo")
    search_fields = ("nombre", "descripcion")
    filter_horizontal = ("productos",)


@admin.register(PromocionProducto)
class PromocionProductoAdmin(admin.ModelAdmin):
    list_display = ("producto", "promocion")
    search_fields = ("producto__nombre", "promocion__nombre")


@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = ("titulo", "activo", "orden")
    list_editable = ("activo", "orden")

@admin.register(Cupon)
class CuponAdmin(admin.ModelAdmin):
    list_display = ("codigo", "tipo", "valor", "activo", "fecha_inicio", "fecha_expiracion", "usos_actuales", "uso_maximo")
    list_filter = ("activo", "tipo")
    search_fields = ("codigo",)
    
admin.site.register(ZonaDespacho)
admin.site.register(Direccion)
admin.site.register(Carrito)
admin.site.register(CarritoItem)
admin.site.register(Pedido)
admin.site.register(ItemPedido)
admin.site.register(PedidoPersonalizado)
admin.site.register(HistorialEstadoPedido)