from flask import jsonify
from sqlalchemy.orm import joinedload

from malla.models import (
    CourseOffering,
    CoursePrerequisite,
    Curriculum,
    CurriculumCourse,
    CurriculumCourseSpecialty,
    Enrollment,
    Section,
    Student,
    StudentCourseProgress,
    StudentCurriculumSimulation,
    StudentSpecialty,
)

# ==========================================
# 1. CONFIGURACION Y RESPUESTA BASE
# ==========================================

SIMULATION_INPUT_STATUS = {
    'approved': 'simulated_approved',
    'in_progress': 'simulated_in_progress',
    'current': 'simulated_in_progress',
}

SIMULATION_RESET_STATUS = {'available'}


# Formato comun para todas las respuestas del modulo.
def api_response(message, data=None, success=True, error=None):
    return {
        'message': message,
        'data': data,
        'success': success,
        'error': error,
    }


# Devuelve una respuesta Flask usando el formato comun del modulo.
def endpoint_response(message, data=None, success=True, error=None, status=200):
    return jsonify(api_response(
        message,
        data=data,
        success=success,
        error=error,
    )), status


# Respuesta repetida cuando el token no tiene estudiante asociado.
def student_not_found_response():
    return endpoint_response(
        'Estudiante no encontrado',
        success=False,
        error='No existe un estudiante asociado al usuario autenticado',
        status=404,
    )


# ==========================================
# 2. CONSULTAS DEL ALUMNO Y SU MALLA
# ==========================================

# Busca el perfil academico del usuario logueado.
def get_student_for_user(session, user_id):
    return (
        session.query(Student)
        .options(
            joinedload(Student.user),
            joinedload(Student.career),
            joinedload(Student.curriculum).joinedload(Curriculum.career),
        )
        .filter(Student.user_id == user_id)
        .first()
    )


# Trae todos los cursos que pertenecen al plan del alumno.
def get_curriculum_courses(session, student):
    return (
        session.query(CurriculumCourse)
        .options(joinedload(CurriculumCourse.course))
        .filter(CurriculumCourse.curriculum_id == student.curriculum_id)
        .order_by(CurriculumCourse.cycle.asc(), CurriculumCourse.display_order.asc())
        .all()
    )


# ==========================================
# 3. CONSULTAS DE PROGRESO, MATRICULA Y SIMULACION
# ==========================================

# Detecta los cursos que el alumno lleva en el ciclo actual.
def get_current_curriculum_course_ids(session, student):
    rows = (
        session.query(CurriculumCourse.id)
        .join(CourseOffering, CourseOffering.course_id == CurriculumCourse.course_id)
        .join(Section, Section.course_offering_id == CourseOffering.id)
        .join(Enrollment, Enrollment.section_id == Section.id)
        .filter(
            CurriculumCourse.curriculum_id == student.curriculum_id,
            Enrollment.student_id == student.id,
            Enrollment.status == 'active',
        )
        .all()
    )
    return {row[0] for row in rows}


# Lee estados reales guardados, como approved o in_progress.
def get_progress_by_course_id(session, student):
    rows = (
        session.query(StudentCourseProgress)
        .filter(
            StudentCourseProgress.student_id == student.id,
            StudentCourseProgress.curriculum_id == student.curriculum_id,
        )
        .all()
    )
    return {row.curriculum_course_id: row.status for row in rows}


# Lee cambios temporales hechos desde la vista de la malla.
def get_simulation_by_course_id(session, student):
    rows = (
        session.query(StudentCurriculumSimulation)
        .filter(
            StudentCurriculumSimulation.student_id == student.id,
            StudentCurriculumSimulation.curriculum_id == student.curriculum_id,
        )
        .all()
    )
    return {row.curriculum_course_id: row.status for row in rows}


# ==========================================
# 4. CONSULTAS DE PRERREQUISITOS Y ESPECIALIDADES
# ==========================================

# Obtiene las especialidades que el alumno tiene activas.
def get_active_student_specialties(session, student):
    rows = (
        session.query(StudentSpecialty)
        .options(joinedload(StudentSpecialty.specialty))
        .filter(
            StudentSpecialty.student_id == student.id,
            StudentSpecialty.is_active.is_(True),
        )
        .all()
    )
    return [row.specialty for row in rows if row.specialty and row.specialty.is_active]


