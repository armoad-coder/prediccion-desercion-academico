from flask import Blueprint, jsonify
from services.predictor_service import predecir_por_cedula

predict_bp = Blueprint("predict", __name__)


@predict_bp.route("/predict/<cedula>", methods=["GET"])
def predict_by_cedula(cedula):
    resultado, status = predecir_por_cedula(cedula)
    return jsonify(resultado), status
