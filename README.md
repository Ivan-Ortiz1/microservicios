Microservicios: Tienda simple

Microservicios: Tienda Simple

Este proyecto implementa un sistema de microservicios simple para gestionar productos, pedidos y pagos, usando FastAPI, SQLAlchemy y JWT para autenticación.

🏗 Arquitectura

El sistema está dividido en tres microservicios independientes:

Microservicio	Puerto	Responsabilidad
Productos	8000	CRUD de productos, gestión de stock
Pedidos	8001	Crear pedidos, verificar stock, llamar a pagos
Pagos	8002	Procesar pagos, registrar estado (aprobado/rechazado)

Cada microservicio tiene su propia base de datos, y se comunican entre sí vía REST API.

⚡ Características

Validaciones robustas de campos (cantidad > 0, stock disponible, total >= 0)

JWT para autenticación entre microservicios

Rollback seguro si falla un pago

Logs informativos y de errores

Endpoints REST bien documentados con Swagger (/docs)

📦 Instalación

Clonar repositorio:
git clone https://github.com/tu_usuario/tu_repositorio.git
cd microservicios
Crear y activar entorno virtual:
python -m venv venv
.\venv\Scripts\activate   # Windows
source venv/bin/activate  # Linux/macOS
Instalar dependencias:
pip install -r requirements.txt
Inicializar bases de datos:

Cada microservicio tiene su propio db.py con función iniciar_bd(). Ejecutar o importar para crear las tablas.

🚀 Ejecutar microservicios

Ejemplo para Productos:
uvicorn productos.main:app --reload --port 8000
Pedidos: --port 8001

Pagos: --port 8002

📝 Endpoints
Productos

GET /productos → Listar productos

POST /productos → Crear producto

PUT /productos/{id} → Actualizar producto

GET /productos/{id} → Obtener producto por ID

Pedidos

POST /pedidos → Crear pedido (verifica stock, calcula total, registra pago)

GET /pedidos → Listar pedidos

GET /pedidos/{id} → Obtener pedido por ID

Pagos

POST /pagos → Registrar pago

GET /pagos → Listar pagos

GET /pagos/{id} → Obtener pago por ID

🔑 Autenticación

Todos los endpoints requieren JWT en el header:
Authorization: Bearer <token>
Token de prueba generado con productos.auth.crear_token({"sub": "admin"})

💡 Casos de prueba recomendados (Postman)

Crear producto con stock > 0

Crear pedido válido → verificar stock descontado y pago registrado

Crear pedido con cantidad > stock → debe fallar

Crear pedido con cantidad 0 → debe fallar

Simular fallo en pagos → verificar rollback del pedido y stock

📖 Notas finales

Principios aplicados: SOLID, Clean Code, separación de responsabilidades

Cada microservicio maneja su propia base de datos y no comparte tablas

Sistema preparado para pruebas locales y futura expansión
