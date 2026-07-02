import traceback

from flask import Blueprint, g, jsonify

from core.database import Session
from login.middlewares import jwt_required
from malla.apis.curriculum import (
    api_response,
    build_progress_payload,
    get_current_curriculum_course_ids,
    get_curriculum_courses,
    get_progress_by_course_id,
    get_student_for_user,
    infer_approved_ids,
)

api = Blueprint('malla_progress', __name__)


@api.route('/api/v1/malla/progress', methods=['GET'])
@jwt_required
def fetch_progress():
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

        curriculum_courses = get_curriculum_courses(session, student)
        progress_by_course_id = get_progress_by_course_id(session, student)
        current_course_ids = get_current_curriculum_course_ids(session, student)
        approved_ids = infer_approved_ids(
            curriculum_courses,
            student,
            progress_by_course_id,
        )

        response = jsonify(api_response(
            'Progreso de malla obtenido correctamente',
            data=build_progress_payload(
                student,
                progress_by_course_id,
                current_course_ids,
                approved_ids,
            ),
        ))
    except Exception as e:
        traceback.print_exc()
        response = jsonify(api_response(
            'Error al obtener progreso de malla',
            success=False,
            error=str(e),
        ))
        status = 500
    finally:
        session.close()
    return response, status
