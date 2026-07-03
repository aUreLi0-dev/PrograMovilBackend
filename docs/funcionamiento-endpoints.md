# Funcionamiento de Endpoints — Login y Notas

## Índice

0. [¿Qué hace cada archivo?](#0-qué-hace-cada-archivo-explicación-sencilla)
1. [Arquitectura General](#1-arquitectura-general)
2. [Cadena de Registro de Blueprints](#2-cadena-de-registro-de-blueprints)
3. [Conexión a Base de Datos](#3-conexión-a-base-de-datos)
4. [Modelos de Datos](#4-modelos-de-datos)
5. [Middleware de Autenticación](#5-middleware-de-autenticación)
6. [Login — Endpoints y Flujo Completo](#6-login--endpoints-y-flujo-completo)
7. [Notas — Endpoints y Flujo Completo](#7-notas--endpoints-y-flujo-completo)
8. [Resumen de Endpoints y Middleware Asociado](#8-resumen-de-endpoints-y-middleware-asociado)

---

## 0. ¿Qué hace cada archivo? (Explicación sencilla)

Antes de entrar en detalle, aquí un resumen de para qué sirve cada pieza del proyecto:

| Archivo/Carpeta | ¿Qué es? | ¿Qué hace? |
|---|---|---|
| `app.py` | **Punto de entrada** | Es el archivo que se ejecuta para arrancar el servidor. Prende Flask, conecta todos los módulos y pone el servidor a escuchar en el puerto 5000. |
| `login/application.py` | **Fábrica de la app** | Crea la instancia de Flask y la configura: le pone clave secreta, activa JWT (tokens), activa sesiones en disco. Es el "cerebro" que prepara la app antes de usarla. |
| `login/blueprints.py` | **Organizador de rutas** | Junta todas las rutas (blueprints) de todos los módulos (login, notas, malla, etc.) y las registra en la app. Es como el directorio telefónico que le dice a Flask "esta ruta va con este código". |
| `login/middlewares.py` | **Guardias de seguridad** | Tiene funciones que se ejecutan ANTES de llegar al endpoint. Por ejemplo: verificar que el JWT sea válido, o redirigir si no has iniciado sesión. |
| `login/models.py` | **Definición de tablas** | Le dice a SQLAlchemy cómo se ve la tabla `app_user` en la base de datos: qué columnas tiene, sus tipos, etc. |
| `login/apis.py` | **Lógica de login REST** | Aquí están los endpoints de la API REST para login: `sign-in`, `me`, `sign-out`. Cada función recibe una petición, consulta la BD y devuelve un JSON. |
| `login/views.py` | **Páginas HTML** | Maneja las rutas que devuelven HTML en lugar de JSON (el login por formulario, la página principal, etc.). Usa sesiones server-side. |
| `core/database.py` | **Conexión a la BD** | Crea el motor de base de datos (SQLite) y la fábrica de sesiones. Todos los demás archivos importan de aquí para poder consultar la BD. |
| `notas/blueprints.py` | **Organizador de notas** | Junta los 7 blueprints del módulo notas (assessment, calculator, delegate, etc.) en una lista para que `login/blueprints.py` los registre. |
| `notas/models.py` | **Definición de tablas** | Define 18 tablas: cursos, matrículas, evaluaciones, notas, horarios, etc. Es el modelo de datos más grande del proyecto. |
| `notas/apis/` | **Lógica de notas** | Cada archivo dentro de esta carpeta es un grupo de endpoints: `assessment.py` (evaluaciones), `student_score.py` (notas), `calculator.py` (promedios), `delegate.py` (delegados), etc. |
| `descripcion_cursos/` | **Módulo descripción cursos** | Sigue la misma estructura que `notas/` pero con endpoints para ver detalle de cursos, asesorías y contactos. |
| `malla/` | **Módulo malla curricular** | Sigue la misma estructura para la malla curricular: progreso, simulación, especialidades. |
| `db/schema.sql` | **Esquema de la BD** | El SQL con la definición de las 27 tablas, sus columnas, llaves foráneas y restricciones. |
| `db/seed.sql` | **Datos de prueba** | Datos precargados (alumnos, cursos, notas) para poder probar la app sin tener que llenar todo manualmente. |

---

## 1. Arquitectura General

```
app.py
  └── importa login.application.APP (instancia Flask)
  └── importa login.blueprints.register
  └── importa login.middlewares.not_found
  └── llama register(APP)
  └── APP.run(debug=True, host='0.0.0.0', port=5000)
```

### Archivo: `app.py`

Es el punto de entrada de la aplicación. Importa:

| Importación | Procedencia | Propósito |
|---|---|---|
| `APP` | `login/application.py` | Instancia de Flask preconfigurada con JWT y sesiones |
| `register` | `login/blueprints.py` | Función que registra todos los blueprints |
| `not_found` | `login/middlewares.py` | Manejador personalizado de error 404 |

### Archivo: `login/application.py`

Crea y configura la instancia de Flask:

```python
APP = Flask(__name__, static_folder='../static', static_url_path='/')
```

**Configuraciones que aplica:**

| Config | Valor | Efecto |
|---|---|---|
| `SECRET_KEY` | `'your_secret_key'` | Firma de cookies de sesión |
| `SESSION_TYPE` | `'filesystem'` | Sesiones guardadas en disco (carpeta `flask_session/`) |
| `SESSION_PERMANENT` | `False` | Sesiones no permanentes (expiran al cerrar navegador) |
| `SESSION_USE_SIGNER` | `True` | Firma las cookies de sesión |
| `SESSION_KEY_PREFIX` | `'session:'` | Prefijo para claves de sesión |
| `JWT_SECRET_KEY` | `'tu_clave_secreta_aqui'` | Clave para firmar tokens JWT |
| `JWT_ACCESS_TOKEN_EXPIRES` | `timedelta(hours=5)` | Tokens JWT expiran en 5 horas |

Inicializa dos extensiones:

- **`Session(APP)`** — Flask-Session (sesiones server-side)
- **`JWTManager(APP)`** — Flask-JWT-Extended (tokens JWT)

Además define:

- `REVOKED_TOKENS` — lista en memoria de tokens revocados (se pierde al reiniciar el servidor)
- `check_if_token_revoked()` — callback que verifica si un JWT está en la lista negra
- Manejadores de error JWT en español: `unauthorized_response`, `expired_token_response`, `invalid_token_response`, `needs_fresh_token_response`

---

## 2. Cadena de Registro de Blueprints

### Archivo: `login/blueprints.py`

```
register(app)
  ├── app.register_blueprint(main_views)     ← login/views.py (rutas HTML)
  ├── app.register_blueprint(main_apis)      ← login/apis.py (login REST)
  └── Por cada módulo en modules_blueprints:
       ├── notas_blueprints                   ← notas/blueprints.py (7 blueprints)
       ├── descripcion_cursos_blueprints      ← descripcion_cursos/blueprints.py (3 blueprints)
       └── malla_blueprints                   ← malla/blueprints.py (4 blueprints)
```

### Archivo: `notas/blueprints.py`

Agrega 7 sub-blueprints del paquete `notas`:

| Blueprint | Archivo | Prefijo de rutas |
|---|---|---|
| `notas_assessment_type` | `notas/apis/assessment_type.py` | `/api/v1/assessment-types` |
| `notas_assessment` | `notas/apis/assessment.py` | `/api/v1/assessments` |
| `notas_student_score` | `notas/apis/student_score.py` | `/api/v1/student-scores` |
| `notas_calculator` | `notas/apis/calculator.py` | `/api/v1/calculator/...` |
| `notas_career_setup` | `notas/apis/career_setup.py` | `/api/v1/careers`, `/api/v1/specialties` |
| `notas_schedule` | `notas/apis/schedule.py` | `/api/v1/students/{id}/schedule` |
| `notas_delegate` | `notas/apis/delegate.py` | `/api/v1/delegate/...` |

**Flujo de importación:**

```
app.py
  → login/blueprints.py
      → importa de notas/blueprints.py → blueprints (lista)
          → importa de notas/apis/assessment_type.py → api
          → importa de notas/apis/assessment.py → api
          → importa de notas/apis/student_score.py → api
          → importa de notas/apis/calculator.py → api
          → importa de notas/apis/career_setup.py → api
          → importa de notas/apis/schedule.py → api
          → importa de notas/apis/delegate.py → api
```

---

## 3. Conexión a Base de Datos

### Archivo: `core/database.py`

Es el núcleo de conexión a la base de datos.

```python
engine = create_engine("sqlite:///db/app.db", echo=True)
Session = sessionmaker(bind=engine)
```

| Elemento | Descripción |
|---|---|
| `engine` | Motor SQLAlchemy conectado a SQLite (`db/app.db`). `echo=True` habilita logs de todas las consultas SQL. |
| `Session` | Fábrica de sesiones. Cada endpoint crea su propia sesión (`Session()`), la usa, y la cierra en un bloque `finally`. |

### Mixin `ToString`

Clase base que provee dos métodos a todos los modelos:

- `to_dict()` — Convierte el objeto SQLAlchemy a diccionario (filtra atributos que empiezan con `_`)
- `__repr__` — Representación legible del objeto

### Uso típico de sesión en cada endpoint:

```python
session = Session()
try:
    item = session.query(Modelo).filter_by(...).first()
    # ... lógica de negocio ...
    session.commit()  # solo si hay escritura
except Exception:
    session.rollback()  # solo si hay escritura
finally:
    session.close()
```

### Base de datos física

- **Motor:** SQLite
- **Archivo:** `db/app.db`
- **Esquema:** `db/schema.sql` (27 tablas con constraints, foreign keys, índices y unique indexes)
- **Seed data:** `db/seed.sql` (datos de prueba con contraseña `ulima123` en texto plano)

### Duplicado legacy

Existe `login/database.py` que es idéntico a `core/database.py`. Todos los endpoints activos importan desde `core.database`.

---

## 4. Modelos de Datos

### 4.1 Modelos del paquete `login` — `login/models.py`

| Modelo | Tabla | Columnas |
|---|---|---|
| `User` | `app_user` | `id`, `code`, `full_name`, `institutional_email`, `password_hash`, `google_id`, `token_version` |

**Propósito:** Autenticación de usuarios. Usado exclusivamente por `login/apis.py`.

### 4.2 Modelos del paquete `notas` — `notas/models.py` (18 modelos)

Son los modelos principales. Cada paquete (`notas`, `descripcion_cursos`, `malla`) define sus propios modelos duplicados para las mismas tablas, pero el paquete `notas` contiene la mayoría.

#### Tablas base (sin foreign keys)

| Modelo | Tabla | Columnas clave |
|---|---|---|
| `AssessmentType` | `assessment_type` | `id`, `name`, `abbreviation`, `description` |
| `Course` | `course` | `id`, `code`, `name`, `default_credit`, `origin_faculty` |
| `AcademicPeriod` | `academic_period` | `id`, `code`, `start_date`, `end_date`, `is_active` |
| `Teacher` | `teacher` | `id`, `teacher_code`, `full_name`, `institutional_email` |
| `AppUser` | `app_user` | Duplicado de `login.models.User` (misma tabla) |

#### Primer nivel de dependencia

| Modelo | Tabla | FK | Relaciones |
|---|---|---|---|
| `CourseOffering` | `course_offering` | `academic_period_id`, `course_id` | `academic_period`, `course` |
| `Syllabus` | `syllabus` | `course_offering_id` | `course_offering` |
| `Section` | `section` | `course_offering_id`, `teacher_id` | `course_offering`, `teacher` |
| `Career` | `career` | — | — |
| `Curriculum` | `curriculum` | `career_id` | `career` |

#### Segundo nivel de dependencia

| Modelo | Tabla | FK | Relaciones |
|---|---|---|---|
| `Student` | `student` | `user_id`, `career_id`, `curriculum_id` | `user`, `career`, `curriculum`, `enrollments` |

#### Tercer nivel de dependencia

| Modelo | Tabla | FK | Relaciones |
|---|---|---|---|
| `Enrollment` | `enrollment` | `student_id`, `section_id` | `student`, `section`, `scores` |
| `Assessment` | `assessment` | `syllabus_id`, `assessment_type_id` | `syllabus`, `assessment_type` |
| `Specialty` | `specialty` | `career_id` | `career` |
| `StudentSpecialty` | `student_specialty` | `student_id`, `specialty_id` (PK compuesta) | `student`, `specialty` |
| `ScheduleSession` | `schedule_session` | `section_id` | `section` |
| `CourseAdvisingSession` | `course_advising_session` | `course_offering_id`, `section_id`, `teacher_id` | `course_offering`, `section`, `teacher` |

#### Cuarto nivel de dependencia

| Modelo | Tabla | FK | Relaciones |
|---|---|---|---|
| `StudentScore` | `student_score` | `enrollment_id`, `assessment_id` | `enrollment`, `assessment` |
| `SectionRepresentative` | `section_representative` | `section_id`, `enrollment_id` | `section`, `enrollment` |
| `Announcement` | `announcement` | `section_representative_id` | `section_representative` |

### 4.3 Relaciones clave entre modelos

```
Student (1) ──────< Enrollment (N) ──────> (1) Section
  │                                        │
  │                                        ├── (1) CourseOffering ──> (1) Course
  │                                        │                         
  │                                        ├── (1) Teacher
  │                                        │
  │                                        └── ScheduleSession (N)
  │
  └── (1) AppUser (User)
  └── (1) Career
  └── (1) Curriculum

Enrollment (1) ──< StudentScore (N) ──> (1) Assessment
                                              │
                                              ├── (1) Syllabus ──> (1) CourseOffering
                                              └── (1) AssessmentType

Section (1) ──< SectionRepresentative (N)
  └── SectionRepresentative (1) ──< Announcement (N)
```

---

## 5. Middleware de Autenticación

### Archivo: `login/middlewares.py`

Define 4 funciones de middleware:

#### 5.1 `jwt_required(fn)` — Middleware JWT personalizado

**Usado por:** `login/apis.py` (profile, signout), `notas/apis/delegate.py`, `descripcion_cursos/*`, `malla/*`

**Flujo:**

1. Llama a `verify_jwt_in_request()` (función de flask-jwt-extended que valida firma, expiración y blocklist)
2. Extrae `claims = get_jwt()`
3. Verifica que exista `claims["user_id"]` (reclamo adicional agregado al crear el token)
4. Guarda `g.user_id` y `g.username` en el contexto global de Flask (`g`)
5. Si algo falla, retorna JSON `401` con mensaje de error

**Diferencia con el decorador estándar:** Este middleware personalizado extrae `user_id` de los claims adicionales y lo expone en `g.user_id`. El estándar (`@jwt_required()` de flask-jwt-extended) solo verifica el token sin exponer claims adicionales automáticamente.

#### 5.2 `@jwt_required()` — Decorador estándar de flask-jwt-extended

**Usado por:** Todos los endpoints CRUD de `notas/apis/` (assessment_type, assessment, student_score, calculator, career_setup, schedule)

**Flujo:**

1. Verifica que el header `Authorization: Bearer <token>` exista y sea un JWT válido
2. Si es inválido o expiró, retorna el error configurado en `login/application.py` (en español)
3. No expone automáticamente claims en `g`; se debe usar `get_jwt()` dentro del endpoint si se necesitan

#### 5.3 `only_logged(fn)` — Middleware de sesión Flask

**Usado por:** Rutas HTML protegidas (no hay en el código actual, pero el decorador está definido)

**Flujo:**

1. Verifica `session.get('status')`
2. Si es `False` o no existe, redirige a `/error/403`
3. Si es `True`, ejecuta la función

#### 5.4 `logged_go_admin(fn)` — Middleware inverso

**Usado por:** `login/views.py` (home, sign-in GET)

**Flujo:**

1. Si `session.get('status') == True`, redirige a `/admin`
2. Si no, permite ejecutar la función (evita que un usuario ya logueado vea la pantalla de login)

#### 5.5 `not_found(e)` — Manejador de error 404

Registrado en `app.py`:

```python
APP.register_error_handler(404, not_found)
```

**Flujo:**

- Si es GET y la URL contiene `.css`, `.js`, `.woff`, o `png`, retorna texto plano `'Recurso no encontrado'`
- Si es GET sin esas extensiones, redirige a `/error/404`
- Si no es GET, retorna texto plano `'Recurso no encontrado'`

---

## 6. Login — Endpoints y Flujo Completo

### 6.1 POST `/api/sign-in` — Inicio de sesión

**Archivo:** `login/apis.py` — función `sign_in()`

**Middleware:** Ninguno (no requiere autenticación)

**Flujo completo:**

```
Cliente                                   Servidor
  │                                         │
  │  POST /api/sign-in                      │
  │  Body: { "code": "...", "password": "..." }
  │────────────────────────────────────────>│
  │                                         │
  │                              1. Validar JSON body
  │                              2. Validar campos code y password
  │                              3. Crear sesión DB: Session()
  │                              4. Consultar User:
  │                                   db_session.query(User)
  │                                     .filter(User.code == username,
  │                                             User.password_hash == password)
  │                                     .first()
  │                              5. Si no existe → 401
  │                              6. Si existe:
  │                                   a. Crear JWT con:
  │                                      - identity = code (username)
  │                                      - additional_claims = { "user_id": user.id }
  │                                      - expira en 5 horas (300 min)
  │                                   b. Almacenar sesión server-side:
  │                                      session['status'] = True
  │                                      session['user'] = user.to_dict()
  │                                   c. Retornar JSON:
  │                                      { data: { user: {...}, jwt: "..." },
  │                                        success: true }
  │                              7. Cerrar sesión DB en finally
  │                                         │
  │  { data: { user: {...}, jwt: "..." },   │
  │    success: true }                      │
  │<────────────────────────────────────────│
```

**Particularidades:**

- **Contraseña en texto plano:** La columna se llama `password_hash` pero almacena la contraseña sin hash (`'ulima123'`)
- **Doble sistema de autenticación:** Crea simultáneamente un JWT (para APIs REST) y una sesión server-side (para vistas HTML)
- **El JWT incluye `user_id` como claim adicional** — esto es crítico porque el middleware `jwt_required` personalizado lo necesita

### 6.2 GET `/api/me` — Perfil del usuario autenticado

**Archivo:** `login/apis.py` — función `profile()`

**Middleware:** `@jwt_required` (personalizado de `login/middlewares.py`)

**¿De dónde sale esta ruta?**

La ruta `/api/me` se construye a través de esta cadena:

1. Se define un **Blueprint** llamado `main_apis` en `login/apis.py:11`:
   ```python
   api = Blueprint('main_apis', __name__)
   ```
2. Se decora la función `profile()` con `@api.route('/api/me', methods=['GET'])` en `login/apis.py:102`
3. Ese blueprint se registra en `login/blueprints.py:14`:
   ```python
   app.register_blueprint(main_apis)
   ```
4. `register(APP)` se llama desde `app.py:8`, lo que vincula `/api/me` al servidor Flask.

En otras palabras: `Blueprint('main_apis')` contiene la ruta `/api/me`, y ese blueprint se monta en la app Flask mediante `app.register_blueprint()`.

**Flujo:**

```
1. Middleware jwt_required:
   a. verify_jwt_in_request() → valida token
   b. get_jwt() → extrae claims
   c. claims["user_id"] → g.user_id
   d. get_jwt_identity() → g.username

2. Consultar User: session.query(User).filter(User.id == g.user_id).first()

3. Consultar Student: session.query(Student).filter(Student.user_id == user.id).first()

4. Si existe Student:
   a. Consultar Career asociada
   b. Consultar Specialties activas vía StudentSpecialty (join)
   c. Agregar al perfil: career, current_level, specialty_setup_completed, especialidades

5. Retornar JSON con datos del usuario (excluyendo password_hash)

6. Cerrar sesión DB
```

### 6.3 GET `/api/sign-out` — Cerrar sesión

**Archivo:** `login/apis.py` — función `signout()`

**Middleware:** `@jwt_required` (personalizado)

**Flujo:**

```
1. Obtener jti (JWT ID) del token actual
2. Agregar jti a REVOKED_TOKENS (lista negra en memoria)
3. Limpiar session (session.clear())
4. Retornar JSON de éxito
```

**Importante:** La lista negra `REVOKED_TOKENS` está en memoria y se pierde al reiniciar el servidor.

### 6.4 Login vía HTML (Flask Sessions)

**Archivo:** `login/views.py` — función `sign_in_login()`

**Ruta:** `POST /sign-in` (form-data)

**Middleware:** Ninguno (pero GET usa `@logged_go_admin`)

**Diferencias con el login API:**

| Aspecto | API REST (`/api/sign-in`) | HTML (`/sign-in`) |
|---|---|---|
| Content-Type | `application/json` | `application/x-www-form-urlencoded` |
| Modelo usado | `login.models.User` | `notas.models.AppUser` |
| Respuesta | JSON | Redirect o render template |
| Autenticación | JWT + Sesión | Solo sesión |
| Códigos de error | 400, 401, 500 | Template con mensaje de error |

---

## 7. Notas — Endpoints y Flujo Completo

### 7.1 CRUD de Assessment Types — `/api/v1/assessment-types`

**Archivo:** `notas/apis/assessment_type.py`

**Blueprint:** `notas_assessment_type`

**Middleware:** `@jwt_required()` (estándar de flask-jwt-extended) en todos los endpoints

| Método | Ruta | Función | Descripción |
|---|---|---|---|
| GET | `/api/v1/assessment-types` | `fetch_all()` | Lista todos los tipos de evaluación |
| GET | `/api/v1/assessment-types/<id>` | `fetch_one(id)` | Obtiene un tipo por ID |
| POST | `/api/v1/assessment-types` | `create_one()` | Crea un nuevo tipo (name, abbreviation, description) |
| PUT | `/api/v1/assessment-types` | `update_one()` | Actualiza un tipo por ID (body incluye id) |
| DELETE | `/api/v1/assessment-types/<id>` | `delete_one(id)` | Elimina un tipo por ID |

**Modelo:** `AssessmentType` → tabla `assessment_type` (id, name, abbreviation, description)

**Patrón común en todos los CRUD de notas:**

```
1. @jwt_required() → verifica token JWT
2. session = Session() → crea sesión DB
3. try:
       session.query(Modelo).filter_by(...).first() / .all()
       o session.add(item) / session.delete(item)
       session.commit() si hay escritura
   except:
       traceback.print_exc()
       response = jsonify({'message': 'Error...', 'error': str(e)})
       status = 500
   finally:
       session.close()
4. return response, status
```

### 7.2 CRUD de Assessments — `/api/v1/assessments`

**Archivo:** `notas/apis/assessment.py`

**Blueprint:** `notas_assessment`

**Middleware:** `@jwt_required()` (estándar)

| Método | Ruta | Descripción |
|---|---|---|
| GET | `/api/v1/assessments?`syllabus_id=N | Lista evaluaciones, opcionalmente filtradas por syllabus |
| GET | `/api/v1/assessments/<id>` | Obtiene una evaluación por ID |
| POST | `/api/v1/assessments` | Crea evaluación (syllabus_id, assessment_type_id, code, name, week_number, weight) |
| PUT | `/api/v1/assessments` | Actualiza evaluación (body incluye id) |
| DELETE | `/api/v1/assessments/<id>` | Elimina evaluación por ID |

**Modelo:** `Assessment` → tabla `assessment`

**Relaciones importantes:**

- `Assessment.syllabus` → `Syllabus` (FK: `syllabus_id`)
- `Assessment.assessment_type` → `AssessmentType` (FK: `assessment_type_id`)

### 7.3 CRUD de Student Scores — `/api/v1/student-scores`

**Archivo:** `notas/apis/student_score.py`

**Blueprint:** `notas_student_score`

**Middleware:** `@jwt_required()` (estándar)

**Particularidad:** El método POST implementa **upsert** (crea o actualiza).

| Método | Ruta | Descripción |
|---|---|---|
| GET | `/api/v1/student-scores?`enrollment_id=N&assessment_id=N | Lista notas, filtrable por enrollment y/o assessment |
| GET | `/api/v1/student-scores/<id>` | Obtiene una nota por ID |
| POST | `/api/v1/student-scores` | **Upsert:** busca por enrollment_id + assessment_id; si existe actualiza value, si no crea nuevo |
| PUT | `/api/v1/student-scores` | Actualiza value de una nota por id |
| DELETE | `/api/v1/student-scores/<id>` | Elimina una nota por ID |

**Lógica de upsert (POST):**

```python
existing = session.query(StudentScore).filter_by(
    enrollment_id=data['enrollment_id'],
    assessment_id=data['assessment_id']
).first()

if existing:
    existing.value = data.get('value', existing.value)  # UPDATE
else:
    item = StudentScore(
        enrollment_id=data['enrollment_id'],
        assessment_id=data['assessment_id'],
        value=data.get('value')
    )  # INSERT
    session.add(item)
```

**Modelo:** `StudentScore` → tabla `student_score` con unique key `(enrollment_id, assessment_id)`

### 7.4 Calculator — Cálculo de promedios

**Archivo:** `notas/apis/calculator.py`

**Blueprint:** `notas_calculator`

**Middleware:** `@jwt_required()` (estándar)

#### Función auxiliar: `calcular_promedio(scores_data)`

```python
def calcular_promedio(scores_data):
    peso_total = 0
    suma_ponderada = 0
    for item in scores_data:
        if item['value'] is not None:
            peso_total += item['weight']
            suma_ponderada += item['value'] * item['weight']
    if peso_total > 0:
        promedio = round(suma_ponderada / peso_total, 2)
    else:
        promedio = None
    return promedio, peso_total, suma_ponderada
```

**Fórmula:** `promedio = Σ(nota × peso) / Σ(peso)`

**Nota:** Los pesos en la BD están como porcentajes (ej. 20 para 20%). Al sumarlos, si el total de pesos con nota es 100, el promedio es directo.

#### Endpoints:

| Método | Ruta | Descripción |
|---|---|---|
| GET | `/api/v1/calculator/student/{student_id}/courses` | Lista todos los cursos del estudiante con su promedio ponderado por curso |
| GET | `/api/v1/calculator/course-offering/{offering_id}/student/{student_id}` | Detalle de un curso específico: notas por evaluación, resumen |
| GET | `/api/v1/calculator/enrollment/{enrollment_id}` | Detalle de una matrícula específica con notas y asistencia |

#### Flujo del endpoint `student_courses` (el más usado):

```
GET /api/v1/calculator/student/2/courses

1. Obtener Student por student_id
2. Obtener todas las Enrollment del estudiante con eager loading:
   - Enrollment → Section → CourseOffering → Course
   - Enrollment → Scores
3. Por cada Enrollment:
   a. Obtener Course de la cadena de relaciones
   b. Buscar Syllabus por course_offering_id
   c. Si existe syllabus, obtener todas sus Assessment
   d. Mapear scores: { assessment_id: value }
   e. Construir scores_data: para cada assessment, armar { weight, value }
   f. Calcular promedio con calcular_promedio()
   g. Agregar resultado al array
4. Retornar JSON con todos los cursos y sus promedios
```

### 7.5 Career Setup — `/api/v1/careers`, `/api/v1/specialties`

**Archivo:** `notas/apis/career_setup.py`

**Blueprint:** `notas_career_setup`

**Middleware:** `@jwt_required()` (estándar)

| Método | Ruta | Descripción |
|---|---|---|
| GET | `/api/v1/careers` | Lista todas las carreras disponibles |
| GET | `/api/v1/specialties?career_id=N` | Lista especialidades, opcionalmente filtradas por carrera |
| POST | `/api/v1/students/{student_id}/setup-career` | Configura carrera y especialidades de un estudiante |

**Nota:** Anteriormente existía `PUT /api/me/setup` en `login/apis.py` que hacía lo mismo que este endpoint pero usando el usuario autenticado (vía `g.user_id`). Fue eliminado porque duplicaba funcionalidad. Ahora solo existe esta versión en `notas/apis/career_setup.py` que recibe el `student_id` explícitamente.

### 7.6 Schedule — Horario del estudiante

**Archivo:** `notas/apis/schedule.py`

**Blueprint:** `notas_schedule`

**Middleware:** `@jwt_required()` (estándar)

| Método | Ruta | Descripción |
|---|---|---|
| GET | `/api/v1/students/{student_id}/schedule` | Obtiene el horario completo del estudiante |

**Flujo:**

```
1. Obtener Student por student_id
2. Obtener todas las Enrollment activas (status='active') con eager loading:
   - Section → CourseOffering → Course
   - Section → Teacher
3. Por cada Enrollment:
   a. Obtener ScheduleSession de la sección (día, hora, salón, color)
   b. Calcular promedio de la sección con get_section_average():
      - Obtener todos los Enrollment de la sección
      - Por cada uno, obtener StudentScore y Assessment
      - Calcular weighted_sum / total_weight
   c. Armar objeto con: código de sección, curso, color, docente, promedio,
      horas de asistencia/inasistencia, horarios
4. Retornar JSON
```

**Mapa de días:** `{1: 'Lunes', 2: 'Martes', ..., 7: 'Domingo'}`

### 7.7 Delegate — Funciones de delegado

**Archivo:** `notas/apis/delegate.py`

**Blueprint:** `notas_delegate`

**Middleware:** `@jwt_required` **personalizado** (de `login/middlewares.py`, no el estándar)

Esto es importante: usa `g.user_id` que provee el middleware personalizado.

| Método | Ruta | Descripción |
|---|---|---|
| GET | `/api/v1/delegate/sections` | Lista las secciones donde el usuario es delegado/subdelegado |
| GET | `/api/v1/sections/{section_id}/announcements` | Lista anuncios activos de una sección |
| POST | `/api/v1/delegate/announcements` | Publica un anuncio como delegado |
| GET | `/api/v1/sections/{section_id}/statistics` | Estadísticas de calificaciones de la sección |

#### Flujo de `get_delegate_sections`:

```
1. Obtener Student por g.user_id
2. Buscar SectionRepresentative activo del estudiante (join con Enrollment)
3. Por cada representación:
   a. Obtener Section → CourseOffering → Course
   b. Contar alumnos activos en la sección
   c. Mapear rol: 'delegate' → 'delegado', 'subdelegate' → 'subdelegado'
4. Retornar lista
```

#### Flujo de `create_announcement`:

```
1. Validar body: section_id, title, message
2. Obtener Student por g.user_id
3. Verificar que el estudiante sea SectionRepresentative activo de la sección
4. Si no tiene permisos → 403 Forbidden
5. Crear Announcement con:
   - section_representative_id del representante encontrado
   - title, message
   - published_at = datetime.now()
   - is_active = True
6. Commit y retornar 201
```

#### Flujo de `get_section_statistics`:

```
1. Obtener todos los Enrollment activos de la sección
2. Por cada Enrollment:
   a. Obtener StudentScore con Assessment
   b. Calcular weighted_sum / total_weight
3. Si no hay calificaciones → valores por defecto (promedio 14.5, 75% aprobados)
4. Calcular:
   - promedio_general
   - porcentaje de aprobados (>= 10.5)
   - rangos: 0-10, 11-13, 14-16, 17-20
5. Retornar JSON
```

---

## 8. Resumen de Endpoints y Middleware Asociado

### Login

| Endpoint | Middleware | Archivo |
|---|---|---|
| `POST /api/sign-in` | Ninguno | `login/apis.py:13` |
| `GET /api/sign-out` | `@jwt_required` (personalizado) | `login/apis.py:89` |
| `GET /api/me` | `@jwt_required` (personalizado) | `login/apis.py:102` |

### Notas — Assessment Types

| Endpoint | Middleware | Archivo |
|---|---|---|
| `GET /api/v1/assessment-types` | `@jwt_required()` (estándar) | `notas/apis/assessment_type.py:9` |
| `POST /api/v1/assessment-types` | `@jwt_required()` (estándar) | `notas/apis/assessment_type.py:47` |
| `PUT /api/v1/assessment-types` | `@jwt_required()` (estándar) | `notas/apis/assessment_type.py:72` |
| `GET /api/v1/assessment-types/{id}` | `@jwt_required()` (estándar) | `notas/apis/assessment_type.py:26` |
| `DELETE /api/v1/assessment-types/{id}` | `@jwt_required()` (estándar) | `notas/apis/assessment_type.py:98` |

### Notas — Assessments

| Endpoint | Middleware | Archivo |
|---|---|---|
| `GET /api/v1/assessments` | `@jwt_required()` (estándar) | `notas/apis/assessment.py:9` |
| `POST /api/v1/assessments` | `@jwt_required()` (estándar) | `notas/apis/assessment.py:51` |
| `PUT /api/v1/assessments` | `@jwt_required()` (estándar) | `notas/apis/assessment.py:79` |
| `GET /api/v1/assessments/{id}` | `@jwt_required()` (estándar) | `notas/apis/assessment.py:30` |
| `DELETE /api/v1/assessments/{id}` | `@jwt_required()` (estándar) | `notas/apis/assessment.py:108` |

### Notas — Student Scores

| Endpoint | Middleware | Archivo |
|---|---|---|
| `GET /api/v1/student-scores` | `@jwt_required()` (estándar) | `notas/apis/student_score.py:9` |
| `POST /api/v1/student-scores` (upsert) | `@jwt_required()` (estándar) | `notas/apis/student_score.py:54` |
| `PUT /api/v1/student-scores` | `@jwt_required()` (estándar) | `notas/apis/student_score.py:88` |
| `GET /api/v1/student-scores/{id}` | `@jwt_required()` (estándar) | `notas/apis/student_score.py:33` |
| `DELETE /api/v1/student-scores/{id}` | `@jwt_required()` (estándar) | `notas/apis/student_score.py:112` |

### Notas — Calculator

| Endpoint | Middleware | Archivo |
|---|---|---|
| `GET /api/v1/calculator/student/{id}/courses` | `@jwt_required()` (estándar) | `notas/apis/calculator.py:26` |
| `GET /api/v1/calculator/course-offering/{oid}/student/{sid}` | `@jwt_required()` (estándar) | `notas/apis/calculator.py:103` |
| `GET /api/v1/calculator/enrollment/{id}` | `@jwt_required()` (estándar) | `notas/apis/calculator.py:201` |

### Notas — Career Setup

| Endpoint | Middleware | Archivo |
|---|---|---|
| `GET /api/v1/careers` | `@jwt_required()` (estándar) | `notas/apis/career_setup.py:9` |
| `GET /api/v1/specialties` | `@jwt_required()` (estándar) | `notas/apis/career_setup.py:46` |
| `POST /api/v1/students/{id}/setup-career` | `@jwt_required()` (estándar) | `notas/apis/career_setup.py:90` |

### Notas — Schedule

| Endpoint | Middleware | Archivo |
|---|---|---|
| `GET /api/v1/students/{id}/schedule` | `@jwt_required()` (estándar) | `notas/apis/schedule.py:46` |

### Notas — Delegate

| Endpoint | Middleware | Archivo |
|---|---|---|
| `GET /api/v1/delegate/sections` | `@jwt_required` (personalizado) | `notas/apis/delegate.py:16` |
| `GET /api/v1/sections/{id}/announcements` | `@jwt_required` (personalizado) | `notas/apis/delegate.py:99` |
| `POST /api/v1/delegate/announcements` | `@jwt_required` (personalizado) | `notas/apis/delegate.py:165` |
| `GET /api/v1/sections/{id}/statistics` | `@jwt_required` (personalizado) | `notas/apis/delegate.py:265` |

---

## Diagrama de Arquitectura (Texto)

```
┌─────────────────────────────────────────────────────────────────────┐
│                          app.py                                      │
│  register(APP)  │  APP.run(debug=True, host='0.0.0.0', port=5000)   │
└──────────────────────┬──────────────────────────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────────────────────────┐
│                  login/application.py (APP)                          │
│  Flask(__name__) + Session + JWTManager                              │
│  Config: SECRET_KEY, SESSION_TYPE=filesystem, JWT_SECRET_KEY         │
│  Handlers: unauthorized, expired, invalid, needs_fresh_token         │
└──────────────────────────────────────────────────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────────────────────────┐
│                  login/blueprints.py (register)                      │
├────────────────┬──────────────────┬──────────────────┬──────────────┤
│ main_views     │ main_apis        │ notas_blueprints  │ otros...     │
│ (login/views)  │ (login/apis)     │ (notas/apis/*)    │              │
└────────────────┴──────────────────┴──────────────────┴──────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────────────────────────┐
│                    core/database.py                                   │
│  engine = create_engine("sqlite:///db/app.db")                       │
│  Session = sessionmaker(bind=engine)                                 │
└──────────────────────────────────────────────────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────────────────────────┐
│                    db/app.db (SQLite)                                 │
│  27 tablas: app_user, course, enrollment, assessment,                │
│  student_score, section, syllabus, etc.                              │
└──────────────────────────────────────────────────────────────────────┘

Flujo de Request:

Cliente → HTTP Request → Flask → Blueprint match → Middleware (JWT)
  → Función endpoint → Session() DB → Query → Response JSON
                                                          ↓
                                                    finally: session.close()
```

---

## Notas Arquitectónicas Importantes

1. **Dos estilos de middleware JWT conviven:** Los endpoints de `notas/apis/` (assessment, assessment_type, student_score, calculator, career_setup, schedule) usan `@jwt_required()` estándar de flask-jwt-extended. Los endpoints de login y delegate usan el `@jwt_required` personalizado de `login/middlewares.py`. El personalizado expone `g.user_id`; el estándar no.

2. **Dos sistemas de autenticación paralelos:** JWT para APIs REST y sesiones server-side (Flask-Session) para vistas HTML. El login API (`/api/sign-in`) crea ambos simultáneamente.

3. **Modelos duplicados:** Los paquetes `notas`, `descripcion_cursos` y `malla` definen modelos separados para las mismas tablas. Funciona porque todos usan `declarative_base()` con los mismos `__tablename__`, pero genera duplicación de código.

4. **Contraseñas en texto plano:** La columna `password_hash` almacena la contraseña sin hash. Esto es una vulnerabilidad de seguridad.

5. **Lista negra de JWT en memoria:** `REVOKED_TOKENS` es una lista Python que se pierde al reiniciar el servidor.

6. **Patrón try/except/finally con sesiones:** Todos los endpoints siguen el mismo patrón de gestión de sesiones DB para asegurar que las conexiones se cierren incluso si hay errores.
