import traceback
from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from sqlalchemy.orm import joinedload
from core.database import Session
from notas.models import (
    Enrollment, Student, Assessment, StudentScore, Course,
    CourseOffering, Section, Syllabus
)

api = Blueprint('notas_calculator', __name__)

def calcular_promedio(scores_data):
    peso_total = 0
    suma_ponderada = 0
    for item in scores_data:
        if item['value'] is not None:
            peso_total += item['weight']
            suma_ponderada += item['value'] * item['weight']
    if peso_total > 0:
        promedio = round(suma_ponderada / peso_total, 2)
    else:
        promedio = None
    return promedio, peso_total, suma_ponderada

@api.route('/api/v1/calculator/student/<int:student_id>/courses', methods=['GET'])
@jwt_required()
def student_courses(student_id):
    response = None
    status = 200
    session = Session()
    try:
        student = session.query(Student).filter_by(id=student_id).first()
        if not student:
            return jsonify({'message': 'Estudiante no encontrado'}), 404

        enrollments = session.query(Enrollment).options(
            joinedload(Enrollment.section).joinedload(Section.course_offering).joinedload(CourseOffering.course),
            joinedload(Enrollment.scores)
        ).filter(Enrollment.student_id == student_id).all()

        results = []
        for enrollment in enrollments:
            course_offering = enrollment.section.course_offering
            course = course_offering.course

            syllabus = session.query(Syllabus).filter_by(
                course_offering_id=course_offering.id
            ).first()

            assessments = []
            if syllabus:
                assessments = session.query(Assessment).filter_by(
                    syllabus_id=syllabus.id
                ).all()

            scores_map = {s.assessment_id: s.value for s in enrollment.scores}

            scores_data = []
            for a in assessments:
                value = scores_map.get(a.id)
                scores_data.append({
                    'assessment_id': a.id,
                    'assessment_name': a.name,
                    'assessment_code': a.code,
                    'weight': float(a.weight),
                    'value': float(value) if value is not None else None
                })

            promedio, peso_total, _ = calcular_promedio(scores_data)

            results.append({
                'enrollment_id': enrollment.id,
                'enrollment_status': enrollment.status,
                'course': {
                    'id': course.id,
                    'code': course.code,
                    'name': course.name,
                    'default_credit': course.default_credit
                },
                'section_code': enrollment.section.code,
                'academic_period_code': course_offering.academic_period.code if course_offering.academic_period else None,
                'assesments_count': len(assessments),
                'scored_count': sum(1 for s in scores_data if s['value'] is not None),
                'weighted_average': promedio,
                'total_weight': peso_total
            })

        return jsonify({
            'student_id': student_id,
            'student_name': student.user.full_name if student.user else None,
            'courses': results
        })

    except Exception as e:
        traceback.print_exc()
        response = jsonify({'message': 'Error al obtener cursos del estudiante', 'error': str(e)})
        status = 500
    finally:
        session.close()
    return response, status

