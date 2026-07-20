import traceback

from flask import Blueprint, g

from core.database import Session
from apps.login.middlewares import jwt_required
from apps.malla.apis.curriculum_logic import (
    endpoint_response,
    get_active_student_specialties,
    get_student_for_user,
    student_not_found_response,
    specialty_to_dict,
)

api = Blueprint('malla_specialty', __name__)


@api.route('/api/v1/malla/specialties', methods=['GET'])
@jwt_required
def fetch_specialties():
    session = Session()
    try:
        student = get_student_for_user(session, g.user_id)
        if not student:
            return student_not_found_response()

        specialties = sorted(
            get_active_student_specialties(session, student),
            key=lambda item: item.name,
        )

        return endpoint_response(
            'Especialidades del alumno obtenidas correctamente',
            data=[specialty_to_dict(item) for item in specialties],
        )
    except Exception as e:
        traceback.print_exc()
        return endpoint_response(
            'Error al obtener especialidades',
            success=False,
            error=str(e),
            status=500,
        )
    finally:
        session.close()
