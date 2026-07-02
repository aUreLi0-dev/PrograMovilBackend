import traceback

from flask import Blueprint, g, jsonify
from sqlalchemy.orm import joinedload

from core.database import Session
from login.middlewares import jwt_required
from malla.models import (
    CourseOffering,
    CoursePrerequisite,
    Curriculum,
    CurriculumCourse,
    CurriculumCourseSpecialty,
    Enrollment,
    Section,
    Student,
    StudentCurriculumSimulation,
    StudentCourseProgress,
    StudentSpecialty,
)

api = Blueprint('malla_curriculum', __name__)

SIMULATION_INPUT_STATUS = {
    'approved': 'simulated_approved',
    'in_progress': 'simulated_in_progress',
    'current': 'simulated_in_progress',
}
SIMULATION_RESET_STATUS = {'available', 'unlocked'}


def api_response(message, data=None, success=True, error=None):
    return {
        'message': message,
        'data': data,
        'success': success,
        'error': error,
    }


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


def specialty_to_dict(specialty):
    return {
        'id': specialty.id,
        'name': specialty.name,
        'description': specialty.description,
        'careerId': specialty.career_id,
        'isActive': bool(specialty.is_active),
    }


def get_active_student_specialties(session, student):
    rows = (
        session.query(StudentSpecialty)
        .options(joinedload(StudentSpecialty.specialty))
        .filter(
            StudentSpecialty.student_id == student.id,
            StudentSpecialty.is_active == True,
        )
        .all()
    )
    return [row.specialty for row in rows if row.specialty and row.specialty.is_active]


def get_curriculum_courses(session, student):
    return (
        session.query(CurriculumCourse)
        .options(joinedload(CurriculumCourse.course))
        .filter(CurriculumCourse.curriculum_id == student.curriculum_id)
        .order_by(CurriculumCourse.cycle.asc(), CurriculumCourse.display_order.asc())
        .all()
    )


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


def has_completed_mandatory_cycles(curriculum_courses, approved_ids, through_level):
    return all(
        item.id in approved_ids
        for item in curriculum_courses
        if item.category != 'elective' and item.cycle <= through_level
    )


def calculate_statuses(
    curriculum_courses,
    student,
    progress_by_course_id,
    current_course_ids,
    prerequisites_by_course_id,
    required_cycles_by_course_id,
    simulation_by_course_id=None,
):
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

    for item in curriculum_courses:
        simulation_status = simulation_by_course_id.get(item.id)
        if simulation_status == 'simulated_approved':
            statuses[item.id] = 'approved'
            continue
        if simulation_status == 'simulated_in_progress':
            statuses[item.id] = 'current'
            continue

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

        required_cycle = required_cycles_by_course_id.get(item.id)
        if required_cycle and not has_completed_mandatory_cycles(
            curriculum_courses,
            approved_ids,
            required_cycle,
        ):
            statuses[item.id] = 'locked'
            continue

        prerequisites = prerequisites_by_course_id.get(item.id, [])
        all_prerequisites_ok = all(
            int(prerequisite_id) in by_id and int(prerequisite_id) in approved_ids
            for prerequisite_id in prerequisites
        )
        statuses[item.id] = 'unlocked' if all_prerequisites_ok else 'locked'

    return statuses, approved_ids, current_course_ids


def curriculum_course_to_dict(
    item,
    status,
    status_source,
    real_status,
    simulation_status,
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
        'source': status_source,
        'realStatus': real_status,
        'simulationStatus': simulation_status,
    }


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


def build_progress_payload(
    student,
    progress_by_course_id,
    current_course_ids,
    approved_ids,
    simulation_by_course_id=None,
):
    current_level = student.current_level or 0
    return {
        'currentLevel': student.current_level,
        'approvedLevels': list(range(1, current_level)),
        'approvedCourseIds': sorted(str(course_id) for course_id in approved_ids),
        'currentCourseIds': sorted(str(course_id) for course_id in current_course_ids),
        'savedStatuses': {
            str(course_id): status
            for course_id, status in sorted(progress_by_course_id.items())
        },
        'simulationStatuses': {
            str(course_id): status
            for course_id, status in sorted((simulation_by_course_id or {}).items())
        },
    }


