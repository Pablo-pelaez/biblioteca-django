from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'libros'

urlpatterns = [
    # Páginas principales
    path('', views.HomeView.as_view(), name='home'),
    path('libros/', views.LibroListView.as_view(), name='libro_list'),
    path('libros/<int:pk>/', views.LibroDetailView.as_view(), name='libro_detail'),
    
    # Gestión de libros (solo administradores)
    path('libros/crear/', views.LibroCreateView.as_view(), name='libro_create'),
    path('libros/<int:pk>/editar/', views.LibroUpdateView.as_view(), name='libro_update'),
    path('libros/<int:pk>/eliminar/', views.LibroDeleteView.as_view(), name='libro_delete'),
    
    # Préstamos (solo usuarios regulares)
    path('prestar/<int:libro_id>/', views.PrestarLibroView.as_view(), name='prestar_libro'),
    path('devolver/<int:prestamo_id>/', views.DevolverLibroView.as_view(), name='devolver_libro'),
    path('mis-prestamos/', views.MisPrestamosView.as_view(), name='mis_prestamos'),
    
    # Autenticación
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/', views.RegisterView.as_view(), name='register'),
]