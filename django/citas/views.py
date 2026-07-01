from django.shortcuts import render
from citas.models import Servicio

def inicio(request):

    servicios = Servicio.objects.all().order_by("id")

    return render(
        request,
        "index.html",
        {
            "servicios": servicios
        }
    )