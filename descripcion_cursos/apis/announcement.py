import traceback

from flask import Blueprint, jsonify
from sqlalchemy.orm import joinedload

from login.middlewares import jwt_required
from descripcion_cursos.apis.helpers import api_response, format_date, role_name
from descripcion_cursos.models import Announcement, Enrollment, SectionRepresentative, Student
from core.database import Session

api = Blueprint('descripcion_cursos_announcement', __name__)


@api.route('/api/v1/descripcion-cursos/sections/<int:section_id>/announcements', methods=['GET'])
@jwt_required
def fetch_announcements(section_id):
    response = None
    status = 200
    session = Session()
    try:
        announcements = (
            session.query(Announcement)
            .join(SectionRepresentative)
            .options(
                joinedload(Announcement.section_representative)
                .joinedload(SectionRepresentative.enrollment)
                .joinedload(Enrollment.student)
                .joinedload(Student.user)
            )
            .filter(
                SectionRepresentative.section_id == section_id,
                Announcement.is_active == True,
            )
            .order_by(Announcement.published_at.desc())
            .all()
        )

        data = []
        for announcement in announcements:
            representative = announcement.section_representative
            enrollment = representative.enrollment if representative else None
            student = enrollment.student if enrollment else None
            user = student.user if student else None

            data.append({
                'id': str(announcement.id),
                'idSeccion': str(section_id),
                'titulo': announcement.title,
                'mensaje': announcement.message,
                'fecha': format_date(announcement.published_at),
                'autorCode': user.code if user else '',
                'autorName': user.full_name if user else '',
                'autorRole': role_name(representative.position if representative else None),
            })

        response = jsonify(api_response(
            'Anuncios obtenidos correctamente',
            data=data,
        ))
    except Exception as e:
        traceback.print_exc()
        response = jsonify(api_response(
            'Error al obtener anuncios',
            success=False,
            error=str(e),
        ))
        status = 500
    finally:
        session.close()
    return response, status
