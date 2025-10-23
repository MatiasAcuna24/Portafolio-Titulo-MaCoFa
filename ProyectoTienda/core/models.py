from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.text import slugify
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal
from django.conf import settings

# Create your models here.

# 1. Usuario personalizado
class Usuarios(AbstractUser):
    nombre = models.CharField("Nombre", max_length=30, blank=True)
    apellido = models.CharField("Apellido", max_length=30, blank=True)
    telefono = models.CharField("Teléfono", max_length=15, blank=True)
    direccion = models.CharField("Dirección", max_length=255, blank=True)


    def __str__(self):
        return self.username
    
class Categoria(models.Model):
    nombre      = models.CharField(max_length=100)
    descripcion = models.TextField()

    class Meta:
        verbose_name_plural = "Categorías"
        ordering = ['nombre']

    def __str__(self):
        return self.nombre



class Producto(models.Model):
    categoria    = models.ForeignKey(Categoria, on_delete=models.CASCADE)
    slug = models.SlugField(max_length=140, unique=True, blank=True)
    nombre       = models.CharField(max_length=100)
    precio       = models.DecimalField(max_digits=10, decimal_places=2)
    descripcion  = models.TextField(max_length=500)
    imagen       = models.ImageField(upload_to='productos/')
    stock        = models.PositiveIntegerField(default=0)
    created_at   = models.DateTimeField(auto_now_add=True)
    updated_at   = models.DateTimeField(auto_now=True)
    activo = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = "Productos"
        ordering = ['nombre']

    def __str__(self):
        return self.nombre




# ---------------------------
# PROMOCIONES / BANNERS
# ---------------------------

class Promocion(models.Model):
    PORCENTAJE = "percent"
    FIJO = "fixed"
    TIPO_CHOICES = [(PORCENTAJE, "Porcentaje"), (FIJO, "Monto fijo")]

    nombre = models.CharField(max_length=120)
    descripcion = models.TextField(blank=True)
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES, default=PORCENTAJE)
    valor = models.DecimalField(max_digits=8, decimal_places=2, help_text="Si es porcentaje, 0–100; si es fijo, CLP.")
    activo = models.BooleanField(default=True)
    productos = models.ManyToManyField(Producto, blank=True, related_name="promociones")
    fecha_inicio = models.DateTimeField(null=True, blank=True)
    fecha_fin = models.DateTimeField(null=True, blank=True)

    def aplicar(self, subtotal: Decimal) -> Decimal:
        if not self.activo:
            return subtotal
        if self.tipo == self.PORCENTAJE:
            pct = max(Decimal("0"), min(self.valor, Decimal("100")))
            return subtotal * (Decimal("1") - pct / Decimal("100"))
        return max(Decimal("0"), subtotal - self.valor)

    def __str__(self):
        return self.nombre


class Banner(models.Model):
    titulo = models.CharField(max_length=120)
    imagen = models.ImageField(upload_to="banners/%Y/%m/")
    url_destino = models.URLField(blank=True)
    activo = models.BooleanField(default=True)
    orden = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["orden"]


# ---------------------------
# DIRECCIONES / ZONAS DESPACHO
# ---------------------------

class ZonaDespacho(models.Model):
    nombre = models.CharField(max_length=80, unique=True)
    costo = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    tiempo_estimado_horas = models.PositiveIntegerField(default=24)

    class Meta:
        verbose_name = "Zona de despacho"
        verbose_name_plural = "Zonas de despacho"
        ordering = ["costo"]

    def __str__(self):
        return f"{self.nombre} (CLP {self.costo})"

class Region(models.Model):
    nombre = models.CharField(max_length=100)

    class Meta:
        verbose_name_plural = "Regiones"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre


class Provincia(models.Model):
    nombre = models.CharField(max_length=100)
    region = models.ForeignKey(Region, on_delete=models.CASCADE, related_name="provincias")

    class Meta:
        verbose_name_plural = "Provincias"
        ordering = ["nombre"]

    def __str__(self):
        return f"{self.nombre} ({self.region.nombre})"


class Comuna(models.Model):
    nombre = models.CharField(max_length=100)
    provincia = models.ForeignKey(Provincia, on_delete=models.CASCADE, related_name="comunas")

    class Meta:
        verbose_name_plural = "Comunas"
        ordering = ["nombre"]

    def __str__(self):
        return f"{self.nombre} ({self.provincia.nombre})"

