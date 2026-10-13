from datetime import date


# =====================================================================
# CLASE BASE: lo que los tres modelos comparten
# =====================================================================
class ModeloBase:
    """Padre de todos los modelos. Guarda el id y define el comportamiento común."""

    def __init__(self, id_registro):
        self.id = int(id_registro)

    @classmethod
    def desde_diccionario(cls, datos):
        """Diccionario -> objeto. Escrito UNA vez y usado por todos los modelos."""
        datos = dict(datos)
        id_registro = datos.pop("id")
        return cls(id_registro, **datos)

    def a_diccionario(self):
        return {"id": self.id}

    def etiqueta(self):
        return f"registro {self.id}"

    def __str__(self):
        return f"[{self.id}] {self.etiqueta()}"


# =====================================================================
# HERENCIA: Persona es la base de Estudiante
# =====================================================================
class Persona(ModeloBase):
    """Todo lo que tiene una persona en el sistema."""

    def __init__(self, id_registro, nombre, apellido, email):
        super().__init__(id_registro)
        self.nombre = nombre
        self.apellido = apellido
        self.email = email

    def nombre_completo(self):
        return f"{self.nombre} {self.apellido}"

    def a_diccionario(self):
        datos = super().a_diccionario()
        datos["nombre"] = self.nombre
        datos["apellido"] = self.apellido
        datos["email"] = self.email
        return datos

    def etiqueta(self):
        return self.nombre_completo()


class Estudiante(Persona):
    """Estudiante ES UNA Persona, con carnet y carrera."""

    def __init__(self, id_registro, nombre, apellido, email, carnet="", carrera=""):
        super().__init__(id_registro, nombre, apellido, email)
        self.carnet = carnet
        self.carrera = carrera

    def a_diccionario(self):
        datos = super().a_diccionario()
        datos["carnet"] = self.carnet
        datos["carrera"] = self.carrera
        return datos

    def etiqueta(self):
        carrera_txt = self.carrera or "sin carrera"
        return f"{super().etiqueta()} · {self.carnet} · {carrera_txt}"


# =====================================================================
# MODELO CON REGLAS Y ATRIBUTOS ESTÁTICOS
# =====================================================================
class Materia(ModeloBase):
    """Materia ES UN ModeloBase. Contiene atributos y métodos estáticos."""

    CUPOS_MAXIMOS = 30        # Atributo estático compartido
    NOTA_APROBACION = 14      # Atributo estático compartido

    def __init__(self, id_registro, nombre, codigo, creditos=0, cupos=0):
        super().__init__(id_registro)
        self.nombre = nombre
        self.codigo = codigo.upper()
        self.creditos = int(creditos)
        self.cupos = int(cupos)

    @staticmethod
    def es_nota_valida(valor):
        """Valida que la nota esté en la escala de 0 a 20."""
        try:
            val = float(valor)
            return 0.0 <= val <= 20.0
        except (TypeError, ValueError):
            return False

    def hay_cupo(self):
        return self.cupos > 0

    def ocupar_cupo(self):
        if self.hay_cupo():
            self.cupos -= 1

    def liberar_cupo(self):
        if self.cupos < Materia.CUPOS_MAXIMOS:
            self.cupos += 1

    def a_diccionario(self):
        datos = super().a_diccionario()
        datos["nombre"] = self.nombre
        datos["codigo"] = self.codigo
        datos["creditos"] = self.creditos
        datos["cupos"] = self.cupos
        return datos

    def etiqueta(self):
        alerta = " ⚠ sin cupo" if not self.hay_cupo() else ""
        return f"{self.nombre} ({self.codigo}) · {self.creditos} créd. · cupos: {self.cupos}{alerta}"


# =====================================================================
# MATRÍCULA
# =====================================================================
class Matricula(ModeloBase):
    """Matrícula académica: une un estudiante, una materia y un periodo."""

    def __init__(self, id_registro, estudiante_id, materia_id, periodo, nota=0.0, fecha=""):
        super().__init__(id_registro)
        self.estudiante_id = int(estudiante_id)
        self.materia_id = int(materia_id)
        self.periodo = periodo
        self.nota = float(nota)
        self.fecha = fecha or date.today().isoformat()

    def esta_aprobada(self):
        return self.nota >= Materia.NOTA_APROBACION

    def estado(self):
        # Se calcula en caliente, nunca se guarda como atributo fijo
        return "Aprobado" if self.esta_aprobada() else "Reprobado"

    def a_diccionario(self):
        datos = super().a_diccionario()
        datos["estudiante_id"] = self.estudiante_id
        datos["materia_id"] = self.materia_id
        datos["periodo"] = self.periodo
        datos["nota"] = self.nota
        datos["fecha"] = self.fecha
        return datos

    def etiqueta(self):
        return (f"{self.fecha} · est. {self.estudiante_id} · "
                f"mat. {self.materia_id} ({self.periodo}) · Nota: {self.nota:.1f} ({self.estado()})")