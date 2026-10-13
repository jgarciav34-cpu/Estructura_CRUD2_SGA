from abc import ABC, abstractmethod

from models import Estudiante, Materia, Matricula
from shared.json_manager import GestorJSON
from shared.herramientas import es_email_valido


# =====================================================================
# CLASE BASE (ABSTRACTA)
# =====================================================================
class CrudBase(ABC):

    @abstractmethod
    def leer(self):
        pass

    @abstractmethod
    def obtener(self, id_registro):
        pass

    @abstractmethod
    def buscar(self, texto):
        pass

    @abstractmethod
    def siguiente(self):
        pass

    @abstractmethod
    def crear(self, datos):
        pass

    @abstractmethod
    def actualizar(self, id_registro, datos):
        pass

    @abstractmethod
    def eliminar(self, id_registro):
        pass


# =====================================================================
# CONTROLADOR DE ESTUDIANTES
# =====================================================================
class EstudianteController(CrudBase):

    def __init__(self, archivo="data/estudiantes.json"):
        self.gestor = GestorJSON(archivo)
        self.lista = []
        for datos in self.gestor.leer():
            self.lista.append(Estudiante.desde_diccionario(datos))

    def guardar(self):
        datos = [e.a_diccionario() for e in self.lista]
        self.gestor.guardar(datos)

    def validar(self, datos, id_actual=None):
        """Valida campos obligatorios y unicidad con conjuntos (set)."""
        # Tupla de campos obligatorios al crear
        if id_actual is None:
            for campo in ("nombre", "apellido", "email", "carnet"):
                if str(datos.get(campo, "")).strip() == "":
                    return f"El campo {campo} es obligatorio"

        if "email" in datos:
            email = str(datos["email"]).strip().lower()
            if not es_email_valido(email):
                return f"Email inválido: '{email}'"
            # CONJUNTO: búsqueda instantánea de emails ya registrados
            emails_usados = {e.email for e in self.lista if e.id != id_actual}
            if email in emails_usados:
                return "Ese email ya está registrado"

        if "carnet" in datos:
            carnet = str(datos["carnet"]).strip().upper()
            # CONJUNTO: unicidad de carnet
            carnets_usados = {e.carnet.upper() for e in self.lista if e.id != id_actual}
            if carnet in carnets_usados:
                return f"El carnet '{carnet}' ya está registrado"

        return None

    def leer(self):
        return self.lista

    def obtener(self, id_estudiante):
        for estudiante in self.lista:
            if estudiante.id == id_estudiante:
                return estudiante
        return None

    def buscar(self, texto):
        texto = texto.strip().lower()
        if not texto:
            return []

        encontrados = []
        for e in self.lista:
            if (texto in e.nombre.lower()
                    or texto in e.apellido.lower()
                    or texto in e.email.lower()
                    or texto in e.carnet.lower()
                    or texto in e.carrera.lower()):
                encontrados.append(e)
        return encontrados

    def siguiente(self):
        mayor = 0
        for e in self.lista:
            if e.id > mayor:
                mayor = e.id
        return mayor + 1

    def crear(self, datos):
        error = self.validar(datos)
        if error:
            return False, error

        estudiante = Estudiante(
            self.siguiente(),
            str(datos["nombre"]).strip().title(),
            str(datos["apellido"]).strip().title(),
            str(datos["email"]).strip().lower(),
            str(datos.get("carnet", "")).strip().upper(),
            str(datos.get("carrera", "")).strip().title()
        )
        self.lista.append(estudiante)
        self.guardar()
        return True, f"Estudiante creado: {estudiante.etiqueta()}"

    def actualizar(self, id_estudiante, datos):
        estudiante = self.obtener(id_estudiante)
        if estudiante is None:
            return False, f"No existe un estudiante con id {id_estudiante}"
        if not datos:
            return False, "No se indicó ningún cambio"

        permitidos = {"nombre", "apellido", "email", "carnet", "carrera"}
        desconocidos = set(datos) - permitidos
        if desconocidos:
            return False, f"Campos no válidos: {', '.join(sorted(desconocidos))}"

        error = self.validar(datos, id_estudiante)
        if error:
            return False, error

        for campo, valor in datos.items():
            valor = str(valor).strip()
            if campo in ("nombre", "apellido", "carrera"):
                valor = valor.title()
            elif campo == "email":
                valor = valor.lower()
            elif campo == "carnet":
                valor = valor.upper()
            setattr(estudiante, campo, valor)

        self.guardar()
        return True, f"Estudiante {id_estudiante} actualizado"

    def eliminar(self, id_estudiante):
        estudiante = self.obtener(id_estudiante)
        if estudiante is None:
            return False, f"No existe un estudiante con id {id_estudiante}"

        self.lista.remove(estudiante)
        self.guardar()
        return True, f"Estudiante {id_estudiante} eliminado"

    def carreras(self):
        """CONJUNTO para descartar duplicados y ordenarlo como lista."""
        return sorted({e.carrera for e in self.lista if e.carrera != ""})


