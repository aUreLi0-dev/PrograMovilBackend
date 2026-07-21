import traceback
from datetime import timedelta
from flask_jwt_extended import create_access_token, get_jwt
from flask import Blueprint, request, session, jsonify, g
from apps.login.middlewares import jwt_required
from core.database import Session
from apps.login.application import REVOKED_TOKENS
from apps.models import AppUser as User
from apps.models import Student, Career, Specialty, StudentSpecialty
from core.text import clean_payload

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
            profile_data['student_id'] = student.id
            profile_data['career_id'] = student.career_id
            profile_data['curriculum_id'] = student.curriculum_id
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

        return jsonify(clean_payload({
            'message': 'Perfil obtenido exitosamente',
            'data': profile_data,
            'success': True,
            'error': None
        })), 200

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
