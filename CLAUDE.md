# CLAUDE.md

Este archivo proporciona orientación a Claude Code (claude.ai/code) al trabajar con código en este repositorio.

## Descripción General del Proyecto

Este es un **Sistema de Gestión de Parqueadero** para "Ssalud Plaza Claro" construido con Python y PyQt5. Gestiona 200 espacios de parqueo, empleados (funcionarios), sus vehículos y asignaciones de parqueadero con un sistema de circulación basado en "pico y placa" (días pares/impares).

## Ejecutar la Aplicación

**Con Autenticación:**
```bash
python main_with_auth.py
```
Esto inicia el sistema con una ventana de login que autentica usuarios contra la tabla `usuarios`.

**Sin Autenticación (Acceso Directo):**
```bash
python main_modular.py
```
Esto omite la autenticación y abre la aplicación principal directamente.

## Configuración de la Base de Datos

### Requisitos Previos
- Servidor MySQL ejecutándose en localhost:3306
- Credenciales de base de datos configuradas en [src/config/settings.py](src/config/settings.py):
  - Usuario por defecto: `root`
  - Contraseña por defecto: `root`
  - Nombre de base de datos: `parking_management`

### Configuración Inicial
Ejecutar los archivos de esquema en orden:
1. `parking_database_schema.sql` - Crea tablas, triggers, vistas y procedimientos almacenados
2. `users_table_schema.sql` - Crea la tabla de autenticación

La base de datos se pre-poblará con 200 espacios de parqueo y datos de ejemplo.

## Arquitectura

### Estructura Modular

```
src/
├── auth/           # Sistema de autenticación
├── config/         # Configuración de base de datos y aplicación
├── database/       # Gestor de base de datos y lógica de eliminación en cascada
├── models/         # Lógica de negocio (operaciones CRUD)
├── ui/             # Componentes de interfaz basados en pestañas
├── widgets/        # Widgets de UI reutilizables y estilos
└── utils/          # Utilidades de validación
```

### Patrones Arquitectónicos Clave

**1. Gestor de Base de Datos (Singleton)**
- [src/database/manager.py](src/database/manager.py) implementa un patrón singleton para conexiones de base de datos
- Todas las operaciones de base de datos pasan por `DatabaseManager.fetch_all()`, `fetch_one()`, o `execute_query()`
- La lógica de reconexión automática asegura conexiones resilientes

