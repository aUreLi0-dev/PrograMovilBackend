import traceback

from flask import Blueprint, g

from core.database import Session
from apps.login.middlewares import jwt_required
from apps.malla.apis.curriculum_logic import (
    build_malla_payload,
    endpoint_response,
    explain_course_status,
    get_simulation_by_course_id,
    get_student_for_user,
    student_not_found_response,
)

api = Blueprint('malla_curriculum', __name__)


@api.route('/api/v1/malla', methods=['GET'])
@jwt_required
def fetch_malla():
    session = Session()
    try:
        student = get_student_for_user(session, g.user_id)
        if not student:
            return student_not_found_response()

        return endpoint_response(
            'Malla curricular obtenida correctamente',
            data=build_malla_payload(
                session,
                student,
                get_simulation_by_course_id(session, student),
            ),
        )
    except Exception as e:
        traceback.print_exc()
        return endpoint_response(
            'Error al obtener la malla curricular',
            success=False,
            error=str(e),
            status=500,
        )
    finally:
        session.close()


@api.route('/api/v1/malla/courses/<int:curriculum_course_id>/status', methods=['GET'])
@jwt_required
def fetch_course_status(curriculum_course_id):
    session = Session()
    try:
        student = get_student_for_user(session, g.user_id)
        if not student:
            return student_not_found_response()

        data = explain_course_status(session, student, curriculum_course_id)
        if not data:
            return endpoint_response(
                'Curso de malla no encontrado',
                success=False,
                error='El curso no pertenece a la malla del estudiante',
                status=404,
            )

        return endpoint_response(
            'Estado del curso explicado correctamente',
            data=data,
        )
    except Exception as e:
        traceback.print_exc()
        return endpoint_response(
            'Error al explicar estado del curso',
            success=False,
            error=str(e),
            status=500,
        )
    finally:
        session.close()
