import traceback

from flask import Blueprint, g, jsonify

from core.database import Session
from login.middlewares import jwt_required
from malla.apis.curriculum import (
    api_response,
    get_active_student_specialties,
    get_student_for_user,
    specialty_to_dict,
)

api = Blueprint('malla_specialty', __name__)


@api.route('/api/v1/malla/specialties', methods=['GET'])
@jwt_required
def fetch_specialties():
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

        specialties = sorted(
            get_active_student_specialties(session, student),
            key=lambda item: item.name,
        )

        response = jsonify(api_response(
            'Especialidades del alumno obtenidas correctamente',
            data=[specialty_to_dict(item) for item in specialties],
        ))
    except Exception as e:
        traceback.print_exc()
        response = jsonify(api_response(
            'Error al obtener especialidades',
            success=False,
            error=str(e),
        ))
        status = 500
    finally:
        session.close()
    return response, status
