API de Kiosco: Proyecto Integrador

Asignatura:Informática
Carrera:Tecnicatura Universitaria en Desarrollo de Software · 1er Año
Institución:Universidad de Mendoza · Sede Río Cuarto
Tema:Cierre de caja y control de ventas

Requisitos previos:
Antes de comenzar, asegurate de tener instalado en tu sistema:
Python 3
Github
Navegador web (para acceder a la documentación interactiva Swagger UI)

instalación y configuración 
Clonar el repositorio y crear el entorno virtual Abrí tu terminal y ejecutá los siguientes comandos para clonar el repositorio y preparar tu entorno aislado: \\\bash
Clonar el repositorio git clone [suspicious link removed]
Crear el entorno virtual (venv) python3 -m venv venv 

una vez echo esto se deberian instalar las dependencias
pip install -r requirements.txt

ejecucion de la API:
y luego para ejecutar la API se debe poner este codigo dentro de la terminal
uvicorn main:app --reload

los Endpoints tiene las siguientes funciones
Inicio (GET /)

Descripción:Endpoint público de bienvenida para verificar el estado de la API.

{
  "message": "Welcome to the API",
 
}

Productos (GET /products)

Descripción:Devuelve el catálogo completo de productos con sus precios y categorías. Permite filtrar opcionalmente por categoría.
Parámetros Query:category (opcional, ej. bebidas, golosinas, snacks).
Ejemplo:GET /products?category=bebidas

(GET /sales/{id})
Descripción:Obtiene los detalles de una venta específica buscando por su ID.
Parámetros Path:id (entero).
Manejo de errores:Devuelve HTTP 404 Not Found si la venta no existe.

Ventas por producto (GET /products/{id}/sales)

Descripción: Recupera el historial de ventas asociadas a un producto determinado según su ID.
Parámetros Path: id (entero).

Histotial de ingresos (GET /expenses)

Descripción:Lista los gastos registrados en el comercio. Permite filtrar opcionalmente por fecha.
Parámetros Query:date (opcional, formato YYYY-MM-DD).


Cierre de caja diario (GET /cash-closing)

Descripción:Calcula dinámicamente el cierre de caja para una fecha requerida. Suma el total vendido, desglosa los montos ingresados según el medio de pago (efectivo, debito, transferencia), suma los egresos y calcula el saldo neto del día.
Parámetros Query:date (obligatorio, formato YYYY-MM-DD).
Respuesta de ejemplo (200 OK):**


{
  "date": "2026-09-10",
  "total_sales": 12500.0,
  "by_payment_method": {
    "efectivo": 5500.0,
    "debito": 4600.0,
    "transferencia": 2400.0
  },
  "total_expenses": 6500.0,
  "daily_balance": 6000.0
}



Registrar egreso / Medios de pago (POST /expenses)

Descripción:Permite crear un nuevo registro de egreso operativo con validación manual del cuerpo JSON.
Cuerpo JSON de ejemplo:**


{
  "date": "2026-09-10",
  "description": "Compra de bolsas plásticas",
  "amount": 1500.0
}



Respuesta:Devuelve HTTP 201 Created al registrarse exitosamente o HTTP 400 Bad Request ante errores de validación.

en este trabajo con mi compañero hemos usado las herramientas de IA (claude,nootboklm.gemini y chatGPT) el uso de la IA se uso para la ayuda de la creacion de las bases y deteccion de errorwes