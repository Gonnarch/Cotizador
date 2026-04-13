import json
import re
from urllib import error, request

from django.conf import settings


def _extraer_json_de_texto(texto):
    texto = texto.strip()

    try:
        return json.loads(texto)
    except json.JSONDecodeError:
        pass

    bloque = re.search(r"```(?:json)?\s*(\{.*\}|\[.*\])\s*```", texto, flags=re.DOTALL)
    if bloque:
        return json.loads(bloque.group(1))

    candidato = re.search(r"(\{.*\}|\[.*\])", texto, flags=re.DOTALL)
    if candidato:
        return json.loads(candidato.group(1))

    raise ValueError("No se encontró un JSON válido en la respuesta de OpenAI.")


def _normalizar_productos_desde_json(payload):
    if isinstance(payload, dict):
        items = payload.get("productos", [])
    elif isinstance(payload, list):
        items = payload
    else:
        return []

    normalizados = []
    for item in items:
        if not isinstance(item, dict):
            continue

        cantidad = item.get("cantidad", 0)
        nombre = str(item.get("nombre", "")).strip().lower()

        try:
            cantidad = int(cantidad)
        except (TypeError, ValueError):
            continue

        if cantidad <= 0 or len(nombre) < 2:
            continue

        nombre = re.sub(r"[^a-záéíóúñ\s]", "", nombre)
        nombre = re.sub(r"\s+", " ", nombre).strip()

        if not nombre:
            continue

        normalizados.append({"cantidad": cantidad, "nombre": nombre})

    return normalizados


def extraer_productos_con_ia(texto_ocr):
    api_key = getattr(settings, "OPENAI_API_KEY", "")
    api_url = getattr(settings, "OPENAI_API_URL", "https://api.openai.com/v1/chat/completions")
    modelo = getattr(settings, "OPENAI_MODEL", "gpt-4o-mini")

    if not api_key:
        return [], "No se configuró OPENAI_API_KEY en el entorno."

    system_prompt = (
        "Eres un parser de listas escolares difíciles (OCR con ruido, columnas y abreviaturas). "
        "Devuelve SOLO JSON con formato exacto: "
        '{"productos":[{"cantidad":2,"nombre":"cuaderno cuadriculado"}]}. '
        "Interpreta líneas multi-columna y expande abreviaturas comunes (lap->lapiz, cuad->cuaderno). "
        "No inventes productos que no aparezcan en el texto."
    )

    body = {
        "model": modelo,
        "temperature": 0,
        "messages": [
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": f"Texto OCR:\n\n{texto_ocr}\n\nDevuelve el JSON ahora.",
            },
        ],
    }

    req = request.Request(
        api_url,
        data=json.dumps(body).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except error.HTTPError as exc:
        detalle = exc.read().decode("utf-8", errors="ignore")
        return [], f"Error HTTP en OpenAI ({exc.code}): {detalle[:200]}"
    except Exception as exc:  # pragma: no cover
        return [], f"No se pudo consultar OpenAI: {exc}"

    content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
    if not content:
        return [], "OpenAI respondió sin contenido útil."

    try:
        parsed = _extraer_json_de_texto(content)
        productos = _normalizar_productos_desde_json(parsed)
    except Exception as exc:
        return [], f"No se pudo interpretar la respuesta de OpenAI: {exc}"

    if not productos:
        return [], "OpenAI no devolvió productos válidos."

    return productos, None
