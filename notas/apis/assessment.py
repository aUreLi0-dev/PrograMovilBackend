import traceback
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from core.database import Session
from notas.models import Assessment

api = Blueprint('notas_assessment', __name__)

@api.route('/api/v1/assessments', methods=['GET'])
@jwt_required()
def fetch_all():
    response = None
    status = 200
    session = Session()
    try:
        query = session.query(Assessment)
        syllabus_id = request.args.get('syllabus_id')
        if syllabus_id:
            query = query.filter_by(syllabus_id=syllabus_id)
        items = query.all()
        response = jsonify([item.to_dict() for item in items])
    except Exception as e:
        traceback.print_exc()
        response = jsonify({'message': 'Error al listar evaluaciones', 'error': str(e)})
        status = 500
    finally:
        session.close()
    return response, status

@api.route('/api/v1/assessments/<int:id>', methods=['GET'])
@jwt_required()
def fetch_one(id):
    response = None
    status = 200
    session = Session()
    try:
        item = session.query(Assessment).filter_by(id=id).first()
        if item:
            response = jsonify(item.to_dict())
        else:
            response = jsonify({'message': 'Evaluación no encontrada', 'error': f'No hay evaluación con id: {id}'})
            status = 404
    except Exception as e:
        traceback.print_exc()
        response = jsonify({'message': 'Error al obtener evaluación', 'error': str(e)})
        status = 500
    finally:
        session.close()
    return response, status

@api.route('/api/v1/assessments', methods=['POST'])
@jwt_required()
def create_one():
    response = None
    status = 200
    session = Session()
    try:
        data = request.get_json()
        item = Assessment(
            syllabus_id=data['syllabus_id'],
            assessment_type_id=data['assessment_type_id'],
            code=data['code'],
            name=data['name'],
            week_number=data['week_number'],
            weight=data['weight']
        )
        session.add(item)
        session.commit()
        response = jsonify(item.to_dict())
        status = 201
    except Exception as e:
        traceback.print_exc()
        response = jsonify({'message': 'Error al crear evaluación', 'error': str(e)})
        status = 500
    finally:
        session.close()
    return response, status

@api.route('/api/v1/assessments', methods=['PUT'])
@jwt_required()
def update_one():
    response = None
    status = 200
    session = Session()
    try:
        data = request.get_json()
        item = session.query(Assessment).filter_by(id=data['id']).first()
        if item:
            item.syllabus_id = data.get('syllabus_id', item.syllabus_id)
            item.assessment_type_id = data.get('assessment_type_id', item.assessment_type_id)
            item.code = data.get('code', item.code)
            item.name = data.get('name', item.name)
            item.week_number = data.get('week_number', item.week_number)
            item.weight = data.get('weight', item.weight)
            session.commit()
            response = jsonify(item.to_dict())
        else:
            response = jsonify({'message': 'Evaluación no encontrada', 'error': f'No hay evaluación con id: {data["id"]}'})
            status = 404
    except Exception as e:
        traceback.print_exc()
        response = jsonify({'message': 'Error al actualizar evaluación', 'error': str(e)})
        status = 500
    finally:
        session.close()
    return response, status

@api.route('/api/v1/assessments/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_one(id):
    response = None
    status = 200
    session = Session()
    try:
        item = session.query(Assessment).filter_by(id=id).first()
        if item:
            session.delete(item)
            session.commit()
            response = jsonify({'message': 'Evaluación eliminada correctamente'})
        else:
            response = jsonify({'message': 'Evaluación no encontrada', 'error': f'No hay evaluación con id: {id}'})
            status = 404
    except Exception as e:
        traceback.print_exc()
        response = jsonify({'message': 'Error al eliminar evaluación', 'error': str(e)})
        status = 500
    finally:
        session.close()
    return response, status
