# 🛡️ AegisShare — AI-Powered Data Loss Prevention (DLP) Platform

**AegisShare** es una plataforma moderna de prevención de pérdida de datos (DLP) diseñada para analizar, detectar y bloquear la exfiltración de información sensible (PII) en tiempo real. Combina una arquitectura de microservicios eficiente con una interfaz de usuario reactiva para ofrecer auditoría de seguridad instantánea.

---

## 🚀 Características Clave (Key Features)

- **Análisis DLP Inteligente**: Motor de escaneo configurable capaz de detectar patrones sensibles (tarjetas de crédito, emails, teléfonos) en archivos de texto, aplicando políticas de seguridad dinámicas.
- **Gestión de Políticas en Tiempo Real**: Sistema flexible para definir reglas de bloqueo (`block`, `warn`, `ignore`) y umbrales de confianza (`min_confidence`) sin reiniciar el servicio.
- **Auditoría y Trazabilidad**: Registro inmutable de todos los escaneos (`ScanLog`), detallando usuario, archivo, nivel de riesgo y entidades detectadas para cumplimiento normativo.
- **Control de Acceso Basado en Roles (RBAC)**: Autenticación segura mediante **JWT (JSON Web Tokens)** con diferenciación de perfiles (Analista vs. Administrador).
- **Interfaz Reactiva Moderna**: Dashboard interactivo con carga de archivos drag-and-drop, visualización de resultados JSON y estado del sistema en tiempo real.

---

## 🛠️ Stack Tecnológico

### Backend (API & Core)

- **Lenguaje**: Python 3.10+
- **Framework**: **FastAPI** (High-performance async driver)
- **Base de Datos**: **SQLAlchemy** (ORM) + SQLite (Dev) / PostgreSQL (Prod ready)
- **Seguridad**: OAuth2 con Password Flow + Bearer JWT Tokens + Hashing de contraseñas (Bcrypt)
- **Validación de Datos**: **Pydantic** v2 para esquemas estrictos y serialización.

### Frontend (User Interface)

- **Framework**: **React 19** + **Vite** (Build tool de última generación)
- **Estilos**: **Tailwind CSS v4** (Utility-first framework)
- **Estado y Consumo de API**: Fetch API con interceptores de autenticación.
- **UX/UI**: Diseño responsivo, feedback visual inmediato (Badges de estado) y navegación fluida (SPA).

---

## 🏗️ Arquitectura del Proyecto

El sistema sigue una arquitectura de capas limpia y modular:

1.  **Routers Layer**: Endpoints RESTful segregados por dominio (`auth`, `scan`, `users`, `policies`).
2.  **Service Layer**: Lógica de negocio pura (ej. motor de análisis DLP) desacoplada de la capa HTTP.
3.  **Data Access Layer (ORM)**: Modelos de SQLAlchemy para interactuar con la base de datos de forma agnóstica.
4.  **Presentation Layer**: SPA (Single Page Application) en React que consume la API de forma asíncrona.

---

## 🔧 Instalación y Despliegue

```bash
# Backend (Puerto 8000)
uvicorn app.main:app --reload

# Frontend (Puerto 5173)
npm run dev
```

---

_Proyecto desarrollado con enfoque en seguridad por diseño (Security by Design) y mejores prácticas estandarizadas de desarrollo de software (Clean Code, PEP8)._
