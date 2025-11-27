#!/usr/bin/env python3
"""
predictor.py

Buscar alumno por cedula en la base de datos, construir el vector de features
(en el orden que necesita el modelo), cargar scaler + modelo y devolver JSON
con predicción y probabilidades.

Uso (CLI):
    python predictor.py 5123456

Uso desde Python:
    from predictor import predecir_por_cedula
    resultado = predecir_por_cedula("5123456")
"""

import sys
import os
import json
from typing import Dict, Any, List

# AÑADIR src al path para poder importar create_app y modelos
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "src")))

from app import create_app
from extensions import db
from models.models import Student, Subject, StudentSubject

import joblib
import numpy as np
import pandas as pd
from datetime import datetime

# -----------------------
# CONFIG
# -----------------------
CAREER = "Informatica"  # carrera por defecto
MODEL_NAME_VISIBLE = "K-Nearest Neighbors"  # nombre visible
MODEL_MAPPING = {
    "Regresión Logística": "regresion_logistica",
    "Árbol de Decisiones": "decision_tree",
    "Random Forest": "random_forest",
    "K-Nearest Neighbors": "knn",
    "SVM": "svm"
}

# Archivos esperados (puedes cambiar si tus rutas son distintas)
def normalized_career(career: str) -> str:
    c = career.lower().replace(" ", "_")
    c = c.replace("á", "a").replace("ó", "o").replace("é", "e").replace("í", "i").replace("ú","u")
    return c

NORMAL_CAREER = normalized_career(CAREER)
SCALER_FILENAME = f"scaler_{NORMAL_CAREER}.joblib"
MODEL_FILENAME = f"{NORMAL_CAREER}/modelo_{MODEL_MAPPING[MODEL_NAME_VISIBLE]}_alumnos_{NORMAL_CAREER}.joblib"

# Orden EXACTO de materias (53)
MATERIAS_EN_ORDEN: List[str] = [
"ADMINISTRACION Y MERCADOTECNIA",
"BASES DE DATOS I",
"BASES DE DATOS II",
"COMPUTACION I",
"COMPUTACION II",
"COMPUTACION III",
"CONTABILIDAD I",
"CALCULO I",
"CALCULO II",
"CALCULO III",
"DERECHO INTELECTUAL Y LABORAL",
"DISENO DE SISTEMA INFORMATICO I",
"DISENO TECNICO",
"ELECTRONICA I",
"EMPRENDEDORISMO",
"ESTRUCTURA DE DATOS I",
"ESTRUCTURAS DE LOS LENGUAJES",
"EVENTOS Y DEPORTES I",
"EVENTOS Y DEPORTES II",
"EVENTOS Y DEPORTES III",
"EVENTOS Y DEPORTES IV",
"EVENTOS Y DEPORTES V",
"EVENTOS Y DEPORTES VI",
"EXPRESION ORAL Y ESCRITA",
"FISICA I",
"FISICA II",
"FISICA III",
"GEOMETRIA ANALITICA Y VECTORIAL",
"IDIOMAS I",
"INFORMATICA I",
"INGENIERIA DE SOFTWARE I",
"INGLES II",
"INGLES III",
"INGLES I",
"INVESTIGACION DE OPERACIONES I",
"LABORATORIO DE IDIOMAS I",
"LABORATORIO I",
"LENGUAJE DE PROGRAMACION  I",
"LENGUAJE DE PROGRAMACION II",
"LENGUAJE DE PROGRAMACION IV",
"LENGUAJES DE PROGRAMACION III",
"MATEMATICA APLICADA",
"METODOLOGIA DE LA INVESTIGACION I",
"METODOS NUMERICOS",
"PROBABILIDADES Y ESTADISTICAS",
"QUIMICA",
"REDES DE COMPUTADORAS I",
"REDES DE COMPUTADORAS II",
"SISTEMAS OPERATIVOS I",
"SISTEMAS OPERATIVOS II",
"TALLER DE HARDWARE I",
"TALLER DE HARDWARE II",
"ALGEBRA I",
"ALGEBRA II",
"ETICA PROFESIONAL"
]

# -----------------------
# UTIL
# -----------------------
def human_state(state_int: int) -> str:
    mapping = {2: "Graduado", 3: "Deserción temprana", 4: "Deserción tardía"}
    return mapping.get(state_int, "Desconocido")

# -----------------------
# CARGA MODELO / SCALER
# -----------------------
def load_scaler(path: str = SCALER_FILENAME):
    if not os.path.isfile(path):
        raise FileNotFoundError(f"Scaler file no encontrado: {path}")
    return joblib.load(path)

def load_model(path: str = MODEL_FILENAME):
    if not os.path.isfile(path):
        raise FileNotFoundError(f"Modelo file no encontrado: {path}")
    return joblib.load(path)

