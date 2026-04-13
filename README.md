# 🚀 Cotizador Escolar - Django App

![Django](https://img.shields.io/badge/Django-6.0-green)
![Python](https://img.shields.io/badge/Python-3.14-blue)
![Status](https://img.shields.io/badge/Status-Activo-success)

---

## 📌 Descripción

Aplicación web Django para cotizar listas escolares desde imágenes.
El flujo combina OCR con Tesseract + parser local avanzado y, opcionalmente, parser con **API de OpenAI**.

---

## ✨ Flujo OCR + OpenAI

1. Subes una imagen con la lista escolar.
2. Tesseract extrae el texto OCR.
3. El parser local avanzado procesa columnas, ruido y abreviaturas.
4. Si activas `usar_ia`, el texto OCR se envía al API de OpenAI para estructurar JSON.
5. Si OpenAI falla, se usa fallback automático al parser OCR local.

---

## 🎨 Interfaz Bootstrap

La pantalla principal usa Bootstrap 5:
- Card principal.
- Formulario estilizado.
- Tablas responsivas para productos y presupuesto.
- Badges/alerts para motor de extracción y mensajes de fallback.

---

## ⚙️ Variables de Entorno

```bash
USE_AI_PARSER=true
OPENAI_API_KEY=tu_api_key
OPENAI_MODEL=gpt-4o-mini
OPENAI_API_URL=https://api.openai.com/v1/chat/completions
TESSERACT_CMD=/usr/bin/tesseract