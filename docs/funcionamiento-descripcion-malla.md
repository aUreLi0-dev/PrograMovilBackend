# Funcionamiento de endpoints: Descripcion de Cursos y Malla

Este documento resume los dos modulos que se van a exponer: `descripcion_cursos` y `malla`. La idea es explicar que endpoint usa cada pantalla, que tablas consulta el backend y como se transforma la informacion antes de llegar al aplicativo movil.

---

## 1. Vista general

Ambos modulos siguen la misma idea base:

1. El usuario inicia sesion y recibe un JWT.
2. El frontend manda el token en `Authorization: Bearer <token>`.
3. El middleware valida el JWT y deja disponible `g.user_id`.
4. El endpoint abre una sesion de BD con `Session()`.
5. Consulta las tablas necesarias.
6. Devuelve una respuesta JSON lista para la pantalla.

Los dos modulos usan:

```python
from core.database import Session
from login.middlewares import jwt_required
```

Esto importa porque ambos dependen del usuario autenticado y de la base de datos real (`db/app.db`).

---

## 2. Modulo `descripcion_cursos`

### 2.1 Para que sirve

Este modulo alimenta la pantalla de detalle de una seccion. Desde esa pantalla se ve:

- el encabezado del curso;
- asistencia del alumno;
- asesorias;
- contactos de docente y alumnos.

Los anuncios tambien se muestran en esa pantalla, pero el endpoint ya no vive dentro de `descripcion_cursos`. Se usa el endpoint compartido:

```txt
GET /api/v1/sections/{section_id}/announcements
```

Ese endpoint esta en `notas/apis/delegate.py`, porque es la misma data que usan delegado y descripcion de cursos.

### 2.2 Archivos principales

| Archivo | Responsabilidad |
|---|---|
| `descripcion_cursos/blueprints.py` | Registra los endpoints propios del modulo. |
| `descripcion_cursos/models.py` | Define los modelos SQLAlchemy que usa esta pantalla. |
| `descripcion_cursos/apis/section.py` | Devuelve la informacion base de la seccion. |
| `descripcion_cursos/apis/advising.py` | Devuelve horarios de asesoria. |
| `descripcion_cursos/apis/contact.py` | Devuelve docente, alumnos y roles. |
| `descripcion_cursos/apis/helpers.py` | Formatea fechas, horas, roles, docentes y usuarios. |
| `requests/api-descripcion-cursos.http` | Requests listos para probar el modulo. |

Actualmente el blueprint registra solo:

```python
api_section
api_advising
api_contact
```

No registra anuncios para evitar duplicar la logica de delegado.

### 2.3 Endpoints

| Metodo | Ruta | Uso en pantalla |
|---|---|---|
| GET | `/api/v1/descripcion-cursos/sections/{section_id}` | Encabezado, curso, seccion y asistencia. |
| GET | `/api/v1/descripcion-cursos/sections/{section_id}/advising` | Tab de asesorias. |
| GET | `/api/v1/descripcion-cursos/sections/{section_id}/contacts` | Tab de contactos. |
| GET | `/api/v1/sections/{section_id}/announcements` | Tab de anuncios, endpoint compartido. |

### 2.4 Flujo del detalle de seccion

Endpoint:

```txt
GET /api/v1/descripcion-cursos/sections/{section_id}
```

Archivo:

```txt
descripcion_cursos/apis/section.py
```

Flujo:

1. Busca la seccion por `section.id`.
2. Carga el docente y el curso usando relaciones:
   - `Section -> Teacher`
   - `Section -> CourseOffering -> Course`
3. Busca la matricula relacionada al alumno.
4. Devuelve un JSON con datos pensados para el header de la pantalla.

Nota:

> El promedio no se calcula aqui. Esa logica pertenece al modulo de notas/delegado, donde ya se visualizan y procesan las notas.

Respuesta importante:

```json
{
  "idSeccion": "1",
  "codigoSeccion": "701",
  "docenteCode": "DOC001",
  "idCurso": "35",
  "curso": "Programacion Web",
  "asistido": 20,
  "inasistencia": 2,
  "total": 22,
  "enrollmentId": "10",
  "enrollmentStatus": "active"
}
```

### 2.5 Flujo de asesorias

Endpoint:

