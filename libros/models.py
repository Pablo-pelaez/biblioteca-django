from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.utils import timezone


class Libro(models.Model):
    titulo = models.CharField(max_length=200, verbose_name="Título")
    autor = models.CharField(max_length=100, verbose_name="Autor")
    año_publicacion = models.IntegerField(
        verbose_name="Año de publicación",
        validators=[MinValueValidator(1000)]
    )
    cantidad_stock = models.PositiveIntegerField(
        default=1,
        verbose_name="Cantidad en stock"
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Libro"
        verbose_name_plural = "Libros"
        ordering = ['titulo']
    
    def __str__(self):
        return f"{self.titulo} - {self.autor}"
    
    @property
    def disponible(self):
        """Retorna True si hay stock disponible"""
        return self.cantidad_stock > 0
    
    @property
    def cantidad_prestados(self):
        """Retorna la cantidad de libros actualmente prestados"""
        return self.prestamos.filter(fecha_devolucion__isnull=True).count()
    
    @property
    def cantidad_disponible(self):
        """Retorna la cantidad disponible para préstamo"""
        return self.cantidad_stock - self.cantidad_prestados


class PerfilUsuario(models.Model):
    ROLES = [
        ('usuario', 'Usuario Regular'),
        ('administrador', 'Administrador'),
    ]
    
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE,
        related_name='perfil'
    )
    rol = models.CharField(
        max_length=20,
        choices=ROLES,
        default='usuario',
        verbose_name="Rol"
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Perfil de Usuario"
        verbose_name_plural = "Perfiles de Usuarios"
    
    def __str__(self):
        return f"{self.user.username} - {self.get_rol_display()}"
    
    @property
    def es_administrador(self):
        return self.rol == 'administrador'
    
    @property
    def es_usuario_regular(self):
        return self.rol == 'usuario'
    
    @property
    def libros_prestados_activos(self):
        """Retorna los libros que tiene prestados actualmente"""
        return Prestamo.objects.filter(
            usuario=self.user,
            fecha_devolucion__isnull=True
        )
    
    @property
    def historial_prestamos(self):
        """Retorna todo el historial de préstamos del usuario"""
        return Prestamo.objects.filter(usuario=self.user)


class Prestamo(models.Model):
    usuario = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='prestamos',
        verbose_name="Usuario"
    )
    libro = models.ForeignKey(
        Libro,
        on_delete=models.CASCADE,
        related_name='prestamos',
        verbose_name="Libro"
    )
    fecha_prestamo = models.DateTimeField(
        default=timezone.now,
        verbose_name="Fecha de préstamo"
    )
    fecha_devolucion = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Fecha de devolución"
    )
    
    class Meta:
        verbose_name = "Préstamo"
        verbose_name_plural = "Préstamos"
        ordering = ['-fecha_prestamo']
        unique_together = ['usuario', 'libro', 'fecha_prestamo']
    
    def __str__(self):
        estado = "Devuelto" if self.fecha_devolucion else "Prestado"
        return f"{self.libro.titulo} - {self.usuario.username} ({estado})"
    
    @property
    def esta_activo(self):
        """Retorna True si el préstamo está activo (no devuelto)"""
        return self.fecha_devolucion is None
    
    @property
    def dias_prestado(self):
        """Retorna los días que lleva prestado el libro"""
        if self.fecha_devolucion:
            return (self.fecha_devolucion - self.fecha_prestamo).days
        else:
            return (timezone.now() - self.fecha_prestamo).days
    
    def devolver(self):
        """Marca el libro como devuelto"""
        if not self.fecha_devolucion:
            self.fecha_devolucion = timezone.now()
            self.save()
            return True
        return False


# Signals para crear automáticamente el perfil de usuario
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=User)
def crear_perfil_usuario(sender, instance, created, **kwargs):
    """Crea automáticamente un perfil cuando se crea un usuario"""
    if created:
        PerfilUsuario.objects.create(user=instance)

@receiver(post_save, sender=User)
def guardar_perfil_usuario(sender, instance, **kwargs):
    """Guarda el perfil cuando se guarda el usuario"""
    if hasattr(instance, 'perfil'):
        instance.perfil.save()