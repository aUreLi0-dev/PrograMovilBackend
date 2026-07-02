import traceback
from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from sqlalchemy.orm import joinedload
from core.database import Session
from notas.models import (
    Enrollment, Student, Section, CourseOffering, Course,
    Teacher, ScheduleSession, StudentScore
)

api = Blueprint('notas_schedule', __name__)

DAYS_MAP = {
    1: 'Lunes',
    2: 'Martes',
    3: 'Miércoles',
    4: 'Jueves',
    5: 'Viernes',
    6: 'Sábado',
    7: 'Domingo'
}

def format_time(time_obj):
    if not time_obj:
        return ""
    return time_obj.strftime("%I:%M %p").lower()

def get_section_average(session, section_id):
    enrollments = session.query(Enrollment).filter_by(section_id=section_id).all()
    student_averages = []
    for enr in enrollments:
        scores = session.query(StudentScore).filter_by(enrollment_id=enr.id).all()
        weighted_sum = 0
        total_weight = 0
        for s in scores:
            if s.value is not None and s.assessment:
                weighted_sum += float(s.value) * float(s.assessment.weight)
                total_weight += float(s.assessment.weight)
        if total_weight > 0:
            student_averages.append(weighted_sum / total_weight)
    
    if student_averages:
        return round(sum(student_averages) / len(student_averages), 1)
    return 15.0

@api.route('/api/v1/students/<int:student_id>/schedule', methods=['GET'])
@jwt_required()
def get_student_schedule(student_id):
    response = None
    status = 200
    session = Session()
    try:
        student = session.query(Student).filter_by(id=student_id).first()
        if not student:
            return jsonify({
                'message': 'Estudiante no encontrado',
                'success': False,
                'error': 'Not Found',
                'data': None
            }), 404

        # Query all active enrollments for the student
        enrollments = session.query(Enrollment).options(
            joinedload(Enrollment.section).joinedload(Section.course_offering).joinedload(CourseOffering.course),
            joinedload(Enrollment.section).joinedload(Section.teacher)
        ).filter_by(student_id=student_id, status='active').all()

        secciones_list = []
        for enr in enrollments:
            section = enr.section
            if not section:
                continue
            
            course_offering = section.course_offering
            course = course_offering.course if course_offering else None
            teacher = section.teacher
            
            # Fetch schedule sessions for this section
            schedule_sessions = session.query(ScheduleSession).filter_by(section_id=section.id).all()
            
            horarios_list = []
            primary_color = "#2196F3" # default blue
            
            for sess in schedule_sessions:
                if sess.color_hex:
                    primary_color = sess.color_hex
                horarios_list.append({
                    'dia': DAYS_MAP.get(sess.day_of_week, 'Lunes'),
                    'hora_inicio': format_time(sess.start_time),
                    'hora_fin': format_time(sess.end_time),
                    'salon': sess.classroom or '',
                    'color': sess.color_hex or primary_color
                })

            promedio = get_section_average(session, section.id)

            secciones_list.append({
                'idSeccion': section.code, # e.g. "IS-856"
                'codigoSeccion': section.code.split('-')[-1] if '-' in section.code else section.code,
                'idCurso': str(course.id) if course else "",
                'curso': course.name if course else "",
                'color': primary_color,
                'docenteCode': teacher.teacher_code if teacher else "",
                'promedioSeccion': promedio,
                'asistido': float(enr.attended_hours),
                'inasistencia': float(enr.absent_hours),
                'total': float(enr.total_hours),
                'horarios': horarios_list
            })

        response = jsonify({
            'message': 'Horario del estudiante',
            'data': {
                'secciones': secciones_list
            },
            'success': True,
            'error': None
        })
    except Exception as e:
        traceback.print_exc()
        response = jsonify({
            'message': 'Error al obtener el horario del estudiante',
            'error': str(e),
            'data': None,
            'success': False
        })
        status = 500
    finally:
        session.close()
    return response, status
