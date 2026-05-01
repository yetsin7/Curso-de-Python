# =============================================================================
# PROYECTO FINAL: Gestor de Tareas
# =============================================================================
#
# Aplicación de consola para gestionar tareas personales.
# Guarda los datos en un archivo JSON local (tareas.json).
#
# USO: python gestor_tareas.py
#
# Este proyecto integra todos los conceptos del libro:
#   - Clases y POO
#   - Manejo de archivos JSON
#   - Manejo de errores
#   - Funciones
#   - Listas y diccionarios
#   - f-strings y formato
#   - Módulos estándar
# =============================================================================

import json
import os
from datetime import datetime


# =============================================================================
# CLASE: Tarea
# Representa una tarea individual con todos sus atributos.
# =============================================================================

class Tarea:
    """Representa una tarea individual con título, descripción y estado."""

    # Prioridades válidas
    PRIORIDADES = ("alta", "media", "baja")

    def __init__(self, id, titulo, descripcion="", prioridad="media"):
        """
        id:           identificador único de la tarea
        titulo:       nombre corto de la tarea
        descripcion:  detalle adicional (opcional)
        prioridad:    'alta', 'media' o 'baja'
        """
        self.id = id
        self.titulo = titulo
        self.descripcion = descripcion
        self.prioridad = prioridad if prioridad in Tarea.PRIORIDADES else "media"
        self.completada = False
        self.fecha_creacion = datetime.now().strftime("%d/%m/%Y %H:%M")
        self.fecha_completada = None

    def completar(self):
        """Marca la tarea como completada y registra la fecha."""
        self.completada = True
        self.fecha_completada = datetime.now().strftime("%d/%m/%Y %H:%M")

    def a_diccionario(self):
        """Convierte la tarea a diccionario para poder guardarla en JSON."""
        return {
            "id": self.id,
            "titulo": self.titulo,
            "descripcion": self.descripcion,
            "prioridad": self.prioridad,
            "completada": self.completada,
            "fecha_creacion": self.fecha_creacion,
            "fecha_completada": self.fecha_completada
        }

    @classmethod
    def desde_diccionario(cls, datos):
        """Crea una Tarea a partir de un diccionario (para cargar desde JSON)."""
        tarea = cls(
            id=datos["id"],
            titulo=datos["titulo"],
            descripcion=datos.get("descripcion", ""),
            prioridad=datos.get("prioridad", "media")
        )
        tarea.completada = datos.get("completada", False)
        tarea.fecha_creacion = datos.get("fecha_creacion", "")
        tarea.fecha_completada = datos.get("fecha_completada")
        return tarea

    def __str__(self):
        """Representación visual de la tarea para mostrar en pantalla."""
        estado = "✔" if self.completada else "○"
        prioridad_symbol = {"alta": "🔴", "media": "🟡", "baja": "🟢"}.get(self.prioridad, "⚪")
        return f"[{estado}] #{self.id:03d} {prioridad_symbol} {self.titulo}"


# =============================================================================
# CLASE: GestorDeTareas
# Maneja la colección completa de tareas y la persistencia en disco.
# =============================================================================

