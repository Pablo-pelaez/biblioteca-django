from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy, reverse
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
)
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib import messages
from django.db import transaction
from django.utils import timezone
from django.http import JsonResponse
from django.views import View

from .models import Libro, Prestamo, PerfilUsuario
from .forms import LibroForm, RegistroForm


class HomeView(TemplateView):
    template_name = 'libros/home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_libros'] = Libro.objects.count()
        context['libros_disponibles'] = Libro.objects.filter(cantidad_stock__gt=0).count()
        context['prestamos_activos'] = Prestamo.objects.filter(fecha_devolucion__isnull=True).count()
        context['libros_recientes'] = Libro.objects.order_by('-fecha_creacion')[:5]
        return context


class LibroListView(ListView):
    model = Libro
    template_name = 'libros/libro_list.html'
    context_object_name = 'libros'
    paginate_by = 12
    
    def get_queryset(self):
        queryset = Libro.objects.all()
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                titulo__icontains=search
            ) | queryset.filter(
                autor__icontains=search
            )
        return queryset.order_by('titulo')


class LibroDetailView(DetailView):
    model = Libro
    template_name = 'libros/libro_detail.html'
    context_object_name = 'libro'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            # Verificar si el usuario ya tiene este libro prestado
            context['ya_prestado'] = Prestamo.objects.filter(
                usuario=self.request.user,
                libro=self.object,
                fecha_devolucion__isnull=True
            ).exists()
        return context


class AdministradorRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return (
            self.request.user.is_authenticated and 
            hasattr(self.request.user, 'perfil') and 
            self.request.user.perfil.es_administrador
        )
    
    def handle_no_permission(self):
        messages.error(self.request, 'No tienes permisos para acceder a esta página.')
        return redirect('libros:home')


class UsuarioRegularRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return (
            self.request.user.is_authenticated and 
            hasattr(self.request.user, 'perfil') and 
            self.request.user.perfil.es_usuario_regular
        )
    
    def handle_no_permission(self):
        messages.error(self.request, 'No tienes permisos para acceder a esta página.')
        return redirect('libros:home')


class LibroCreateView(AdministradorRequiredMixin, CreateView):
    model = Libro
    form_class = LibroForm
    template_name = 'libros/libro_form.html'
    success_url = reverse_lazy('libros:libro_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Libro creado exitosamente.')
        return super().form_valid(form)


class LibroUpdateView(AdministradorRequiredMixin, UpdateView):
    model = Libro
    form_class = LibroForm
    template_name = 'libros/libro_form.html'
    success_url = reverse_lazy('libros:libro_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Libro actualizado exitosamente.')
        return super().form_valid(form)


class LibroDeleteView(AdministradorRequiredMixin, DeleteView):
    model = Libro
    template_name = 'libros/libro_confirm_delete.html'
    success_url = reverse_lazy('libros:libro_list')
    
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Libro eliminado exitosamente.')
        return super().delete(request, *args, **kwargs)


class PrestarLibroView(UsuarioRegularRequiredMixin, View):
    def post(self, request, libro_id):
        libro = get_object_or_404(Libro, id=libro_id)
        
        # Verificar si ya tiene el libro prestado
        if Prestamo.objects.filter(
            usuario=request.user, 
            libro=libro, 
            fecha_devolucion__isnull=True
        ).exists():
            messages.error(request, 'Ya tienes este libro prestado.')
            return redirect('libros:libro_detail', pk=libro.id)
        
        # Verificar disponibilidad
        if libro.cantidad_disponible <= 0:
            messages.error(request, 'Este libro no está disponible.')
            return redirect('libros:libro_detail', pk=libro.id)
        
        # Crear préstamo
        Prestamo.objects.create(
            usuario=request.user,
            libro=libro
        )
        
        messages.success(request, f'Has tomado prestado "{libro.titulo}" exitosamente.')
        return redirect('libros:mis_prestamos')#xd


class DevolverLibroView(UsuarioRegularRequiredMixin, View):
    def post(self, request, prestamo_id):
        prestamo = get_object_or_404(
            Prestamo, 
            id=prestamo_id, 
            usuario=request.user,
            fecha_devolucion__isnull=True
        )
        
        prestamo.devolver()
        messages.success(request, f'Has devuelto "{prestamo.libro.titulo}" exitosamente.')
        return redirect('libros:mis_prestamos')


class MisPrestamosView(UsuarioRegularRequiredMixin, ListView):
    template_name = 'libros/mis_prestamos.html'
    context_object_name = 'prestamos'
    paginate_by = 10
    
    def get_queryset(self):
        return Prestamo.objects.filter(usuario=self.request.user).order_by('-fecha_prestamo')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['prestamos_activos'] = Prestamo.objects.filter(
            usuario=self.request.user,
            fecha_devolucion__isnull=True
        )
        context['prestamos_devueltos'] = Prestamo.objects.filter(
            usuario=self.request.user,
            fecha_devolucion__isnull=False
        )
        return context


class RegisterView(CreateView):
    form_class = RegistroForm
    template_name = 'registration/register.html'
    success_url = reverse_lazy('libros:home')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)
        messages.success(self.request, 'Te has registrado exitosamente.')
        return response
    