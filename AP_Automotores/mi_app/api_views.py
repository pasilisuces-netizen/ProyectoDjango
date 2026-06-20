"""
api_views.py
Punto 7 — API interna con Django REST Framework
Endpoint: GET /api/solicitudes/
Solo accesible para usuarios autenticados (IsAuthenticated).
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import serializers, permissions
from .models import Solicitud


# ── Serializer ────────────────────────────────────────────────────────────────
class SolicitudSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Solicitud
        fields = [
            "id",
            # Titular
            "nombre", "apellido", "email", "telefono",
            # Garante
            "garante_nombre", "garante_dni", "garante_ingreso",
            "garante_antiguedad", "garante_relacion", "garante_telefono",
            # Plan
            "modelo_auto", "precio_auto", "cantidad_cuotas", "ingreso_mensual",
            # Resultado
            "cuota_mensual", "porcentaje_ingreso",
            # Metadata
            "fecha_solicitud", "cotizacion_dolar",
        ]


# ── Vista ─────────────────────────────────────────────────────────────────────
class SolicitudListAPI(APIView):
    """
    GET /api/solicitudes/
    Devuelve todas las solicitudes en formato JSON.
    Requiere estar autenticado (admin o staff).
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        solicitudes = Solicitud.objects.all()
        serializer  = SolicitudSerializer(solicitudes, many=True)
        return Response({
            "total":       solicitudes.count(),
            "solicitudes": serializer.data,
        })