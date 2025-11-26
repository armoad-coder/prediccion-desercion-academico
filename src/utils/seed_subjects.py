import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import create_app
from extensions import db
from models.models import Subject

MATERIAS = [
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

def run():
    app = create_app()
    with app.app_context():
        for idx, name in enumerate(MATERIAS, start=1):
            if not Subject.query.get(idx):
                s = Subject(id=idx, nombre=name)
                db.session.add(s)

        db.session.commit()
        print("Materias cargadas correctamente.")

if __name__ == "__main__":
    run()
