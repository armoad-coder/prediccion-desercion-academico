import os
import sys
import numpy as np
import joblib
from extensions import db
from models.models import Student, StudentSubject
from datetime import datetime

# ================================
# DEBUG (prints en consola)
# ================================
DEBUG = True
def log(msg):
    if DEBUG:
        print(f"[PREDICTOR DEBUG] {msg}")

# ================================
# CONSTANTES
# ================================

MATERIAS_EN_ORDEN_CSV = [
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
    "LENGUAJE DE PROGRAMACION I",
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

BASE_PATH = os.path.join("src", "utils")
SCALER_PATH = os.path.join(BASE_PATH, "scaler_informatica.joblib")
MODEL_PATH  = os.path.join(BASE_PATH, "modelo_informatica_regresion.joblib")

# ================================
# UTILS
# ================================

def human_state(state_int):
    mapping = {2: "Graduado", 3: "Deserción temprana", 4: "Deserción tardía"}
    return mapping.get(state_int, "Desconocido")


def load_scaler_and_model():
    log(f"Cargando scaler desde: {SCALER_PATH}")
    log(f"Cargando modelo desde: {MODEL_PATH}")

    if not os.path.isfile(SCALER_PATH):
        raise FileNotFoundError(f"No existe el scaler en: {SCALER_PATH}")

    if not os.path.isfile(MODEL_PATH):
        raise FileNotFoundError(f"No existe el modelo en: {MODEL_PATH}")

    scaler = joblib.load(SCALER_PATH)
    modelo = joblib.load(MODEL_PATH)

    log("Scaler y modelo cargados correctamente.")
    return scaler, modelo


def build_feature_vector_interfaz_style(student):
    log(f"Construyendo vector para alumno ID={student.id} ({student.nombre})")

    vector = []

    # Campos generales
    vector.append(float(getattr(student, "sexo", 2)))
    vector.append(float(student.estado_carrera))
    vector.append(float(student.tiempo_estudio))
    vector.append(float(student.ausencias))
    vector.append(float(student.cinco_f))
    vector.append(float(student.aplazos))
    vector.append(float(student.promedio))

    # Materias en orden EXACTO
    materias_dict = {ss.subject.nombre: ss.nota for ss in student.subjects}

    for materia in MATERIAS_EN_ORDEN_CSV:
        vector.append(float(materias_dict.get(materia, 0)))

    log(f"Vector construido con {len(vector)} features.")
    print(vector)
    return vector

# ================================
# FUNCIÓN PRINCIPAL
# ================================

def predecir_por_cedula(cedula):
    log(f"Buscando alumno con cédula: {cedula}")

    alumno = Student.query.filter_by(cedula=str(cedula)).first()

    if not alumno:
        log("Alumno no encontrado.")
        return {"error": f"No existe alumno con cedula {cedula}"}, 404

    log(f"Alumno encontrado: {alumno.nombre} {alumno.apellido}")

    # Construcción vector
    vector = build_feature_vector_interfaz_style(alumno)
    X = np.array(vector).reshape(1, -1)

    # Cargar scaler y modelo
    scaler, modelo = load_scaler_and_model()

    # Escalar
    log("Escalando vector...")
    X_scaled = scaler.transform(X)
    print(X_scaled)

    # Predicción
    log("Ejecutando predicción...")
    pred_raw = modelo.predict(X_scaled)[0]  
    print(pred_raw)

    # Probabilidades
    probas_map = None
    result_text = ""

    state_mapping = {2: "Graduado", 3: "Deserción temprana", 4: "Deserción tardía"}

    if hasattr(modelo, "predict_proba"):
        probas = modelo.predict_proba(X_scaled)[0]
        clases = modelo.classes_

        probas_map = {}

        result_text += "El alumno tiene las siguientes probabilidades:\n"

        for cls, prob in zip(clases, probas):

            # Convertir clase safely ("2.0" → 2)
            cls_int = int(float(cls))

            estado_desc = state_mapping.get(cls_int, "Desconocido")
            percentage = round(prob * 100, 2)

            result_text += f"- {estado_desc}: {percentage}%\n"

            probas_map[str(cls_int)] = float(prob)

        # Predicción final
        pred_int = int(float(pred_raw))
        pred_desc = state_mapping.get(pred_int, "Desconocido")
        result_text += f"\nPredicción final: El estado más probable es {pred_desc}.\n"

    print(result_text)

    # Datos de materias
    materias_dict = {ss.subject.nombre: ss.nota for ss in alumno.subjects}

    resultado = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "alumno": {
            "id": alumno.id,
            "nombre": alumno.nombre,
            "apellido": alumno.apellido,
            "cedula": alumno.cedula,
            "estado_carrera": alumno.estado_carrera,
            "tiempo_estudio": alumno.tiempo_estudio,
            "ausencias": alumno.ausencias,
            "cinco_F": alumno.cinco_f,
            "aplazos": alumno.aplazos,
            "promedio": alumno.promedio,
            "sexo": alumno.sexo
        },
        "materias": {
            materia: float(materias_dict.get(materia, 0))
            for materia in MATERIAS_EN_ORDEN_CSV
        },
        "prediccion": {
            "estado": int(float(pred_raw)),
            "descripcion": human_state(int(float(pred_raw))),
            "probabilidades": probas_map,
            "texto": result_text
        }
    }

    log(f"Predicción final enviada.")
    return resultado, 200
