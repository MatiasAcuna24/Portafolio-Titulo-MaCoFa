import openpyxl
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages  # Import messages for success/error notifications
from .forms import * # Import the forms from your forms.py
from .models import *  # Import the Usuarios model
from django.core.paginator import Paginator  # Import Paginator for pagination
from django.db.models import Q 
from django.conf import settings  # Import settings for STATIC_URL
from decimal import Decimal  # Import Decimal for currency calculations
from django.views.decorators.http import require_POST, require_http_methods  # Import require_POST and require_http_methods for HTTP method restrictions
from django.contrib.auth.decorators import login_required, user_passes_test  # Import login_required and user_passes_test for view protection
from django.contrib.admin.views.decorators import staff_member_required  # Import staff_member_required for admin-only views
from django.utils import timezone  # Import timezone for date/time operations
from django.utils.crypto import get_random_string  # Import get_random_string for generating random strings
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from core.notifications import *
from django.core.mail import send_mail  # Import send_mail for sending emails
from django.http import JsonResponse  # Import JsonResponse for AJAX responses
from django.http import HttpResponse  # Import HttpResponse for file responses
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from django.http import FileResponse
from io import BytesIO

# Create your views here.

def index(request):
    return render(request, 'core/index.html')

@login_required
def perfil_usuario(request):
    usuario = request.user  # ✅ obtiene el usuario logueado

    return render(request, "usuarios/perfil.html", {
        "usuario": usuario
    })
#usuarios admin
@staff_member_required
def perfil_admin(request):
    return render(request, "usuarios/admin/perfil_admin.html")

@staff_member_required
def listar_usuarios(request):
    usuarios = Usuarios.objects.all()
    return render(request, "usuarios/admin/listar_usuarios.html", {"usuarios": usuarios})

@staff_member_required
def cambiar_rol_usuario(request, user_id):
    usuario = get_object_or_404(Usuarios, id=user_id)
    
    if request.method == "POST":
        nuevo_rol = request.POST.get("rol")
        if nuevo_rol == "admin":
            usuario.is_staff = True
            usuario.is_superuser = True  # opcional si quieres que tenga acceso total
        else:
            usuario.is_staff = False
            usuario.is_superuser = False
        usuario.save()
        return redirect("listar_usuarios")
    
    return render(request, "usuarios/admin/cambiar_rol.html", {"usuario": usuario})

@login_required
def editar_perfil(request):
    usuario = request.user

    if request.method == 'POST':
        form = PerfilUsuarioForm(request.POST, instance=usuario)
        if form.is_valid():
            form.save()
            messages.success(request, "✅ Tu perfil ha sido actualizado correctamente.")
            return redirect('perfil_usuario')
        else:
            messages.error(request, "❌ Por favor corrige los errores en el formulario.")
    else:
        form = PerfilUsuarioForm(instance=usuario)

    return render(request, 'usuarios/editar_perfil.html', {'form': form})

def productos(request):
    # Base: solo activos, optimizando la FK categoría y orden alfabético
    queryset = (Producto.objects
                .filter(activo=True)
                .select_related('categoria')
                .order_by('nombre'))

    # Todas las categorías para los chips
    categorias = Categoria.objects.all().order_by('nombre')

    # Filtro por categoría (?categoria=<id>)
    categoria_id = request.GET.get('categoria')
    categoria_seleccionada = None
    if categoria_id:
        categoria_seleccionada = get_object_or_404(Categoria, pk=categoria_id)
        queryset = queryset.filter(categoria=categoria_seleccionada)

    # (Opcional) búsqueda por texto (?q=)
    search = (request.GET.get('q') or '').strip()
    if search:
        queryset = queryset.filter(
            Q(nombre__icontains=search) | Q(descripcion__icontains=search)
        )

    # Paginación
    paginator = Paginator(queryset, 12)  # 12 productos por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    data = {
        'productos': page_obj.object_list,
        'categorias': categorias,
        'page_obj': page_obj,
        'is_paginated': page_obj.has_other_pages(),
        'categoria_seleccionada': categoria_seleccionada,
        'q': search,
    }
    return render(request, 'catalogo/productos.html', data)


