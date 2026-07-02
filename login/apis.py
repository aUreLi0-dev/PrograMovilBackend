import traceback
from datetime import timedelta
from flask_jwt_extended import create_access_token, get_jwt
from flask import Blueprint, request, session, jsonify, g
from login.middlewares import jwt_required
from core.database import Session
from login.application import REVOKED_TOKENS
from login.models import User
from notas.models import Student, Career, Specialty, StudentSpecialty

api = Blueprint('main_apis', __name__)

@api.route('/api/sign-in', methods=["POST"])
def sign_in():
    data = request.get_json()

    if not data:
        return jsonify({
            'message': 'Debe enviar un JSON válido',
            'data': None,
            'success': False,
            'error': 'Bad Request'
        }), 400

    username = data.get('code')
    password = data.get('password')

    if not username or not password:
        return jsonify({
            'message': 'code y password son obligatorios',
            'data': None,
            'success': False,
            'error': 'Missing required fields'
        }), 400

    db_session = Session()

    try:
        user = (
            db_session.query(User)
            .filter(
                User.code == username,
                User.password_hash == password
            )
            .first()
        )

        if not user:
            return jsonify({
                'message': 'Código o contraseña incorrectos',
                'data': None,
                'success': False,
                'error': 'Unauthorized'
            }), 401

        expires = timedelta(minutes=300)
        access_token = create_access_token(
            identity=username,
            additional_claims={
                "user_id": user.id
            }
        )

        session['status'] = True
        session['user'] = user.to_dict()

        return jsonify({
            'message': 'Login exitoso',
            'data': {
                'user': user.to_dict(),
                'jwt': access_token
            },
            'success': True,
            'error': None
        }), 200

    except Exception as e:
        traceback.print_exc()
        return jsonify({
            'message': 'Ocurrió un error durante el login',
            'data': None,
            'success': False,
            'error': str(e)
        }), 500

    finally:
        db_session.close()

@api.route('/api/sign-out', methods=['GET'])
@jwt_required
def signout():
    jti = get_jwt()["jti"]
    REVOKED_TOKENS.append(jti)
    session.clear()
    return jsonify({
        'message': 'Sesión cerrada exitosamente',
        'data': None,
        'success': True,
        'error': None
    }), 200

@api.route('/api/me', methods=['GET'])
@jwt_required
def profile():
    db_session = Session()
    try:
        user = db_session.query(User).filter(User.id == g.user_id).first()
        if not user:
            return jsonify({
                'message': 'Usuario no encontrado',
                'data': None,
                'success': False,
                'error': 'Not Found'
            }), 404

        student = db_session.query(Student).filter(Student.user_id == user.id).first()

        profile_data = user.to_dict()
        profile_data.pop('password_hash', None)

        if student:
            career = db_session.query(Career).filter(Career.id == student.career_id).first()
            profile_data['career'] = career.to_dict() if career else None
            profile_data['current_level'] = student.current_level
            profile_data['specialty_setup_completed'] = student.specialty_setup_completed

            specialties = (
                db_session.query(Specialty)
                .join(StudentSpecialty, StudentSpecialty.specialty_id == Specialty.id)
                .filter(
                    StudentSpecialty.student_id == student.id,
                    StudentSpecialty.is_active == True
                )
                .all()
            )
            profile_data['especialidades'] = [s.to_dict() for s in specialties]

        return jsonify({
            'message': 'Perfil obtenido exitosamente',
            'data': profile_data,
            'success': True,
            'error': None
        }), 200

    except Exception as e:
        traceback.print_exc()
        return jsonify({
            'message': 'Ocurrió un error al obtener el perfil',
            'data': None,
            'success': False,
            'error': str(e)
        }), 500

    finally:
        db_session.close()

