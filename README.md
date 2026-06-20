# 🚗 AP Automotores — Simulador de Planes de Ahorro

Proyecto web desarrollado con **Django** como parte de mi aprendizaje autodidacta. Es un sitio para una concesionaria ficticia que permite simular planes de financiación de autos, registrar usuarios y gestionar solicitudes desde un panel interno.

> ⚠️ Proyecto de estudiante — desarrollado de forma independiente, sin cursada formal, aprendiendo sobre la marcha.

---

## 🌐 Demo en vivo

**[https://proyectodjango-s7vb.onrender.com](https://proyectodjango-s7vb.onrender.com)**

> Hosteado en Render (plan gratuito). Puede tardar unos segundos en despertar si estuvo inactivo.

---

## ✨ Funcionalidades

- Simulador de plan de ahorro con cálculo de cuotas
- Cotización del dólar en tiempo real (via dolarapi.com)
- Registro e inicio de sesión de usuarios
- Panel interno para ver todas las solicitudes (solo staff)
- Panel de administración Django
- Diseño responsivo con menú hamburguesa tipo drawer

---

## 🛠️ Tecnologías usadas

| Tecnología | Uso |
|---|---|
| Python / Django | Backend y lógica principal |
| PostgreSQL | Base de datos (Render) |
| Django REST Framework | API interna de solicitudes |
| WhiteNoise | Servicio de archivos estáticos |
| HTML / CSS / JS vanilla | Frontend sin frameworks |
| Render | Deploy y hosting |

---

## 🔐 Acceso al admin

Panel de administración: [https://proyectodjango-s7vb.onrender.com/admin](https://proyectodjango-s7vb.onrender.com/admin)

```
Usuario:    postgres
Contraseña: Django
```

---

## 🚀 Correr el proyecto localmente

```bash
# Clonar el repositorio
git clone https://github.com/pasilisuces-netizen/ProyectoDjango
cd ProyectoDjango

# Crear entorno virtual
python -m venv .venv
source .venv/bin/activate        # Linux/Mac
.venv\Scripts\activate           # Windows

# Instalar dependencias
pip install -r requirements.txt

# Aplicar migraciones
python manage.py migrate

# Crear superusuario
python manage.py createsuperuser

# Correr el servidor
python manage.py runserver
```

---

## 📁 Estructura del proyecto

```
AP_Automotores/
├── AP_Automotores/       # Configuración del proyecto (settings, urls)
├── mi_app/               # App principal
│   ├── templates/        # HTMLs
│   ├── static/           # CSS y JS
│   ├── models.py         # Modelo de Solicitud
│   ├── views.py          # Lógica de vistas
│   ├── forms.py          # Formularios
│   └── urls.py           # Rutas de la app
├── templates/            # Base y header global
├── static/               # CSS y JS globales
└── manage.py
```

---

## 📌 Notas del desarrollador

Este proyecto lo arranqué sin saber prácticamente nada de Django. Fui aprendiendo a medida que lo construía — errores, bugs, Stack Overflow, documentación oficial y mucha prueba y error.

Algunas cosas que aprendí en el camino:
- Cómo funciona el ciclo request/response de Django
- Manejo de formularios con validación server-side y client-side
- Deploy en Render con PostgreSQL y variables de entorno
- Por qué no hay que dejar credenciales hardcodeadas en el código 😅

---

## 👤 Autor

**Armando** — estudiante autodidacta argentino
GitHub: [@pasilisuces-netizen](https://github.com/pasilisuces-netizen)
