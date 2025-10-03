from django.contrib import admin
from .models import (
    Categoria, Producto, Promocion, Banner,
    ZonaDespacho, Direccion, Carrito, CarritoItem,
    Pedido, ItemPedido, PedidoPersonalizado, HistorialEstadoPedido
)

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

admin.site.register(Banner)
admin.site.register(ZonaDespacho)
admin.site.register(Direccion)
admin.site.register(Carrito)
admin.site.register(CarritoItem)
admin.site.register(Pedido)
admin.site.register(ItemPedido)
admin.site.register(PedidoPersonalizado)
admin.site.register(HistorialEstadoPedido)