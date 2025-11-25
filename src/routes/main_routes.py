from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
@jwt_required()
def home():
    return jsonify({'message': 'Bienvenido a la API Flask'})

@main_bp.route('/status')
@jwt_required()
def status():
    return jsonify({'status': 'OK', 'app': 'Flask API Funcionando'})