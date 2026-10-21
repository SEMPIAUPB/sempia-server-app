# SEMPIA Server App (Backend Core API)

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white&style=for-the-badge" alt="Python" />
  <img src="https://img.shields.io/badge/Django-4.2%20LTS-092E20?logo=django&logoColor=white&style=for-the-badge" alt="Django" />
  <img src="https://img.shields.io/badge/Django_REST-Framework-A30000?style=for-the-badge" alt="DRF" />
  <img src="https://img.shields.io/badge/PostgreSQL-15-336791?logo=postgresql&logoColor=white&style=for-the-badge" alt="PostgreSQL" />
  <img src="https://img.shields.io/badge/Redis-7-DC382D?logo=redis&logoColor=white&style=for-the-badge" alt="Redis" />
  <img src="https://img.shields.io/badge/JWT-SimpleJWT-black?style=for-the-badge" alt="JWT" />
</p>

---

## 📖 Descripción

**`sempia-server-app`** es el servidor central autoritativo de la plataforma SEMPIA. Implementado sobre **Django** y **Django REST Framework (DRF)**, orquesta la persistencia transaccional relacional, la autenticación y autorización criptográfica, la máquina de estados de envíos al juez, el motor de gamificación, la gestión del grafo pedagógico y la intermediación segura (*API Gateway*) hacia el microservicio cognitivo de Inteligencia Artificial.

---

## ✨ Módulos y Arquitectura de Dominio

El backend está desacoplado en aplicaciones Django modulares que responden a la arquitectura de dominio:

* **`accounts` (Gestión de Identidad y Seguridad):**
  * Modelo `User` personalizado con roles (`STUDENT`, `ADMIN_TEACHER`, `SUPER_ADMIN`) y metadatos académicos (semestre, facultad, universidad).
  * Autenticación basada en JSON Web Tokens (JWT) mediante `djangorestframework-simplejwt`.
  * Cierre de sesión seguro con revocación forzosa en backend mediante lista negra de tokens (`token_blacklist`).
  * Contraseñas hasheadas con PBKDF2-HMAC-SHA256 ($600{,}000$ iteraciones, $H = 78.65\text{ bits}$ de entropía).
* **`exercises` (Catálogo y Banco de Problemas):**
  * Modelo `Exercise` con máquina de estados (`DRAFT`, `PUBLISHED`, `ARCHIVED`) y borrado lógico (*soft-delete*) mediante `is_deleted` para proteger la autoría y consistencia histórica de envíos (RNF-08).
  * Casos de prueba `TestCase` clasificados como `VISIBLE` (ejemplos públicos) y `HIDDEN` (evaluación privada del juez).
  * Límites de CPU (`time_limit_ms`) y memoria RAM (`memory_limit_kb`) parametrizados por ejercicio.
* **`skills` (Grafo Cognitivo y Diagnóstico):**
  * Grafo Acíclico Dirigido (DAG) de habilidades algorítmicas con validador DFS para impedir ciclos.
  * Banco de preguntas diagnósticas (`DiagnosticQuestion`) con limitador teórico inicial del 40% de maestría.
  * Trazabilidad de dominio continuo `UserSkillProgress` sincronizado con las inferencias de DKT.
* **`submissions` (Envíos, Despacho y Callback del Juez):**
  * Recepción inmutable de código fuente.
  * Encolamiento asíncrono hacia Redis en la cola `judge_submissions` bajo el contrato versionado `SubmissionContract`.
  * Endpoint receptor de calificaciones: `POST /api/v1/submissions/{id}/callback` consumido por el worker de ejecución.
  * Registro de auditoría de ciclo de vida en `SubmissionTransition` (`PENDING` $\to$ `RUNNING` $\to$ `COMPLETED`).
* **`gamification` (Ecosistema de Motivación y Competencia):**
  * Despacho reactivo de experiencia ($XP$) mediante señales Django post-guardado (`post_save`).
  * Protección anti-farming con clave de idempotencia única `reference_id` (solo el primer `ACCEPTED` acredita experiencia).
  * Progresión de nivel cuadrática: $XP = 100 \times L^2 \implies L = \lfloor \sqrt{XP/100} \rfloor + 1$.
  * Ranking optimizado con índices B-Tree en PostgreSQL, garantizando lecturas en $\mathcal{O}(K)$.
  * Desafíos semanales (`Challenge`) y desbloqueo de medallas e insignias (`Achievement`).
