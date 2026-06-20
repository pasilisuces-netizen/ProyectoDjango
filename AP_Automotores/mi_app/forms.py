from django import forms
from django.core.exceptions import ValidationError
from .models import Solicitud
from datetime import date
import re


class SolicitudForm(forms.ModelForm):
    class Meta:
        model = Solicitud
        fields = [
            # Titular
            "nombre", "apellido", "fecha_nacimiento", "email", "telefono",
            # Garante
            "garante_nombre","garante_fecha_nacimiento", "garante_dni", "garante_ingreso",
            "garante_antiguedad", "garante_relacion", "garante_telefono",
            # Plan
            "modelo_auto", "precio_auto", "cantidad_cuotas", "ingreso_mensual",
        ]

        widgets = {
            # ── Titular ────────────────────────────────────────────────────
            "nombre": forms.TextInput(attrs={
                "class": "form-input", "placeholder": "Tu nombre", "required": True,
            }),
            "garante_fecha_nacimiento": forms.DateInput(attrs={
                "class": "form-input", "type": "date", "required": True,
                "max": str(date.today()),
            }),
            "apellido": forms.TextInput(attrs={
                "class": "form-input", "placeholder": "Tu apellido", "required": True,
            }),
            "fecha_nacimiento": forms.DateInput(attrs={
                "class": "form-input", "type": "date", "required": True,
                "max": str(date.today()),
            }),
            "email": forms.EmailInput(attrs={
                "class": "form-input", "placeholder": "correo@ejemplo.com", "required": True,
            }),
            "telefono": forms.TextInput(attrs={
                "class": "form-input", "placeholder": "+54 11 0000-0000",
            }),

            # ── Garante ────────────────────────────────────────────────────
            "garante_nombre": forms.TextInput(attrs={
                "class": "form-input", "placeholder": "Nombre del garante", "required": True,
            }),
            "garante_dni": forms.TextInput(attrs={
                "class": "form-input", "placeholder": "Número de DNI", "required": True,
            }),
            "garante_ingreso": forms.NumberInput(attrs={
                "class": "form-input", "placeholder": "0.00", "required": True, "min": "1",
            }),
            "garante_antiguedad": forms.Select(
                choices=[
                    ("", "Seleccionar..."),
                    (1, "1 año"),
                    (2, "2 años"),
                    (3, "3 años o más"),
                ],
                attrs={"class": "form-input", "required": True},
            ),
            "garante_relacion": forms.Select(
                choices=[
                    ("", "Seleccionar..."),
                    ("dependencia", "Relación de dependencia"),
                    ("independiente", "Trabajador independiente"),
                ],
                attrs={"class": "form-input", "required": True},
            ),
            "garante_telefono": forms.TextInput(attrs={
                "class": "form-input", "placeholder": "+54 11 0000-0000",
            }),

            # ── Plan ───────────────────────────────────────────────────────
            "modelo_auto": forms.Select(
                choices=[
                    ("", "Seleccionar modelo"),
                    ("Fiat Mobi", "Fiat Mobi"),
                    ("Volkswagen Polo", "Volkswagen Polo"),
                    ("Toyota Corolla", "Toyota Corolla"),
                    ("BMW Serie 3", "BMW Serie 3"),
                ],
                attrs={"class": "form-input", "required": True},
            ),
            "precio_auto": forms.NumberInput(attrs={
                "class": "form-input", "placeholder": "0.00",
                "required": True, "min": "1",
            }),
            "cantidad_cuotas": forms.Select(
                choices=[
                    (48, "48 cuotas"),
                    (60, "60 cuotas"),
                    (72, "72 cuotas"),
                    (84, "84 cuotas"),
                ],
                attrs={"class": "form-input", "required": True},
            ),
            "ingreso_mensual": forms.NumberInput(attrs={
                "class": "form-input", "placeholder": "0.00",
                "required": True, "min": "1",
            }),
        }

    # ══════════════════════════════════════════════════════════
    # VALIDACIONES INDIVIDUALES
    # ══════════════════════════════════════════════════════════

    def _solo_letras(self, valor, campo):
        if not re.match(r'^[A-Za-zÁÉÍÓÚáéíóúñÑ ]+$', valor):
            raise ValidationError(f"El {campo} solo puede contener letras.")
        return valor

    def clean_nombre(self):
        return self._solo_letras(self.cleaned_data["nombre"], "nombre")

    def clean_apellido(self):
        return self._solo_letras(self.cleaned_data["apellido"], "apellido")

    def clean_fecha_nacimiento(self):
        nac = self.cleaned_data["fecha_nacimiento"]
        hoy = date.today()

        # Calcular edad exacta
        edad = hoy.year - nac.year - ((hoy.month, hoy.day) < (nac.month, nac.day))

        if edad < 18:
            raise ValidationError("Debés tener al menos 18 años para solicitar el plan.")

        # Validar que no supere 78 años al finalizar el plan
        # El plan máximo es 84 cuotas = 7 años
        anios_plan = 7
        edad_al_finalizar = edad + anios_plan
        if edad_al_finalizar > 78:
            raise ValidationError(
                f"Con {edad} años, al finalizar el plan tendrías {edad_al_finalizar} años. "
                "El plan no puede extenderse más allá de los 78 años del titular."
            )

        return nac

    def clean_garante_nombre(self):
        return self._solo_letras(self.cleaned_data["garante_nombre"], "nombre del garante")

    def clean_telefono(self):
        tel = self.cleaned_data["telefono"]
        if tel and not re.match(r'^[0-9+\-\s()]+$', tel):
            raise ValidationError("Teléfono inválido.")
        return tel

    def clean_garante_telefono(self):
        tel = self.cleaned_data["garante_telefono"]
        if tel and not re.match(r'^[0-9+\-\s()]+$', tel):
            raise ValidationError("Teléfono del garante inválido.")
        return tel

    def clean_precio_auto(self):
        precio = self.cleaned_data["precio_auto"]
        if precio <= 0:
            raise ValidationError("El precio debe ser mayor a 0.")
        if precio < 5_000_000:
            raise ValidationError("El vehículo es demasiado económico para un plan.")
        return precio

    def clean_modelo_auto(self):
        modelo = self.cleaned_data["modelo_auto"]
        modelos_validos = ["Fiat Mobi", "Volkswagen Polo", "Toyota Corolla", "BMW Serie 3"]
        if modelo not in modelos_validos:
            raise ValidationError("El modelo seleccionado no es válido.")
        return modelo

    def clean_ingreso_mensual(self):
        ingreso = self.cleaned_data["ingreso_mensual"]
        if ingreso <= 0:
            raise ValidationError("El ingreso debe ser mayor a 0.")
        return ingreso

    def clean_garante_ingreso(self):
        ingreso = self.cleaned_data["garante_ingreso"]
        if ingreso <= 0:
            raise ValidationError("El ingreso del garante debe ser mayor a 0.")
        return ingreso

    def clean_cantidad_cuotas(self):
        cuotas = self.cleaned_data["cantidad_cuotas"]
        if cuotas not in [48, 60, 72, 84]:
            raise ValidationError("Cantidad de cuotas inválida.")
        return cuotas

    # ══════════════════════════════════════════════════════════
    # VALIDACIÓN CRUZADA
    # ══════════════════════════════════════════════════════════

    def clean(self):
        cleaned = super().clean()
        precio           = cleaned.get("precio_auto")
        ingreso          = cleaned.get("ingreso_mensual")
        cuotas           = cleaned.get("cantidad_cuotas")
        garante_ingreso  = cleaned.get("garante_ingreso")
        garante_relacion = cleaned.get("garante_relacion")
        garante_antiguedad = cleaned.get("garante_antiguedad")
        nac              = cleaned.get("fecha_nacimiento")



        # Validar edad máxima cruzada con cuotas elegidas
        if nac and cuotas:
            hoy  = date.today()
            edad = hoy.year - nac.year - ((hoy.month, hoy.day) < (nac.month, nac.day))
            anios_plan = cuotas / 12
            edad_al_finalizar = edad + anios_plan
            if edad_al_finalizar > 78:
                raise ValidationError(
                    f"Con {edad} años y {cuotas} cuotas, al finalizar el plan tendrías "
                    f"{edad_al_finalizar:.0f} años. El máximo permitido es 78 años."
                )

        if precio and ingreso and cuotas:
            cuota_estimada = precio / cuotas
            porcentaje = (cuota_estimada / ingreso) * 100
            if porcentaje > 35:
                raise ValidationError(
                    "La cuota supera el 35 % de los ingresos mensuales del titular."
                )

            if garante_ingreso and garante_ingreso < cuota_estimada * 4:
                raise ValidationError(
                    "El ingreso del garante debe ser al menos 4 veces la cuota estimada "
                    f"(mínimo ${cuota_estimada * 4:,.0f})."
                )

            if garante_relacion and garante_antiguedad is not None:
                 if garante_relacion == "dependencia" and int(garante_antiguedad) < 1:
                    self.add_error("garante_antiguedad",
                "El garante en relación de dependencia debe tener al menos 1 año de antigüedad.")
            if garante_relacion == "independiente" and int(garante_antiguedad) < 2:
                 self.add_error("garante_antiguedad",
                "El garante independiente debe tener al menos 2 años de antigüedad.")

        return cleaned