from shared.herramientas import (
    imprimir_titulo, imprimir_exito, imprimir_error, imprimir_info, confirmar
)
from views import EstudianteController, MateriaController, MatriculaController

# Controladores
estudiantes = EstudianteController()
materias = MateriaController()
matriculas = MatriculaController(estudiantes, materias)


# =====================================================================
# AYUDAS DE PANTALLA
# =====================================================================

def pausa():
    input("\nPresione Enter para continuar...")


def pedir_entero(etiqueta):
    try:
        return int(input(etiqueta))
    except ValueError:
        return None


def mostrar_resultado(exito, mensaje):
    if exito:
        imprimir_exito(mensaje)
    else:
        imprimir_error(mensaje)


def mostrar_lista(objetos, vacio="No hay registros todavía."):
    """Polimorfismo puro: funciona con Estudiante, Materia o Matricula."""
    if not objetos:
        imprimir_info(vacio)
        return
    for objeto in objetos:
        print(f"  {objeto}")
    imprimir_info(f"Total: {len(objetos)}")


def mostrar_detalle(objeto):
    for clave, valor in objeto.a_diccionario().items():
        print(f"  {str(clave).replace('_', ' ').capitalize():<16}: {valor}")


# =====================================================================
# MENÚ DE ESTUDIANTES
# =====================================================================

def crear_estudiante():
    imprimir_titulo("CREAR ESTUDIANTE")
    datos = {
        "nombre": input("Nombre: "),
        "apellido": input("Apellido: "),
        "email": input("Email: "),
        "carnet": input("Carnet (ej. EST2026001): "),
        "carrera": input("Carrera: "),
    }
    mostrar_resultado(*estudiantes.crear(datos))
    pausa()


def listar_estudiantes():
    imprimir_titulo("ESTUDIANTES")
    mostrar_lista(estudiantes.leer(), "Todavía no hay estudiantes registrados.")
    pausa()


def buscar_estudiante():
    imprimir_titulo("BUSCAR ESTUDIANTE")
    termino = input("Nombre, carnet, email o carrera: ")
    encontrados = estudiantes.buscar(termino)
    mostrar_lista(encontrados, f"Ningún estudiante coincide con '{termino}'.")
    pausa()


def ver_estudiante():
    imprimir_titulo("VER ESTUDIANTE POR ID")
    estudiante = estudiantes.obtener(pedir_entero("Id: "))
    if estudiante is None:
        imprimir_error("No encontrado")
    else:
        mostrar_detalle(estudiante)
        prom = matriculas.promedio_de_estudiante(estudiante.id)
        imprimir_info(f"Promedio general: {prom:.2f}")
    pausa()


def actualizar_estudiante():
    imprimir_titulo("ACTUALIZAR ESTUDIANTE")
    id_est = pedir_entero("Id: ")
    estudiante = estudiantes.obtener(id_est)
    if estudiante is None:
        imprimir_error("No encontrado")
        return pausa()

    imprimir_info(f"Editando: {estudiante.etiqueta()}")
    print("Deje en blanco lo que no quiera cambiar.\n")

    cambios = {}
    for campo in ("nombre", "apellido", "email", "carnet", "carrera"):
        actual = getattr(estudiante, campo)
        nuevo = input(f"{campo.capitalize()} [{actual}]: ").strip()
        if nuevo:
            cambios[campo] = nuevo

    mostrar_resultado(*estudiantes.actualizar(id_est, cambios))
    pausa()


def eliminar_estudiante():
    imprimir_titulo("ELIMINAR ESTUDIANTE")
    id_est = pedir_entero("Id: ")
    estudiante = estudiantes.obtener(id_est)
    if estudiante is None:
        imprimir_error("No encontrado")
        return pausa()

    imprimir_info(f"Se eliminará: {estudiante.etiqueta()}")
    if confirmar("¿Confirma?"):
        mostrar_resultado(*estudiantes.eliminar(id_est))
    else:
        imprimir_info("Operación cancelada")
    pausa()


# =====================================================================
# MENÚ DE MATERIAS
# =====================================================================

def crear_materia():
    imprimir_titulo("CREAR MATERIA")
    datos = {
        "nombre": input("Nombre: "),
        "codigo": input("Código (ej. MAT101): "),
        "creditos": input("Créditos (1 a 10): "),
        "cupos": input("Cupos (0 a 30): "),
    }
    mostrar_resultado(*materias.crear(datos))
    pausa()


def listar_materias():
    imprimir_titulo("MATERIAS")
    mostrar_lista(materias.leer(), "Todavía no hay materias.")
    pausa()


def buscar_materia():
    imprimir_titulo("BUSCAR MATERIA")
    termino = input("Nombre o código: ")
    mostrar_lista(materias.buscar(termino), "Sin coincidencias.")
    pausa()


def ver_materia():
    imprimir_titulo("VER MATERIA POR ID")
    materia = materias.obtener(pedir_entero("Id: "))
    if materia is None:
        imprimir_error("No encontrada")
    else:
        mostrar_detalle(materia)
    pausa()


def actualizar_materia():
    imprimir_titulo("ACTUALIZAR MATERIA")
    id_mat = pedir_entero("Id: ")
    materia = materias.obtener(id_mat)
    if materia is None:
        imprimir_error("No encontrada")
        return pausa()

    imprimir_info(f"Editando: {materia.etiqueta()}")
    print("Deje en blanco lo que no quiera cambiar.\n")

    cambios = {}
    for campo in ("nombre", "codigo", "creditos", "cupos"):
        actual = getattr(materia, campo)
        nuevo = input(f"{campo.capitalize()} [{actual}]: ").strip()
        if nuevo:
            cambios[campo] = nuevo

    mostrar_resultado(*materias.actualizar(id_mat, cambios))
    pausa()