def build_malla_payload(session, student, simulation_by_course_id=None):
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
                status_source_for_course(
                    item,
                    statuses.get(item.id, 'locked'),
                    progress_by_course_id.get(item.id),
                    simulation_by_course_id.get(item.id),
                    item.id in enrolled_course_ids,
                    approved_ids,
                ),
                progress_by_course_id.get(item.id),
                simulation_by_course_id.get(item.id),
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
        ),
    }


def simulation_to_visual_status(simulation_status):
    if simulation_status == 'simulated_approved':
        return 'approved'
    if simulation_status == 'simulated_in_progress':
        return 'current'
    return None


def status_source_for_course(
    course,
    status,
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
    if status in ('locked', 'unlocked'):
        return 'calculated'
    return 'calculated'


def explain_course_status(session, student, curriculum_course_id):
    curriculum_courses = get_curriculum_courses(session, student)
    by_id = {item.id: item for item in curriculum_courses}
    course = by_id.get(curriculum_course_id)
    if not course:
        return None

    progress_by_course_id = get_progress_by_course_id(session, student)
    simulation_by_course_id = get_simulation_by_course_id(session, student)
    current_course_ids = get_current_curriculum_course_ids(session, student)
    prerequisites_by_course_id, required_cycles_by_course_id = (
        get_prerequisites_by_course_id(session, student.curriculum_id)
    )

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
        base_status,
        real_status,
        None,
        is_enrolled,
        base_approved_ids,
    )
    final_source = 'simulation' if simulation_status else base_source

    required_level = required_cycles_by_course_id.get(course.id)
    required_level_met = True
    if required_level:
        required_level_met = has_completed_mandatory_cycles(
            curriculum_courses,
            final_approved_ids,
            required_level,
        )

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


@api.route('/api/v1/malla', methods=['GET'])
@jwt_required
def fetch_malla():
    response = None
    status = 200
    session = Session()
    try:
        student = get_student_for_user(session, g.user_id)
        if not student:
            response = jsonify(api_response(
                'Estudiante no encontrado',
                success=False,
                error='No existe un estudiante asociado al usuario autenticado',
            ))
            status = 404
            return response, status

        response = jsonify(api_response(
            'Malla curricular obtenida correctamente',
            data=build_malla_payload(
                session,
                student,
                get_simulation_by_course_id(session, student),
            ),
        ))
    except Exception as e:
        traceback.print_exc()
        response = jsonify(api_response(
            'Error al obtener la malla curricular',
            success=False,
            error=str(e),
        ))
        status = 500
    finally:
        session.close()
    return response, status


@api.route('/api/v1/malla/courses/<int:curriculum_course_id>/status', methods=['GET'])
@jwt_required
def fetch_course_status(curriculum_course_id):
    response = None
    status = 200
    session = Session()
    try:
        student = get_student_for_user(session, g.user_id)
        if not student:
            response = jsonify(api_response(
                'Estudiante no encontrado',
                success=False,
                error='No existe un estudiante asociado al usuario autenticado',
            ))
            status = 404
            return response, status

        data = explain_course_status(session, student, curriculum_course_id)
        if not data:
            response = jsonify(api_response(
                'Curso de malla no encontrado',
                success=False,
                error='El curso no pertenece a la malla del estudiante',
            ))
            status = 404
            return response, status

        response = jsonify(api_response(
            'Estado del curso explicado correctamente',
            data=data,
        ))
    except Exception as e:
        traceback.print_exc()
        response = jsonify(api_response(
            'Error al explicar estado del curso',
            success=False,
            error=str(e),
        ))
        status = 500
    finally:
        session.close()
    return response, status