# -----------------------
# CONVERSIÓN AL VECTOR DEL MODELO
# -----------------------
# Campos generales que esperamos en la tabla students (ordén definido)
GENERAL_FIELDS = ["estado_carrera", "tiempo_estudio", "ausencias", "cincoF", "aplazos", "promedio"]

def build_feature_vector(student: Student) -> List[float]:
    """
    Construye la lista de features en el orden esperado por el modelo:
    [estado_carrera, tiempo_estudio, ausencias, cincoF, aplazos, promedio,
     materia_1, materia_2, ..., materia_53]
    """
    # Verificar que student tenga los atributos generales
    missing = [f for f in GENERAL_FIELDS if not hasattr(student, f)]
    if missing:
        raise AttributeError(f"El registro Student no contiene los campos generales requeridos: {missing}. "
                             "Agregar esos campos a la tabla 'students' o ajusta este código.")

    vector = []
    # Agregar campos generales (en el orden)
    for f in GENERAL_FIELDS:
        val = getattr(student, f)
        if val is None:
            # Si hay None, usamos 0 como valor por defecto (puedes cambiar)
            val = 0
        vector.append(float(val))

    # Obtener diccionario de materias: nombre -> nota
    materias_dict = { ss.subject.nombre: ss.nota for ss in student.subjects }

    # Asegurar el orden exacto de las materias
    for materia in MATERIAS_EN_ORDEN:
        nota = materias_dict.get(materia)
        if nota is None:
            # si falta la materia, asumimos 0 (o podrías lanzar error)
            vector.append(0.0)
        else:
            vector.append(float(nota))

    return vector

# -----------------------
# PREDICIÓN PRINCIPAL
# -----------------------
def predecir_por_cedula(cedula: str, career: str = CAREER, model_visible_name: str = MODEL_NAME_VISIBLE) -> Dict[str, Any]:
    """
    Busca el alumno por cedula, construye vector, escala, predice y retorna JSON.
    """
    app = create_app()
    with app.app_context():
        alumno = Student.query.filter_by(cedula=str(cedula)).first()
        if alumno is None:
            raise ValueError(f"No se encontró alumno con cedula={cedula}")

        # Build vector
        vector = build_feature_vector(alumno)

    # Cargar scaler y modelo (fuera del contexto DB)
    # Aceptamos career pasado como argumento, pero por defecto usamos CAREER
    normalized = normalized_career(career)
    scaler_path = f"scaler_{normalized}.joblib"
    model_key = MODEL_MAPPING.get(model_visible_name)
    if model_key is None:
        raise ValueError(f"Modelo visible no reconocido: {model_visible_name}")
    model_path = f"{normalized}/modelo_{model_key}_alumnos_{normalized}.joblib"

    scaler = load_scaler(scaler_path)
    model = load_model(model_path)

    # Convertir a DataFrame/np.array para aplicar scaler
    X = np.array(vector).reshape(1, -1)
    if not hasattr(scaler, "mean_"):
        raise ValueError("Scaler cargado no parece estar ajustado (faltan atributos como mean_).")

    X_scaled = scaler.transform(X)

    # Predecir
    if hasattr(model, "predict_proba"):
        probabilities = model.predict_proba(X_scaled)[0]
    else:
        # Si el modelo no soporta predict_proba, devolver solo la predicción
        probabilities = None

    prediction_raw = model.predict(X_scaled)[0]

    # Construir output
    result: Dict[str, Any] = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "cedula": cedula,
        "nombre": f"{getattr(alumno, 'nombre', '')} {getattr(alumno, 'apellido', '')}".strip(),
        "prediccion_raw": int(prediction_raw) if isinstance(prediction_raw, (int, np.integer)) else str(prediction_raw),
        "prediccion_descripcion": human_state(int(prediction_raw)) if isinstance(prediction_raw, (int, np.integer)) else "Desconocido",
    }

    if probabilities is not None:
        # Mapear probabilidades a los labels del modelo (model.classes_)
        # Para obtener clases necesitamos inspeccionar model.classes_
        classes = getattr(model, "classes_", None)
        if classes is not None:
            prob_map = {}
            for cls, prob in zip(classes, probabilities):
                prob_map[str(cls)] = float(round(prob, 6))
            result["probabilidades_por_clase"] = prob_map

            # También, presentar como % legible y con descripción si coincide con los números esperados
            readable = {}
            for cls, prob in zip(classes, probabilities):
                readable[human_state(int(cls))] = float(round(prob * 100, 2))
            result["probabilidades_legible_por_estado_pct"] = readable

        else:
            result["probabilidades"] = [float(round(float(p), 6)) for p in probabilities]

    return result

# -----------------------
# CLI
# -----------------------
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python predictor.py <cedula> [<career>]")
        sys.exit(1)

    ced = sys.argv[1]
    career_arg = sys.argv[2] if len(sys.argv) >= 3 else CAREER

    try:
        salida = predecir_por_cedula(ced, career=career_arg)
        print(json.dumps(salida, indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(2)
