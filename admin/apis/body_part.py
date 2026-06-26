import traceback
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from main.models import User, BodyPart
from main.database import Session

api = Blueprint('admin_apis_body_part', __name__)

@api.route('/admin/apis/body-parts', methods=['GET'])
@jwt_required()
def fetch_all():
  # data
  response = None
  status = 200
  # blogic
  session = Session()
  try:
    body_parts = session.query(BodyPart).all()
    body_part_list = [body_part.to_dict() for body_part in body_parts]
    response = jsonify(body_part_list)
  except Exception as e:
    traceback.print_exc()
    response = jsonify({
      'message': 'Ocurrió un error en listar las partes del cuerpo',
      'error': str(e)
    })
    status = 500
  finally:
    session.close()
  # response
  return response, status

@api.route('/api/admin/users/<int:id>', methods=['GET'])
def fetch_one(id):
  # data
  response = None
  status = 200
  # blogic
  session = Session()
  try:
    user = session.query(User).filter_by(id=id).first()
    if user:
      response = jsonify(user.to_dict())
    else:
      response = jsonify({
        'message': 'Usuario no encontrado',
        'error': f'No hay usuario con el id: ${id}'
      })
      status = 404
  except Exception as e:
    traceback.print_exc()
    response = jsonify({
      'message': 'Ocurrió un error en ...',
      'error': str(e)
    })
    status = 500
  finally:
    session.close()
  # response
  return response, status

@api.route('/api/admin/users/<int:id>', methods=['DELETE'])
def delete_one(id):
  # data
  response = None
  status = 200
  # blogic
  session = Session()
  try:
    user = session.query(User).filter_by(id=id).first()
    if user:
      session.delete(user)
      session.commit()
      response = 'ok'
    else:
      response = jsonify({
        'message': 'Usuario no encontrado',
        'error': f'No hay usuario con el id: ${id}'
      })
  except Exception as e:
    traceback.print_exc()
    response = jsonify({
      'message': 'Ocurrió un error en ...',
      'error': str(e)
    })
    status = 500
  finally:
    session.close()
  # response
  return response, status

@api.route('/api/admin/users', methods=['POST'])
def create_one():
  # data
  response = None
  status = 200
  # blogic
  session = Session()
  try:
    session = Session()
    data = request.get_json()
    user = User(
      user_name = data['user_name'],
      password = data['password'],
      member_id = data['member_id']
    )
    # Agregar y confirmar la inserción en la base de datos
    session.add(user)
    session.commit()
    response = str(user.id)
  except Exception as e:
    traceback.print_exc()
    response = jsonify({
      'message': 'Ocurrió un error en ...',
      'error': str(e)
    })
    status = 500
  finally:
    session.close()
  # response
  return response, status

@api.route('/api/admin/users', methods=['PUT'])
def update_one():
  # data
  response = None
  status = 200
  # blogic
  session = Session()
  try:
    session = Session()
    data = request.get_json()
    user = session.query(User).filter_by(id=data['id']).first()
    if user:
      # Actualizar campos específicos
      user.user_name =  data['user_name']
      user.password =  data['password']
      user.member_id =  data['member_id']
      # Guardar los cambios
      session.commit()
      # Mostrar el registro actualizado
      response = '=)'
    else:
      response = jsonify({
        'message': 'Usuario no encontrado',
        'error': f'No hay usuario con el id: ${id}'
      })
  except Exception as e:
    traceback.print_exc()
    response = jsonify({
      'message': 'Ocurrió un error en ...',
      'error': str(e)
    })
    status = 500
  finally:
    session.close()
  # response
  return response, status
