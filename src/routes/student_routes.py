from flask import Blueprint, request, jsonify
from extensions import db
from models.models import Student, Subject, StudentSubject

student_bp = Blueprint("students", __name__)


@student_bp.route("/students/create", methods=["POST"])
def create_student():
    data = request.get_json()

    try:
        # Validar campos mínimos
        required = ["nombre", "apellido", "cedula", "estado", "sexo", "materias"]
        for r in required:
            if r not in data:
                return jsonify({"error": f"Falta el campo obligatorio: {r}"}), 400

        # Validar sexo (1=Masculino, 2=Femenino)
        if data["sexo"] not in [1, 2]:
            return jsonify({"error": "El campo 'sexo' debe ser 1 (Masculino) o 2 (Femenino)"}), 400

        # Validar cedula duplicada
        if Student.query.filter_by(cedula=data["cedula"]).first():
            return jsonify({"error": "Ya existe un alumno con esta cedula"}), 400

        # Crear alumno
        student = Student(
            nombre=data["nombre"],
            apellido=data["apellido"],
            cedula=data["cedula"],
            estado=data["estado"],
            sexo=data["sexo"],        # ← AGREGADO
            estado_carrera=data.get("estado_carrera", 0),
            tiempo_estudio=data.get("tiempo_estudio", 0),
            ausencias=data.get("ausencias", 0),
            cinco_f=data.get("cinco_f", 0),
            aplazos=data.get("aplazos", 0),
            promedio=data.get("promedio", 0)
        )
        db.session.add(student)
        db.session.flush()  # para obtener student.id

        # Materias (diccionario)
        materias_dict = data["materias"]

        # Obtener todas las materias existentes
        subjects_db = {s.nombre: s.id for s in Subject.query.all()}

        # Validar que no falten materias
        for materia in materias_dict:
            if materia not in subjects_db:
                return jsonify({"error": f"La materia '{materia}' no existe en BD"}), 400

        # Insertar StudentSubject
        for materia, nota in materias_dict.items():
            ss = StudentSubject(
                student_id=student.id,
                subject_id=subjects_db[materia],
                nota=nota
            )
            db.session.add(ss)

        db.session.commit()

        return jsonify({"message": "Alumno creado con éxito", "id": student.id}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

from flask import Blueprint, request, jsonify
from extensions import db
from models.models import Student, Subject, StudentSubject

student_bp = Blueprint("students", __name__)

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
