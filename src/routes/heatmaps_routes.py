from flask import Blueprint, jsonify, request
from extensions import db
from models.models import Student, Subject, StudentSubject

heatmaps_bp = Blueprint('api', __name__)

# Definimos el mapeo de materias según el JSON que aprobaste
# IMPORTANTE: Los nombres deben ser idénticos a los de la base de datos
MATERIAS_POR_SEMESTRE = {
    "1": [
        "COMPUTACION I", "ELECTRONICA I", "FISICA I", "ALGEBRA I",
        "CALCULO I", "GEOMETRIA ANALITICA Y VECTORIAL", "DISENO TECNICO",
        "QUIMICA", "INGLES I", "EVENTOS Y DEPORTES I"
    ],
    "2": [
        "COMPUTACION II", "INFORMATICA I", "LABORATORIO I", "FISICA II",
        "CACLCULO II", "ALGEBRA II", "ADMINISTRACION Y MERCADOTECNIA",
        "INGLES II", "EVENTOS Y DEPORTES II"
    ]
}

@heatmaps_bp.route('/api/heatmap-data', methods=['GET'])
def get_heatmap_data():
    semestre_id = request.args.get('semestre') # Recibe "1" o "2"

    # 1. Validación básica
    if semestre_id not in MATERIAS_POR_SEMESTRE:
        return jsonify({"error": "Semestre no válido"}), 400

    nombres_materias_objetivo = MATERIAS_POR_SEMESTRE[semestre_id]

    # 2. Obtener los objetos Subject de la BD que coincidan con los nombres de la lista
    # Esto asegura que el orden en el gráfico sea el mismo que en tu lista
    subjects_db = Subject.query.filter(Subject.nombre.in_(nombres_materias_objetivo)).all()
    
    # Ordenamos los subjects encontrados según el orden de la lista original
    # (Opcional, pero ayuda a mantener consistencia visual)
    subjects_db.sort(key=lambda s: nombres_materias_objetivo.index(s.nombre))

    # 3. Obtener todos los Estudiantes
    # Ordenados por apellido para el eje X
    students_db = Student.query.order_by(Student.apellido, Student.nombre).all()

    # 4. Obtener las notas (StudentSubject)
    # Filtramos solo las notas que pertenecen a las materias de este semestre
    grades = db.session.query(StudentSubject).join(Subject).filter(
        Subject.nombre.in_(nombres_materias_objetivo)
    ).all()

    # 5. Crear mapa de acceso rápido: (student_id, subject_id) -> nota
    grades_map = { (g.student_id, g.subject_id): g.nota for g in grades }

    # 6. Construir la estructura para ApexCharts
    series_data = []

    for subject in subjects_db:
        data_points = []
        for student in students_db:
            # Buscamos la nota. Si no existe, enviamos None (se verá vacío en el heatmap)
            nota = grades_map.get((student.id, subject.id), None)
            
            data_points.append({
                "x": f"{student.nombre} {student.apellido}", # Etiqueta Eje X
                "y": nota                                     # Valor (Color)
            })

        series_data.append({
            "name": subject.nombre, # Etiqueta Eje Y (Materia)
            "data": data_points
        })

    return jsonify(series_data)