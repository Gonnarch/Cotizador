import re

ABREVIATURAS = {
    "lap": "lapiz",
    "lap.": "lapiz",
    "cuad": "cuaderno",
    "cuad.": "cuaderno",
    "col.": "colores",
    "taj.": "tajador",
    "borr.": "borrador",
    "plum.": "plumones",
}

RUIDO = {
    "uniforme",
    "niños",
    "niñas",
    "todos los materiales",
    "uso personal",
}


def limpiar_texto(texto):
    texto = texto.lower()
    texto = texto.replace("\t", " ")
    texto = re.sub(r"(\d)([a-záéíóúñ])", r"\1 \2", texto)
    texto = re.sub(r"\n+", "\n", texto)
    return texto


def _expandir_abreviaturas(nombre):
    tokens = nombre.split()
    normalizados = [ABREVIATURAS.get(t, t) for t in tokens]
    return " ".join(normalizados)


def _segmentar_linea_multicolumna(linea):
    """Divide una línea en segmentos posibles de producto.

    Soporta:
    - columnas separadas por 2+ espacios
    - bloques concatenados tipo: `2 lapiz 1 borrador`
    """
    por_columnas = [s.strip() for s in re.split(r"\s{2,}", linea) if s.strip()]
    if len(por_columnas) > 1:
        return por_columnas

    return [s.strip() for s in re.split(r"(?=\d+\s+[a-záéíóúñ])", linea) if s.strip()]


def extraer_productos_ocr(texto):
    texto = limpiar_texto(texto)
    lineas = texto.split("\n")
    productos = []

    for linea in lineas:
        linea = linea.strip()
        if not linea:
            continue

        if any(palabra in linea for palabra in RUIDO):
            continue

        if "/" in linea:
            continue

        segmentos = _segmentar_linea_multicolumna(linea)

        for segmento in segmentos:
            match = re.match(r"^(\d+)\s+(.*)$", segmento)
            if not match:
                continue

            cantidad = int(match.group(1))
            nombre = match.group(2)
            nombre = re.sub(r"\d+", "", nombre)
            nombre = re.sub(r"[^a-záéíóúñ\s.]", " ", nombre)
            nombre = re.sub(r"\s+", " ", nombre).strip()
            nombre = _expandir_abreviaturas(nombre)
            nombre = re.sub(r"\s+", " ", nombre).strip()

            if cantidad <= 0 or len(nombre) < 3:
                continue

            productos.append({"cantidad": cantidad, "nombre": nombre})

    return productos
