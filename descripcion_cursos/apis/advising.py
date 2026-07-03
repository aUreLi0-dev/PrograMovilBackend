import traceback

from flask import Blueprint, jsonify
from sqlalchemy import or_
from sqlalchemy.orm import joinedload

from login.middlewares import jwt_required
from descripcion_cursos.apis.helpers import (
    api_response,
    day_name,
    format_time,
    teacher_to_dict,
)
from descripcion_cursos.models import CourseAdvisingSession, Section
from core.database import Session

api = Blueprint('descripcion_cursos_advising', __name__)


@api.route('/api/v1/descripcion-cursos/sections/<int:section_id>/advising', methods=['GET'])
@jwt_required
def fetch_advising_sessions(section_id):
    response = None
    status = 200
    session = Session()
    try:
        # Valida que la seccion exista
        section = session.query(Section).filter(Section.id == section_id).first()
        if not section:
            response = jsonify(api_response(
                'Seccion no encontrada',
                success=False,
                error=f'No hay seccion con id: {section_id}',
            ))
            status = 404
            return response, status

        # Busca las asesorias del curso y las especificas de esta seccion
        sessions = (
            session.query(CourseAdvisingSession)
            .options(joinedload(CourseAdvisingSession.teacher))
            .filter(
                CourseAdvisingSession.course_offering_id == section.course_offering_id,
                or_(
                    CourseAdvisingSession.section_id == section_id,
                    CourseAdvisingSession.section_id.is_(None),
                ),
            )
            .order_by(
                CourseAdvisingSession.day_of_week.asc(),
                CourseAdvisingSession.start_time.asc(),
            )
            .all()
        )

        data = []
        for item in sessions:
            data.append({
                'id': str(item.id),
                'courseId': str(section.course_offering.course_id),
                'docenteCode': item.teacher.teacher_code if item.teacher else '',
                'docente': teacher_to_dict(item.teacher),
                'dia': day_name(item.day_of_week),
                'inicio': format_time(item.start_time),
                'fin': format_time(item.end_time),
                'aula': item.classroom or '',
                'zoom': item.meeting_url or '',
                'modality': item.modality,
                'note': item.note,
            })

        response = jsonify(api_response(
            'Asesorias obtenidas correctamente',
            data=data,
        ))
    except Exception as e:
        traceback.print_exc()
        response = jsonify(api_response(
            'Error al obtener asesorias',
            success=False,
            error=str(e),
        ))
        status = 500
    finally:
        session.close()
    return response, status
