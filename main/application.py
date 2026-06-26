# !/usr/bin/env python
# -*- coding: utf-8 -*-
from flask import Flask, jsonify
from flask_jwt_extended import JWTManager
from flask_session import Session

APP = Flask(
  __name__,
  static_folder='../static',
  static_url_path='/'
)

APP.config['SECRET_KEY'] = 'your_secret_key'
APP.config['SESSION_TYPE'] = 'filesystem'
APP.config['SESSION_PERMANENT'] = False
APP.config['SESSION_USE_SIGNER'] = True
APP.config['SESSION_KEY_PREFIX'] = 'session:'
APP.config['JWT_SECRET_KEY'] = 'tu_clave_secreta_aqui' 
Session(APP)

jwt = JWTManager(APP)

REVOKED_TOKENS = []

@jwt.token_in_blocklist_loader
def check_if_token_revoked(jwt_header, jwt_payload):
  jti = jwt_payload['jti']
  return jti in REVOKED_TOKENS

@jwt.unauthorized_loader
def unauthorized_response(callback):
  return jsonify({"error": "Acceso no autorizado. Debes proporcionar un token válido."}), 401

@jwt.expired_token_loader
def expired_token_response(jwt_header, jwt_payload):
  return jsonify({"error": "El token ha expirado. Por favor, inicia sesión nuevamente."}), 401

@jwt.invalid_token_loader
def invalid_token_response(reason):
  return jsonify({"error": "Token inválido o corrupto. Revisa tu autenticación."}), 401

@jwt.needs_fresh_token_loader
def needs_fresh_token_response(jwt_header, jwt_payload):
  return jsonify({"error": "Se requiere un token fresco. Vuelve a iniciar sesión."}), 401
