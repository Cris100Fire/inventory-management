# Sistema de Gestión de Inventario

Aplicación web desarrollada con **Python y Django** para administrar productos, categorías, proveedores y movimientos de inventario, con control de acceso basado en roles, indicadores operativos y generación de reportes.

El sistema está diseñado para centralizar la gestión de existencias, registrar operaciones de entrada y salida de productos y facilitar la consulta de información del inventario.

## Características principales

### Gestión de usuarios y permisos

- Autenticación mediante inicio y cierre de sesión.
- Administración de usuarios.
- Control de acceso basado en grupos y permisos.
- Roles de administradores, almaceneros y usuarios de consulta.
- Cambio de contraseña.

### Catálogo de productos

- Administración de productos, categorías y proveedores.
- Identificación de productos mediante códigos SKU.
- Registro de precios, existencias y stock mínimo.
- Activación y desactivación de registros.

### Gestión de inventario

- Registro de entradas y salidas de productos.
- Ajustes de inventario.
- Actualización de existencias.
- Historial de movimientos con información del usuario responsable.
- Validaciones de operaciones de inventario.

### Dashboard

- Panel principal con indicadores del inventario.
- Visualización de información relevante para el seguimiento de existencias.

### Reportes

- **Reporte de existencias:** consulta de productos, cantidades disponibles y valor estimado del inventario.
- **Reporte de stock bajo:** identificación de productos con existencias insuficientes o agotadas.
- **Reporte de movimientos:** historial de entradas, salidas y ajustes de inventario.
- Filtros de búsqueda para consultar información específica.
- Exportación de reportes en formatos **CSV y Excel (.xlsx)**.

### Interfaz

- Diseño adaptable a dispositivos móviles y computadoras.
- Modo claro y oscuro.
- Mensajes de validación y retroalimentación al usuario.

## Tecnologías utilizadas

| Tecnología    | Uso                                                           |
| ------------- | ------------------------------------------------------------- |
| Python        | Lenguaje principal del backend                                |
| Django 6.1    | Framework web                                                 |
| MySQL         | Base de datos relacional                                      |
| HTML          | Estructura de las páginas                                     |
| CSS           | Diseño e interfaz                                             |
| JavaScript    | Interacciones del frontend                                    |
| WhiteNoise    | Servicio de archivos estáticos en producción, si se configura |
| OpenPyXL      | Generación de archivos Excel                                  |
| python-dotenv | Gestión de variables de entorno                               |

## Arquitectura del proyecto

El sistema utiliza una arquitectura modular basada en aplicaciones de Django.

```text
apps/
├── accounts/       # Usuarios, autenticación y permisos
├── catalog/        # Productos, categorías y proveedores
├── inventory/      # Movimientos y operaciones de stock
├── dashboard/      # Panel principal e indicadores
└── reports/        # Consultas y exportaciones

config/             # Configuración principal de Django
static/             # Archivos CSS y JavaScript
templates/          # Plantillas HTML
manage.py           # Administración de Django
requirements.txt    # Dependencias de Python
```

La separación por aplicaciones permite organizar las responsabilidades del sistema y facilitar su mantenimiento.

## Instalación local

### Requisitos

- Python compatible con la versión de Django utilizada.
- MySQL.
- Git.
- Un entorno virtual de Python.

### 1. Clonar el repositorio

```bash
git clone https://github.com/TU_USUARIO/TU_REPOSITORIO.git
cd TU_REPOSITORIO
```

### 2. Crear y activar el entorno virtual

En Linux o WSL:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno

Crear un archivo `.env` en la raíz del proyecto tomando como referencia `.env.example`.

```dotenv
SECRET_KEY=tu_clave_secreta
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost

DB_NAME=inventory_db
DB_USER=inventory_user
DB_PASSWORD=tu_contraseña
DB_HOST=127.0.0.1
DB_PORT=3306
```

### 5. Preparar la base de datos

Crear una base de datos MySQL y un usuario con los permisos necesarios.

Después ejecutar:

```bash
python manage.py migrate
```

### 6. Crear un superusuario

```bash
python manage.py createsuperuser
```

### 7. Iniciar el servidor

```bash
python manage.py runserver
```

Abrir en el navegador:

`http://127.0.0.1:8000/`

## Pruebas automatizadas

El proyecto incluye pruebas para verificar el funcionamiento de sus componentes.

Para ejecutar las pruebas:

```bash
python manage.py test
```

## Capturas de pantalla

_Pendiente: incorporar capturas reales del dashboard, catálogo, movimientos y reportes._

## Estado del proyecto

Funcionalidades principales implementadas. Preparación del repositorio y despliegue pendientes.

## Autor

Desarrollado como proyecto de portafolio para demostrar conocimientos de desarrollo backend con Python, Django, bases de datos relacionales y arquitectura modular de aplicaciones web.