# Separa prerequisitos por curso y requisitos por ciclo.
def get_prerequisites_by_course_id(session, curriculum_id):
    prerequisites = (
        session.query(CoursePrerequisite)
        .filter(CoursePrerequisite.curriculum_id == curriculum_id)
        .all()
    )
    by_course = {}
    required_cycles = {}
    for item in prerequisites:
        if item.prerequisite_type == 'course':
            by_course.setdefault(item.curriculum_course_id, []).append(
                str(item.prerequisite_curriculum_course_id)
            )
        elif item.prerequisite_type == 'completed_cycle':
            current = required_cycles.get(item.curriculum_course_id)
            required_cycles[item.curriculum_course_id] = max(
                current or 0,
                item.required_cycle or 0,
            )
    return by_course, required_cycles


# Agrupa que especialidades habilitan cada electivo.
def get_specialties_by_curriculum_course_id(session):
    relations = (
        session.query(CurriculumCourseSpecialty)
        .options(joinedload(CurriculumCourseSpecialty.specialty))
        .all()
    )
    by_course = {}
    ids_by_course = {}
    for relation in relations:
        specialty = relation.specialty
        if not specialty or not specialty.is_active:
            continue
        by_course.setdefault(relation.curriculum_course_id, []).append(specialty.name)
        ids_by_course.setdefault(relation.curriculum_course_id, set()).add(specialty.id)
    return by_course, ids_by_course


# ==========================================
# 5. CALCULO DE ESTADOS DE LA MALLA
# ==========================================

# Arma el set base de cursos aprobados para calcular desbloqueos.
def infer_approved_ids(
    curriculum_courses,
    student,
    progress_by_course_id,
    simulation_by_course_id=None,
):
    simulation_by_course_id = simulation_by_course_id or {}
    simulated_ids = set(simulation_by_course_id.keys())
    approved = {
        course_id
        for course_id, status in progress_by_course_id.items()
        if status == 'approved' and course_id not in simulated_ids
    }
    approved.update(
        course_id
        for course_id, status in simulation_by_course_id.items()
        if status == 'simulated_approved'
    )

    current_level = student.current_level or 0
    for item in curriculum_courses:
        if (
            item.category != 'elective'
            and item.cycle < current_level
            and item.id not in simulated_ids
        ):
            approved.add(item.id)
    return approved


# Confirma si todos los obligatorios hasta cierto ciclo estan aprobados.
def has_completed_mandatory_cycles(curriculum_courses, approved_ids, through_level):
    return all(
        item.id in approved_ids
        for item in curriculum_courses
        if item.category != 'elective' and item.cycle <= through_level
    )


# Calcula el estado visual final de cada curso.
def calculate_statuses(
    curriculum_courses,
    student,
    progress_by_course_id,
    current_course_ids,
    prerequisites_by_course_id,
    required_cycles_by_course_id,
    simulation_by_course_id=None,
):
    # Primero mezcla matriculas reales con cursos marcados en simulacion.
    simulation_by_course_id = simulation_by_course_id or {}
    simulated_current_ids = {
        course_id
        for course_id, status in simulation_by_course_id.items()
        if status == 'simulated_in_progress'
    }
    current_course_ids = set(current_course_ids).union(simulated_current_ids)
    approved_ids = infer_approved_ids(
        curriculum_courses,
        student,
        progress_by_course_id,
        simulation_by_course_id,
    )
    statuses = {}
    by_id = {item.id: item for item in curriculum_courses}

    # Luego revisa cada curso siguiendo la prioridad de estados.
    for item in curriculum_courses:
        # La simulacion tiene prioridad sobre el resto.
        simulation_status = simulation_by_course_id.get(item.id)
        if simulation_status == 'simulated_approved':
            statuses[item.id] = 'approved'
            continue
        if simulation_status == 'simulated_in_progress':
            statuses[item.id] = 'current'
            continue

        # Despues vienen progreso real, matricula activa y nivel actual.
        saved_status = progress_by_course_id.get(item.id)
        if saved_status == 'approved':
            statuses[item.id] = 'approved'
            continue
        if saved_status == 'in_progress' or item.id in current_course_ids:
            statuses[item.id] = 'current'
            continue
        if item.id in approved_ids:
            statuses[item.id] = 'approved'
            continue

        # Si no cumple ciclo requerido, queda bloqueado.
        required_cycle = required_cycles_by_course_id.get(item.id)
        if required_cycle and not has_completed_mandatory_cycles(
            curriculum_courses,
            approved_ids,
            required_cycle,
        ):
            statuses[item.id] = 'locked'
            continue

        # Finalmente revisa prerequisitos de cursos.
        prerequisites = prerequisites_by_course_id.get(item.id, [])
        all_prerequisites_ok = all(
            int(prerequisite_id) in by_id and int(prerequisite_id) in approved_ids
            for prerequisite_id in prerequisites
        )
        statuses[item.id] = 'unlocked' if all_prerequisites_ok else 'locked'

    return statuses, approved_ids, current_course_ids