**2. Comunicación Basada en Señales**
- La ventana principal ([main_modular.py](main_modular.py)) conecta señales PyQt entre pestañas para sincronización en tiempo real
- Cuando los datos cambian en una pestaña (ej. eliminar un funcionario), las señales propagan actualizaciones a todas las pestañas afectadas
- Ver `MainWindow.conectar_senales()` en [main_modular.py:73-117](main_modular.py#L73-L117) para el grafo completo de señales

**3. Sistema de Eliminación en Cascada**
- [src/database/eliminacion_cascada.py](src/database/eliminacion_cascada.py) implementa eliminación en cascada completa
- Cuando un funcionario es eliminado, se remueven TODOS los datos asociados:
  - Vehículos → Asignaciones → Espacios de parqueo (liberados) → Historial de accesos
- Usa transacciones de base de datos para asegurar atomicidad
- Incluye lógica de verificación para confirmar eliminación completa

**4. Separación Modelo-Vista**
- Los modelos ([src/models/](src/models/)) manejan lógica de negocio y operaciones de base de datos
- Los componentes UI ([src/ui/](src/ui/)) manejan presentación e interacción con el usuario
- Cada entidad principal (Funcionario, Vehiculo, Parqueadero, Asignacion) tiene su propio modelo y pestaña

### Reglas de Negocio Críticas

**Lógica de Pico y Placa:**
- Carros con último dígito de placa 1-5 → IMPAR
- Carros con último dígito de placa 6-9, 0 → PAR
- Calculado automáticamente mediante trigger de base de datos `before_insert_vehiculo`
- Cada espacio de parqueo puede contener hasta 2 carros, pero DEBEN tener diferentes tipos de circulación (uno PAR, uno IMPAR)

**Estados de Espacios de Parqueo:**
- `Disponible` - Vacío
- `Parcialmente_Asignado` - 1 carro asignado
- `Completo` - 2 carros asignados (uno PAR, uno IMPAR)
- Los estados se actualizan automáticamente mediante triggers `after_insert_asignacion` y `after_update_asignacion`

**Restricciones de Unicidad:**
- La `cedula` del empleado debe ser única en todo el sistema
- La `placa` del vehículo debe ser única
- Un vehículo solo puede tener una asignación activa a la vez (forzado por clave única en `vehiculo_id, activo`)

## Flujos de Desarrollo Comunes

### Agregar una Nueva Pestaña UI
1. Crear nuevo archivo en [src/ui/](src/ui/)
2. Heredar de `QWidget`
3. Definir señales PyQt para cambios de datos (ej. `vehiculo_creado = pyqtSignal()`)
4. Agregar pestaña a [main_modular.py](main_modular.py) en `setup_ui()`
5. Conectar señales en `conectar_senales()`

### Modificar el Esquema de Base de Datos
1. Actualizar [parking_database_schema.sql](parking_database_schema.sql)
2. Probar localmente: `DROP DATABASE parking_management; SOURCE parking_database_schema.sql;`
3. Actualizar clases de modelo en [src/models/](src/models/) si es necesario
4. Actualizar triggers si el comportamiento de cascada cambia

### Probar Eliminación en Cascada
El sistema de eliminación en cascada es crítico. Para probar:
```python
from src.database.eliminacion_cascada import GestorEliminacionCascada
gestor = GestorEliminacionCascada(db_manager)

# Previsualizar lo que será eliminado
reporte = gestor.generar_reporte_previa_eliminacion("12345678")  # cedula
print(reporte)

# Ejecutar eliminación
exito, mensaje, detalles = gestor.eliminar_funcionario_completo("12345678")
```

## Configuración de Base de Datos

Configuración por defecto en [src/config/settings.py](src/config/settings.py):
- Modificar dataclass `DatabaseConfig` para cambiar configuración de conexión
- Actualizar `CARGOS_DISPONIBLES` y `DIRECCIONES_DISPONIBLES` para opciones de menús desplegables
- Los enums `TipoVehiculo` y `TipoCirculacion` definen tipos de vehículos válidos

## Archivos Importantes

- [main_with_auth.py](main_with_auth.py) - Punto de entrada con autenticación
- [main_modular.py](main_modular.py) - Ventana principal de aplicación y conexiones de señales
- [src/database/manager.py](src/database/manager.py) - Capa de abstracción de base de datos
- [src/database/eliminacion_cascada.py](src/database/eliminacion_cascada.py) - Lógica de eliminación en cascada
- [parking_database_schema.sql](parking_database_schema.sql) - Esquema completo de base de datos con triggers
- [src/config/settings.py](src/config/settings.py) - Todas las constantes de configuración

## Sistema de Autenticación

Los usuarios se autentican mediante [src/auth/auth_manager.py](src/auth/auth_manager.py):
- Las contraseñas se almacenan en texto plano (NO LISTO PARA PRODUCCIÓN)
- Los usuarios tienen roles (almacenados en columna `rol`)
- Se rastrea la marca de tiempo del último acceso
- Ventana de login: [src/auth/login_window.py](src/auth/login_window.py)

## Notas

- El sistema usa PyQt5 para la GUI con un estilo "Fusion" personalizado
- Todo el texto está en español
- El código usa codificación UTF-8
- Los triggers de base de datos manejan la mayor parte de la gestión de estado automáticamente
- Las conexiones de señales aseguran que la UI se mantenga sincronizada en todas las pestañas
