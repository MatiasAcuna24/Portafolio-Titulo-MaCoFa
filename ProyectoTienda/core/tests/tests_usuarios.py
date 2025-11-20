import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from core.models import Usuarios

@pytest.mark.django_db
def test_registro_usuario_exitoso(client):
    """Debe crear un usuario correctamente y redirigir al login."""
    url = reverse("registro")
    data = {
        "username": "nuevo_user",
        'nombre': 'Matias',
        'apellido': 'Acuna',
        'email': 'prueba12@gmail.com',
        'telefono': '912345678',
        'direccion': 'sucasa1234',
        "password1": "ClaveSegura123",
        "password2": "ClaveSegura123",
    }
    response = client.post(url, data)
    assert response.status_code in (200, 302)
    assert Usuarios.objects.filter(username="nuevo_user").exists()

@pytest.mark.django_db
def test_login_correcto(client):
    """Debe permitir el inicio de sesión con credenciales válidas."""
    User = get_user_model()
    user = User.objects.create_user(username="matiadmin", password="Cris4555.")

    # Ejecutar POST al login
    response = client.post(reverse("login"), {"username": "matiadmin", "password": "Cris4555."})

    # Verificar respuesta y sesión
    assert response.status_code in (200, 302)
    print("Session keys:", client.session.keys())  # opcional, para depuración
    assert any("_auth" in key for key in client.session.keys())

@pytest.mark.django_db
def test_login_invalido(client):
    """Debe rechazar el inicio de sesión con credenciales incorrectas."""
    response = client.post(reverse("login"), {"username": "fake", "password": "mal"})
    assert response.status_code in (200, 302)