```txt
GET /api/v1/descripcion-cursos/sections/{section_id}/advising
```

Archivo:

```txt
descripcion_cursos/apis/advising.py
```

Flujo:

1. Busca la seccion.
2. Busca asesorias del mismo `course_offering_id`.
3. Acepta asesorias generales del curso (`section_id IS NULL`) o especificas de la seccion.
4. Ordena por dia y hora.
5. Devuelve docente, horario, aula, Zoom, modalidad y nota.

Tablas principales:

- `section`
- `course_advising_session`
- `teacher`

### 2.6 Flujo de contactos

Endpoint:

```txt
GET /api/v1/descripcion-cursos/sections/{section_id}/contacts
```

Archivo:

```txt
descripcion_cursos/apis/contact.py
```

Flujo:

1. Busca la seccion y su docente.
2. Busca representantes activos de la seccion.
3. Busca las matriculas de la seccion.
4. Por cada matricula, carga el alumno y su usuario.
5. Marca si el alumno es delegado, subdelegado o estudiante.
6. Ordena primero delegado, luego subdelegado y luego estudiantes.

Tablas principales:

- `section`
- `teacher`
- `enrollment`
- `student`
- `app_user`
- `section_representative`

### 2.7 Flujo de anuncios

Endpoint usado por esta pantalla:

```txt
GET /api/v1/sections/{section_id}/announcements
```

Archivo:

```txt
notas/apis/delegate.py
```

Este endpoint lista anuncios activos de una seccion. La creacion de anuncios se mantiene aparte:

```txt
POST /api/v1/delegate/announcements
```

Idea para explicar:

> Descripcion de cursos solo consume los anuncios. La creacion pertenece al flujo de delegado.

---

## 3. Modulo `malla`

### 3.1 Para que sirve

Este modulo arma la malla curricular del alumno autenticado. No solo lista cursos: tambien calcula el estado visual de cada curso.

Estados visuales:

| Estado | Significado |
|---|---|
| `approved` | El curso esta aprobado. |
| `current` | El curso esta en curso. |
| `unlocked` | El curso esta disponible. |
| `locked` | El curso esta bloqueado. |

En el request de simulacion, el frontend manda:

| Valor enviado | Estado visual |
|---|---|
| `in_progress` o `current` | `current` |
| `approved` | `approved` |
| `available` | vuelve a disponible si el backend recalcula `unlocked` |

### 3.2 Archivos principales

| Archivo | Responsabilidad |
|---|---|
| `malla/blueprints.py` | Registra los endpoints del modulo. |
| `malla/models.py` | Modelos SQLAlchemy para cursos, malla, progreso y simulacion. |
| `malla/apis/curriculum.py` | Expone el endpoint principal de la malla. |
| `malla/apis/curriculum_logic.py` | Centraliza consultas, filtros y calculo de estados. |
| `malla/apis/progress.py` | Devuelve resumen de progreso usando la logica compartida. |
| `malla/apis/simulation.py` | Guarda cambios temporales y valida estados con la logica compartida. |
| `malla/apis/specialty.py` | Lista especialidades activas del alumno. |
| `requests/api-malla.http` | Requests listos para probar la malla. |

Idea para explicar:

> `curriculum.py`, `progress.py` y `simulation.py` no repiten el calculo de estados. Todos se apoyan en `curriculum_logic.py`, asi la malla responde igual en todos los endpoints.

### 3.3 Endpoints

| Metodo | Ruta | Uso |
|---|---|---|
| GET | `/api/v1/malla` | Vista final de la malla para pintar la pantalla. |
| GET | `/api/v1/malla/progress` | Resumen de progreso real. |
| GET | `/api/v1/malla/specialties` | Especialidades activas del alumno. |
| GET | `/api/v1/malla/courses/{curriculum_course_id}/status` | Explica el estado de un curso puntual. |
| PUT | `/api/v1/malla/simulation/course-status` | Cambia estado dentro de la simulacion. |
| DELETE | `/api/v1/malla/simulation` | Limpia todos los cambios simulados. |

### 3.4 Tablas que usa la malla