# Decide que cursos se muestran segun obligatorios, electivos y especialidades.
def visible_curriculum_courses(
    curriculum_courses,
    active_specialty_ids,
    specialty_ids_by_course_id,
    approved_ids,
    current_course_ids,
):
    visible = []
    for item in curriculum_courses:
        if item.category != 'elective':
            visible.append(item)
            continue
        if item.id in approved_ids or item.id in current_course_ids:
            visible.append(item)
            continue
        if not active_specialty_ids:
            continue
        item_specialty_ids = specialty_ids_by_course_id.get(item.id, set())
        if item_specialty_ids and item_specialty_ids.intersection(active_specialty_ids):
            visible.append(item)
    return visible


# ==========================================
# 6. ARMADO DEL JSON PARA LA APP
# ==========================================

# Convierte una especialidad a JSON simple.
def specialty_to_dict(specialty):
    return {
        'id': specialty.id,
        'name': specialty.name,
        'description': specialty.description,
        'careerId': specialty.career_id,
        'isActive': bool(specialty.is_active),
    }


# Convierte un curso de malla a la forma que espera la app.
def curriculum_course_to_dict(
    item,
    status,
    prerequisites_by_course_id,
    required_cycles_by_course_id,
    specialties_by_course_id,
):
    course = item.course
    return {
        'id': str(item.id),
        'curriculumCourseId': item.id,
        'courseId': course.id if course else None,
        'code': course.code if course else None,
        'name': course.name if course else 'Sin curso',
        'credits': item.credit,
        'level': item.cycle,
        'row': item.display_order - 1,
        'category': item.category,
        'externalFaculty': course.origin_faculty if course else None,
        'prerequisites': prerequisites_by_course_id.get(item.id, []),
        'requiredCompletedLevel': required_cycles_by_course_id.get(item.id),
        'specialties': specialties_by_course_id.get(item.id, []),
        'status': status,
    }


# Resume progreso real y calculado para la respuesta.
def build_progress_payload(
    student,
    progress_by_course_id,
    current_course_ids,
    approved_ids,
    simulation_by_course_id=None,
    include_status_maps=True,
):
    current_level = student.current_level or 0
    payload = {
        'currentLevel': student.current_level,
        'approvedLevels': list(range(1, current_level)),
        'approvedCourseIds': sorted(str(course_id) for course_id in approved_ids),
        'currentCourseIds': sorted(str(course_id) for course_id in current_course_ids),
    }
    if include_status_maps:
        payload['savedStatuses'] = {
            str(course_id): status
            for course_id, status in sorted(progress_by_course_id.items())
        }
        payload['simulationStatuses'] = {
            str(course_id): status
            for course_id, status in sorted((simulation_by_course_id or {}).items())
        }
    return payload


# Devuelve la Malla completa
def build_malla_payload(session, student, simulation_by_course_id=None):
    # Carga toda la data base que se necesita para calcular la malla.
    curriculum_courses = get_curriculum_courses(session, student)
    progress_by_course_id = get_progress_by_course_id(session, student)
    simulation_by_course_id = simulation_by_course_id or {}
    enrolled_course_ids = get_current_curriculum_course_ids(session, student)
    active_specialties = get_active_student_specialties(session, student)
    active_specialty_ids = {specialty.id for specialty in active_specialties}
    prerequisites_by_course_id, required_cycles_by_course_id = (
        get_prerequisites_by_course_id(session, student.curriculum_id)
    )
    specialties_by_course_id, specialty_ids_by_course_id = (
        get_specialties_by_curriculum_course_id(session)
    )

    # Calcula estados y decide que cursos entran en la vista final.
    statuses, approved_ids, current_course_ids = calculate_statuses(
        curriculum_courses,
        student,
        progress_by_course_id,
        enrolled_course_ids,
        prerequisites_by_course_id,
        required_cycles_by_course_id,
        simulation_by_course_id,
    )
    visible_courses = visible_curriculum_courses(
        curriculum_courses,
        active_specialty_ids,
        specialty_ids_by_course_id,
        approved_ids,
        current_course_ids,
    )

    # para endpoint GET /malla.
    return {
        'currentLevel': student.current_level,
        'curriculum': {
            'id': student.curriculum.id if student.curriculum else student.curriculum_id,
            'name': student.curriculum.name if student.curriculum else None,
            'careerId': student.career_id,
        },
        'specialties': [specialty_to_dict(item) for item in active_specialties],
        'courses': [
            curriculum_course_to_dict(
                item,
                statuses.get(item.id, 'locked'),
                prerequisites_by_course_id,
                required_cycles_by_course_id,
                specialties_by_course_id,
            )
            for item in visible_courses
        ],
        'progress': build_progress_payload(
            student,
            progress_by_course_id,
            current_course_ids,
            approved_ids,
            simulation_by_course_id,
            include_status_maps=False,
        ),
    }


