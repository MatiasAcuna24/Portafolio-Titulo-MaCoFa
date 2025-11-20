import pytest
from django.urls import reverse
from core.models import Categoria, Producto

@pytest.mark.django_db
def test_agregar_al_carrito(client):
    """Debe agregar un producto al carrito."""
    cat = Categoria.objects.create(nombre="Galletas")
    prod = Producto.objects.create(nombre="Galleta chips", categoria=cat, precio=1490)
    response = client.post(reverse("agregar_al_carrito", args=[prod.id]))
    assert response.status_code in (200, 302)

@pytest.mark.django_db
def test_modificar_cantidad_carrito(client):
    """Debe permitir cambiar la cantidad de un producto en el carrito."""
    cat = Categoria.objects.create(nombre="Helados")
    prod = Producto.objects.create(nombre="Helado vainilla", categoria=cat, precio=1990)
    client.post(reverse("agregar_al_carrito", args=[prod.id]))
    response = client.post(reverse("modificar_cantidad", args=[prod.id,"restar"]), {"cantidad": 2})
    assert response.status_code in (200, 302)

@pytest.mark.django_db
def test_eliminar_del_carrito(client):
    """Debe eliminar un producto del carrito."""
    cat = Categoria.objects.create(nombre="Tartas")
    prod = Producto.objects.create(nombre="Tarta de frutilla", categoria=cat, precio=5990)
    client.post(reverse("agregar_al_carrito", args=[prod.id]))
    response = client.post(reverse("eliminar_item", args=[prod.id]))
    assert response.status_code in (200, 302)
