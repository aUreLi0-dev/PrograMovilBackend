import traceback

from flask import Blueprint, g

from core.database import Session
from login.middlewares import jwt_required

# Reutiliza la logica central de la malla para no calcular distinto.
from malla.apis.curriculum_logic import (
    build_progress_payload,
    endpoint_response,
    get_current_curriculum_course_ids,
    get_curriculum_courses,
    get_progress_by_course_id,
    get_student_for_user,
    infer_approved_ids,
    student_not_found_response,
)

api = Blueprint('malla_progress', __name__)


@api.route('/api/v1/malla/progress', methods=['GET'])
@jwt_required
def fetch_progress():
    session = Session()
    try:
        # Usa la misma busqueda de alumno que el endpoint principal de malla.
        student = get_student_for_user(session, g.user_id)
        if not student:
            return student_not_found_response()

        # Trae los mismos datos base que usa la malla completa.
        curriculum_courses = get_curriculum_courses(session, student)
        progress_by_course_id = get_progress_by_course_id(session, student)
        current_course_ids = get_current_curriculum_course_ids(session, student)

        # Aplica el mismo criterio de aprobados que se pinta en la malla.
        approved_ids = infer_approved_ids(
            curriculum_courses,
            student,
            progress_by_course_id,
        )

        # Arma el resumen con el formato compartido del modulo.
        return endpoint_response(
            'Progreso de malla obtenido correctamente',
            data=build_progress_payload(
                student,
                progress_by_course_id,
                current_course_ids,
                approved_ids,
            ),
        )
    except Exception as e:
        traceback.print_exc()
        return endpoint_response(
            'Error al obtener progreso de malla',
            success=False,
            error=str(e),
            status=500,
        )
    finally:
        session.close()
