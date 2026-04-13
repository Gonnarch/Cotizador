import pytesseract
from PIL import Image
from django.conf import settings
from django.shortcuts import render

from .forms import ListaForm
from .models import Producto
from .services.ai_parser import extraer_productos_con_ia
from .services.ocr_parser import extraer_productos_ocr

if getattr(settings, "TESSERACT_CMD", ""):
    pytesseract.pytesseract.tesseract_cmd = settings.TESSERACT_CMD


def calcular_presupuesto(productos_detectados):
    resultado = []
    total = 0

    productos_bd = Producto.objects.all()

    for item in productos_detectados:
        texto = item["nombre"]
        cantidad = item["cantidad"]

        for p in productos_bd:
            if p.nombre in texto:
                subtotal = cantidad * float(p.precio)

                resultado.append(
                    {
                        "nombre": p.nombre,
                        "cantidad": cantidad,
                        "precio": p.precio,
                        "subtotal": subtotal,
                    }
                )

                total += subtotal
                break

    return resultado, total


def inicio(request):
    texto = ""
    productos = []
    resultado = []
    total = 0
    motor_extraccion = "local-avanzado"
    aviso_ia = ""

    if request.method == "POST":
        form = ListaForm(request.POST, request.FILES)

        if form.is_valid():
            imagen = request.FILES["imagen"]
            img = Image.open(imagen)

            texto = pytesseract.image_to_string(img, lang="spa")
            usar_ia = form.cleaned_data.get("usar_ia", False)

            if usar_ia:
                productos, error_ia = extraer_productos_con_ia(texto)

                if error_ia:
                    aviso_ia = f"IA no disponible: {error_ia} Se usó parser OCR local avanzado."
                    productos = extraer_productos_ocr(texto)
                else:
                    motor_extraccion = "api-ia"
            else:
                productos = extraer_productos_ocr(texto)

            resultado, total = calcular_presupuesto(productos)
    else:
        form = ListaForm()

    return render(
        request,
        "cotizador/inicio.html",
        {
            "form": form,
            "texto": texto,
            "productos": productos,
            "resultado": resultado,
            "total": total,
            "motor_extraccion": motor_extraccion,
            "aviso_ia": aviso_ia,
        },
    )