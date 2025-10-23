from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Usuarios, Producto, PedidoPersonalizado

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = Usuarios
        fields = (
            'username', 'nombre', 'apellido',
            'email', 'telefono', 'direccion',
            'password1', 'password2'
        )
        labels = {
            'username': 'Nombre de usuario',
            'nombre': 'Nombre',
            'apellido': 'Apellido',
            'email': 'Correo electrónico',
            'telefono': 'Teléfono',
            'direccion': 'Dirección',
            'password1': 'Contraseña',
            'password2': 'Confirmar contraseña',
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if Usuarios.objects.filter(email=email).exists():
            raise forms.ValidationError("Este correo ya está registrado.")
        return email
    
class PerfilUsuarioForm(forms.ModelForm):
    class Meta:
        model = Usuarios
        fields = ['first_name', 'last_name', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Apellido'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Correo electrónico'
            }),
        }
        labels = {
            'first_name': 'Nombre',
            'last_name': 'Apellido',
            'email': 'Correo electrónico'
        }

class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ["nombre","slug", "precio", "stock", "categoria", "imagen"]
        widgets = {
            "nombre": forms.TextInput(attrs={"class": "form-control", "required": True}),
            "slug": forms.TextInput(attrs={"class": "form-control", "required": True}),
            "precio": forms.NumberInput(attrs={"class": "form-control", "step": "0.01", "min": "0", "required": True}),
            "stock": forms.NumberInput(attrs={"class": "form-control", "min": "0", "value": "0", "required": True}),
            "categoria": forms.Select(attrs={"class": "form-select", "required": True}),
            "imagen": forms.ClearableFileInput(attrs={"class": "form-control", "accept": "image/*"}),
        }

class ActualizarProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ["nombre", "precio", "stock", "categoria", "imagen"]
        widgets = {
            "nombre": forms.TextInput(attrs={"class": "form-control", "required": True}),
            "precio": forms.NumberInput(attrs={"class": "form-control", "step": "0.01", "min": "0", "required": True}),
            "stock": forms.NumberInput(attrs={"class": "form-control", "min": "0", "value": "0", "required": True}),
            "categoria": forms.Select(attrs={"class": "form-select", "required": True}),
            "imagen": forms.ClearableFileInput(attrs={"class": "form-control", "accept": "image/*"}),
        }

class PedidoPersonalizadoForm(forms.ModelForm):
    class Meta:
        model = PedidoPersonalizado
        fields = [
            "descripcion",
            "mensaje_en_torta",
            "color_predominante",
            "fecha_evento",
            "archivo_referencia",
        ]
        widgets = {
            "descripcion": forms.Textarea(attrs={"class": "form-control", "rows": 4, "required": True}),
            "mensaje_en_torta": forms.TextInput(attrs={"class": "form-control", "maxlength": 80}),
            "color_predominante": forms.TextInput(attrs={"class": "form-control", "maxlength": 40, "placeholder": "Ej: rosa pastel"}),
            "fecha_evento": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "archivo_referencia": forms.ClearableFileInput(attrs={"class": "form-control", "accept": ".jpg,.jpeg,.png,.pdf"}),
        }