# =====================================================================
# CONTROLADOR DE MATERIAS
# =====================================================================
class MateriaController(CrudBase):

    def __init__(self, archivo="data/materias.json"):
        self.gestor = GestorJSON(archivo)
        self.lista = []
        for datos in self.gestor.leer():
            self.lista.append(Materia.desde_diccionario(datos))

    def guardar(self):
        datos = [m.a_diccionario() for m in self.lista]
        self.gestor.guardar(datos)

    def validar(self, datos, id_actual=None):
        if id_actual is None:
            for campo in ("nombre", "codigo"):
                if str(datos.get(campo, "")).strip() == "":
                    return f"El campo {campo} es obligatorio"

        if "codigo" in datos:
            codigo = str(datos["codigo"]).strip().upper()
            # CONJUNTO de códigos únicos
            codigos_usados = {m.codigo for m in self.lista if m.id != id_actual}
            if codigo in codigos_usados:
                return f"El código '{codigo}' ya existe"

        if "creditos" in datos:
            try:
                cred = int(datos["creditos"])
                if not (1 <= cred <= 10):
                    return "Los créditos deben ser un número entero entre 1 y 10"
            except (TypeError, ValueError):
                return "Los créditos deben ser un número entero"

        if "cupos" in datos:
            try:
                cup = int(datos["cupos"])
                if not (0 <= cup <= Materia.CUPOS_MAXIMOS):
                    return f"Los cupos deben estar entre 0 y {Materia.CUPOS_MAXIMOS}"
            except (TypeError, ValueError):
                return "Los cupos deben ser un número entero"

        return None

    def leer(self):
        return self.lista

    def obtener(self, id_materia):
        for materia in self.lista:
            if materia.id == id_materia:
                return materia
        return None

    def buscar(self, texto):
        texto = texto.strip().lower()
        if not texto:
            return []

        encontrados = []
        for m in self.lista:
            if texto in m.nombre.lower() or texto in m.codigo.lower():
                encontrados.append(m)
        return encontrados

    def siguiente(self):
        mayor = 0
        for m in self.lista:
            if m.id > mayor:
                mayor = m.id
        return mayor + 1

    def crear(self, datos):
        error = self.validar(datos)
        if error:
            return False, error

        creditos = int(datos.get("creditos", 3))
        cupos = int(datos.get("cupos", Materia.CUPOS_MAXIMOS))

        materia = Materia(
            self.siguiente(),
            str(datos["nombre"]).strip().title(),
            str(datos["codigo"]).strip().upper(),
            creditos,
            cupos
        )
        self.lista.append(materia)
        self.guardar()
        return True, f"Materia creada: {materia.etiqueta()}"

    def actualizar(self, id_materia, datos):
        materia = self.obtener(id_materia)
        if materia is None:
            return False, f"No existe la materia con id {id_materia}"
        if not datos:
            return False, "No se indicó ningún cambio"

        permitidos = {"nombre", "codigo", "creditos", "cupos"}
        desconocidos = set(datos) - permitidos
        if desconocidos:
            return False, f"Campos no válidos: {', '.join(sorted(desconocidos))}"

        error = self.validar(datos, id_materia)
        if error:
            return False, error

        if "nombre" in datos:
            materia.nombre = str(datos["nombre"]).strip().title()
        if "codigo" in datos:
            materia.codigo = str(datos["codigo"]).strip().upper()
        if "creditos" in datos:
            materia.creditos = int(datos["creditos"])
        if "cupos" in datos:
            materia.cupos = int(datos["cupos"])

        self.guardar()
        return True, f"Materia {id_materia} actualizada"

    def eliminar(self, id_materia):
        materia = self.obtener(id_materia)
        if materia is None:
            return False, f"No existe la materia con id {id_materia}"

        self.lista.remove(materia)
        self.guardar()
        return True, f"Materia {id_materia} eliminada"

    def materias_sin_cupo(self):
        return [m for m in self.lista if not m.hay_cupo()]


