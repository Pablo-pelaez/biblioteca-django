from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Libro, PerfilUsuario


class LibroForm(forms.ModelForm):
    class Meta:
        model = Libro
        fields = ['titulo', 'autor', 'año_publicacion', 'cantidad_stock']
        widgets = {
            'titulo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Título del libro'
            }),
            'autor': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre del autor'
            }),
            'año_publicacion': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Año de publicación'
            }),
            'cantidad_stock': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Cantidad en stock',
                'min': '1'
            }),
        }
    
    def clean_año_publicacion(self):
        año = self.cleaned_data['año_publicacion']
        if año < 1000 or año > 2030:
            raise forms.ValidationError('El año debe estar entre 1000 y 2030.')
        return año
    
    def clean_cantidad_stock(self):
        cantidad = self.cleaned_data['cantidad_stock']
        if cantidad < 1:
            raise forms.ValidationError('La cantidad debe ser al menos 1.')
        return cantidad


class RegistroForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True, label='Nombre')
    last_name = forms.CharField(max_length=30, required=True, label='Apellido')
    rol = forms.ChoiceField(
        choices=PerfilUsuario.ROLES,
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2', 'rol')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Agregar clases CSS a todos los campos
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            
        # Personalizar labels
        self.fields['username'].label = 'Nombre de usuario'
        self.fields['email'].label = 'Correo electrónico'
        self.fields['password1'].label = 'Contraseña'
        self.fields['password2'].label = 'Confirmar contraseña'
        self.fields['rol'].label = 'Tipo de usuario'
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        
        if commit:
            user.save()
            # Actualizar el perfil con el rol seleccionado
            perfil, created = PerfilUsuario.objects.get_or_create(user=user)
            perfil.rol = self.cleaned_data['rol']
            perfil.save()
        
        return user