class GestorDeTareas:
    """Gestiona una lista de tareas con persistencia en archivo JSON."""

    def __init__(self, archivo="tareas.json"):
        """
        archivo: nombre del archivo JSON donde se guardan las tareas.
                 Se crea en la misma carpeta que este script.
        """
        # Ruta absoluta al archivo — relativa a donde está este script
        carpeta = os.path.dirname(os.path.abspath(__file__))
        self.archivo = os.path.join(carpeta, archivo)
        self.tareas = []
        self._proximo_id = 1
        self.cargar()

    def cargar(self):
        """Carga las tareas desde el archivo JSON."""
        if not os.path.exists(self.archivo):
            return   # primer uso, sin tareas guardadas

        try:
            with open(self.archivo, "r", encoding="utf-8") as f:
                datos = json.load(f)
            self.tareas = [Tarea.desde_diccionario(d) for d in datos]
            # Calcular el próximo ID disponible
            if self.tareas:
                self._proximo_id = max(t.id for t in self.tareas) + 1
        except (json.JSONDecodeError, KeyError):
            print("⚠ Error al cargar el archivo. Iniciando con lista vacía.")
            self.tareas = []

    def guardar(self):
        """Guarda todas las tareas en el archivo JSON."""
        datos = [t.a_diccionario() for t in self.tareas]
        with open(self.archivo, "w", encoding="utf-8") as f:
            json.dump(datos, f, indent=2, ensure_ascii=False)

    def agregar_tarea(self, titulo, descripcion="", prioridad="media"):
        """Crea y agrega una nueva tarea a la lista."""
        tarea = Tarea(self._proximo_id, titulo, descripcion, prioridad)
        self.tareas.append(tarea)
        self._proximo_id += 1
        self.guardar()
        return tarea

    def obtener_tarea(self, id_tarea):
        """Busca y devuelve una tarea por su ID. Devuelve None si no existe."""
        for tarea in self.tareas:
            if tarea.id == id_tarea:
                return tarea
        return None

    def completar_tarea(self, id_tarea):
        """Marca una tarea como completada."""
        tarea = self.obtener_tarea(id_tarea)
        if tarea is None:
            return False, "Tarea no encontrada"
        if tarea.completada:
            return False, "La tarea ya estaba completada"
        tarea.completar()
        self.guardar()
        return True, tarea

    def eliminar_tarea(self, id_tarea):
        """Elimina una tarea por su ID."""
        tarea = self.obtener_tarea(id_tarea)
        if tarea is None:
            return False, "Tarea no encontrada"
        self.tareas.remove(tarea)
        self.guardar()
        return True, tarea

    def listar(self, solo_pendientes=False, prioridad=None):
        """
        Devuelve la lista de tareas con filtros opcionales.

        solo_pendientes: si True, excluye las tareas completadas
        prioridad:       si se indica, filtra por esa prioridad
        """
        resultado = self.tareas

        if solo_pendientes:
            resultado = [t for t in resultado if not t.completada]

        if prioridad and prioridad in Tarea.PRIORIDADES:
            resultado = [t for t in resultado if t.prioridad == prioridad]

        # Ordenar: primero pendientes, luego por prioridad
        orden_prioridad = {"alta": 0, "media": 1, "baja": 2}
        resultado.sort(key=lambda t: (t.completada, orden_prioridad[t.prioridad]))
        return resultado

    def estadisticas(self):
        """Devuelve un resumen del estado de las tareas."""
        total = len(self.tareas)
        completadas = sum(1 for t in self.tareas if t.completada)
        pendientes = total - completadas
        por_prioridad = {
            p: sum(1 for t in self.tareas if t.prioridad == p and not t.completada)
            for p in Tarea.PRIORIDADES
        }
        return {
            "total": total,
            "completadas": completadas,
            "pendientes": pendientes,
            "por_prioridad": por_prioridad
        }


# =============================================================================
# INTERFAZ DE USUARIO (funciones de menú)
# =============================================================================

def limpiar_pantalla():
    """Limpia la consola según el sistema operativo."""
    os.system("cls" if os.name == "nt" else "clear")


def mostrar_separador(titulo=""):
    """Imprime un separador visual con título opcional."""
    if titulo:
        print(f"\n{'═' * 10} {titulo} {'═' * (30 - len(titulo))}")
    else:
        print("─" * 45)


def mostrar_tareas(gestor, filtro_pendientes=False, filtro_prioridad=None):
    """Muestra la lista de tareas con formato."""
    tareas = gestor.listar(solo_pendientes=filtro_pendientes, prioridad=filtro_prioridad)

    if not tareas:
        print("\n  (No hay tareas que mostrar)")
        return

    print()
    for tarea in tareas:
        print(f"  {tarea}")
        if tarea.descripcion:
            print(f"         → {tarea.descripcion}")
        if tarea.completada:
            print(f"         ✔ Completada: {tarea.fecha_completada}")


def menu_agregar(gestor):
    """Flujo para agregar una nueva tarea."""
    mostrar_separador("Nueva Tarea")

    titulo = input("  Título de la tarea: ").strip()
    if not titulo:
        print("  El título no puede estar vacío.")
        return

    descripcion = input("  Descripción (opcional): ").strip()

    print("  Prioridad: [1] Alta  [2] Media  [3] Baja")
    opcion = input("  Opción (Enter = Media): ").strip()

    prioridades = {"1": "alta", "2": "media", "3": "baja"}
    prioridad = prioridades.get(opcion, "media")

    tarea = gestor.agregar_tarea(titulo, descripcion, prioridad)
    print(f"\n  ✅ Tarea #{tarea.id:03d} creada: '{tarea.titulo}'")