@api.route('/api/me/setup', methods=['PUT'])
@jwt_required
def setup():
    data = request.get_json()

    if not data:
        return jsonify({
            'message': 'Debe enviar un JSON válido',
            'data': None,
            'success': False,
            'error': 'Bad Request'
        }), 400

    career_id = data.get('career_id')
    especialidades = data.get('especialidades', [])

    if not career_id:
        return jsonify({
            'message': 'career_id es obligatorio',
            'data': None,
            'success': False,
            'error': 'Missing required fields'
        }), 400

    db_session = Session()
    try:
        user = db_session.query(User).filter(User.id == g.user_id).first()
        if not user:
            return jsonify({
                'message': 'Usuario no encontrado',
                'data': None,
                'success': False,
                'error': 'Not Found'
            }), 404

        student = db_session.query(Student).filter(Student.user_id == user.id).first()
        if not student:
            return jsonify({
                'message': 'Estudiante no encontrado',
                'data': None,
                'success': False,
                'error': 'Not Found'
            }), 404

        career = db_session.query(Career).filter(Career.id == career_id).first()
        if not career:
            return jsonify({
                'message': 'Carrera no encontrada',
                'data': None,
                'success': False,
                'error': 'Not Found'
            }), 404

        student.career_id = career_id
        student.specialty_setup_completed = True
        student.current_level = data.get('current_level', student.current_level)

        db_session.query(StudentSpecialty).filter(
            StudentSpecialty.student_id == student.id,
            StudentSpecialty.is_active == True
        ).update({'is_active': False})

        for esp_id in especialidades:
            ss = StudentSpecialty(
                student_id=student.id,
                specialty_id=esp_id,
                selection_type='interest',
                is_active=True
            )
            db_session.add(ss)

        db_session.commit()

        return jsonify({
            'message': 'Setup completado exitosamente',
            'data': {'setup_complete': True},
            'success': True,
            'error': None
        }), 200

    except Exception as e:
        db_session.rollback()
        traceback.print_exc()
        return jsonify({
            'message': 'Ocurrió un error al guardar el setup',
            'data': None,
            'success': False,
            'error': str(e)
        }), 500

    finally:
        db_session.close()

@api.route('/api/me/especialidades', methods=['PUT'])
@jwt_required
def update_especialidades():
    data = request.get_json()

    if not data or 'especialidades' not in data:
        return jsonify({
            'message': 'Debe enviar un JSON con la lista de especialidades',
            'data': None,
            'success': False,
            'error': 'Bad Request'
        }), 400

    especialidades = data['especialidades']

    db_session = Session()
    try:
        user = db_session.query(User).filter(User.id == g.user_id).first()
        if not user:
            return jsonify({
                'message': 'Usuario no encontrado',
                'data': None,
                'success': False,
                'error': 'Not Found'
            }), 404

        student = db_session.query(Student).filter(Student.user_id == user.id).first()
        if not student:
            return jsonify({
                'message': 'Estudiante no encontrado',
                'data': None,
                'success': False,
                'error': 'Not Found'
            }), 404

        db_session.query(StudentSpecialty).filter(
            StudentSpecialty.student_id == student.id,
            StudentSpecialty.is_active == True
        ).update({'is_active': False})

        for esp_id in especialidades:
            ss = StudentSpecialty(
                student_id=student.id,
                specialty_id=esp_id,
                selection_type='interest',
                is_active=True
            )
            db_session.add(ss)

        db_session.commit()

        return jsonify({
            'message': 'Especialidades actualizadas exitosamente',
            'data': None,
            'success': True,
            'error': None
        }), 200

    except Exception as e:
        db_session.rollback()
        traceback.print_exc()
        return jsonify({
            'message': 'Ocurrió un error al actualizar especialidades',
            'data': None,
            'success': False,
            'error': str(e)
        }), 500

    finally:
        db_session.close()

@api.route('/api/comments', methods=['GET'])
def comments():
  comments = [
    {
      'guest': 'Juan Pérez',
      'date': '10 de julio, 2023',
      'comment': 'Un lugar maravilloso para visitar con la familia. ¡Las vistas son impresionantes y el personal muy amable!'
    },
    {
      'guest': 'Ana Gómez',
      'date': '15 de julio, 2023',
      'comment': '¡Absolutamente recomendado! Un excelente lugar para desconectar y disfrutar de la naturaleza.'
    },
    {
      'guest': 'Carlos Ruiz',
      'date': '20 de julio, 2023',
      'comment': 'Muy organizado, limpio y lleno de actividades para todas las edades. Sin duda volveremos.'
    },
  ]
  return jsonify(comments)

@api.route('/api/v1/demo')
def demo():
  return '<h1>Bienvenido a la api de demo</h1>'
