import traceback
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from core.database import Session
from notas.models import Career, Specialty, Student, StudentSpecialty

api = Blueprint('notas_career_setup', __name__)

@api.route('/api/v1/careers', methods=['GET'])
@jwt_required()
def get_careers():
    response = None
    status = 200
    session = Session()
    try:
        careers = session.query(Career).all()
        careers_list = []
        for c in careers:
            careers_list.append({
                'id': c.id,
                'code': c.code,
                'name': c.name,
                'faculty': c.faculty,
                'is_active': True
            })
        
        response = jsonify({
            'message': 'lista de carreras',
            'data': careers_list,
            'success': True,
            'error': None
        })
    except Exception as e:
        traceback.print_exc()
        response = jsonify({
            'message': 'Error al obtener carreras',
            'error': str(e),
            'data': None,
            'success': False
        })
        status = 500
    finally:
        session.close()
    return response, status

@api.route('/api/v1/specialties', methods=['GET'])
@jwt_required()
def get_specialties():
    response = None
    status = 200
    session = Session()
    try:
        career_id = request.args.get('career_id', type=int)
        query = session.query(Specialty)
        if career_id is not None:
            query = query.filter_by(career_id=career_id)
        
        specialties = query.all()
        
        specialties_list = []
        for s in specialties:
            specialties_list.append({
                'id': s.id,
                'carrera_id': s.career_id,
                'name': s.name,
                'description': s.description,
                'display_order': s.id,
                'is_active': s.is_active
            })
            
        response = jsonify({
            'message': 'lista de especialidades',
            'data': specialties_list,
            'success': True,
            'error': None
        })
    except Exception as e:
        traceback.print_exc()
        response = jsonify({
            'message': 'Error al obtener especialidades',
            'error': str(e),
            'data': None,
            'success': False
        })
        status = 500
    finally:
        session.close()
    return response, status

@api.route('/api/v1/students/<int:student_id>/setup-career', methods=['POST'])
@jwt_required()
def setup_career(student_id):
    response = None
    status = 200
    session = Session()
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'message': 'Petición inválida, JSON requerido',
                'success': False,
                'error': 'Bad Request',
                'data': None
            }), 400

        career_id = data.get('career_id')
        specialty_ids = data.get('specialty_ids', [])

        if not career_id:
            return jsonify({
                'message': 'El campo career_id es obligatorio',
                'success': False,
                'error': 'Bad Request',
                'data': None
            }), 400

        student = session.query(Student).filter_by(id=student_id).first()
        if not student:
            return jsonify({
                'message': 'Estudiante no encontrado',
                'success': False,
                'error': 'Not Found',
                'data': None
            }), 404

        career = session.query(Career).filter_by(id=career_id).first()
        if not career:
            return jsonify({
                'message': 'Carrera especificada no existe',
                'success': False,
                'error': 'Not Found',
                'data': None
            }), 404

        student.career_id = career_id
        student.specialty_setup_completed = True

        session.query(StudentSpecialty).filter_by(student_id=student_id).delete()

        for spec_id in specialty_ids:
            spec = session.query(Specialty).filter_by(id=spec_id).first()
            if spec:
                student_spec = StudentSpecialty(
                    student_id=student_id,
                    specialty_id=spec_id,
                    selection_type='interest',
                    is_active=True
                )
                session.add(student_spec)

        session.commit()

        response = jsonify({
            'message': 'Configuración de carrera guardada con éxito',
            'success': True,
            'data': None,
            'error': None
        })
    except Exception as e:
        session.rollback()
        traceback.print_exc()
        response = jsonify({
            'message': 'Error al guardar la configuración de carrera',
            'error': str(e),
            'data': None,
            'success': False
        })
        status = 500
    finally:
        session.close()
    return response, status
