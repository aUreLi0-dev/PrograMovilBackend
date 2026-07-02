import traceback

from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from sqlalchemy.orm import joinedload

from descripcion_cursos.apis.helpers import api_response, role_name, teacher_to_dict, user_to_dict
from descripcion_cursos.models import Enrollment, Section, SectionRepresentative, Student
from main.database import Session

api = Blueprint('descripcion_cursos_contact', __name__)


@api.route('/api/v1/descripcion-cursos/sections/<int:section_id>/contacts', methods=['GET'])
@jwt_required()
def fetch_contacts(section_id):
    response = None
    status = 200
    session = Session()
    try:
        section = (
            session.query(Section)
            .options(joinedload(Section.teacher))
            .filter(Section.id == section_id)
            .first()
        )
        if not section:
            response = jsonify(api_response(
                'Seccion no encontrada',
                success=False,
                error=f'No hay seccion con id: {section_id}',
            ))
            status = 404
            return response, status

        representatives = (
            session.query(SectionRepresentative)
            .filter(
                SectionRepresentative.section_id == section_id,
                SectionRepresentative.is_active == True,
            )
            .all()
        )
        roles_by_enrollment = {
            representative.enrollment_id: role_name(representative.position)
            for representative in representatives
        }

        enrollments = (
            session.query(Enrollment)
            .options(joinedload(Enrollment.student).joinedload(Student.user))
            .filter(Enrollment.section_id == section_id)
            .all()
        )

        students = []
        for enrollment in enrollments:
            user = enrollment.student.user if enrollment.student else None
            students.append({
                'enrollmentId': str(enrollment.id),
                'user': user_to_dict(user),
                'roleInSection': roles_by_enrollment.get(enrollment.id, 'estudiante'),
            })

        role_priority = {'delegado': 0, 'subdelegado': 1, 'estudiante': 2}
        students.sort(
            key=lambda item: (
                role_priority.get(item['roleInSection'], 2),
                item['user']['lastName'] if item['user'] else '',
            )
        )

        response = jsonify(api_response(
            'Contactos obtenidos correctamente',
            data={
                'docente': teacher_to_dict(section.teacher),
                'alumnos': students,
            },
        ))
    except Exception as e:
        traceback.print_exc()
        response = jsonify(api_response(
            'Error al obtener contactos',
            success=False,
            error=str(e),
        ))
        status = 500
    finally:
        session.close()
    return response, status
