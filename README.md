# Sistema de Gestión de Inventario

Aplicación web desarrollada con **Python y Django** para administrar productos, categorías, proveedores y movimientos de inventario, con control de acceso basado en roles, indicadores operativos y generación de reportes.

El sistema está diseñado para centralizar la gestión de existencias, registrar operaciones de entrada y salida de productos y facilitar la consulta de información del inventario.

## Características principales

### Gestión de usuarios y permisos

- Autenticación mediante inicio y cierre de sesión.
- Administración de usuarios por personal autorizado.
- Control de acceso basado en grupos y permisos de Django.
- Tres roles: **Administradores**, **Almaceneros** y **Consultas**.
- Cambio de contraseña y solicitud de cambio en el primer inicio de sesión para cuentas configuradas con esa condición.

### Catálogo de productos

- Administración de productos, categorías y proveedores.
- Identificación de productos mediante códigos SKU.
- Registro de precios, existencias y stock mínimo.
- Activación y desactivación de registros.

### Gestión de inventario

- Registro de entradas y salidas de productos.
- Ajustes positivos y negativos de inventario.
- Actualización automática de existencias al registrar movimientos.
- Historial de movimientos con fecha, tipo, cantidad y usuario responsable.
- Validaciones para impedir cantidades no válidas y salidas superiores al stock disponible.

### Dashboard

- Panel principal con indicadores del inventario.
- Visualización de información relevante para el seguimiento de existencias.

### Reportes

- **Reporte de existencias:** productos, cantidades disponibles y valor estimado del inventario.
- **Reporte de stock bajo:** productos con existencias insuficientes o agotadas.
- **Reporte de movimientos:** historial de entradas, salidas y ajustes de inventario.
- Filtros de búsqueda para consultar información específica.
- Exportación de reportes en formatos **CSV y Excel (.xlsx)**.

### Interfaz

- Diseño adaptable a dispositivos móviles y computadoras.
- Modo claro y oscuro.
- Mensajes de validación y retroalimentación al usuario.

## Roles y permisos

El sistema utiliza los grupos y permisos de Django para controlar el acceso a las operaciones. Las opciones de navegación se muestran según el rol, y las vistas protegidas también comprueban los permisos desde el servidor.

| Funcionalidad                           | Administradores | Almaceneros | Consultas |
| --------------------------------------- | :-------------: | :---------: | :-------: |
| Ver productos, categorías y proveedores |       Sí        |     Sí      |    Sí     |
| Crear y editar productos                |       Sí        |     Sí      |    No     |
| Crear y editar categorías y proveedores |       Sí        |     Sí      |    No     |
| Consultar movimientos de inventario     |       Sí        |     Sí      |    Sí     |
| Registrar entradas, salidas y ajustes   |       Sí        |     Sí      |    No     |
| Consultar y exportar reportes           |       Sí        |     Sí      |    Sí     |
| Gestionar usuarios                      |       Sí        |     No      |    No     |

**Administradores:** gestionan el catálogo, las operaciones de inventario y las cuentas de usuario. Para administrar usuarios se requiere el permiso `accounts.manage_users`.

**Almaceneros:** mantienen el catálogo y registran movimientos de stock, pero no pueden administrar cuentas de usuario.

**Consultas:** acceden a la información del inventario y a los reportes sin permisos para modificar productos o registrar movimientos.

> La tabla describe la configuración de permisos preparada para la demostración. El acceso efectivo depende de los permisos asignados a los grupos en la base de datos.

## Cómo utilizar el sistema

### 1. Iniciar sesión

Acceder a la aplicación e ingresar el nombre de usuario y la contraseña proporcionados. El menú mostrará las secciones habilitadas para la cuenta.

Las cuentas normales que tengan activada la opción de cambio obligatorio de contraseña deberán actualizarla cuando el sistema lo solicite.

### 2. Consultar el dashboard

Desde el panel principal se pueden revisar los indicadores disponibles para obtener una visión general del inventario.

### 3. Gestionar el catálogo

Los usuarios con permisos de edición pueden:

1. Crear categorías para clasificar los productos.
2. Registrar proveedores.
3. Crear productos indicando nombre, SKU, precio, categoría, proveedor y stock mínimo.
4. Editar la información de los registros existentes.

Los usuarios de **Consultas** pueden visualizar el catálogo, pero no crear ni editar registros.

### 4. Registrar movimientos de inventario

