# 1. Definir la estructura del Estado
import os
import sys
from typing import TypedDict, List, Optional
from langgraph.graph import StateGraph, START, END


from leer_sol import LectorSolicitudCotizacion
from leer_cotis import LectorCotizaciones

class CotizacionState(TypedDict):
    solicitud_content: str
    cotizaciones_content: List[str]
    postores: List[dict]
    ganador: Optional[dict]
    message: str

def read_solicitud_node(state: CotizacionState):
    """Lee y parsea el archivo de solicitud de cotización"""
    try:
        lector = LectorSolicitudCotizacion('./emails/solicitud-cotizacion.html')
        state['solicitud_content'] = lector.procesar()
        state['message'] = "Solicitud de cotización leída exitosamente"

        print (state['message'])
    except FileNotFoundError:
        state['message'] = "Error: No se encontró el archivo solicitud-cotizacion.html"
    return state

def read_cotizaciones_node(state: CotizacionState):
    """Lee y parsea los archivos de cotizaciones"""
    cotizaciones_path = './emails'
    cotizaciones_template = 'cotizacion*.html'
    state['cotizaciones_content'] = []

    
    try:
        lector = LectorCotizaciones(cotizaciones_path, cotizaciones_template, True)
        state['cotizaciones_content'] = lector.procesar()
        state['postores'] = lector.cotizaciones
        state['message'] = f"Se procesaron {len(lector.cotizaciones)} cotizaciones"

        print (state['message'])
    except Exception as e:
        print(f"Error procesando cotizaciones: {str(e)}")
        return state

    
    return state

def determine_winner_node(state: CotizacionState):
    """Determina el postor ganador basado en el menor monto_total"""
    if not state.get('postores'):
        state['message'] = "No hay postores para evaluar"
        return state

    ganador = min(state['postores'], key=lambda x: x['monto_total'])
    state['ganador'] = ganador
    state['message'] = f"El ganador es {ganador['empresa']} del archivo {ganador['archivo']} con un monto de {ganador['monto_total']}"
    return state

def workflow_cotizacion():
    """Crea y ejecuta el flujo de trabajo de cotización"""
    workflow = StateGraph(CotizacionState)
    
    # Agregar nodos
    workflow.add_node("read_solicitud", read_solicitud_node)
    workflow.add_node("read_cotizaciones", read_cotizaciones_node)
    workflow.add_node("determine_winner", determine_winner_node)
    
    # Definir el flujo
    workflow.add_edge(START, "read_solicitud")
    workflow.add_edge("read_solicitud", "read_cotizaciones")
    workflow.add_edge("read_cotizaciones", "determine_winner")
    workflow.add_edge("determine_winner", END)
    
    # Compilar el workflow
    cotizacion_app = workflow.compile()
    
    # Estado inicial
    initial_state = {
        "solicitud_content": "",
        "cotizaciones_content": [],
        "postores": [],
        "ganador": None,
        "message": ""
    }
    
    # Ejecutar el workflow
    result = cotizacion_app.invoke(initial_state)
    print("\nResultado del proceso:")
    print(f"Mensaje final: {result['message']}")
    if result['ganador']:
        print(f"Postor ganador: {result['ganador']['empresa']}")
        print(f"Archivo: {result['ganador']['archivo']}")
        print(f"Monto: {result['ganador']['monto_total']}")


    # Visualiza el grafo

    # Opción A: Mostrar como imagen PNG (ideal para Jupyter Notebooks o entornos que soportan IPython.display)
    try:
        print("Generando imagen PNG...")
        # El método draw_mermaid_png() devuelve bytes PNG
        png_graph = cotizacion_app.get_graph().draw_mermaid_png()
        with open("my_graph.png", "wb") as f:
            f.write(png_graph)
        print(f"Gráfico guardado como 'my_graph.png' en {os.getcwd()}")
    except Exception as e:
        print(f"No se pudo guardar la imagen PNG. Error: {e}")


def main():
    """Punto de entrada principal."""
    try:
        workflow_cotizacion()
    except Exception as e:
        print(f"Error en la ejecución: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()