# Evaluación 3 - Backend

| Concepto | Detalle |
| :--- | :--- |
| **Nombre de la Plataforma** | Nómade |
| **Modelo de Negocio** | Agencia de paquetes turísticos |
| **Integrantes** | Vicente Cabrera: 21.014.795-0 - Tamara Soto: 20.515.480-9 |
| **Entidad de Contexto** | Categoría de Destino |
| **Entidad Principal Gestionable (ORM)** | Paquete Turístico |
| **Propósito de la Sesión (request.session)** | Carrito de Reservas |

## Requisitos Previos

Antes de comenzar, asegúrate de tener instalado en tu sistema:
*   **Python 3.10+**
*   **Git**

## Instalación y Ejecución Paso a Paso

Sigue estos pasos en tu terminal para ejecutar el proyecto de forma local sin problemas de dependencias:

**1. Clonar el repositorio**\
git clone https://github.com/tamiicat/ev3_backend_borrador
Abrir carpeta del proyecto: cd ev3_backend

**2. Crear y activar el entorno virtual**\
En Windows (PowerShell/CMD):\
python -m venv venv\
venv\Scripts\activate

En macOS/Linux:\
python3 -m venv venv\
source venv/bin/activate

**3. Instalar las dependencias**\
pip install -r requirements.txt

**4. Aplicar las migraciones de la Base de Datos**\
python manage.py makemigrations\
python manage.py migrate

**5. Poblar la Base de Datos (Opcional pero Recomendado)**\
python manage.py poblar_nomade

**6. Iniciar el Servidor de Desarrollo**\
python manage.py runserver

Abrir navegador web y visitar: http://127.0.0.1:8000/

## Credenciales de Acceso
**Usuario Administrador**
*   Correo Electrónico: admin@nomade.cl
*   Password: admin

## Usamos IA xd