import pytest
from django.urls import reverse
from core.models import Categoria, Producto

@pytest.mark.django_db
def test_listar_productos(client):
    """Debe listar los productos disponibles."""
    cat = Categoria.objects.create(nombre="Pasteles", descripcion="Deliciosos")
    Producto.objects.create(nombre="Torta Chocolate", categoria=cat, precio=9990)
    response = client.get(reverse("productos"))
    assert response.status_code == 200
    assert b"Torta" in response.content

@pytest.mark.django_db
def test_filtrar_por_categoria(client):
    """Debe filtrar los productos por categoría."""
    cat1 = Categoria.objects.create(nombre="Donas")
    cat2 = Categoria.objects.create(nombre="Galletas")
    Producto.objects.create(nombre="Dona frutilla", categoria=cat1, precio=1990,slug="dona-frutilla")
    Producto.objects.create(nombre="Galleta chips", categoria=cat2, precio=1490,slug="galleta-chips")
    response = client.get(reverse("productos") + f"?categoria={cat1.id}")
    assert response.status_code == 200
    assert b"Dona" in response.content
   

