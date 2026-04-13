from django import forms
from django.conf import settings


class ListaForm(forms.Form):
    imagen = forms.ImageField(label="Imagen de lista escolar")
    usar_ia = forms.BooleanField(
        required=False,
        initial=getattr(settings, "USE_AI_PARSER", False),
        label="Usar OpenAI para estructurar texto OCR",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["imagen"].widget.attrs.update({"class": "form-control"})
        self.fields["usar_ia"].widget.attrs.update({"class": "form-check-input"})