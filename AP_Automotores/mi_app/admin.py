
from django.contrib import admin
from .models import Solicitud


@admin.register(Solicitud)
class SolicitudAdmin(admin.ModelAdmin):
    list_display  = (
        "id", "nombre", "apellido", "email",
        "modelo_auto", "cuota_mensual", "porcentaje_ingreso", "fecha_solicitud",
    )
    list_filter   = ("modelo_auto", "cantidad_cuotas", "garante_relacion")
    search_fields = ("nombre", "apellido", "email", "garante_nombre", "garante_dni")
    readonly_fields = ("cuota_mensual", "porcentaje_ingreso", "fecha_solicitud")

    fieldsets = (
        ("Datos del titular", {
            "fields": ("nombre", "apellido", "email", "telefono", "ingreso_mensual")
        }),
        ("Datos del garante", {
            "fields": (
                "garante_nombre", "garante_dni", "garante_ingreso",
                "garante_antiguedad", "garante_relacion", "garante_telefono",
            )
        }),
        ("Datos del plan", {
            "fields": ("modelo_auto", "precio_auto", "cantidad_cuotas")
        }),
        ("Resultado y metadata", {
            "fields": (
                "cuota_mensual", "porcentaje_ingreso",
                "cotizacion_dolar", "fecha_solicitud",
            )
        }),
    )