def menu_completar(gestor):
    """Flujo para marcar una tarea como completada."""
    mostrar_separador("Completar Tarea")
    mostrar_tareas(gestor, filtro_pendientes=True)

    try:
        id_tarea = int(input("\n  ID de la tarea a completar: "))
    except ValueError:
        print("  ID inválido.")
        return

    exito, resultado = gestor.completar_tarea(id_tarea)
    if exito:
        print(f"\n  ✅ Tarea '{resultado.titulo}' marcada como completada.")
    else:
        print(f"\n  ❌ {resultado}")


def menu_eliminar(gestor):
    """Flujo para eliminar una tarea."""
    mostrar_separador("Eliminar Tarea")
    mostrar_tareas(gestor)

    try:
        id_tarea = int(input("\n  ID de la tarea a eliminar: "))
    except ValueError:
        print("  ID inválido.")
        return

    tarea = gestor.obtener_tarea(id_tarea)
    if tarea is None:
        print("  ❌ Tarea no encontrada.")
        return

    confirmacion = input(f"  ¿Eliminar '{tarea.titulo}'? (s/n): ").lower()
    if confirmacion != "s":
        print("  Cancelado.")
        return

    gestor.eliminar_tarea(id_tarea)
    print(f"  🗑 Tarea '{tarea.titulo}' eliminada.")


def menu_estadisticas(gestor):
    """Muestra estadísticas del estado de las tareas."""
    mostrar_separador("Estadísticas")
    stats = gestor.estadisticas()

    print(f"\n  Total de tareas:  {stats['total']}")
    print(f"  ✔ Completadas:    {stats['completadas']}")
    print(f"  ○ Pendientes:     {stats['pendientes']}")
    print(f"\n  Pendientes por prioridad:")
    print(f"    🔴 Alta:   {stats['por_prioridad']['alta']}")
    print(f"    🟡 Media:  {stats['por_prioridad']['media']}")
    print(f"    🟢 Baja:   {stats['por_prioridad']['baja']}")


# =============================================================================
# BUCLE PRINCIPAL DEL PROGRAMA
# =============================================================================

def main():
    """Función principal — arranca el programa y muestra el menú."""
    gestor = GestorDeTareas()

    while True:
        limpiar_pantalla()

        print("╔═══════════════════════════════════════╗")
        print("║        GESTOR DE TAREAS               ║")
        print("║        Curso de Python                ║")
        print("╠═══════════════════════════════════════╣")
        print("║  1. Ver todas las tareas              ║")
        print("║  2. Ver solo pendientes               ║")
        print("║  3. Agregar tarea                     ║")
        print("║  4. Completar tarea                   ║")
        print("║  5. Eliminar tarea                    ║")
        print("║  6. Estadísticas                      ║")
        print("║  0. Salir                             ║")
        print("╚═══════════════════════════════════════╝")

        stats = gestor.estadisticas()
        print(f"\n  [{stats['pendientes']} pendientes | {stats['completadas']} completadas]")

        opcion = input("\n  Elige una opción: ").strip()

        if opcion == "0":
            print("\n  ¡Hasta luego!\n")
            break
        elif opcion == "1":
            mostrar_separador("Todas las Tareas")
            mostrar_tareas(gestor)
        elif opcion == "2":
            mostrar_separador("Tareas Pendientes")
            mostrar_tareas(gestor, filtro_pendientes=True)
        elif opcion == "3":
            menu_agregar(gestor)
        elif opcion == "4":
            menu_completar(gestor)
        elif opcion == "5":
            menu_eliminar(gestor)
        elif opcion == "6":
            menu_estadisticas(gestor)
        else:
            print("\n  Opción no válida.")

        input("\n  Presiona Enter para continuar...")


# Punto de entrada del programa
# Solo se ejecuta cuando se corre este archivo directamente
if __name__ == "__main__":
    main()
