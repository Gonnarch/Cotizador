import re
import pytesseract
from PIL import Image
from django.shortcuts import render
from .forms import ListaForm
from .models import Producto

# Ruta Tesseract
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


# -----------------------------
# LIMPIEZA BÁSICA OCR
# -----------------------------
def limpiar_texto(texto):
    texto = texto.lower()

    # separar 1cuaderno -> 1 cuaderno
    texto = re.sub(r"(\d)([a-záéíóúñ])", r"\1 \2", texto)

    # normalizar saltos
    texto = re.sub(r"\n+", "\n", texto)

    return texto


# -----------------------------
# EXTRAER PRODUCTOS
# -----------------------------
def extraer_productos(texto):
    texto = limpiar_texto(texto)
    lineas = texto.split("\n")

    productos = []

    for linea in lineas:
        linea = linea.strip()

        if not linea:
            continue

        # ignorar ruido claro
        if any(p in linea for p in [
            "uniforme", "niños", "niñas",
            "todos los materiales", "uso personal"
        ]):
            continue

        # ignorar fracciones 5/8
        if "/" in linea:
            continue

        # solo líneas que empiezan con número
        if not re.match(r"^\d+\s+", linea):
            continue

        partes = re.split(r"(?=\d+\s)", linea)

        for p in partes:
            p = p.strip()

            if not p:
                continue

            match = re.match(r"^(\d+)\s+(.*)$", p)
            if not match:
                continue

            cantidad = int(match.group(1))
            nombre = match.group(2)

            # eliminar números internos (50 hojas, etc)
            nombre = re.sub(r"\d+", "", nombre)

            # limpiar símbolos
            nombre = re.sub(r"[^a-záéíóúñ\s]", "", nombre)

            nombre = nombre.strip()

            if len(nombre) < 3:
                continue

            productos.append({
                "cantidad": cantidad,
                "nombre": nombre
            })

    return productos


# -----------------------------
# CALCULAR PRESUPUESTO
# -----------------------------
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

                resultado.append({
                    "nombre": p.nombre,
                    "cantidad": cantidad,
                    "precio": p.precio,
                    "subtotal": subtotal
                })

                total += subtotal
                break

    return resultado, total


# -----------------------------
# VIEW PRINCIPAL
# -----------------------------
def inicio(request):
    texto = ""
    productos = []
    resultado = []
    total = 0

    if request.method == "POST":
        form = ListaForm(request.POST, request.FILES)

        if form.is_valid():
            imagen = request.FILES["imagen"]
            img = Image.open(imagen)

            texto = pytesseract.image_to_string(img, lang="spa")

            productos = extraer_productos(texto)

            resultado, total = calcular_presupuesto(productos)

    else:
        form = ListaForm()

    return render(request, "cotizador/inicio.html", {
        "form": form,
        "texto": texto,
        "productos": productos,
        "resultado": resultado,
        "total": total
    })