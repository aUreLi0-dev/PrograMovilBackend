# Conexión Frontend ↔ Backend

## Objetivo

Eliminar los datos mockeados del frontend Flutter (`assets/data/*.json`) y conectar las pantallas de **Login**, **Setup de Carrera** y **Calculadora de Notas** con los endpoints reales del backend Flask.

---

## 1. Backend: CORS

### Archivos modificados

**`requirements.txt`** — Se agregó la dependencia:
```
flask-cors
```

**`apps/login/application.py`** — Se importó e inicializó CORS:
```python
from flask_cors import CORS

CORS(APP, supports_credentials=True, resources={r"/api/*": {"origins": "*"}})
```

Esto permite que el frontend Flutter (desde cualquier origen) haga peticiones a las rutas `/api/*` del backend.

---

## 2. Frontend: Dependencias

### `pubspec.yaml`

Se agregaron dos dependencias:

| Paquete | Propósito |
|---|---|
| `http: ^1.2.0` | Cliente HTTP para hacer requests REST |
| `shared_preferences: ^2.3.0` | Persistencia local del JWT token |

Se ejecutó `flutter pub get` para instalarlas.

---

## 3. ApiService — Cliente HTTP base

### Archivo nuevo: `lib/services/api_service.dart`

Clase singleton que hereda de `GetxService` para integrarse con el ecosistema GetX.

#### Responsabilidades

- **Base URL**: Por defecto `http://10.0.2.2:5000` (Android emulator → localhost). Se almacena en `SharedPreferences` para futura configuración.
- **Token JWT**: Se guarda en `SharedPreferences` con clave `jwt_token`. Se inyecta automáticamente en el header `Authorization: Bearer <token>` en cada request.
- **Métodos HTTP**: `get()`, `post()`, `put()`, `delete()` — todos devuelven un `ApiResponse`.
- **Manejo de errores**: Captura excepciones de red y parsea la respuesta estándar del backend.

#### Estructura `ApiResponse`

```dart
class ApiResponse {
  final bool success;
  final dynamic data;
  final String? message;
  final String? error;
}
```

El método `_handleResponse()` parsea el JSON del backend que sigue el formato:
```json
{ "success": true/false, "data": ..., "message": "...", "error": null }
```

Si la respuesta no es JSON válido, intenta inferir éxito del código HTTP.

#### Flujo de inicialización

En `main.dart`:
```dart
final apiService = ApiService();
await apiService.init();       // carga token guardado
Get.put<ApiService>(apiService, permanent: true);
```

---

## 4. UserModel

### Archivo modificado: `lib/models/user_model.dart`

#### Cambios

1. **Se agregó el campo `id`** (int) — necesario para los endpoints que requieren `student_id`.
2. **`fromJson()` unificado** — Ahora parsea ambos formatos:

| Campo Backend | Campo Mock antiguo |
|---|---|
| `full_name` | `firstName` + `lastName` |
| `institutional_email` | `email` |
| `career` (Map con `name`) | `career` (String directa) |
| `especialidades` (List<Map> con `name`) | `especialidades` (List<String>) |
| `specialty_setup_completed` | `setupComplete` |
| `current_level` | `currentCycle` |

El parsing usa `??` (fallback) para ser compatible con ambos orígenes:
```dart
email: json['institutional_email'] as String? ?? json['email'] as String? ?? '',
```

---

## 5. AuthService

### Archivo reescrito: `lib/services/auth_service.dart`

Antes cargaba `assets/data/users.json` y comparaba credenciales en memoria. Ahora hace llamadas reales al backend.

#### Métodos

| Método | Endpoint | Descripción |
|---|---|---|
| `login(code, password)` | `POST /api/sign-in` | Envía credenciales, recibe JWT + datos del usuario. Luego llama a `/api/me` para obtener perfil completo (carrera, especialidades, ciclo). |
| `completeSetup(careerId, specialtyIds)` | `POST /api/v1/students/{id}/setup-career` | Guarda la carrera y especialidades seleccionadas. Refresca el perfil con `/api/me`. |
| `logout()` | `GET /api/sign-out` | Invalida el token en el backend y limpia el almacenamiento local. |

#### Flujo de login

