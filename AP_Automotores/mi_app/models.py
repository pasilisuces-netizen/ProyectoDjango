from django.db import models


class Solicitud(models.Model):

    # ── Datos del titular ──────────────────────────────────────
    nombre          = models.CharField(max_length=100)
    apellido        = models.CharField(max_length=100)
    email           = models.EmailField()
    fecha_nacimiento = models.DateField()
    telefono        = models.CharField(max_length=20, blank=True)

    # ── Datos del garante ──────────────────────────────────────
    garante_nombre      = models.CharField(max_length=100)
    garante_fecha_nacimiento = models.DateField(null=True, blank=True)
    garante_dni         = models.CharField(max_length=20)
    garante_ingreso     = models.DecimalField(max_digits=15, decimal_places=2)
    garante_antiguedad  = models.IntegerField()          # años
    garante_relacion    = models.CharField(
        max_length=20,
        choices=[("dependencia", "Relación de dependencia"),
                 ("independiente", "Trabajador independiente")],
    )
    garante_telefono    = models.CharField(max_length=20, blank=True)

    # ── Datos del plan ─────────────────────────────────────────
    modelo_auto     = models.CharField(max_length=100)
    precio_auto     = models.DecimalField(max_digits=15, decimal_places=2)
    cantidad_cuotas = models.IntegerField()
    ingreso_mensual = models.DecimalField(max_digits=15, decimal_places=2)

    # ── Resultado de la simulación ─────────────────────────────
    cuota_mensual       = models.DecimalField(max_digits=15, decimal_places=2)
    porcentaje_ingreso  = models.DecimalField(max_digits=5, decimal_places=2)

    # ── Metadata ───────────────────────────────────────────────
    fecha_solicitud  = models.DateTimeField(auto_now_add=True)
    cotizacion_dolar = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )

    class Meta:
        verbose_name        = "Solicitud"
        verbose_name_plural = "Solicitudes"
        ordering            = ["-fecha_solicitud"]

    def __str__(self):
        return (
            f"{self.nombre} {self.apellido} — "
            f"{self.modelo_auto} "
            f"({self.fecha_solicitud.strftime('%d/%m/%Y')})"
        )