Un usuario con permisos de inventario selecciona un producto, el tipo de movimiento y una cantidad positiva. Los tipos disponibles son:

- **Entrada:** aumenta las existencias.
- **Salida:** disminuye las existencias.
- **Ajuste de entrada:** incrementa el stock por una corrección.
- **Ajuste de salida:** reduce el stock por una corrección.

Al confirmar la operación, el sistema actualiza el stock y guarda el movimiento con su usuario responsable. **No se permiten salidas o ajustes negativos que superen las existencias disponibles.**

### 5. Consultar movimientos y reportes

Los usuarios autorizados pueden revisar el historial de movimientos, consultar existencias y detectar productos con stock bajo. Los reportes disponibles permiten filtrar información y exportarla a **CSV** o **Excel**.

### 6. Administrar usuarios

Solo los usuarios con el permiso correspondiente pueden acceder a la sección de administración de usuarios. Desde allí pueden gestionar las cuentas según las reglas y validaciones implementadas por la aplicación.

## Entorno de demostración

La aplicación se encuentra desplegada utilizando **Render** para el servicio web de Django y **Aiven MySQL** para la base de datos.

Para facilitar la evaluación, se prepararon tres cuentas con permisos diferenciados:

| Cuenta          | Rol             | Propósito                                                   |
| --------------- | --------------- | ----------------------------------------------------------- |
| `demo_admin`    | Administradores | Probar la gestión de usuarios, el catálogo y el inventario. |
| `demo_almacen`  | Almaceneros     | Probar la gestión de productos y los movimientos de stock.  |
| `demo_consulta` | Consultas       | Comprobar el acceso de solo lectura y los reportes.         |

Las credenciales se proporcionan **por separado** a los evaluadores autorizados; no se publican contraseñas en este repositorio.

El entorno puede incluir categorías, proveedores, productos y movimientos ficticios para facilitar las pruebas. No deben utilizarse datos personales o empresariales reales durante la evaluación.

## Tecnologías utilizadas

| Tecnología    | Uso                                          |
| ------------- | -------------------------------------------- |
| Python        | Lenguaje principal del backend               |
| Django 6.1    | Framework web                                |
| MySQL         | Base de datos relacional                     |
| HTML          | Estructura de las páginas                    |
| CSS           | Diseño e interfaz                            |
| JavaScript    | Interacciones del frontend                   |
| Gunicorn      | Servidor de aplicación en producción         |
| WhiteNoise    | Servicio de archivos estáticos en producción |
| OpenPyXL      | Generación de archivos Excel                 |
| python-dotenv | Gestión de variables de entorno              |
| Render        | Alojamiento de la aplicación Django          |
| Aiven         | Alojamiento de la base de datos MySQL        |

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

- Una versión de Python compatible con la versión de Django utilizada.
- MySQL.
- Git.
- Un entorno virtual de Python.

### 1. Clonar el repositorio

```bash
git clone https://github.com/TU_USUARIO/TU_REPOSITORIO.git
cd TU_REPOSITORIO
```

> Sustituir la URL y el nombre del directorio por los datos reales del repositorio.

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

No subir archivos `.env` ni credenciales a GitHub.

### 5. Preparar la base de datos

Crear una base de datos MySQL y un usuario con los permisos necesarios. Después ejecutar:

```bash
python manage.py migrate
```

**Importante:** las migraciones crean las tablas y los permisos definidos por Django, pero los grupos personalizados y sus asignaciones deben configurarse por separado para habilitar los tres roles.

### 6. Crear un superusuario

```bash
python manage.py createsuperuser
```

### 7. Iniciar el servidor

```bash
python manage.py runserver
```

Abrir en el navegador: `http://127.0.0.1:8000/`.

## Pruebas automatizadas

El proyecto incluye pruebas para verificar el funcionamiento de sus componentes.

Para ejecutar las pruebas:

```bash
python manage.py test
```

Las pruebas deben ejecutarse en un entorno aislado de los datos de producción.

## Estado del proyecto

Las funcionalidades principales están implementadas y la aplicación se encuentra desplegada para demostración y evaluación. Se han configurado la conexión a MySQL en Aiven y los roles de acceso para las cuentas de prueba.

## Autor

**Cristopher Cienfuegos**

Proyecto de portafolio desarrollado para demostrar conocimientos de desarrollo backend con Python, Django, bases de datos relacionales, control de acceso y arquitectura modular de aplicaciones web.