# =====================================================================
# CONTROLADOR DE MATRÍCULAS
# =====================================================================
class MatriculaController(CrudBase):

    def __init__(self, estudiantes, materias, archivo="data/matriculas.json"):
        self.estudiantes = estudiantes
        self.materias = materias
        self.gestor = GestorJSON(archivo)

        self.lista = []
        for datos in self.gestor.leer():
            self.lista.append(Matricula.desde_diccionario(datos))

    def guardar(self):
        datos = [m.a_diccionario() for m in self.lista]
        self.gestor.guardar(datos)

    def validar(self, datos):
        try:
            estudiante_id = int(datos.get("estudiante_id", 0))
            materia_id = int(datos.get("materia_id", 0))
            periodo = str(datos.get("periodo", "")).strip()
        except (TypeError, ValueError):
            return "estudiante_id y materia_id deben ser números enteros"

        if not periodo:
            return "El periodo es obligatorio (ej. 2026-1)"

        if self.estudiantes.obtener(estudiante_id) is None:
            return f"No existe el estudiante con id {estudiante_id}"

        materia = self.materias.obtener(materia_id)
        if materia is None:
            return f"No existe la materia con id {materia_id}"

        if not materia.hay_cupo():
            return f"Sin cupos disponibles para {materia.nombre}"

        # Validación de duplicidad: no matricular dos veces al mismo estudiante en la misma materia y periodo
        for mat in self.lista:
            if (mat.estudiante_id == estudiante_id and
                    mat.materia_id == materia_id and
                    mat.periodo.upper() == periodo.upper()):
                return f"El estudiante ya está matriculado en {materia.nombre} para el periodo {periodo}"

        return None

    def leer(self):
        return self.lista

    def obtener(self, id_matricula):
        for m in self.lista:
            if m.id == id_matricula:
                return m
        return None

    def buscar(self, texto):
        texto = texto.strip().lower()
        if not texto:
            return []

        encontradas = []
        for m in self.lista:
            if texto in m.periodo.lower() or texto in m.fecha:
                encontradas.append(m)
        return encontradas

    def siguiente(self):
        mayor = 0
        for m in self.lista:
            if m.id > mayor:
                mayor = m.id
        return mayor + 1

    def crear(self, datos):
        error = self.validar(datos)
        if error:
            return False, error

        materia = self.materias.obtener(int(datos["materia_id"]))
        matricula = Matricula(
            self.siguiente(),
            int(datos["estudiante_id"]),
            materia.id,
            str(datos["periodo"]).strip(),
            nota=float(datos.get("nota", 0.0))
        )

        materia.ocupar_cupo()
        self.materias.guardar()
        self.lista.append(matricula)
        self.guardar()
        return True, f"Matrícula {matricula.id} registrada exitosamente"

    def actualizar(self, id_matricula, datos):
        return False, "Las matrículas no se modifican directamente: use 'Registrar nota' o 'Retirar matrícula'"

    def eliminar(self, id_matricula):
        """Retirar matrícula: se borra y se devuelve el cupo a la materia."""
        matricula = self.obtener(id_matricula)
        if matricula is None:
            return False, f"No existe la matrícula {id_matricula}"

        materia = self.materias.obtener(matricula.materia_id)
        if materia is not None:
            materia.liberar_cupo()
            self.materias.guardar()

        self.lista.remove(matricula)
        self.guardar()
        return True, f"Matrícula {id_matricula} retirada y cupo liberado"

    # --- Métodos específicos del dominio académico ---
    def registrar_nota(self, id_matricula, nota):
        matricula = self.obtener(id_matricula)
        if matricula is None:
            return False, f"No existe la matrícula {id_matricula}"

        if not Materia.es_nota_valida(nota):
            return False, f"Nota inválida: '{nota}' (debe ser de 0 a 20)"

        matricula.nota = float(nota)
        self.guardar()
        return True, f"Nota actualizada: {matricula.nota:.1f} ({matricula.estado()})"

    def certificado(self, id_matricula):
        """Cruza los objetos usando diccionarios índice {id: objeto} para búsqueda rápida."""
        matricula = self.obtener(id_matricula)
        if matricula is None:
            return None

        # DICCIONARIOS ÍNDICE {id: objeto}
        mapa_estudiantes = {e.id: e for e in self.estudiantes.leer()}
        mapa_materias = {m.id: m for m in self.materias.leer()}

        estudiante = mapa_estudiantes.get(matricula.estudiante_id)
        materia = mapa_materias.get(matricula.materia_id)

        est_txt = f"{estudiante.nombre_completo()} ({estudiante.carnet})" if estudiante else "Estudiante no registrado"
        mat_txt = f"{materia.nombre} ({materia.codigo}) · {materia.creditos} créditos" if materia else "Materia no registrada"

        texto = f"CERTIFICADO #{matricula.id}   periodo: {matricula.periodo}\n"
        texto += f"Estudiante: {est_txt}\n"
        texto += f"Materia   : {mat_txt}\n"
        texto += "-" * 42 + "\n"
        texto += f"Nota      : {matricula.nota:.1f}\n"
        texto += f"Estado    : {matricula.estado()}"
        return texto

    def matriculas_por_estudiante(self):
        """DICCIONARIO DE LISTAS: {estudiante_id: [matriculas]}."""
        agrupadas = {}
        for mat in self.lista:
            agrupadas.setdefault(mat.estudiante_id, []).append(mat)
        return agrupadas

    def promedio_de_estudiante(self, id_estudiante):
        mats = [m for m in self.lista if m.estudiante_id == id_estudiante]
        if not mats:
            return 0.0
        return round(sum(m.nota for m in mats) / len(mats), 2)