```
LoginController.submit()
  → AuthService.login(code, password)
    → ApiService.post('/api/sign-in', body: {code, password})
      → Backend valida credenciales
      → Backend devuelve {success, data: {user, jwt}}
    → ApiService.setToken(jwt)
    → UserModel.fromJson(userData)
    → ApiService.get('/api/me')
      → UserModel.fromJson(meData) con datos enriquecidos
  → LoginController redirige a /home o /setup-carrera
```

---

## 6. SetupCarreraController + Page

### Archivos modificados

**`lib/pages/setup_carrera/setup_carrera_controller.dart`** — Reescrito.
**`lib/pages/setup_carrera/setup_carrera_page.dart`** — Adaptado.

#### Cambios en el controlador

| Aspecto | Antes | Ahora |
|---|---|---|
| Carreras | Lista hardcodeada `['Ingeniería de Sistemas']` | Carga desde `GET /api/v1/careers` |
| Especialidades | Lista hardcodeada `['Desarrollo de Software', ...]` | Carga desde `GET /api/v1/specialties?career_id=X` |
| Selección | Strings | IDs (int) |
| Guardado | `_auth.completeSetup(career, especialidades)` con strings | `_auth.completeSetup(careerId, specialtyIds)` con IDs |
| Loading states | No tenía | `cargandoCarreras`, `cargandoEspecialidades`, `saving` observables |

#### Nuevo modelo de datos

```dart
// Carreras desde API
[{ "id": 1, "code": "ISI", "name": "Ingeniería de Sistemas", "faculty": "FIIS" }]

// Especialidades desde API  
[{ "id": 1, "carrera_id": 1, "name": "Desarrollo de Software", ... }]
```

#### Flujo

```
SetupCarreraPage.onInit()
  → _cargarCarreras() → GET /api/v1/careers → poblar dropdown

Usuario selecciona carrera
  → onCarreraChanged(id) → _cargarEspecialidades(id) → GET /api/v1/specialties?career_id=X

Usuario presiona "Finalizar"
  → finish() → AuthService.completeSetup(careerId, specialtyIds)
    → POST /api/v1/students/{id}/setup-career
    → GET /api/me (refrescar)
  → Get.offAllNamed('/home')
```

---

## 7. EvaluationModel

### Archivo modificado: `lib/models/evaluation_model.dart`

#### EvaluationComponent

| Campo antiguo | Campo nuevo (backend) | Tipo |
|---|---|---|
| `id` (String) | `assessment_id` | `int` |
| `nombre` | `assessment_name` | `String` |
| `sigla` | `assessment_code` | `String` |
| `peso` | `weight` | `double` |
| `tipo` | `assessment_type` | `String?` |

El factory `fromJson` ahora parsea ambos conjuntos de claves con fallbacks:
```dart
id: json['assessment_id'] as int? ?? int.tryParse(json['assessment_id'].toString()) ?? 0,
nombre: json['assessment_name'] as String? ?? json['nombre'] as String? ?? '',
```

#### CourseSyllabus

El factory ahora parsea desde el array `assesments` que devuelve el backend (en vez de `evaluaciones`).

---

## 8. CalculadoraController

### Archivo reescrito: `lib/pages/calculadora/calculadora_controller.dart`

#### Flujo de carga

```
onInit()
  → _cargarCursos()
    → GET /api/v1/calculator/student/{userId}/courses
      → Devuelve lista de cursos con promedios ponderados
    → Para cada curso:
      → GET /api/v1/calculator/enrollment/{enrollmentId}
        → Devuelve detalle con todas las evaluaciones y notas
      → Mapea a estructura interna:
        { enrollment_id, course_id, nombre, ciclo, seccion,
          weighted_average, total_weight, notas: [{student_score_id, titulo, peso, valor, assessment_id}] }
      → Construye CourseSyllabus desde el detalle
```

#### Operaciones CRUD

| Operación | Método | Endpoint |
|---|---|---|
| Agregar nota | `agregarNota()` | `POST /api/v1/student-scores` con `{enrollment_id, assessment_id, value}` |
| Eliminar nota | `eliminarNota()` | `DELETE /api/v1/student-scores/{student_score_id}` |

