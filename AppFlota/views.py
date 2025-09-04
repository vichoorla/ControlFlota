from django.shortcuts import render
from django.http import HttpResponse
# Create your views here.

def bienvenida(request):
    return HttpResponse(request, "<h1>Bienvenido/a a la página!</h1>")

def AgregarChofer(request):
    return render(request, 'TemplatesFlota/index.html') 