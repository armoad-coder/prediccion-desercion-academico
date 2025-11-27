from extensions import db


class Student(db.Model):
    __tablename__ = "students"

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(255), nullable=False)
    apellido = db.Column(db.String(255), nullable=False)
    cedula = db.Column(db.String(50), unique=True, nullable=False)

    # Campos necesarios para el modelo predictivo
    estado = db.Column(db.Float, nullable=False, default=0)
    sexo = db.Column(db.Integer, nullable=False)
    estado_carrera = db.Column(db.Integer, nullable=True)
    tiempo_estudio = db.Column(db.Integer, nullable=True)
    ausencias = db.Column(db.Integer, nullable=True)
    cinco_f = db.Column(db.Integer, nullable=True)
    aplazos = db.Column(db.Integer, nullable=True)
    promedio = db.Column(db.Float, nullable=True)

    subjects = db.relationship(
        "StudentSubject",
        back_populates="student",
        cascade="all, delete-orphan"
    )

    def to_dict(self):
        return {
            "id": self.id,
            "nombre": self.nombre,
            "apellido": self.apellido,
            "cedula": self.cedula,
            "estado": self.estado,
            "sexo": self.sexo,
            "estado_carrera": self.estado_carrera,
            "tiempo_estudio": self.tiempo_estudio,
            "ausencias": self.ausencias,
            "cinco_f": self.cinco_f,
            "aplazos": self.aplazos,
            "promedio": self.promedio,
            "materias": {
                ss.subject.nombre: ss.nota
                for ss in self.subjects
            }
        }


class Subject(db.Model):
    __tablename__ = "subjects"

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(255), nullable=False)

    students = db.relationship(
        "StudentSubject",
        back_populates="subject",
        cascade="all, delete-orphan"
    )


class StudentSubject(db.Model):
    __tablename__ = "students_subjects"  # <–– ESTA ES LA TABLA REAL EN POSTGRES

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("students.id"), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey("subjects.id"), nullable=False)
    nota = db.Column(db.Float, nullable=False)

    student = db.relationship("Student", back_populates="subjects")
    subject = db.relationship("Subject", back_populates="students")