# ==========================================
# 7. ESTADO DE UN CURSO
# ==========================================

# Traduce el estado interno de simulacion a estado visual.
def simulation_to_visual_status(simulation_status):
    if simulation_status == 'simulated_approved':
        return 'approved'
    if simulation_status == 'simulated_in_progress':
        return 'current'
    return None


# Indica de donde salio el estado mostrado.
def status_source_for_course(
    course,
    real_status,
    simulation_status,
    is_enrolled,
    approved_ids,
):
    if simulation_status:
        return 'simulation'
    if real_status in ('approved', 'in_progress'):
        return 'real_progress'
    if is_enrolled:
        return 'enrollment'
    if course.id in approved_ids and course.category != 'elective':
        return 'current_level'
    return 'calculated'


# Detalla por que un curso esta aprobado, cursando, disponible o bloqueado.
def explain_course_status(session, student, curriculum_course_id):
    # Primero carga la malla y ubica el curso solicitado.
    curriculum_courses = get_curriculum_courses(session, student)
    by_id = {item.id: item for item in curriculum_courses}
    course = by_id.get(curriculum_course_id)
    if not course:
        return None

    # Luego carga progreso, simulacion, matriculas y prerequisitos.
    progress_by_course_id = get_progress_by_course_id(session, student)
    simulation_by_course_id = get_simulation_by_course_id(session, student)
    current_course_ids = get_current_curriculum_course_ids(session, student)
    prerequisites_by_course_id, required_cycles_by_course_id = (
        get_prerequisites_by_course_id(session, student.curriculum_id)
    )

    # Compara el estado base contra el estado final con simulacion.
    base_statuses, base_approved_ids, base_current_course_ids = calculate_statuses(
        curriculum_courses,
        student,
        progress_by_course_id,
        current_course_ids,
        prerequisites_by_course_id,
        required_cycles_by_course_id,
    )
    final_statuses, final_approved_ids, _ = calculate_statuses(
        curriculum_courses,
        student,
        progress_by_course_id,
        current_course_ids,
        prerequisites_by_course_id,
        required_cycles_by_course_id,
        simulation_by_course_id,
    )

    simulation_status = simulation_by_course_id.get(course.id)
    real_status = progress_by_course_id.get(course.id)
    base_status = base_statuses.get(course.id, 'locked')
    final_status = final_statuses.get(course.id, 'locked')
    is_enrolled = course.id in base_current_course_ids
    base_source = status_source_for_course(
        course,
        real_status,
        None,
        is_enrolled,
        base_approved_ids,
    )
    final_source = 'simulation' if simulation_status else base_source

    # Revisa si el requisito por ciclo se cumple.
    required_level = required_cycles_by_course_id.get(course.id)
    required_level_met = True
    if required_level:
        required_level_met = has_completed_mandatory_cycles(
            curriculum_courses,
            final_approved_ids,
            required_level,
        )

    # Lista prerequisitos y marca cuales ya estan cumplidos.
    prerequisites = []
    for prerequisite_id in prerequisites_by_course_id.get(course.id, []):
        prerequisite_course = by_id.get(int(prerequisite_id))
        prerequisites.append({
            'curriculumCourseId': int(prerequisite_id),
            'name': (
                prerequisite_course.course.name
                if prerequisite_course and prerequisite_course.course
                else None
            ),
            'status': final_statuses.get(int(prerequisite_id), 'locked'),
            'met': int(prerequisite_id) in final_approved_ids,
        })

    return {
        'curriculumCourseId': course.id,
        'name': course.course.name if course.course else None,
        'base': {
            'status': base_status,
            'source': base_source,
            'realProgress': {
                'hasRecord': real_status is not None,
                'status': real_status,
            },
            'isEnrolled': is_enrolled,
            'isApprovedByCurrentLevel': (
                course.id in base_approved_ids and course.category != 'elective'
            ),
        },
        'simulation': {
            'hasOverride': simulation_status is not None,
            'status': simulation_status,
            'visualStatus': simulation_to_visual_status(simulation_status),
            'applied': simulation_status is not None,
        },
        'final': {
            'status': final_status,
            'source': final_source,
            'checks': {
                'hasRealProgress': real_status is not None,
                'hasSimulation': simulation_status is not None,
                'isEnrolled': is_enrolled,
                'requiredCompletedLevel': required_level,
                'requiredCompletedLevelMet': required_level_met,
                'prerequisites': prerequisites,
            },
        },
    }
