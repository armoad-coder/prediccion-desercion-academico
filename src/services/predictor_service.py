import os
import sys
import numpy as np
import joblib
from extensions import db
from models.models import Student, StudentSubject
from datetime import datetime


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



FEATURES_EN_ORDEN = [
    "Sexo",
    "Estado_Carrera",
    "TiempoEstudio",
    "Ausencias",
    "CincoF",
    "aplazos",
    "Promedio",
] + MATERIAS_EN_ORDEN_CSV

# GENERAL_FIELDS = [
#    "sexo",
#   "estado_carrera",
#   "tiempo_estudio",
#   "ausencias",
#   "cinco_f",
#   "aplazos",
#   "promedio"
#]

def human_state(state_int):
    mapping = {2: "Graduado", 3: "Deserción temprana", 4: "Deserción tardía"}
    return mapping.get(state_int, "Desconocido")

BASE_PATH = os.path.join("src", "utils")

SCALER_PATH = os.path.join(BASE_PATH, "scaler_informatica.joblib")
MODEL_PATH  = os.path.join(BASE_PATH, "modelo_informatica_regresion.joblib")

def load_scaler_and_model():
    """Carga del scaler y modelo para Informática desde utils/."""

    if not os.path.isfile(SCALER_PATH):
        raise FileNotFoundError(f"No existe el scaler en: {SCALER_PATH}")

    if not os.path.isfile(MODEL_PATH):
        raise FileNotFoundError(f"No existe el modelo en: {MODEL_PATH}")

    scaler = joblib.load(SCALER_PATH)
    modelo = joblib.load(MODEL_PATH)

    print(list(scaler.feature_names_in_))

    return scaler, modelo


def build_feature_vector_interfaz_style(student):
    """
    Construye el vector exactamente igual al que genera interfaz.py.
    SIN IDAlumno, SIN Estado.
    """

    vector = []


    # 1. Sexo
    sexo = getattr(student, "sexo", 2)  # por defecto masculino
    vector.append(float(sexo))

    # 2. Estado_Carrera
    vector.append(float(student.estado_carrera))

    # 3. TiempoEstudio
    vector.append(float(student.tiempo_estudio))

    # 4. Ausencias
    vector.append(float(student.ausencias))

    # 5. CincoF
    vector.append(float(student.cinco_f))

    # 6. Aplazos
    vector.append(float(student.aplazos))

    # 7. Promedio
    vector.append(float(student.promedio))

    # 8. Materias (55 en orden EXACTO del CSV)
    materias_dict = {ss.subject.nombre: ss.nota for ss in student.subjects}
    print(materias_dict)
    for materia in MATERIAS_EN_ORDEN_CSV:
        vector.append(float(materias_dict.get(materia, 0)))
    print(vector)
    print(len(vector))
    return vector


def predecir_por_cedula(cedula):
    """Función principal llamada desde el endpoint."""
    
    alumno = Student.query.filter_by(cedula=str(cedula)).first()

    if not alumno:
        return {"error": f"No existe alumno con cedula {cedula}"}, 404

def predecir_por_cedula(cedula):
    """Función principal llamada desde el endpoint."""
    
    alumno = Student.query.filter_by(cedula=str(cedula)).first()

    if not alumno:
        return {"error": f"No existe alumno con cedula {cedula}"}, 404

    # Convertir a vector
    vector = build_feature_vector_interfaz_style(alumno)
    X = np.array(vector).reshape(1, -1)

    # Cargar scaler + modelo
    scaler, modelo = load_scaler_and_model()
    X_scaled = scaler.transform(X)
    # Predicción
    pred_raw = modelo.predict(X_scaled)[0]

    # Probabilidades (si existen)
    if hasattr(modelo, "predict_proba"):
        probas = modelo.predict_proba(X_scaled)[0]
        clases = modelo.classes_
        probas_map = {str(cls): float(probas[i]) for i, cls in enumerate(clases)}
    else:
        probas_map = None

    # Orden correcto de materias como en el CSV
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
            "estado": int(pred_raw),
            "descripcion": human_state(int(pred_raw)),
            "probabilidades": probas_map
        }
    }

    return resultado, 200
