import traceback

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from sqlalchemy.orm import joinedload

from descripcion_cursos.apis.helpers import (
    api_response,
    decimal_to_float,
    decimal_to_int,
)
from descripcion_cursos.models import (
    AppUser,
    CourseOffering,
    Enrollment,
    Section,
    Student,
    StudentScore,
    Syllabus,
)
from main.database import Session

api = Blueprint('descripcion_cursos_section', __name__)


def _find_enrollment_for_section(session, section_id):
    student_code = request.args.get('student_code') or get_jwt_identity()
    enrollment = None

    if student_code:
        enrollment = (
            session.query(Enrollment)
            .join(Student)
            .join(AppUser)
            .filter(
                Enrollment.section_id == section_id,
                AppUser.code == str(student_code),
            )
            .first()
        )

    if enrollment:
        return enrollment

    student_id = request.args.get('student_id')
    if student_id:
        enrollment = (
            session.query(Enrollment)
            .filter(
                Enrollment.section_id == section_id,
                Enrollment.student_id == student_id,
            )
            .first()
        )

    if enrollment:
        return enrollment

    return (
        session.query(Enrollment)
        .filter(Enrollment.section_id == section_id)
        .order_by(Enrollment.id.asc())
        .first()
    )


def _calculate_section_average(session, section):
    syllabus = (
        session.query(Syllabus)
        .filter(Syllabus.course_offering_id == section.course_offering_id)
        .first()
    )
    if not syllabus:
        return 0.0

    scores = (
        session.query(StudentScore)
        .join(Enrollment)
        .filter(
            Enrollment.section_id == section.id,
            StudentScore.value.isnot(None),
        )
        .all()
    )
    if not scores:
        return 0.0

    values = [decimal_to_float(score.value) for score in scores if score.value is not None]
    if not values:
        return 0.0
    return round(sum(values) / len(values), 2)


@api.route('/api/v1/descripcion-cursos/sections/<int:section_id>', methods=['GET'])
@jwt_required()
def fetch_section_detail(section_id):
    response = None
    status = 200
    session = Session()
    try:
        section = (
            session.query(Section)
            .options(
                joinedload(Section.teacher),
                joinedload(Section.course_offering).joinedload(CourseOffering.course),
            )
            .filter(Section.id == section_id)
            .first()
        )

        if not section:
            response = jsonify(api_response(
                'Seccion no encontrada',
                error=f'No hay seccion con id: {section_id}',
                success=False,
            ))
            status = 404
            return response, status

        enrollment = _find_enrollment_for_section(session, section_id)
        course = section.course_offering.course if section.course_offering else None

        data = {
            'idSeccion': str(section.id),
            'codigoSeccion': section.code,
            'docenteCode': section.teacher.teacher_code if section.teacher else None,
            'promedioSeccion': _calculate_section_average(session, section),
            'idCurso': str(course.id) if course else None,
            'curso': course.name if course else 'Sin curso',
            'asistido': decimal_to_int(enrollment.attended_hours) if enrollment else 0,
            'inasistencia': decimal_to_int(enrollment.absent_hours) if enrollment else 0,
            'total': decimal_to_int(enrollment.total_hours) if enrollment else 0,
            'enrollmentId': str(enrollment.id) if enrollment else None,
            'enrollmentStatus': enrollment.status if enrollment else None,
        }

        response = jsonify(api_response(
            'Detalle de seccion obtenido correctamente',
            data=data,
        ))
    except Exception as e:
        traceback.print_exc()
        response = jsonify(api_response(
            'Error al obtener detalle de seccion',
            success=False,
            error=str(e),
        ))
        status = 500
    finally:
        session.close()
    return response, status
