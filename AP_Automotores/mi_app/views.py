from django.shortcuts import render, redirect
import json
import requests
from decimal import Decimal, ROUND_HALF_UP
from .forms import SolicitudForm
from django.core.mail import send_mail
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import serializers, permissions
from .models import Solicitud
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_GET, require_POST
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test


# Create your views here.

def login(request):
    if request.user.is_authenticated:
        return redirect('index')

    form = AuthenticationForm()

    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)
            if user.is_staff or user.is_superuser:
                return redirect('panel_solicitudes')
            return redirect('index')
        else:
            messages.error(request, 'Usuario o contraseña incorrectos. Verificá tus datos.')

    return render(request, 'mi_app/login.html', {
        'show_register': False,
    })


def registro(request):
    register_form = UserCreationForm()

    if request.method == 'POST':
        register_form = UserCreationForm(request.POST)
        if register_form.is_valid():
            user = register_form.save()
            user.first_name = request.POST.get('first_name', '')
            user.last_name = request.POST.get('last_name', '')
            user.email = request.POST.get('email', '')
            user.save()
            messages.success(request, '¡Cuenta creada! Ya podés iniciar sesión.')
            return redirect('login')


    return render(request, 'mi_app/login.html', {
        'show_register': True,
        'register_form': register_form,
    })


def solo_staff(user):
    return user.is_staff or user.is_superuser


@login_required
@user_passes_test(solo_staff, login_url='login')
def panel_solicitudes(request):
    solicitudes = Solicitud.objects.all().order_by('-fecha_solicitud')
    return render(request, 'mi_app/panel_solicitudes.html', {'solicitudes': solicitudes})





# Formulario de plan


# ── Página de inicio / simulador ───────────────────────────────────────────────
def pagina_inicio(request):
    """
    Muestra el index con el formulario de simulación.
    También procesa el POST cuando el usuario envía la solicitud.
    """
    mensaje_exito = None
    resultado = None

    if request.method == "POST":
        form = SolicitudForm(request.POST)

        if form.is_valid():
            solicitud = form.save(commit=False)

            # ── Cálculos ───────────────────────────────────────
            cuota = solicitud.precio_auto / solicitud.cantidad_cuotas
            porcentaje = (cuota / solicitud.ingreso_mensual) * 100

            solicitud.cuota_mensual = round(cuota, 2)
            solicitud.porcentaje_ingreso = round(porcentaje, 2)

            # Guardar cotización dólar si viene del front
            solicitud.cotizacion_dolar = request.POST.get("cotizacion_dolar") or None

            solicitud.save()

            resultado = {
                "cuota": round(cuota, 2),
                "porcentaje": round(porcentaje, 2),
                "solicitud": solicitud,
            }

            # ── Email ──────────────────────────────────────────
            asunto = f"Nueva solicitud — {solicitud.nombre} {solicitud.apellido}"
            cuerpo = f"""
Nueva simulación recibida:
 
================================
DATOS DEL TITULAR
Nombre:    {solicitud.nombre} {solicitud.apellido}
Email:     {solicitud.email}
Teléfono:  {solicitud.telefono}
 
================================
DATOS DEL GARANTE
Nombre:       {solicitud.garante_nombre}
DNI:          {solicitud.garante_dni}
Ingreso:      ${solicitud.garante_ingreso}
Antigüedad:   {solicitud.garante_antiguedad} año(s)
Relación:     {solicitud.get_garante_relacion_display()}
Teléfono:     {solicitud.garante_telefono}
 
================================
DATOS DEL VEHÍCULO
Modelo:   {solicitud.modelo_auto}
Precio:   ${solicitud.precio_auto}
Cuotas:   {solicitud.cantidad_cuotas}
 
================================
ANÁLISIS FINANCIERO
Ingreso mensual:         ${solicitud.ingreso_mensual}
Cuota estimada:          ${round(cuota, 2)}
Porcentaje comprometido: {round(porcentaje, 2)} %
================================
"""

            try:
                send_mail(
                    asunto,
                    cuerpo,
                    settings.DEFAULT_FROM_EMAIL,
                    [solicitud.email],
                    fail_silently=True,
                )
                mensaje_exito = "¡Simulación enviada! Revisá tu correo."
            except Exception:
                mensaje_exito = "Solicitud guardada. Hubo un problema al enviar el email."

            # Limpiar el formulario después del éxito
            # form = SolicitudForm()

    else:
        form = SolicitudForm()

    return render(request, "mi_app/index.html", {
        "form": form,
        "mensaje_exito": mensaje_exito,
        "resultado": resultado,
    })


