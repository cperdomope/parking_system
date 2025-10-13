# SecureShield - Agente de Seguridad OWASP

Ejecuta un análisis completo de seguridad del Sistema de Gestión de Parqueadero basado en las mejores prácticas de OWASP Top 10 (2021).

## Funcionalidad

El agente SecureShield escaneará el código buscando:

1. **Contraseñas hardcodeadas** - Credenciales en texto plano
2. **Vulnerabilidades SQL Injection** - Consultas no parametrizadas
3. **Falta de hashing de contraseñas** - Almacenamiento inseguro
4. **Conexiones sin SSL/TLS** - Transmisión de datos sin cifrar
5. **Imports inseguros** - pickle, eval, exec
6. **Falta de validación de entradas** - Sanitización insuficiente
7. **Sin protección contra fuerza bruta** - Intentos de login ilimitados
8. **Falta de logging de auditoría** - Sin registros de eventos de seguridad

## Salida

Genera un reporte completo `SECURITY_AUDIT.md` con:

- Puntuación de seguridad (0-100)
- Nivel de riesgo (Bajo/Medio/Alto/Crítico)
- Hallazgos detallados por severidad (CRITICAL/HIGH/MEDIUM/LOW)
- Categorización según OWASP Top 10 y CWE
- Plan de remediación priorizado
- Ejemplos de código para implementar correcciones
- Checklist de seguridad

## Uso

Invoca este comando para ejecutar el análisis:

```bash
/secureshield
```

O ejecuta directamente el script:

```bash
python .claude/secureshield_analyzer.py
```

## Implementaciones Recomendadas

El agente recomendará implementar:

1. **Hash seguro con bcrypt**
2. **Variables de entorno con .env**
3. **Protección contra fuerza bruta**
4. **Sistema de logging cifrado**
5. **Consultas parametrizadas**
6. **SSL/TLS en MySQL**
7. **Sanitización de entradas**
8. **Autenticación de dos factores (2FA)**

## Tiempo de Ejecución

~10-30 segundos dependiendo del tamaño del proyecto

## Requisitos

- Python 3.8+
- Acceso al código fuente del proyecto
