import traceback
from datetime import datetime

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from sqlalchemy.orm import joinedload

from descripcion_cursos.apis.helpers import api_response, format_date, role_name
from descripcion_cursos.models import Announcement, AppUser, Enrollment, SectionRepresentative, Student
from main.database import Session

api = Blueprint('descripcion_cursos_announcement', __name__)


@api.route('/api/v1/descripcion-cursos/sections/<int:section_id>/announcements', methods=['GET'])
@jwt_required()
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


@api.route('/api/v1/descripcion-cursos/sections/<int:section_id>/announcements', methods=['POST'])
@jwt_required()
def create_announcement(section_id):
    response = None
    status = 201
    session = Session()
    try:
        data = request.get_json() or {}
        title = data.get('title') or data.get('titulo')
        message = data.get('message') or data.get('mensaje')
        author_code = data.get('authorCode') or data.get('autorCode') or get_jwt_identity()

        if not title or not message:
            response = jsonify(api_response(
                'Datos incompletos para crear anuncio',
                success=False,
                error='Los campos title/titulo y message/mensaje son obligatorios',
            ))
            status = 400
            return response, status

        representative = (
            session.query(SectionRepresentative)
            .join(Enrollment)
            .join(Student)
            .join(AppUser)
            .filter(
                SectionRepresentative.section_id == section_id,
                SectionRepresentative.is_active == True,
                AppUser.code == str(author_code),
            )
            .first()
        )

        if not representative:
            response = jsonify(api_response(
                'Representante no encontrado para la seccion',
                success=False,
                error='Solo un delegado o subdelegado activo puede crear anuncios en esta seccion',
            ))
            status = 403
            return response, status

        announcement = Announcement(
            section_representative_id=representative.id,
            title=title,
            message=message,
            published_at=datetime.now(),
            is_active=True,
        )
        session.add(announcement)
        session.commit()

        response = jsonify(api_response(
            'Anuncio creado correctamente',
            data={
                'id': str(announcement.id),
                'idSeccion': str(section_id),
                'titulo': announcement.title,
                'mensaje': announcement.message,
                'fecha': format_date(announcement.published_at),
                'autorCode': author_code,
                'autorRole': role_name(representative.position),
            },
        ))
    except Exception as e:
        session.rollback()
        traceback.print_exc()
        response = jsonify(api_response(
            'Error al crear anuncio',
            success=False,
            error=str(e),
        ))
        status = 500
    finally:
        session.close()
    return response, status