# /////////////////

"""
 API interna con Django REST Framework

"""


# ── Serializer ────────────────────────────────────────────────────────────────
class SolicitudSerializer(serializers.ModelSerializer):
    class Meta:
        model = Solicitud
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

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        solicitudes = Solicitud.objects.all()
        serializer = SolicitudSerializer(solicitudes, many=True)
        return Response({
            "total": solicitudes.count(),
            "solicitudes": serializer.data,
        })


PRECIOS = {
    'Fiat': Decimal('12000000'),
    'Volkswagen': Decimal('20000000'),
    'Toyota': Decimal('35000000'),
    'BMW': Decimal('75000000'),
}

TASA_INTERES = Decimal('14.50')


def calcular_cuota(precio, plan, cuotas):
    precio = Decimal(str(precio))
    cuotas = int(cuotas)

    if plan == '70-30':
        pct_financiado = Decimal('0.70')
        adj = precio * Decimal('0.30')
    elif plan == '50-50':
        pct_financiado = Decimal('0.50')
        adj = precio * Decimal('0.50')
    else:
        pct_financiado = Decimal('1.00')
        adj = Decimal('0')

    capital = precio * pct_financiado
    tasa_mensual = TASA_INTERES / Decimal('100') / Decimal('12')

    factor = (tasa_mensual * (1 + tasa_mensual) ** cuotas) / ((1 + tasa_mensual) ** cuotas - 1)
    cuota_mensual = capital * factor
    retiro = precio * Decimal('0.05')

    return (
        adj.quantize(Decimal('1'), rounding=ROUND_HALF_UP),
        retiro.quantize(Decimal('1'), rounding=ROUND_HALF_UP),
        cuota_mensual.quantize(Decimal('1'), rounding=ROUND_HALF_UP),
    )


def fmt(valor):
    return '$' + f"{int(valor):,}".replace(',', '.')


@require_POST
def simular(request):
    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        data = request.POST.dict()

    modelo = data.get('modelo', 'Fiat')
    precio_vehiculo = PRECIOS.get(modelo, PRECIOS['Fiat'])
    plan = data.get('plan', '70-30')
    cuotas = data.get('cuotas', 84)

    adj, retiro, cuota = calcular_cuota(precio_vehiculo, plan, cuotas)

    data_completa = dict(data)
    data_completa['precio_vehiculo'] = str(precio_vehiculo)
    data_completa['tasa_interes'] = str(TASA_INTERES)
    data_completa['importe_adjudicacion'] = str(adj)
    data_completa['importe_retiro'] = str(retiro)
    data_completa['cuota_mensual'] = str(cuota)

    form = SolicitudSimulacionForm(data_completa)

    if form.is_valid():
        solicitud = form.save(commit=False)
        solicitud.precio_vehiculo = precio_vehiculo
        solicitud.tasa_interes = TASA_INTERES
        solicitud.importe_adjudicacion = adj
        solicitud.importe_retiro = retiro
        solicitud.cuota_mensual = cuota
        solicitud.save()

        return JsonResponse({
            'ok': True,
            'mensaje': '¡Simulación guardada con éxito!',
            'informe': {
                'modelo': modelo,
                'precio': fmt(precio_vehiculo),
                'plan': plan,
                'cuotas': int(cuotas),
                'adjudicacion': fmt(adj),
                'retiro': fmt(retiro),
                'tasa': '14,50%',
                'cuota_mensual': fmt(cuota),
            }
        })
    else:
        errores = {campo: list(msgs) for campo, msgs in form.errors.items()}
        return JsonResponse({'ok': False, 'errores': errores}, status=400)


@require_GET
def cotizacion_dolar(request):
    try:
        resp = requests.get('https://dolarapi.com/v1/dolares/oficial', timeout=5)
        resp.raise_for_status()
        dato = resp.json()
        venta = dato.get('venta') or dato.get('compra')
        return JsonResponse({'ok': True, 'venta': venta})
    except Exception as e:
        return JsonResponse({'ok': False, 'error': str(e)}, status=500)
