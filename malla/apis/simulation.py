import traceback

from flask import Blueprint, g, jsonify, request

from core.database import Session
from login.middlewares import jwt_required
from malla.apis.curriculum import (
    SIMULATION_INPUT_STATUS,
    SIMULATION_RESET_STATUS,
    api_response,
    explain_course_status,
    get_student_for_user,
)
from malla.models import CurriculumCourse, StudentCurriculumSimulation

api = Blueprint('malla_simulation', __name__)


def _find_curriculum_course(session, student, curriculum_course_id):
    return (
        session.query(CurriculumCourse)
        .filter(
            CurriculumCourse.id == int(curriculum_course_id),
            CurriculumCourse.curriculum_id == student.curriculum_id,
        )
        .first()
    )


def _visual_status(requested_status):
    if requested_status in ('current', 'in_progress'):
        return 'current'
    return requested_status


def _status_transition_error(current_status, requested_status):
    requested_visual_status = _visual_status(requested_status)
    if requested_visual_status == 'current' and current_status != 'unlocked':
        return 'Solo un curso disponible puede pasar a cursando'
    if requested_visual_status == 'approved' and current_status != 'current':
        return 'Solo un curso en curso puede pasar a aprobado'
    return None


@api.route('/api/v1/malla/simulation/course-status', methods=['PUT'])
@jwt_required
def update_simulated_course_status():
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

        body = request.get_json() or {}
        curriculum_course_id = body.get('curriculumCourseId') or body.get('curriculum_course_id')
        requested_status = body.get('status')

        if not curriculum_course_id or not requested_status:
            response = jsonify(api_response(
                'Datos invalidos para actualizar simulacion',
                success=False,
                error='curriculumCourseId y status son obligatorios',
            ))
            status = 400
            return response, status

        normalized_status = str(requested_status).strip().lower()
        if (
            normalized_status not in SIMULATION_INPUT_STATUS
            and normalized_status not in SIMULATION_RESET_STATUS
        ):
            response = jsonify(api_response(
                'Estado de simulacion invalido',
                success=False,
                error='Usa approved, in_progress, current o available',
            ))
            status = 400
            return response, status

        curriculum_course = _find_curriculum_course(session, student, curriculum_course_id)
        if not curriculum_course:
            response = jsonify(api_response(
                'Curso de malla no encontrado',
                success=False,
                error='El curso no pertenece a la malla del estudiante',
            ))
            status = 404
            return response, status

        simulation = (
            session.query(StudentCurriculumSimulation)
            .filter(
                StudentCurriculumSimulation.student_id == student.id,
                StudentCurriculumSimulation.curriculum_course_id == curriculum_course.id,
            )
            .first()
        )

        if normalized_status in SIMULATION_RESET_STATUS:
            if simulation:
                session.delete(simulation)
            session.commit()
            calculated_status = explain_course_status(session, student, curriculum_course.id)
            final_status = calculated_status['final']['status']
            final_source = calculated_status['final']['source']
            if final_status != 'unlocked':
                response = jsonify(api_response(
                    'El curso no puede quedar disponible',
                    success=False,
                    error='El estado recalculado no es unlocked',
                    data={
                        'curriculumCourseId': curriculum_course.id,
                        'status': final_status,
                        'source': final_source,
                        'storedStatus': None,
                    },
                ))
                status = 409
                return response, status

            response = jsonify(api_response(
                'Curso cambiado a disponible correctamente',
                data={
                    'curriculumCourseId': curriculum_course.id,
                    'status': 'available',
                    'source': final_source,
                    'storedStatus': None,
                },
            ))
            return response, status

        current_status_data = explain_course_status(session, student, curriculum_course.id)
        current_status = current_status_data['final']['status']
        transition_error = _status_transition_error(current_status, normalized_status)
        if transition_error:
            response = jsonify(api_response(
                'Cambio de estado no permitido',
                success=False,
                error=transition_error,
                data={
                    'curriculumCourseId': curriculum_course.id,
                    'currentStatus': current_status,
                    'requestedStatus': _visual_status(normalized_status),
                },
            ))
            status = 409
            return response, status

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

        response = jsonify(api_response(
            'Estado simulado actualizado correctamente',
            data={
                'curriculumCourseId': simulation.curriculum_course_id,
                'status': _visual_status(normalized_status),
                'source': 'simulation',
                'storedStatus': simulation.status,
            },
        ))
    except Exception as e:
        session.rollback()
        traceback.print_exc()
        response = jsonify(api_response(
            'Error al actualizar simulacion de malla',
            success=False,
            error=str(e),
        ))
        status = 500
    finally:
        session.close()
    return response, status


@api.route('/api/v1/malla/simulation', methods=['DELETE'])
@jwt_required
def clear_simulation():
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

        deleted = (
            session.query(StudentCurriculumSimulation)
            .filter(
                StudentCurriculumSimulation.student_id == student.id,
                StudentCurriculumSimulation.curriculum_id == student.curriculum_id,
            )
            .delete()
        )
        session.commit()

        response = jsonify(api_response(
            'Simulacion de malla limpiada correctamente',
            data={'deleted': deleted},
        ))
    except Exception as e:
        session.rollback()
        traceback.print_exc()
        response = jsonify(api_response(
            'Error al limpiar simulacion de malla',
            success=False,
            error=str(e),
        ))
        status = 500
    finally:
        session.close()
    return response, status