| Tabla | Uso |
|---|---|
| `student` | Ubica al alumno autenticado y su `current_level`. |
| `curriculum` | Identifica la malla activa del alumno. |
| `course` | Datos base del curso: codigo, nombre y creditos. |
| `curriculum_course` | Ubicacion del curso dentro de la malla: ciclo, orden, categoria. |
| `course_prerequisite` | Reglas de prerequisitos y ciclos requeridos. |
| `specialty` | Catalogo de especialidades. |
| `student_specialty` | Especialidades activas del alumno. |
| `curriculum_course_specialty` | Electivos asociados a especialidades. |
| `student_course_progress` | Progreso real guardado del alumno. |
| `student_curriculum_simulation` | Cambios temporales hechos desde la malla. |
| `enrollment`, `section`, `course_offering` | Cursos que el alumno esta llevando ahora. |

### 3.5 Como se arma `GET /api/v1/malla`

Archivo:

```txt
malla/apis/curriculum.py
```

La ruta vive en `curriculum.py`, pero el armado fuerte se hace en:

```txt
malla/apis/curriculum_logic.py
```

Flujo:

1. Obtiene el estudiante desde `g.user_id`.
2. Carga todos los cursos de su `curriculum_id`.
3. Carga progreso real desde `student_course_progress`.
4. Carga matriculas activas para detectar cursos en curso.
5. Carga especialidades activas del alumno desde `student_specialty`.
6. Carga prerequisitos desde `course_prerequisite`.
7. Carga simulacion desde `student_curriculum_simulation`.
8. Calcula el estado final de cada curso.
9. Filtra electivos segun especialidades.
10. Devuelve cursos listos para la pantalla.

En codigo, el endpoint llama a `build_malla_payload()`. Esa funcion es la que une las tablas y devuelve el JSON final.

### 3.6 Prioridad para calcular estados

El estado final sale con esta prioridad:

1. Si hay simulacion `simulated_approved`, se muestra `approved`.
2. Si hay simulacion `simulated_in_progress`, se muestra `current`.
3. Si hay progreso real `approved`, se muestra `approved`.
4. Si hay progreso real `in_progress`, se muestra `current`.
5. Si hay matricula activa, se muestra `current`.
6. Si el curso obligatorio esta en un ciclo menor al `current_level`, se muestra `approved`.
7. Si no cumple prerequisitos o ciclo requerido, se muestra `locked`.
8. Si cumple todo, se muestra `unlocked`.

Idea para explicar:

> La base real viene de progreso, matricula y nivel actual. La simulacion solo se aplica encima cuando el alumno cambia estados en la malla.

Este mismo orden se reutiliza en:

- `GET /api/v1/malla`, para pintar toda la malla.
- `GET /api/v1/malla/progress`, para resumir avance.
- `GET /api/v1/malla/courses/{id}/status`, para explicar un curso.
- `PUT /api/v1/malla/simulation/course-status`, para validar si un cambio se permite.

Asi no hay dos respuestas distintas para el mismo curso.

### 3.7 Progreso de malla

Endpoint:

```txt
GET /api/v1/malla/progress
```

Archivo:

```txt
malla/apis/progress.py
```

Este endpoint devuelve un resumen mas corto que `GET /api/v1/malla`. Sirve para ver avance sin traer todo el detalle visual de cada curso.

Usa funciones de `curriculum_logic.py` para:

- encontrar al alumno autenticado;
- traer cursos de su malla;
- leer progreso real;
- detectar cursos actuales;
- inferir aprobados por `current_level`.

Idea para explicar:

> `progress.py` no tiene una segunda logica de avance. Solo arma un resumen usando las mismas reglas que ya usa la malla completa.

### 3.8 Flujo de cambio de estado

Endpoint:

```txt
PUT /api/v1/malla/simulation/course-status
```

Archivo:

```txt
malla/apis/simulation.py
```

Este archivo no vuelve a calcular toda la malla. Usa `explain_course_status()` de `curriculum_logic.py` para saber el estado actual antes y despues del cambio.

Flujo permitido:

```txt
disponible -> cursando -> aprobado -> disponible
```

Equivalencia tecnica:

| Pantalla | Request | BD |
|---|---|---|
| disponible | `available` | no guarda fila; borra simulacion |
| cursando | `in_progress` o `current` | `simulated_in_progress` |
| aprobado | `approved` | `simulated_approved` |

