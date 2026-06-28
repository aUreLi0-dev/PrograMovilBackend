import traceback
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from main.database import Session
from notas.models import StudentScore

api = Blueprint('notas_student_score', __name__)

@api.route('/api/v1/student-scores', methods=['GET'])
@jwt_required()
def fetch_all():
    response = None
    status = 200
    session = Session()
    try:
        query = session.query(StudentScore)
        enrollment_id = request.args.get('enrollment_id')
        assessment_id = request.args.get('assessment_id')
        if enrollment_id:
            query = query.filter_by(enrollment_id=enrollment_id)
        if assessment_id:
            query = query.filter_by(assessment_id=assessment_id)
        items = query.all()
        response = jsonify([item.to_dict() for item in items])
    except Exception as e:
        traceback.print_exc()
        response = jsonify({'message': 'Error al listar notas', 'error': str(e)})
        status = 500
    finally:
        session.close()
    return response, status

@api.route('/api/v1/student-scores/<int:id>', methods=['GET'])
@jwt_required()
def fetch_one(id):
    response = None
    status = 200
    session = Session()
    try:
        item = session.query(StudentScore).filter_by(id=id).first()
        if item:
            response = jsonify(item.to_dict())
        else:
            response = jsonify({'message': 'Nota no encontrada', 'error': f'No hay nota con id: {id}'})
            status = 404
    except Exception as e:
        traceback.print_exc()
        response = jsonify({'message': 'Error al obtener nota', 'error': str(e)})
        status = 500
    finally:
        session.close()
    return response, status

@api.route('/api/v1/student-scores', methods=['POST'])
@jwt_required()
def create_or_update():
    response = None
    status = 200
    session = Session()
    try:
        data = request.get_json()
        existing = session.query(StudentScore).filter_by(
            enrollment_id=data['enrollment_id'],
            assessment_id=data['assessment_id']
        ).first()
        if existing:
            existing.value = data.get('value', existing.value)
            session.commit()
            response = jsonify(existing.to_dict())
        else:
            item = StudentScore(
                enrollment_id=data['enrollment_id'],
                assessment_id=data['assessment_id'],
                value=data.get('value')
            )
            session.add(item)
            session.commit()
            response = jsonify(item.to_dict())
            status = 201
    except Exception as e:
        traceback.print_exc()
        response = jsonify({'message': 'Error al crear/actualizar nota', 'error': str(e)})
        status = 500
    finally:
        session.close()
    return response, status

@api.route('/api/v1/student-scores', methods=['PUT'])
@jwt_required()
def update_one():
    response = None
    status = 200
    session = Session()
    try:
        data = request.get_json()
        item = session.query(StudentScore).filter_by(id=data['id']).first()
        if item:
            item.value = data.get('value', item.value)
            session.commit()
            response = jsonify(item.to_dict())
        else:
            response = jsonify({'message': 'Nota no encontrada', 'error': f'No hay nota con id: {data["id"]}'})
            status = 404
    except Exception as e:
        traceback.print_exc()
        response = jsonify({'message': 'Error al actualizar nota', 'error': str(e)})
        status = 500
    finally:
        session.close()
    return response, status

@api.route('/api/v1/student-scores/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_one(id):
    response = None
    status = 200
    session = Session()
    try:
        item = session.query(StudentScore).filter_by(id=id).first()
        if item:
            session.delete(item)
            session.commit()
            response = jsonify({'message': 'Nota eliminada correctamente'})
        else:
            response = jsonify({'message': 'Nota no encontrada', 'error': f'No hay nota con id: {id}'})
            status = 404
    except Exception as e:
        traceback.print_exc()
        response = jsonify({'message': 'Error al eliminar nota', 'error': str(e)})
        status = 500
    finally:
        session.close()
    return response, status