#producto admin
@login_required
@user_passes_test(lambda u: u.is_staff)
def eliminar_producto(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    if request.method == "POST":
        producto.delete()
        messages.success(request, f"El producto '{producto.nombre}' fue eliminado exitosamente.")
    return redirect("productos")

@login_required
@user_passes_test(lambda u: u.is_staff)
def actualizar_producto(request, producto_id):
    producto = get_object_or_404(Producto, pk=producto_id)
    if request.method == "POST":
        form = ActualizarProductoForm(request.POST, request.FILES, instance=producto)
        if form.is_valid():
            form.save()  # el save del modelo mantiene o genera slug si está vacío
            messages.success(request, "Producto actualizado exitosamente.")
            return redirect("productos")
        messages.error(request, "Revisa los campos del formulario.")
    else:
        form = ActualizarProductoForm(instance=producto)
    return render(request, "catalogo/actualizar_producto.html", {"form": form})

#admin pedidos
@login_required
@user_passes_test(lambda u: u.is_staff)
def crear_producto(request):
    if request.method == "POST":
        form = ProductoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Producto creado exitosamente.")
            return redirect("productos")
        else:
            print(form.errors)
            messages.error(request, "Revisa los campos del formulario.")
    else:
        form = ProductoForm()

    return render(request, "catalogo/crear_producto.html", {"form": form})


@login_required
def agregar_al_carrito(request, producto_id):
    producto = get_object_or_404(Producto, pk=producto_id)


    if producto.stock < 1:
        messages.error(request, f"No hay stock disponible para {producto.nombre}.")
        return redirect('productos')

    carrito, _ = Carrito.objects.get_or_create(usuario=request.user)

    item, creado = CarritoItem.objects.get_or_create(
        carrito=carrito,
        producto=producto,
        defaults={'cantidad': 1}
    )

    if not creado:
        if producto.stock < 1:
            messages.error(request, f"Stock insuficiente para agregar más de {producto.nombre}.")
            return redirect('productos')
        item.cantidad += 1
        item.save()
    producto.stock -= 1
    producto.save()

    messages.success(request, f"Agregaste {producto.nombre} al carrito.")
    return redirect('ver_carrito')


@login_required
def ver_carrito(request):
    carrito, _ = Carrito.objects.get_or_create(usuario=request.user)
    
    items = carrito.items.select_related('producto').all()

    subtotal = sum(item.producto.precio * item.cantidad for item in items)
    descuento = 0  # podrías calcularlo si aplicas promociones
    total = subtotal - descuento

    return render(request, 'carrito/carrito.html', {
        'items': items,
        'subtotal': subtotal,
        'descuento': descuento,
        'total': total
    })

@login_required
def modificar_cantidad(request, item_id, accion):
    item = get_object_or_404(CarritoItem, pk=item_id, carrito__usuario=request.user)

    if accion == 'sumar':
        item.cantidad += 1
    elif accion == 'restar' and item.cantidad > 1:
        item.cantidad -= 1
    item.save()

    return redirect('ver_carrito')

@login_required
def eliminar_item(request, item_id):
    item = get_object_or_404(CarritoItem, pk=item_id, carrito__usuario=request.user)
    producto = item.producto

    # Reintegrar el stock
    producto.stock += item.cantidad
    producto.save()

    item.delete()

    messages.success(request, f"{producto.nombre} fue eliminado del carrito y el stock fue restablecido.")
    return redirect('ver_carrito')


@login_required
def vaciar_carrito(request):
    carrito = Carrito.objects.filter(usuario=request.user).first()
    if carrito:
        for item in carrito.items.all():
            item.producto.stock += item.cantidad
            item.producto.save()
        carrito.items.all().delete()
    messages.success(request, "Carrito vaciado y stock restablecido.")
    return redirect('ver_carrito')

@login_required
@require_http_methods(["GET", "POST"])
def checkout(request, pedido_id=None):
    carrito = get_object_or_404(Carrito, usuario=request.user)
    items = carrito.items.select_related('producto').all()

    if pedido_id:
        pedido = get_object_or_404(Pedido, id=pedido_id, usuario=request.user)
        return render(request, 'carrito/pedido_confirmado.html', {'pedido': pedido})

    if not items:
        messages.error(request, "Tu carrito está vacío.")
        return redirect('ver_carrito')

    if request.method == "POST":
        calle = request.POST.get("calle")
        numero = request.POST.get("numero")
        comuna_id = request.POST.get("comuna")
        provincia_id = request.POST.get("provincia")
        region_id = request.POST.get("region")
        referencia = request.POST.get("referencia", "")
        zona_id = request.POST.get("zona")

        if not all([calle, comuna_id, region_id, zona_id]):
            messages.error(request, "Todos los campos obligatorios deben ser completados.")
            return redirect('checkout')

        comuna = Comuna.objects.get(id=comuna_id)
        provincia = Provincia.objects.get(id=provincia_id) if provincia_id else comuna.provincia
        region = Region.objects.get(id=region_id)
        zona = ZonaDespacho.objects.filter(id=zona_id).first()

        direccion = Direccion.objects.create(
            usuario=request.user,
            alias="Dirección rápida",
            calle=calle,
            numero=numero,
            comuna=comuna,
            provincia=provincia,
            region=region,
            referencia=referencia,
            activa=True,
            zona=zona
        )

        subtotal = sum(item.producto.precio * item.cantidad for item in items)
        descuento = 0
        costo_despacho = zona.costo if zona else 0
        total = subtotal - descuento + costo_despacho

        numero_pedido = f"PED-{timezone.now().strftime('%Y%m%d')}-{get_random_string(6).upper()}"
        pedido = Pedido.objects.create(
            usuario=request.user,
            direccion_envio=direccion,
            subtotal=subtotal,
            descuento=descuento,
            costo_despacho=costo_despacho,
            total=total,
            estado='pendiente',
            zona=zona,
            numero=numero_pedido,
        )

        for item in items:
            ItemPedido.objects.create(
                pedido=pedido,
                producto=item.producto,
                cantidad=item.cantidad,
                precio_unitario=item.producto.precio
            )
            item.producto.stock -= item.cantidad
            item.producto.save()

        carrito.items.all().delete()

        if request.user.email:
            send_order_confirmation(request.user, pedido)

        messages.success(request, "¡Pedido creado exitosamente!")
        return redirect("pedido_confirmado", pedido_id=pedido.id)

    else:
        subtotal = sum(item.producto.precio * item.cantidad for item in items)
        descuento = 0
        zonas = ZonaDespacho.objects.all().order_by("costo")
        regiones = Region.objects.all().order_by("nombre")
        provincias = Provincia.objects.all().order_by("nombre")
        comunas = Comuna.objects.all().order_by("nombre")

        return render(request, 'carrito/checkout.html', {
            'items': items,
            'subtotal': subtotal,
            'descuento': descuento,
            'total': subtotal - descuento,
            'zonas': zonas,
            'regiones': regiones,
            'provincias': provincias,
            'comunas': comunas,
        })

def cargar_provincias(request):
    region_id = request.GET.get("region_id")
    provincias = list(Provincia.objects.filter(region_id=region_id).values("id", "nombre"))
    return JsonResponse(provincias, safe=False)

def cargar_comunas(request):
    provincia_id = request.GET.get("provincia_id")
    comunas = list(Comuna.objects.filter(provincia_id=provincia_id).values("id", "nombre"))
    return JsonResponse(comunas, safe=False)

@login_required
def pedido_confirmado(request, pedido_id):
    if request.user.is_staff:
        # 👑 Admin puede ver cualquier pedido
        pedido = get_object_or_404(Pedido, id=pedido_id)
    else:
        # 👤 Usuario normal solo puede ver los suyos
        pedido = get_object_or_404(Pedido, id=pedido_id, usuario=request.user)

    return render(request, 'pedidos/pedido_confirmado.html', {'pedido': pedido})

@login_required
def ver_pedidos(request):
    if request.user.is_staff:
        # 👑 Si es admin → ve todos los pedidos
        pedidos = Pedido.objects.all().order_by('-creado_en')
    else:
        # 👤 Si es usuario normal → ve solo los suyos
        pedidos = Pedido.objects.filter(usuario=request.user).order_by('-creado_en')

    return render(request, "pedidos/pedidos_usuario.html", {"pedidos": pedidos})

#pedido personalizado
@login_required
def pedido_personalizado(request, pedido_id):
    pedido = get_object_or_404(Pedido, pk=pedido_id)

    # Solo el dueño del pedido o staff (ajusta si tu modelo de usuario usa otro campo)
    if (getattr(pedido, "usuario_id", None) != request.user.id) and (not request.user.is_staff):
        messages.error(request, "No tienes permisos para editar este pedido.")
        return redirect("ver_pedidos")  # ajusta a tu nombre real

    personalizado, _created = PedidoPersonalizado.objects.get_or_create(pedido=pedido)

    if request.method == "POST":
        form = PedidoPersonalizadoForm(request.POST, request.FILES, instance=personalizado)
        if form.is_valid():
            form.save()
            messages.success(request, "Tus notas de personalización fueron guardadas.")
            return redirect("detalle_pedido", pedido_id=pedido.id)  # ajusta a tu vista de detalle
        messages.error(request, "Revisa los campos del formulario.")
    else:
        form = PedidoPersonalizadoForm(instance=personalizado)

    return render(request, "pedidos/personalizados/pedido_personalizado.html", {
        "pedido": pedido,
        "form": form,
        "personalizado": personalizado,
    })

#admin pedidos
@login_required
@user_passes_test(lambda u: u.is_staff)  # Solo admin
def actualizar_estado_pedido(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id)
    
    if request.method == "POST":
        nuevo_estado = request.POST.get("estado")
        mensaje_extra = request.POST.get("mensaje_extra", "")

        if nuevo_estado in ["pendiente", "preparando", "enviado", "entregado", "cancelado"]:
            pedido.estado = nuevo_estado
            pedido.save()
            messages.success(request, f"Estado del pedido actualizado a '{nuevo_estado.title()}'.")

            # ✉️ Enviar notificación al cliente
            if pedido.usuario and pedido.usuario.email:
                send_order_status_update(
                    pedido.usuario,
                    pedido,
                    nuevo_estado,
                    mensaje_extra
                )

        return redirect("ver_pedidos")

    return render(request, "pedidos/actualizar_pedido.html", {"pedido": pedido})

@login_required
@user_passes_test(lambda u: u.is_staff)  # 👈 solo administradores
def eliminar_pedido(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id)
    
    if request.method == "POST":
        if pedido.estado == "entregado":
            messages.error(request, "No se pueden eliminar pedidos ya entregados.")
        else:
            pedido.delete()
            messages.success(request, f"El pedido {pedido.numero} ha sido eliminado exitosamente.")
        
    return redirect("ver_pedidos")

@login_required
@user_passes_test(lambda u: u.is_staff)
def exportar_pedidos_excel(request):
    pedidos = Pedido.objects.select_related('usuario', 'direccion_envio').all().order_by('-id')

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Pedidos Dulce Arte"

    # Encabezados
    headers = ['N° Pedido', 'Cliente', 'Dirección', 'Zona', 'Total (CLP)', 'Estado', 'Fecha']
    ws.append(headers)

    for pedido in pedidos:
        ws.append([
            pedido.numero,
            pedido.usuario.username,
            str(pedido.direccion_envio),
            pedido.zona.nombre if pedido.zona else "",
            float(pedido.total),
            pedido.estado,
            pedido.creado_en.strftime('%Y-%m-%d %H:%M'),
        ])

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=Reporte_Pedidos_DulceArte.xlsx'
    wb.save(response)
    return response

@login_required
@user_passes_test(lambda u: u.is_staff)
def exportar_pedidos_pdf(request):
    pedidos = Pedido.objects.select_related('usuario', 'direccion_envio').all().order_by('-creado_en')

    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    c.setFont("Helvetica-Bold", 14)
    c.drawString(200, 770, "Reporte de Pedidos - Dulce Arte")

    y = 730
    c.setFont("Helvetica", 10)
    for pedido in pedidos:
        linea = f"{pedido.numero} - {pedido.usuario.username} - {pedido.total} CLP - {pedido.estado}"
        c.drawString(50, y, linea)
        y -= 20
        if y < 50:
            c.showPage()
            y = 770
            c.setFont("Helvetica", 10)

    c.save()
    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename='Reporte_Pedidos_DulceArte.pdf')

#Login y registro
def registro(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            user = authenticate(username=form.cleaned_data["username"], password=form.cleaned_data["password1"])
            login(request, user)
            messages.success(request, 'Usuario registrado con éxito.')
            return redirect('index')  # o la ruta que tú definas
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

@login_required
def cambiar_contrasena(request):
    if request.method == 'POST':
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            # Mantiene la sesión activa tras el cambio
            update_session_auth_hash(request, user)
            messages.success(request, "✅ Tu contraseña ha sido actualizada correctamente.")
            return redirect('perfil_usuario')
        else:
            messages.error(request, "❌ Por favor corrige los errores en el formulario.")
    else:
        form = PasswordChangeForm(user=request.user)

    return render(request, 'usuarios/cambiar_contrasena.html', {'form': form})

def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, "Has iniciado sesión correctamente.")
            return redirect("index")  # cambia "home" por tu vista de inicio
        else:
            messages.error(request, "Nombre de usuario o contraseña incorrectos.")
            redirect("login")

    return render(request, "registration/login.html")

def logout_view(request):
    logout(request)
    return redirect("index")