@api.route('/api/v1/calculator/course-offering/<int:offering_id>/student/<int:student_id>', methods=['GET'])
@jwt_required()
def student_course_detail(offering_id, student_id):
    response = None
    status = 200
    session = Session()
    try:
        student = session.query(Student).filter_by(id=student_id).first()
        if not student:
            return jsonify({'message': 'Estudiante no encontrado'}), 404

        course_offering = session.query(CourseOffering).options(
            joinedload(CourseOffering.course),
            joinedload(CourseOffering.academic_period)
        ).filter_by(id=offering_id).first()

        if not course_offering:
            return jsonify({'message': 'Oferta de curso no encontrada'}), 404

        section = session.query(Section).filter_by(
            course_offering_id=offering_id
        ).first()

        if not section:
            return jsonify({'message': 'No hay sección para esta oferta de curso'}), 404

        enrollment = session.query(Enrollment).options(
            joinedload(Enrollment.scores)
        ).filter_by(
            student_id=student_id,
            section_id=section.id
        ).first()

        if not enrollment:
            return jsonify({'message': 'El estudiante no está matriculado en este curso'}), 404

        syllabus = session.query(Syllabus).filter_by(
            course_offering_id=offering_id
        ).first()

        assessments = []
        if syllabus:
            assessments = session.query(Assessment).options(
                joinedload(Assessment.assessment_type)
            ).filter_by(syllabus_id=syllabus.id).all()

        scores_map = {s.assessment_id: float(s.value) if s.value is not None else None for s in enrollment.scores}

        scores_data = []
        for a in assessments:
            value = scores_map.get(a.id)
            scores_data.append({
                'assessment_id': a.id,
                'assessment_code': a.code,
                'assessment_name': a.name,
                'assessment_type': a.assessment_type.name if a.assessment_type else None,
                'week_number': a.week_number,
                'weight': float(a.weight),
                'value': value
            })

        promedio, peso_total, suma_ponderada = calcular_promedio(scores_data)

        return jsonify({
            'student': {
                'id': student.id,
                'full_name': student.user.full_name if student.user else None,
                'code': student.user.code if student.user else None
            },
            'course': {
                'id': course_offering.course.id,
                'code': course_offering.course.code,
                'name': course_offering.course.name,
                'credit': course_offering.course.default_credit
            },
            'academic_period': course_offering.academic_period.code if course_offering.academic_period else None,
            'section_code': section.code,
            'enrollment_status': enrollment.status,
            'syllabus_title': syllabus.title if syllabus else None,
            'assesments': scores_data,
            'summary': {
                'total_assessments': len(assessments),
                'scored': sum(1 for s in scores_data if s['value'] is not None),
                'missing': sum(1 for s in scores_data if s['value'] is None),
                'total_weight': peso_total,
                'sum_weighted': round(suma_ponderada, 2),
                'weighted_average': promedio
            }
        })

    except Exception as e:
        traceback.print_exc()
        response = jsonify({'message': 'Error al obtener detalle del curso', 'error': str(e)})
        status = 500
    finally:
        session.close()
    return response, status

@api.route('/api/v1/calculator/enrollment/<int:enrollment_id>', methods=['GET'])
@jwt_required()
def enrollment_detail(enrollment_id):
    response = None
    status = 200
    session = Session()
    try:
        enrollment = session.query(Enrollment).options(
            joinedload(Enrollment.student).joinedload(Student.user),
            joinedload(Enrollment.section).joinedload(Section.course_offering).joinedload(CourseOffering.course),
            joinedload(Enrollment.section).joinedload(Section.course_offering).joinedload(CourseOffering.academic_period),
            joinedload(Enrollment.scores)
        ).filter_by(id=enrollment_id).first()

        if not enrollment:
            return jsonify({'message': 'Matrícula no encontrada'}), 404

        course_offering = enrollment.section.course_offering

        syllabus = session.query(Syllabus).filter_by(
            course_offering_id=course_offering.id
        ).first()

        assessments = []
        if syllabus:
            assessments = session.query(Assessment).options(
                joinedload(Assessment.assessment_type)
            ).filter_by(syllabus_id=syllabus.id).all()

        scores_map = {s.assessment_id: float(s.value) if s.value is not None else None for s in enrollment.scores}

        scores_data = []
        for a in assessments:
            value = scores_map.get(a.id)
            scores_data.append({
                'assessment_id': a.id,
                'assessment_code': a.code,
                'assessment_name': a.name,
                'assessment_type': a.assessment_type.name if a.assessment_type else None,
                'week_number': a.week_number,
                'weight': float(a.weight),
                'value': value
            })

        promedio, peso_total, suma_ponderada = calcular_promedio(scores_data)

        return jsonify({
            'enrollment_id': enrollment.id,
            'student': {
                'id': enrollment.student.id,
                'full_name': enrollment.student.user.full_name if enrollment.student.user else None,
                'code': enrollment.student.user.code if enrollment.student.user else None
            },
            'course': {
                'id': course_offering.course.id,
                'code': course_offering.course.code,
                'name': course_offering.course.name
            },
            'section_code': enrollment.section.code,
            'academic_period': course_offering.academic_period.code if course_offering.academic_period else None,
            'enrollment_status': enrollment.status,
            'attendance': {
                'attended_hours': float(enrollment.attended_hours),
                'absent_hours': float(enrollment.absent_hours),
                'total_hours': float(enrollment.total_hours)
            },
            'assesments': scores_data,
            'summary': {
                'total_assessments': len(assessments),
                'scored': sum(1 for s in scores_data if s['value'] is not None),
                'missing': sum(1 for s in scores_data if s['value'] is None),
                'total_weight': peso_total,
                'sum_weighted': round(suma_ponderada, 2),
                'weighted_average': promedio
            }
        })

    except Exception as e:
        traceback.print_exc()
        response = jsonify({'message': 'Error al obtener detalle de matrícula', 'error': str(e)})
        status = 500
    finally:
        session.close()
    return response, status
