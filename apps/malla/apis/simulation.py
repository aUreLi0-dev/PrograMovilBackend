import traceback

from flask import Blueprint, g, request

from core.database import Session
from apps.login.middlewares import jwt_required

# Reutiliza respuestas, estados y calculos finales de curriculum_logic.
from apps.malla.apis.curriculum_logic import (
    SIMULATION_INPUT_STATUS,
    SIMULATION_RESET_STATUS,
    endpoint_response,
    explain_course_status,
    get_student_for_user,
    student_not_found_response,
)
from apps.models import CurriculumCourse, StudentCurriculumSimulation

api = Blueprint('malla_simulation', __name__)


def _read_status_request():
    body = request.get_json() or {}
    curriculum_course_id = (
        body.get('curriculumCourseId') or body.get('curriculum_course_id')
    )
    requested_status = body.get('status')
    if not curriculum_course_id or not requested_status:
        return None, None, endpoint_response(
            'Datos invalidos para actualizar simulacion',
            success=False,
            error='curriculumCourseId y status son obligatorios',
            status=400,
        )

    try:
        curriculum_course_id = int(curriculum_course_id)
    except (TypeError, ValueError):
        return None, None, endpoint_response(
            'Curso de malla invalido',
            success=False,
            error='curriculumCourseId debe ser numerico',
            status=400,
        )

    return curriculum_course_id, str(requested_status).strip().lower(), None


def _find_curriculum_course(session, student, curriculum_course_id):
    # Confirma que el curso pertenece a la malla del alumno.
    return (
        session.query(CurriculumCourse).filter(
            CurriculumCourse.id == curriculum_course_id,
            CurriculumCourse.curriculum_id == student.curriculum_id,
        ).first()
    )


def _find_simulation(session, student, curriculum_course):
    # Revisa si ya existe una simulacion para este curso.
    return (
        session.query(StudentCurriculumSimulation)
        .filter(
            StudentCurriculumSimulation.student_id == student.id,
            StudentCurriculumSimulation.curriculum_course_id == curriculum_course.id,
        )
        .first()
    )


def _visual_status(requested_status):
    if requested_status in ('current', 'in_progress'):
        return 'current'
    return requested_status


def _validate_requested_status(normalized_status):
    # Valida contra los estados permitidos definidos para la simulacion.
    if (
        normalized_status in SIMULATION_INPUT_STATUS
        or normalized_status in SIMULATION_RESET_STATUS
    ):
        return None

    return endpoint_response(
        'Estado de simulacion invalido',
        success=False,
        error='Usa approved, in_progress, current, available, unlocked, official o reset',
        status=400,
    )


def _locked_course_response(curriculum_course):
    return endpoint_response(
        'Cambio de estado no permitido',
        data={
            'curriculumCourseId': curriculum_course.id,
            'currentStatus': 'locked',
        },
        success=False,
        error='El curso esta bloqueado hasta cumplir sus prerrequisitos',
        status=409,
    )


def _reset_to_official(session, student, curriculum_course, simulation):
    if simulation:
        session.delete(simulation)
    session.commit()

    # Recalcula con la logica central para confirmar si queda disponible.
    calculated_status = explain_course_status(
        session,
        student,
        curriculum_course.id,
    )
    final_status = calculated_status['final']['status']
    final_source = calculated_status['final']['source']
    response_data = {
        'curriculumCourseId': curriculum_course.id,
        'status': final_status,
        'source': final_source,
        'storedStatus': None,
    }

    return endpoint_response(
        'Curso restaurado a su estado oficial correctamente',
        data=response_data,
    )


def _save_simulation(session, student, curriculum_course, simulation, normalized_status):
    # Traduce el estado visual al valor que se guarda en simulacion.
    stored_status = SIMULATION_INPUT_STATUS[normalized_status]
    if not simulation:
        simulation = StudentCurriculumSimulation(
            student_id=student.id,
            curriculum_id=student.curriculum_id,
            curriculum_course_id=curriculum_course.id,
            status=stored_status,
        )
        session.add(simulation)
    else:
        simulation.status = stored_status

    session.commit()
    return simulation


@api.route('/api/v1/malla/simulation/course-status', methods=['PUT'])
@jwt_required
def update_simulated_course_status():
    session = Session()
    try:
        # Usa la misma busqueda de alumno que el resto de endpoints de malla.
        student = get_student_for_user(session, g.user_id)
        if not student:
            return student_not_found_response()

        curriculum_course_id, normalized_status, error_response = _read_status_request()
        if error_response:
            return error_response

        error_response = _validate_requested_status(normalized_status)
        if error_response:
            return error_response

        curriculum_course = _find_curriculum_course(
            session,
            student,
            curriculum_course_id,
        )
        if not curriculum_course:
            return endpoint_response(
                'Curso de malla no encontrado',
                success=False,
                error='El curso no pertenece a la malla del estudiante',
                status=404,
            )

        simulation = _find_simulation(session, student, curriculum_course)

        if normalized_status in SIMULATION_RESET_STATUS:
            return _reset_to_official(session, student, curriculum_course, simulation)

        current_status_data = explain_course_status(
            session,
            student,
            curriculum_course.id,
        )
        if current_status_data['final']['status'] == 'locked':
            return _locked_course_response(curriculum_course)

        simulation = _save_simulation(
            session,
            student,
            curriculum_course,
            simulation,
            normalized_status,
        )

        return endpoint_response(
            'Estado simulado actualizado correctamente',
            data={
                'curriculumCourseId': simulation.curriculum_course_id,
                'status': _visual_status(normalized_status),
                'source': 'simulation',
                'storedStatus': simulation.status,
            },
        )
    except Exception as e:
        session.rollback()
        traceback.print_exc()
        return endpoint_response(
            'Error al actualizar simulacion de malla',
            success=False,
            error=str(e),
            status=500,
        )
    finally:
        session.close()


@api.route('/api/v1/malla/simulation', methods=['DELETE'])
@jwt_required
def clear_simulation():
    session = Session()
    try:
        # Usa la misma busqueda compartida antes de limpiar la simulacion.
        student = get_student_for_user(session, g.user_id)
        if not student:
            return student_not_found_response()

        # Borra todas las simulaciones del alumno en esta malla.
        deleted = (
            session.query(StudentCurriculumSimulation)
            .filter(
                StudentCurriculumSimulation.student_id == student.id,
                StudentCurriculumSimulation.curriculum_id == student.curriculum_id,
            )
            .delete()
        )
        session.commit()

        return endpoint_response(
            'Simulacion de malla limpiada correctamente',
            data={'deleted': deleted},
        )
    except Exception as e:
        session.rollback()
        traceback.print_exc()
        return endpoint_response(
            'Error al limpiar simulacion de malla',
            success=False,
            error=str(e),
            status=500,
        )
    finally:
        session.close()
