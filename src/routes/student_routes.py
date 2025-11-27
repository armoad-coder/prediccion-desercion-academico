from flask import Blueprint, request, jsonify
from extensions import db
from models.models import Student, Subject, StudentSubject
import pandas as pd
from sqlalchemy.exc import IntegrityError
from config import MATERIAS_EN_ORDEN_CSV
from flask import current_app


student_bp = Blueprint("students", __name__)


@student_bp.route("/students/create", methods=["POST"])
def create_student():
    data = request.get_json()
    return create_student_from_dict(data)

@student_bp.route("/students/bulk_create", methods=["POST"])
def bulk_create_students():
    data = request.get_json()

    if not isinstance(data, list):
        return jsonify({"error": "Debes enviar una lista de alumnos"}), 400

    # Mapa de materias en BD
    subjects_db = {s.nombre: s.id for s in Subject.query.all()}

    resultados = []
    insertados = 0
    fallos = 0

    try:
        for alumno in data:

            cedula = alumno.get("cedula")
            materias = alumno.get("materias", {})

            # Validaciones mínimas
            if Student.query.filter_by(cedula=cedula).first():
                resultados.append({
                    "cedula": cedula,
                    "estado": "fallo",
                    "error": "Alumno ya existe en base de datos"
                })
                fallos += 1
                continue

            faltantes = [m for m in materias.keys() if m not in subjects_db]
            if faltantes:
                resultados.append({
                    "cedula": cedula,
                    "estado": "fallo",
                    "error": f"Materias inexistentes: {faltantes}"
                })
                fallos += 1
                continue

            # Crear alumno
            student = Student(
                nombre=alumno.get("nombre"),
                apellido=alumno.get("apellido"),
                cedula=cedula,
                sexo=alumno.get("sexo"),
                estado_carrera=alumno.get("estado_carrera"),
                tiempo_estudio=alumno.get("tiempo_estudio"),
                ausencias=alumno.get("ausencias"),
                cinco_f=alumno.get("cinco_f"),
                aplazos=alumno.get("aplazos"),
                promedio=alumno.get("promedio")
            )
            db.session.add(student)
            db.session.flush()  # obtener ID

            # Insertar sus materias
            for materia, nota in materias.items():
                db.session.add(StudentSubject(
                    student_id=student.id,
                    subject_id=subjects_db[materia],
                    nota=nota
                ))

            resultados.append({
                "cedula": cedula,
                "estado": "ok"
            })
            insertados += 1

        db.session.commit()

    except Exception as e:
        db.session.rollback()
        return jsonify({
            "error": "Error general en la carga masiva",
            "detalle": str(e)
        }), 500

    return jsonify({
        "insertados": insertados,
        "fallos": fallos,
        "detalles": resultados
    }), 201

def create_student_from_dict(data):
    try:
        # Validaciones mínimas
        required = ["nombre", "apellido", "cedula", "estado", "sexo", "materias"]
        for r in required:
            if r not in data:
                return {"error": f"Falta el campo obligatorio: {r}"}, 400

        if data["sexo"] not in [1, 2]:
            return {"error": "El campo 'sexo' debe ser 1 (Masculino) o 2 (Femenino)"}, 400

        # Verificar duplicado
        if Student.query.filter_by(cedula=data["cedula"]).first():
            return {"error": "Ya existe un alumno con esta cedula"}, 400

        # Crear alumno
        student = Student(
            nombre=data["nombre"],
            apellido=data["apellido"],
            cedula=data["cedula"],
            estado=data["estado"],
            sexo=data["sexo"],
            estado_carrera=data.get("estado_carrera", 0),
            tiempo_estudio=data.get("tiempo_estudio", 0),
            ausencias=data.get("ausencias", 0),
            cinco_f=data.get("cinco_f", 0),
            aplazos=data.get("aplazos", 0),
            promedio=data.get("promedio", 0)
        )
        db.session.add(student)
        db.session.flush()

        # Materias
        subjects_db = {s.nombre: s.id for s in Subject.query.all()}

        for materia, nota in data["materias"].items():
            if materia not in subjects_db:
                return {"error": f"La materia '{materia}' no existe en BD"}, 400

            db.session.add(StudentSubject(
                student_id=student.id,
                subject_id=subjects_db[materia],
                nota=nota
            ))

        db.session.commit()
        return {"message": "Alumno creado con éxito", "id": student.id}, 201

    except Exception as e:
        db.session.rollback()
        return {"error": str(e)}, 500

@student_bp.route("/students/bulk_csv", methods=["POST"])
def bulk_csv():
    try:
        if "file" not in request.files:
            return jsonify({"error": "No se envió ningún archivo CSV en 'file'"}), 400

        file = request.files["file"]
        df = pd.read_csv(file, sep=";")
        base_cols = [
            "sexo", "estado_carrera", "tiempo_estudio",
            "ausencias", "cinco_f", "aplazos", "promedio"
        ]

        materias = MATERIAS_EN_ORDEN_CSV
        columnas_necesarias = base_cols + materias
        # Crear columnas faltantes con 0
        for col in columnas_necesarias:
            if col not in df.columns:
                df[col] = 0

        resultados = []
        insertados = 0

        for index, row in df.iterrows():

            # Cedula
            if "IDAlumno" in df.columns:
                cedula = str(row["IDAlumno"])
            else:
                cedula = f"{index}"

            nombre = f"Alumno{cedula}"
            apellido = "Test"

            # Construir dict de materias con valores reales
            materias_dict = {}
            for m in materias:
                val = row.get(m, 0)
                if pd.isna(val):
                    val = 0
                materias_dict[m] = float(val)

            data = {
                "nombre": nombre,
                "apellido": apellido,
                "cedula": cedula,
                "estado": int(row.get("Estado", 1)),
                "sexo": int(row.get("Sexo", 1)),
                "materias": materias_dict,
                "estado_carrera": int(row.get("Estado_Carrera", 0)),
                "tiempo_estudio": int(row.get("TiempoEstudio", 0)),
                "ausencias": int(row.get("Ausencias", 0)),
                "cinco_f": int(row.get("CincoF", 0)),
                "aplazos": int(row.get("aplazos", 0)),
                "promedio": float(row.get("Promedio", 0))
            }

            resp_json, status = create_student_from_dict(data)

            resultados.append({
                "cedula": cedula,
                "status": status,
                "resultado": resp_json
            })

            if status == 201:
                insertados += 1

        return jsonify({
            "message": "Carga finalizada",
            "insertados": insertados,
            "resultados": resultados
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