Reglas:

- Un curso `locked` no puede pasar a `current`.
- Un curso `unlocked` puede pasar a `current`.
- Un curso `current` puede pasar a `approved`.
- Un curso `approved` puede volver a `available` solo si al borrar la simulacion recalcula `unlocked`.

Ejemplo de respuesta corta:

```json
{
  "curriculumCourseId": 46,
  "status": "current",
  "source": "simulation",
  "storedStatus": "simulated_in_progress"
}
```

Si el request manda `available`, el backend borra la simulacion de ese curso y recalcula. Solo acepta dejarlo disponible si el resultado vuelve a ser `unlocked`.

### 3.9 Endpoint para explicar un estado

Endpoint:

```txt
GET /api/v1/malla/courses/{curriculum_course_id}/status
```

Este endpoint no es necesario para pintar la pantalla, pero sirve para probar y explicar por que un curso tiene cierto color.

Internamente usa `explain_course_status()` de `curriculum_logic.py`, la misma funcion que usa simulacion para validar cambios.

Devuelve:

- `base`: estado sin considerar simulacion;
- `simulation`: override temporal, si existe;
- `final`: estado final que debe pintar la malla.

Ejemplo:

```json
{
  "curriculumCourseId": 46,
  "name": "Planeamiento Estrategico",
  "base": {
    "status": "unlocked",
    "source": "calculated"
  },
  "simulation": {
    "hasOverride": false
  },
  "final": {
    "status": "unlocked",
    "source": "calculated"
  }
}
```

### 3.10 Casos de prueba recomendados

Estos IDs sirven para demostrar estados distintos:

| Curso | ID | Caso |
|---|---:|---|
| Lenguaje y Comunicacion I | 1 | Aprobado por nivel actual. |
| Programacion Movil | 63 | En curso por progreso real. |
| Planeamiento Estrategico | 46 | Disponible; sirve para el flujo completo. |
| Sistemas ERP | 43 | Bloqueado; sirve para mostrar error 409. |

Flujo recomendado para demo:

1. Limpiar simulacion.
2. Ver `Planeamiento Estrategico (46)` como disponible.
3. Cambiarlo a `in_progress`.
4. Cambiarlo a `approved`.
5. Cambiarlo a `available`.
6. Intentar poner `Sistemas ERP (43)` como `in_progress` y mostrar que falla.

---

## 4. Requests para probar

### Descripcion de cursos

Archivo:

```txt
requests/api-descripcion-cursos.http
```

Usa:

- `sectionId = 1`
- usuario `20232637`

Requests principales:

```txt
GET /api/v1/descripcion-cursos/sections/{sectionId}
GET /api/v1/sections/{sectionId}/announcements
GET /api/v1/descripcion-cursos/sections/{sectionId}/advising
GET /api/v1/descripcion-cursos/sections/{sectionId}/contacts
```

### Malla

Archivo:

```txt
requests/api-malla.http
```

Usa:

- usuario `20232637`
- Planeamiento Estrategico `(46)` para el flujo de simulacion;
- Sistemas ERP `(43)` para error de bloqueado.

Requests principales:

```txt
GET /api/v1/malla
GET /api/v1/malla/progress
PUT /api/v1/malla/simulation/course-status
DELETE /api/v1/malla/simulation
GET /api/v1/malla/specialties
GET /api/v1/malla/courses/{id}/status
```

---

## 5. Frases cortas para exposicion

### Descripcion de cursos

> Esta pantalla parte de una seccion. Con ese ID se cargan el encabezado, las asesorias, los contactos y los anuncios.

> Los anuncios no se duplican en descripcion de cursos; se consume el endpoint compartido de secciones.

> Contactos cruza docente, matriculas, alumnos y representantes de seccion para ordenar delegado, subdelegado y estudiantes.

### Malla

> La malla combina datos reales y simulacion. Lo real viene de progreso, matricula y nivel actual; la simulacion solo se aplica encima.

> `locked` y `unlocked` no se guardan en la base de datos. Se calculan usando prerequisitos y progreso.

> El cambio manual respeta el flujo de la app: disponible, cursando, aprobado y de vuelta a disponible.

> Si un curso esta bloqueado, el backend no permite ponerlo como cursando.
