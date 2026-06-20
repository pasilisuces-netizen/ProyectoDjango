from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from .views import SolicitudListAPI

urlpatterns = [
    path('', views.pagina_inicio, name='index'),
    path('login/', views.login, name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('registro/', views.registro, name='registro'),
    path('panel/solicitudes/', views.panel_solicitudes, name='panel_solicitudes'),
      path('api/solicitudes/', SolicitudListAPI.as_view(), name='api_solicitudes'),
    path('api/cotizacion-dolar/', views.cotizacion_dolar, name='cotizacion_dolar'),
]