#### Estructura de datos interna de cada curso

```dart
{
  'enrollment_id': int,
  'course_id': int,
  'nombre': String,           // course.name
  'ciclo': String,            // academic_period_code
  'seccion': String,          // section_code
  'weighted_average': double?,
  'total_weight': double,
  'notas': RxList<Map>        // [{student_score_id, titulo, peso, valor, assessment_id}]
}
```

#### Evaluaciones disponibles (para agregar notas)

`getAvailableEvaluations(cursoIndex)`:
1. Obtiene todas las evaluaciones del sílabo (del `CourseSyllabus` cargado vía enrollment detail)
2. Obtiene los `assessment_id` ya registrados en las notas locales
3. Retorna solo las evaluaciones **no registradas**

---

## 9. main.dart

### Archivo modificado: `lib/main.dart`

#### Antes

```dart
void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  Get.put<AuthService>(AuthService(), permanent: true);
  await Future.wait([
    EvaluationSyllabusService().loadEvaluationData(),   // carga JSON local
    CoursesService().loadCoursesData(),                  // carga JSON local
  ]);
  runApp(const MyApp());
}
```

#### Después

```dart
void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  final apiService = ApiService();
  await apiService.init();
  Get.put<ApiService>(apiService, permanent: true);
  Get.put<AuthService>(AuthService(), permanent: true);
  runApp(const MyApp());
}
```

- Se eliminó la precarga de JSON locales (`evaluaciones.json`, `courses.json`)
- Se inicializa `ApiService` (carga JWT guardado de sesiones anteriores)
- `ApiService` y `AuthService` son servicios permanentes de GetX

---

## 10. Resumen de endpoints utilizados

| Endpoint | Método | Uso |
|---|---|---|
| `/api/sign-in` | POST | Login |
| `/api/sign-out` | GET | Logout |
| `/api/me` | GET | Perfil del usuario autenticado |
| `/api/v1/careers` | GET | Listado de carreras (setup) |
| `/api/v1/specialties?career_id=N` | GET | Especialidades por carrera |
| `/api/v1/students/{id}/setup-career` | POST | Guardar carrera+especialidades |
| `/api/v1/calculator/student/{id}/courses` | GET | Cursos del estudiante con promedios |
| `/api/v1/calculator/enrollment/{id}` | GET | Detalle de matrícula con evaluaciones y notas |
| `/api/v1/student-scores` | POST | Crear/actualizar nota |
| `/api/v1/student-scores/{id}` | DELETE | Eliminar nota |

---

## 11. Formato de respuesta esperado del backend

### Formato estándar (login, me, careers, specialties, setup-career)

```json
{
  "success": true,
  "data": { ... },
  "message": "Mensaje legible",
  "error": null
}
```

### Formato de calculator y student-scores

Estos endpoints devuelven el objeto directamente sin wrapper. El `ApiService` los maneja correctamente:
```dart
// calculator/student/{id}/courses devuelve:
{ "student_id": 1, "student_name": "...", "courses": [...] }

// calculator/enrollment/{id} devuelve:
{ "student": {...}, "course": {...}, "assesments": [...], "summary": {...} }

// POST student-scores devuelve:
{ "id": 1, "enrollment_id": 1, "assessment_id": 1, "value": 15.5 }
```

---

## 12. Consideraciones adicionales

### CORS
El backend ahora acepta requests desde cualquier origen en rutas `/api/*`. Para producción, restringir `origins` a dominios específicos.

### JWT
- El token se almacena en `SharedPreferences` (persistente entre sesiones).
- El token expira en 5 horas (configurado en el backend con `JWT_ACCESS_TOKEN_EXPIRES`).
- Si el token expira, el usuario debe volver a iniciar sesión (no hay refresh token implementado).

### Android Emulator
La base URL `http://10.0.2.2:5000` funciona para Android Emulator (mapea a `localhost` del host).
Para iOS simulator, cambiar a `http://localhost:5000`.
Para dispositivo físico, usar la IP local de la máquina.

### Archivos JSON locales
Los archivos `assets/data/*.json` se mantienen en el proyecto pero ya no se precargan.
Pueden ser eliminados en una limpieza futura si ninguna otra funcionalidad los requiere.
