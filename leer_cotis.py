import json
import os
from pathlib import Path
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

#from scripts.parse_cotizaciones import ROOT

class LectorCotizaciones:
    def __init__(self, carpeta='./emails', plantilla='cotizacion*.html', usar_llm=True):
        self.carpeta = carpeta
        self.archivos = [f for f in os.listdir(carpeta) if f.startswith(plantilla.split('*')[0]) and f.endswith('.html')]
        self.cotizaciones = []
        self.usar_llm = usar_llm

        #print(f"Archivos encontrados para procesar: {self.archivos}")
 
        # Cargar variables de entorno y configurar OpenAI
        load_dotenv()
        if(self.usar_llm):
            self.llm = ChatOpenAI(temperature=0)

    def leer_archivo(self, nombre_archivo):
        """Lee un archivo HTML de cotización individual"""
        ruta_completa = os.path.join(self.carpeta, nombre_archivo)
        try:
            with open(ruta_completa, 'r', encoding='utf-8') as file:
                return file.read()
        except Exception as e:
            print(f"Error al leer {nombre_archivo}: {str(e)}")
            return None

    def extraer_datos_con_llm(self, contenido_html, nombre_archivo):
        """Extrae los datos usando LLM"""
        prompt = f"""
        Analiza el siguiente HTML de una cotización y extrae la información en formato JSON.
        El JSON debe tener esta estructura:
        {{
            "archivo": "nombre del archivo",
            "empresa": "nombre de la empresa",
            "ruc": "número de RUC",
            "fecha": "fecha de cotización",
            "items": [
                {{
                    "item": "número de item",
                    "descripcion": "descripción del producto",
                    "cantidad": número,
                    "precio": número decimal
                }}
            ],
            "monto_total": suma total
        }}

        HTML:
        {contenido_html}
        """

        try:
            response = self.llm.invoke(prompt).content
            datos = json.loads(response)
            datos["archivo"] = nombre_archivo
            return datos
        except Exception as e:
            print(f"Error procesando con LLM {nombre_archivo}: {str(e)}")
            return None

    def procesar(self):
        """Procesa todos los archivos de cotización y devuelve un JSON con la información"""
        self.cotizaciones = []
        
        if(self.usar_llm is False):
            print('Usando datos simulados sin LLM')
            self.cotizaciones = [
                {
                    "archivo": "cotizacion001.html",
                    "empresa": "FERTILIZANTES UNIDOS S.A.",
                    "ruc": "",
                    "fecha": "Miércoles, 3 de septiembre de 2025 09:30",
                    "items": [
                        {
                        "item": "1",
                        "descripcion": "CLIP PH (1 LT)",
                        "cantidad": 5.0,
                        "precio": 19.0
                        },
                        {
                        "item": "2",
                        "descripcion": "UPAXIAL (1 LT)",
                        "cantidad": 5.0,
                        "precio": 130.0
                        }
                    ],
                    "monto_total": 745.0
                },
                {
                    "archivo": "cotizacion002.html",
                    "empresa": "AGRO CLINJER S.A.C.",
                    "ruc": "",
                    "fecha": "Miércoles, 3 de septiembre de 2025 11:20",
                    "items": [
                        {
                        "item": "1",
                        "descripcion": "CLIP PH (1 LT)",
                        "cantidad": 5.0,
                        "precio": 90.0
                        },
                        {
                        "item": "2",
                        "descripcion": "UPAXIAL (1 LT)",
                        "cantidad": 5.0,
                        "precio": 700.0
                        }
                    ],
                    "monto_total": 790.0
                },
                {
                    "archivo": "cotizacion003.html",
                    "empresa": "INVERSIONES AGRICOLAS S.A.C.",
                    "ruc": "",
                    "fecha": "Jueves, 4 de septiembre de 2025 08:30",
                    "items": [
                        {
                        "item": "1",
                        "descripcion": "CLIP PH (1 LT)",
                        "cantidad": 5.0,
                        "precio": 80.0
                        },
                        {
                        "item": "2",
                        "descripcion": "UPAXIAL (1 LT)",
                        "precio": 80.0
                        },
                        {
                        "item": "2",
                        "descripcion": "UPAXIAL (1 LT)",
                        "cantidad": 5.0,
                        "precio": 600.0
                        }
                    ],
                    "monto_total": 680.0
                }
                ]
            
        else:
            print('Usando LLM para extraer datos de cotizaciones')
            for archivo in self.archivos:
                contenido = self.leer_archivo(archivo)
                if contenido:
                    datos = self.extraer_datos_con_llm(contenido, archivo)
                    if datos:
                        self.cotizaciones.append(datos)

        resultado = {
            "total_cotizaciones": len(self.cotizaciones),
            "cotizaciones": self.cotizaciones
        }

        return json.dumps(resultado, ensure_ascii=False, indent=2)


def main():
    """Función principal para probar la clase"""
    lector = LectorCotizaciones('./emails', 'cotizacion*.html', usar_llm=False)
    resultado = lector.procesar()
    print("Resultado del procesamiento:")
    print(resultado)

    # Analizar el ganador
    if lector.cotizaciones:
        ganador = min(lector.cotizaciones, key=lambda x: x['monto_total'])
        print("\nGanador de la cotización:")
        print(f"Empresa: {ganador['empresa']}")
        print(f"Archivo: {ganador['archivo']}")
        print(f"Monto total: S/. {ganador['monto_total']:.2f}")

if __name__ == "__main__":
    main()