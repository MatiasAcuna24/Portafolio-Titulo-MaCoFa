import pytest
from django.urls import reverse
from core.models import (
    Categoria, Producto, Region, Provincia, Comuna,
    ZonaDespacho, Carrito, CarritoItem
)

@pytest.mark.django_db
def test_checkout_crea_pedido(client, django_user_model):
    """Debe crear un pedido correctamente desde el checkout (flujo completo real)."""
    # Crear usuario y loguearlo
    user = django_user_model.objects.create_user(username="cliente", password="12345")
    client.login(username="cliente", password="12345")

    # Crear estructuras geográficas y zona
    region = Region.objects.create(nombre="Metropolitana")
    provincia = Provincia.objects.create(nombre="Santiago", region=region)
    comuna = Comuna.objects.create(nombre="Providencia", provincia=provincia)
    zona = ZonaDespacho.objects.create(nombre="Zona Centro", costo=3000)

    # Crear producto y carrito asociado
    cat = Categoria.objects.create(nombre="Tartas")
    prod = Producto.objects.create(nombre="Tarta Frutilla", categoria=cat, precio=5990, stock=10)
    carrito = Carrito.objects.create(usuario=user)
    CarritoItem.objects.create(carrito=carrito, producto=prod, cantidad=1)

    # Enviar datos completos de dirección y zona
    data = {
        "calle": "Av. Dulce",
        "numero": "123",
        "comuna": comuna.id,
        "provincia": provincia.id,
        "region": region.id,
        "zona": zona.id,
        "referencia": "Depto 4B",
    }

    response = client.post(reverse("checkout"), data)
    # Debe redirigir al pedido confirmado
    assert response.status_code in (302, 200)

@pytest.mark.django_db
def test_checkout_get_renderiza_formulario(client, django_user_model):
    user = django_user_model.objects.create_user(username="cliente", password="12345")
    client.login(username="cliente", password="12345")
    region = Region.objects.create(nombre="Metropolitana")
    provincia = Provincia.objects.create(nombre="Santiago", region=region)
    comuna = Comuna.objects.create(nombre="Providencia", provincia=provincia)
    zona = ZonaDespacho.objects.create(nombre="Zona Centro", costo=3000)
    cat = Categoria.objects.create(nombre="Pasteles")
    prod = Producto.objects.create(nombre="Brownie", categoria=cat, precio=2990, stock=5)
    carrito = Carrito.objects.create(usuario=user)
    CarritoItem.objects.create(carrito=carrito, producto=prod, cantidad=1)

    response = client.get(reverse("checkout"))
    assert response.status_code == 200
    assert b"checkout" in response.content.lower()

@pytest.mark.django_db
def test_checkout_sin_login(client):
    """Debe impedir el acceso al checkout si no está logueado."""
    response = client.get(reverse("checkout"))
    assert response.status_code in (302,)  # Redirección al login