* **`config` (API Gateway & Proxy de IA):**
  * `DKTProxyView` y `TutoringProxyView`: Proxy inverso autenticado que reenvía solicitudes hacia `sempia-ai-worker` (FastAPI en puerto 8001) ocultándolo de la red pública.
  * Motor de contingencia (*fallback*) heurístico ante errores HTTP 429 / 503 del microservicio de IA.

---

## 🛠️ Stack Tecnológico

* **Lenguaje:** Python 3.11
* **Framework:** Django 4.2 LTS & Django REST Framework 3.14
* **Base de Datos:** PostgreSQL 15 (soporta SQLite3 para desarrollo local rápido)
* **Broker / Colas:** Celery 5 & Redis 7
* **Autenticación:** SimpleJWT con rotación de tokens y lista negra
* **Documentación API:** `drf-spectacular` (OpenAPI 3.0 / Swagger UI)
* **Pruebas Automatizadas:** `pytest` & `pytest-django`

---

## 🚀 Instalación y Puesta en Marcha

### 1. Requisitos Previos
* Python 3.11 instalado
* PostgreSQL 15 y Redis 7 (o Docker para levantarlos como servicios)

### 2. Configuración del Entorno Virtual
```bash
# Crear y activar entorno virtual
python -m venv venv
# En Linux/macOS:
source venv/bin/activate
# En Windows:
venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt
```

### 3. Configuración de Variables de Entorno (`.env`)
Crea un archivo `.env` en la raíz de `sempia-server-app/`:
```bash
SECRET_KEY=clave_secreta_django_produccion_2026
DEBUG=True
ALLOWED_HOSTS=*
POSTGRES_DB=sempia
POSTGRES_USER=sempia
POSTGRES_PASSWORD=sempia
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
CELERY_BROKER_URL=redis://localhost:6379/1
AI_WORKER_URL=http://localhost:8001
```

### 4. Migraciones y Datos Semilla (Fixtures)
```bash
# Aplicar migraciones
python manage.py migrate

# Crear cuenta de Administrador / Docente
python manage.py createsuperuser

# Poblar catálogos iniciales
python load_graph.py
python populate_diagnostics.py
python populate_exercises.py
python populate_achievements.py
```

### 5. Iniciar Servidor de Desarrollo
```bash
# Escuchando en 0.0.0.0 para acceso local y por Wi-Fi
python manage.py runserver 0.0.0.0:8000
```

---

## 📖 Documentación de la API (OpenAPI 3.0)

Con el servidor en ejecución, accede interactivamente a los contratos de la API:
* **Swagger UI Interactivo:** `http://localhost:8000/api/v1/docs/`
* **Especificación YAML en Crudo:** `http://localhost:8000/api/v1/schema/`

---

## 🧪 Pruebas Automatizadas

El repositorio incluye suites de pruebas unitarias y de integración que verifican la lógica de negocio, la inmutabilidad de la autoría y la idempotencia de gamificación:

```bash
pytest
```
*Cobertura: 60 casos de prueba unitarios en `accounts`, `exercises`, `submissions` y `gamification` con 100% de éxito.*

---

## 📂 Estructura del Proyecto

```
sempia-server-app/
├── accounts/            # Modelos de Usuario, Autenticación JWT y Roles
├── exercises/           # Modelos de Ejercicios, Casos de Prueba y Soft-Delete
├── skills/              # Grafo DAG de Habilidades y Evaluación Diagnóstica
├── submissions/         # Envíos de Código, Despacho a Redis y Callbacks
├── gamification/        # Puntos XP, Rachas, Niveles, Retos y Logros
├── config/              # Configuración Django, URLs, API Gateway Proxy y Autenticación
├── load_graph.py        # Script semilla: Grafo de Habilidades
├── populate_*.py        # Scripts semilla: Diagnósticos, Ejercicios y Logros
├── manage.py            # CLI de administración de Django
└── requirements.txt     # Dependencias de Python
```
