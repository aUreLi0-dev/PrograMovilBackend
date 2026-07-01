import traceback
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from core.database import Session
from notas.models import AssessmentType

api = Blueprint('notas_assessment_type', __name__)

@api.route('/api/v1/assessment-types', methods=['GET'])
@jwt_required()
def fetch_all():
    response = None
    status = 200
    session = Session()
    try:
        items = session.query(AssessmentType).all()
        response = jsonify([item.to_dict() for item in items])
    except Exception as e:
        traceback.print_exc()
        response = jsonify({'message': 'Error al listar tipos de evaluación', 'error': str(e)})
        status = 500
    finally:
        session.close()
    return response, status

@api.route('/api/v1/assessment-types/<int:id>', methods=['GET'])
@jwt_required()
def fetch_one(id):
    response = None
    status = 200
    session = Session()
    try:
        item = session.query(AssessmentType).filter_by(id=id).first()
        if item:
            response = jsonify(item.to_dict())
        else:
            response = jsonify({'message': 'Tipo de evaluación no encontrado', 'error': f'No hay tipo con id: {id}'})
            status = 404
    except Exception as e:
        traceback.print_exc()
        response = jsonify({'message': 'Error al obtener tipo de evaluación', 'error': str(e)})
        status = 500
    finally:
        session.close()
    return response, status

@api.route('/api/v1/assessment-types', methods=['POST'])
@jwt_required()
def create_one():
    response = None
    status = 200
    session = Session()
    try:
        data = request.get_json()
        item = AssessmentType(
            name=data['name'],
            abbreviation=data.get('abbreviation'),
            description=data.get('description')
        )
        session.add(item)
        session.commit()
        response = jsonify(item.to_dict())
        status = 201
    except Exception as e:
        traceback.print_exc()
        response = jsonify({'message': 'Error al crear tipo de evaluación', 'error': str(e)})
        status = 500
    finally:
        session.close()
    return response, status

@api.route('/api/v1/assessment-types', methods=['PUT'])
@jwt_required()
def update_one():
    response = None
    status = 200
    session = Session()
    try:
        data = request.get_json()
        item = session.query(AssessmentType).filter_by(id=data['id']).first()
        if item:
            item.name = data.get('name', item.name)
            item.abbreviation = data.get('abbreviation', item.abbreviation)
            item.description = data.get('description', item.description)
            session.commit()
            response = jsonify(item.to_dict())
        else:
            response = jsonify({'message': 'Tipo de evaluación no encontrado', 'error': f'No hay tipo con id: {data["id"]}'})
            status = 404
    except Exception as e:
        traceback.print_exc()
        response = jsonify({'message': 'Error al actualizar tipo de evaluación', 'error': str(e)})
        status = 500
    finally:
        session.close()
    return response, status

@api.route('/api/v1/assessment-types/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_one(id):
    response = None
    status = 200
    session = Session()
    try:
        item = session.query(AssessmentType).filter_by(id=id).first()
        if item:
            session.delete(item)
            session.commit()
            response = jsonify({'message': 'Tipo de evaluación eliminado correctamente'})
        else:
            response = jsonify({'message': 'Tipo de evaluación no encontrado', 'error': f'No hay tipo con id: {id}'})
            status = 404
    except Exception as e:
        traceback.print_exc()
        response = jsonify({'message': 'Error al eliminar tipo de evaluación', 'error': str(e)})
        status = 500
    finally:
        session.close()
    return response, status