class Direccion(models.Model):
    usuario = models.ForeignKey(Usuarios,on_delete=models.CASCADE,related_name="direcciones")
    alias = models.CharField(max_length=60,blank=True,help_text="Ej: Casa, Trabajo")
    calle = models.CharField(max_length=120)
    numero = models.CharField(max_length=20, blank=True)
    # Relaciones normalizadas
    comuna = models.ForeignKey(Comuna,on_delete=models.PROTECT,related_name="direcciones")
    provincia = models.ForeignKey(Provincia,on_delete=models.PROTECT,related_name="direcciones",null=True,blank=True)
    region = models.ForeignKey(Region,on_delete=models.PROTECT,related_name="direcciones",null=True,blank=True)
    referencia = models.CharField(max_length=180, blank=True)
    zona = models.ForeignKey(ZonaDespacho,on_delete=models.PROTECT,null=True,blank=True)
    activa = models.BooleanField(default=True)

    class Meta:
        ordering = ["usuario", "id"]
        verbose_name = "Dirección"
        verbose_name_plural = "Direcciones"

    def __str__(self):
        return f"{self.calle} {self.numero}, {self.comuna.nombre}"



# ---------------------------
# CARRITO PERSISTENTE
# (si prefieres carrito de sesión, puedes omitir estos modelos)
# ---------------------------

class Carrito(models.Model):
    usuario    = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    creado_en  = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)
    activo        = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = "Carritos"
        ordering = ['-actualizado_en']

    def __str__(self):
        return f"Carro #{self.id} ({self.usuario.username})"

    @property
    def total(self):
        return sum(item.total for item in self.items.all())


class CarritoItem(models.Model):
    carrito        = models.ForeignKey(Carrito, related_name='items', on_delete=models.CASCADE)
    producto       = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad       = models.PositiveIntegerField(default=1)
    fecha_agregado = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Items del Carrito"
        ordering = ['-fecha_agregado']

    def __str__(self):
        return f"{self.cantidad}×{self.producto.nombre} (Carro #{self.carrito.id})"

    @property
    def total(self):
        return self.cantidad * self.producto.precio


# ---------------------------
# PEDIDOS
# ---------------------------

class Pedido(models.Model):
    class Estado(models.TextChoices):
        PENDIENTE = "pendiente", "Pendiente"
        PREPARACION = "preparacion", "En preparación"
        ENVIADO = "enviado", "Enviado"
        ENTREGADO = "entregado", "Entregado"
        CANCELADO = "cancelado", "Cancelado"

    usuario = models.ForeignKey(Usuarios, on_delete=models.PROTECT, related_name="pedidos")
    numero = models.CharField(max_length=20, unique=True)
    direccion_envio = models.ForeignKey(Direccion, on_delete=models.PROTECT, related_name="pedidos")
    zona = models.ForeignKey(ZonaDespacho, on_delete=models.PROTECT, related_name="pedidos")
    estado = models.CharField(max_length=20, choices=Estado.choices, default=Estado.PENDIENTE)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2)
    descuento = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    costo_despacho = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=12, decimal_places=2)
    notas_cliente = models.TextField(blank=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-creado_en"]
        indexes = [models.Index(fields=["numero"]), models.Index(fields=["estado"])]

    def __str__(self):
        return f"Pedido {self.numero}"

    def recomputar_totales(self):
        subtotal = sum((i.subtotal() for i in self.items.all()), Decimal("0"))
        self.subtotal = subtotal
        self.total = max(Decimal("0"), subtotal - self.descuento + self.costo_despacho)


class ItemPedido(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name="items")
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT)
    nombre = models.CharField(max_length=120)  # snapshot
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    cantidad = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])

    def subtotal(self) -> Decimal:
        return self.precio_unitario * self.cantidad


# ---------------------------
# PEDIDOS PERSONALIZADOS
# ---------------------------

class PedidoPersonalizado(models.Model):
    pedido = models.OneToOneField(Pedido, on_delete=models.CASCADE, related_name="personalizado", null=True, blank=True)
    descripcion = models.TextField(help_text="Descripción/Detalle solicitado por el cliente.")
    mensaje_en_torta = models.CharField(max_length=80, blank=True)
    color_predominante = models.CharField(max_length=40, blank=True)
    fecha_evento = models.DateField(null=True, blank=True)
    archivo_referencia = models.FileField(upload_to="pedidos_personalizados/%Y/%m/", blank=True)

    def __str__(self):
        return f"Personalizado de {self.pedido.numero if self.pedido_id else 'N/A'}"


# ---------------------------
# SEGUIMIENTO / HISTORIAL DE ESTADO
# ---------------------------

class HistorialEstadoPedido(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name="historial")
    estado = models.CharField(max_length=20, choices=Pedido.Estado.choices)
    comentario = models.CharField(max_length=180, blank=True)
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-creado_en"]


class Contacto(models.Model):
    nombre = models.CharField(max_length=100)
    email = models.EmailField()
    mensaje = models.TextField()

    def __str__(self):
        return f"Contacto de {self.nombre} ({self.email})"
    class Meta:
        verbose_name = "Contacto"
        verbose_name_plural = "Contactos"
        ordering = ['-id']