from flask import Blueprint, request, jsonify
from extensions import db, bcrypt
from models.user import User
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity

auth_bp = Blueprint('auth', __name__)

# Ruta para el registro de usuarios nuevos.
@auth_bp.route('/register', methods=['POST'])
@jwt_required()
def register():
    data = request.get_json()

    if not data or 'username' not in data or 'password' not in data:
        return jsonify({'error': 'Datos Invalidos'}), 400

    username = data['username']
    password = data['password']

    if User.query.filter_by(username=username).first():
        return jsonify({'error': 'El usuarui ya existe'}), 400

    user = User(username=username)
    user.set_password(password)

    db.session.add(user)
    db.session.commit()

    return jsonify({'message': 'Usuario Registrado correctamente'}), 201

# Ruta para realizar login en el sistema.
@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    username = data.get('username')
    password = data.get('password')

    # Verificar si existe usuario

    user = User.query.filter_by(username=username).first()

    if not user or not bcrypt.check_password_hash(user.password , password):
        return jsonify({'msg': 'Credenciales invalidos'}), 401

    # Crear token JWT
    access_token = create_access_token(identity=str(user.id))

    return jsonify({
        'msg': 'Login exitoso',
        'access_token': access_token
    })

@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def profile():
    user_id = int(get_jwt_identity())
    return {'msg': f'Bienvenido usuario {user_id}'}