from bs4 import BeautifulSoup
import json
from pathlib import Path
import re
import os

class LectorSolicitudCotizacion:

    # Configuración
    ROOT = Path(__file__).resolve().parents[1]
    EMAILS_DIR = ROOT / "emails"

    def __init__(self, ruta_archivo='./emails/solicitud-cotizacion.html'):
        self.ruta_archivo = ruta_archivo
        self.contenido = None
        self.soup = None
        
    def leer_archivo(self):
        """Lee el archivo HTML de solicitud de cotización"""
        try:
            with open(self.ruta_archivo, 'r', encoding='utf-8') as file:
                self.contenido = file.read()
                self.soup = BeautifulSoup(self.contenido, 'html.parser')
                return True
        except FileNotFoundError:
            print(f"Error: No se encontró el archivo {self.ruta_archivo}")
            return False
        except Exception as e:
            print(f"Error al leer el archivo: {str(e)}")
            return False

    
    def parse_table(self, table):
        headers = [th.get_text(strip=True).upper() for th in table.find_all('th')]
        rows = []
        for tr in table.find_all('tr'):
            tds = tr.find_all('td')
            if not tds:
                continue
            cells = [td.get_text(strip=True) for td in tds]
            row = {}
            for i, h in enumerate(headers):
                val = cells[i] if i < len(cells) else ''
                if 'PRODUCT' in h or 'DESCRIP' in h or 'ITEM' in h:
                    row['product'] = val
                if 'CANT' in h:
                    row['quantity'] = val
                if 'UNID' in h or 'UNIT' in h:
                    row['unit'] = val
                if 'P.V.' in h or 'P.V.U.' in h or 'PRECIO' in h or 'UNITARIO' in h or 'PVU' in h:
                    row['unit_price'] = val
                if 'IMP' in h or 'IMPORTE' in h or 'SUBTOTAL' in h:
                    row['importe'] = val
            rows.append(row)
        return rows


    def extraer_datos(self):
        """Extrae los datos relevantes del HTML"""
        if not self.soup:
            return None


        items_solicitados = []
        tables = self.soup.find_all('table')
        if tables:
            for table in tables:
                headers = [th.get_text(strip=True).upper() for th in table.find_all('th')]
                if any(h for h in headers if 'PRODUCT' in h or 'DESCRIP' in h or 'ITEM' in h):
                    rows = self.parse_table(table)
                    for row in rows:
                        items_solicitados.append({
                            'producto': row.get('product'),
                            'cantidad': row.get('quantity'),
                            'unidad': row.get('unit')
                        })

        fecha = None
        # intento razonable de extraer fecha
        fecha_tag = self.soup.find(['fecha', 'date', 'span'], string=re.compile(r'\d{4}-\d{2}-\d{2}')) if self.soup else None
        if fecha_tag:
            fecha = fecha_tag.text.strip()
        else:
            mdate = re.search(r"Enviado el:\s*(.+)", self.soup.get_text(separator='\n')) if self.soup else None
            fecha = mdate.group(1).strip() if mdate else 'No especificada'

        datos = {
            'items_solicitados': items_solicitados,
            'fecha_solicitud': fecha
        }
        return datos


    def procesar(self):
        """Procesa el archivo y devuelve un JSON con toda la información"""
        if not self.leer_archivo():
            return json.dumps({"error": "No se pudo leer el archivo"})
        
        datos = self.extraer_datos()
        if not datos:
            return json.dumps({"error": "No se pudieron extraer los datos"})
        
        return json.dumps(datos, ensure_ascii=False, indent=2)

def main():
    """Función principal para probar la clase"""
    lector = LectorSolicitudCotizacion()
    resultado = lector.procesar()
    print("Resultado del procesamiento:")
    print(resultado)

if __name__ == "__main__":
    main()