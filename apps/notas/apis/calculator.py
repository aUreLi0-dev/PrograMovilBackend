import traceback
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from sqlalchemy.orm import joinedload
from core.database import Session
from apps.models import (
    Enrollment, Student, Assessment, SimulatedGrade,
    Course, CourseOffering, Section, Syllabus
)

api = Blueprint('notas_calculator', __name__)


def ok(data, message='OK'):
    return jsonify({'success': True, 'data': data, 'message': message, 'error': None})


def fail(message, error=None, status=400):
    return jsonify({'success': False, 'data': None, 'message': message, 'error': error}), status


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
    session = Session()
    try:
        student = session.query(Student).filter_by(id=student_id).first()
        if not student:
            return fail('Estudiante no encontrado', status=404)

        enrollments = session.query(Enrollment).options(
            joinedload(Enrollment.section).joinedload(Section.course_offering).joinedload(CourseOffering.course),
            joinedload(Enrollment.section).joinedload(Section.course_offering).joinedload(CourseOffering.academic_period)
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

            simulated = session.query(SimulatedGrade).filter_by(
                enrollment_id=enrollment.id
            ).all()
            sim_map = {s.assessment_id: s.value for s in simulated}

            scores_data = []
            for a in assessments:
                value = sim_map.get(a.id)
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

        return ok({
            'student_id': student_id,
            'student_name': student.user.full_name if student.user else None,
            'courses': results
        })

    except Exception as e:
        traceback.print_exc()
        return fail('Error al obtener cursos del estudiante', str(e), 500)
    finally:
        session.close()


@api.route('/api/v1/calculator/enrollment/<int:enrollment_id>', methods=['GET'])
@jwt_required()
def enrollment_detail(enrollment_id):
    session = Session()
    try:
        enrollment = session.query(Enrollment).options(
            joinedload(Enrollment.student).joinedload(Student.user),
            joinedload(Enrollment.section).joinedload(Section.course_offering).joinedload(CourseOffering.course),
            joinedload(Enrollment.section).joinedload(Section.course_offering).joinedload(CourseOffering.academic_period)
        ).filter_by(id=enrollment_id).first()

        if not enrollment:
            return fail('Matrícula no encontrada', status=404)

        course_offering = enrollment.section.course_offering

        syllabus = session.query(Syllabus).filter_by(
            course_offering_id=course_offering.id
        ).first()

        assessments = []
        if syllabus:
            assessments = session.query(Assessment).options(
                joinedload(Assessment.assessment_type)
            ).filter_by(syllabus_id=syllabus.id).all()

        simulated = session.query(SimulatedGrade).filter_by(
            enrollment_id=enrollment.id
        ).all()
        sim_map = {s.assessment_id: s for s in simulated}

        scores_data = []
        for a in assessments:
            sim = sim_map.get(a.id)
            value = float(sim.value) if sim and sim.value is not None else None
            scores_data.append({
                'assessment_id': a.id,
                'assessment_code': a.code,
                'assessment_name': a.name,
                'assessment_type': a.assessment_type.name if a.assessment_type else None,
                'week_number': a.week_number,
                'weight': float(a.weight),
                'value': value,
                'simulated_grade_id': sim.id if sim else None
            })

        promedio, peso_total, suma_ponderada = calcular_promedio(scores_data)

        return ok({
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
                'attended_hours': float(enrollment.attended_hours) if enrollment.attended_hours else 0,
                'absent_hours': float(enrollment.absent_hours) if enrollment.absent_hours else 0,
                'total_hours': float(enrollment.total_hours) if enrollment.total_hours else 0
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
        return fail('Error al obtener detalle de matrícula', str(e), 500)
    finally:
        session.close()


@api.route('/api/v1/calculator/simulated-grades', methods=['GET'])
@jwt_required()
def list_simulated_grades():
    session = Session()
    try:
        query = session.query(SimulatedGrade)
        enrollment_id = request.args.get('enrollment_id', type=int)
        if enrollment_id:
            query = query.filter_by(enrollment_id=enrollment_id)
        items = query.all()
        return ok([item.to_dict() for item in items])
    except Exception as e:
        traceback.print_exc()
        return fail('Error al listar notas simuladas', str(e), 500)
    finally:
        session.close()


@api.route('/api/v1/calculator/simulated-grades', methods=['POST'])
@jwt_required()
def upsert_simulated_grade():
    session = Session()
    try:
        data = request.get_json()
        if not data:
            return fail('JSON requerido', 'Bad Request')

        enrollment_id = data.get('enrollment_id')
        assessment_id = data.get('assessment_id')
        value = data.get('value')

        if not enrollment_id or not assessment_id:
            return fail('enrollment_id y assessment_id son obligatorios')

        if value is not None and (not isinstance(value, (int, float)) or value < 0 or value > 20):
            return fail('value debe ser un número entre 0 y 20')

        enrollment = session.query(Enrollment).filter_by(id=enrollment_id).first()
        if not enrollment:
            return fail('Matrícula no encontrada', status=404)

        assessment = session.query(Assessment).filter_by(id=assessment_id).first()
        if not assessment:
            return fail('Evaluación no encontrada', status=404)

        existing = session.query(SimulatedGrade).filter_by(
            enrollment_id=enrollment_id,
            assessment_id=assessment_id
        ).first()

        if existing:
            existing.value = value
            session.commit()
            return ok(existing.to_dict(), 'Nota simulada actualizada')
        else:
            item = SimulatedGrade(
                enrollment_id=enrollment_id,
                assessment_id=assessment_id,
                value=value
            )
            session.add(item)
            session.commit()
            return ok(item.to_dict(), 'Nota simulada creada'), 201

    except Exception as e:
        session.rollback()
        traceback.print_exc()
        return fail('Error al crear/actualizar nota simulada', str(e), 500)
    finally:
        session.close()


@api.route('/api/v1/calculator/simulated-grades/<int:grade_id>', methods=['DELETE'])
@jwt_required()
def delete_simulated_grade(grade_id):
    session = Session()
    try:
        item = session.query(SimulatedGrade).filter_by(id=grade_id).first()
        if not item:
            return fail('Nota simulada no encontrada', status=404)

        session.delete(item)
        session.commit()
        return ok(None, 'Nota simulada eliminada correctamente')

    except Exception as e:
        session.rollback()
        traceback.print_exc()
        return fail('Error al eliminar nota simulada', str(e), 500)
    finally:
        session.close()
