from django.urls import path
from . import views
from django.http import HttpResponse

def pagina_inicio(request):
    return HttpResponse("Bienvenido al sistema de biblioteca")

urlpatterns = [
    path('', pagina_inicio, name='inicio'),
]