def eliminar_materia():
    imprimir_titulo("ELIMINAR MATERIA")
    id_mat = pedir_entero("Id: ")
    materia = materias.obtener(id_mat)
    if materia is None:
        imprimir_error("No encontrada")
        return pausa()

    imprimir_info(f"Se eliminará: {materia.etiqueta()}")
    if confirmar("¿Confirma?"):
        mostrar_resultado(*materias.eliminar(id_mat))
    else:
        imprimir_info("Operación cancelada")
    pausa()


# =====================================================================
# MENÚ DE MATRÍCULAS
# =====================================================================

def matricular():
    imprimir_titulo("REGISTRAR MATRÍCULA")
    imprimir_info("Estudiantes:")
    mostrar_lista(estudiantes.leer())
    imprimir_info("Materias:")
    mostrar_lista(materias.leer())

    datos = {
        "estudiante_id": pedir_entero("\nId del estudiante: "),
        "materia_id": pedir_entero("Id de la materia: "),
        "periodo": input("Periodo académico (ej. 2026-1): ").strip(),
    }
    if None in (datos["estudiante_id"], datos["materia_id"]):
        imprimir_error("Los IDs deben ser números enteros")
        return pausa()

    mostrar_resultado(*matriculas.crear(datos))
    pausa()


def listar_matriculas():
    imprimir_titulo("MATRÍCULAS")
    mostrar_lista(matriculas.leer(), "Todavía no hay matrículas.")
    pausa()


def registrar_nota():
    imprimir_titulo("REGISTRAR NOTA")
    id_mat = pedir_entero("Id de la matrícula: ")
    if id_mat is None:
        imprimir_error("ID inválido")
        return pausa()

    nota = input("Nota obtenida (0 a 20): ")
    mostrar_resultado(*matriculas.registrar_nota(id_mat, nota))
    pausa()


def ver_certificado():
    imprimir_titulo("CERTIFICADO")
    id_mat = pedir_entero("Id de la matrícula: ")
    texto = matriculas.certificado(id_mat)
    if texto is None:
        imprimir_error("No existe esa matrícula")
    else:
        print(texto)
    pausa()


def retirar_matricula():
    imprimir_titulo("RETIRAR MATRÍCULA")
    id_mat = pedir_entero("Id de la matrícula: ")
    if id_mat and confirmar("Se liberará el cupo en la materia. ¿Confirma?"):
        mostrar_resultado(*matriculas.eliminar(id_mat))
    else:
        imprimir_info("Operación cancelada")
    pausa()


def resumen():
    imprimir_titulo("RESUMEN ACADÉMICO")
    print(f"  Estudiantes       : {len(estudiantes.leer())}")
    print(f"  Carreras          : {', '.join(estudiantes.carreras()) or '-'}")
    print(f"  Materias          : {len(materias.leer())}")
    sin_cupo = materias.materias_sin_cupo()
    print(f"  Materias sin cupo : {', '.join(m.nombre for m in sin_cupo) or 'ninguna'}")
    
    lista_mat = matriculas.leer()
    aprobadas = sum(1 for m in lista_mat if m.esta_aprobada())
    print(f"  Total matrículas  : {len(lista_mat)}")
    print(f"  Aprobadas         : {aprobadas}")
    pausa()


# =====================================================================
# MENÚS: DICCIONARIOS tecla -> (texto, función)
# =====================================================================

MENU_ESTUDIANTES = {
    "1": ("Crear estudiante", crear_estudiante),
    "2": ("Ver todos", listar_estudiantes),
    "3": ("Buscar", buscar_estudiante),
    "4": ("Ver por id", ver_estudiante),
    "5": ("Actualizar", actualizar_estudiante),
    "6": ("Eliminar", eliminar_estudiante),
    "0": ("Volver", None),
}

MENU_MATERIAS = {
    "1": ("Crear materia", crear_materia),
    "2": ("Ver todas", listar_materias),
    "3": ("Buscar", buscar_materia),
    "4": ("Ver por id", ver_materia),
    "5": ("Actualizar", actualizar_materia),
    "6": ("Eliminar", eliminar_materia),
    "0": ("Volver", None),
}

MENU_MATRICULAS = {
    "1": ("Matricular", matricular),
    "2": ("Ver todas", listar_matriculas),
    "3": ("Registrar nota", registrar_nota),
    "4": ("Ver certificado", ver_certificado),
    "5": ("Retirar matrícula", retirar_matricula),
    "0": ("Volver", None),
}


def ejecutar_menu(titulo, opciones):
    while True:
        imprimir_titulo(titulo)
        for tecla, (texto, _funcion) in opciones.items():
            print(f"  {tecla}. {texto}")
        print()

        tecla = input("Opción: ").strip()
        if tecla not in opciones:
            imprimir_error("Opción no válida")
            pausa()
            continue

        _texto, funcion = opciones[tecla]
        if funcion is None:
            break
        funcion()


def main():
    while True:
        imprimir_titulo("SISTEMA ACADÉMICO")
        print("  1. Estudiantes")
        print("  2. Materias")
        print("  3. Matrículas")
        print("  4. Resumen")
        print("  0. Salir\n")

        tecla = input("Opción: ").strip()
        if tecla == "1":
            ejecutar_menu("ESTUDIANTES", MENU_ESTUDIANTES)
        elif tecla == "2":
            ejecutar_menu("MATERIAS", MENU_MATERIAS)
        elif tecla == "3":
            ejecutar_menu("MATRÍCULAS", MENU_MATRICULAS)
        elif tecla == "4":
            resumen()
        elif tecla == "0":
            imprimir_info("¡Hasta luego! 👋")
            break
        else:
            imprimir_error("Opción no válida")
            pausa()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nPrograma interrumpido por el usuario.")