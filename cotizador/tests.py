from django.test import SimpleTestCase

from .forms import ListaForm
from .services.ai_parser import _normalizar_productos_desde_json
from .services.ocr_parser import extraer_productos_ocr


class ParserOcrAvanzadoTests(SimpleTestCase):
    def test_extraer_productos_basico(self):
        texto = "1 Cuaderno cuadriculado\n2 Lapiz HB\n"
        productos = extraer_productos_ocr(texto)

        self.assertEqual(productos[0]["cantidad"], 1)
        self.assertIn("cuaderno", productos[0]["nombre"])
        self.assertEqual(productos[1]["cantidad"], 2)

    def test_soporta_columnas_y_abreviaturas(self):
        texto = "2 lap. hb   1 borr.\n3 cuad. rayado"
        productos = extraer_productos_ocr(texto)

        self.assertEqual(len(productos), 3)
        self.assertEqual(productos[0]["nombre"], "lapiz hb")
        self.assertEqual(productos[1]["nombre"], "borrador")
        self.assertEqual(productos[2]["nombre"], "cuaderno rayado")


class NormalizacionIaTests(SimpleTestCase):
    def test_normaliza_payload_dict(self):
        payload = {
            "productos": [
                {"cantidad": "2", "nombre": "Lápiz HB #2"},
                {"cantidad": 0, "nombre": "inválido"},
            ]
        }

        productos = _normalizar_productos_desde_json(payload)

        self.assertEqual(productos, [{"cantidad": 2, "nombre": "lápiz hb"}])


class ListaFormTests(SimpleTestCase):
    def test_form_tiene_campo_usar_ia(self):
        form = ListaForm()
        self.assertIn("usar_ia", form.fields)