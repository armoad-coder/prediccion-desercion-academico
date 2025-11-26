from extensions import db


class Student(db.Model):
    __tablename__ = "students"

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(255), nullable=False)
    apellido = db.Column(db.String(255), nullable=False)
    cedula = db.Column(db.String(50), unique=True, nullable=False)

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

