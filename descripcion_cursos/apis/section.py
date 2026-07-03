import traceback

from flask import Blueprint, g, jsonify
from sqlalchemy.orm import joinedload

from login.middlewares import jwt_required
from descripcion_cursos.apis.helpers import (
    api_response,
    decimal_to_int,
)
from descripcion_cursos.models import (
    CourseOffering,
    Enrollment,
    Section,
    Student,
)
from core.database import Session

api = Blueprint('descripcion_cursos_section', __name__)


def _find_enrollment_for_section(session, section_id):
    # Busca la matricula del alumno autenticado en esta seccion.
    return (
        session.query(Enrollment)
        .join(Student)
        .filter(Enrollment.section_id == section_id)
        .filter(Student.user_id == g.user_id)
        .first()
    )


@api.route('/api/v1/descripcion-cursos/sections/<int:section_id>', methods=['GET'])
@jwt_required
def fetch_section_detail(section_id):
    response = None
    status = 200
    session = Session()
    try:
        # Trae la seccion con su docente y curso para armar el encabezado.
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
