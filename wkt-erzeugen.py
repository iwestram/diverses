import requests
import xml.etree.ElementTree as ET
from urllib.parse import urlencode

def extract_polygon_from_file(file_path, title):
    """
    Extrahiert das Polygon aus der XML-Datei anhand des Titels.
    :param file_path: Der Pfad zur Textdatei.
    :param title: Der Titel (app:Gebietsname), nach dem gesucht werden soll.
    :return: Das Polygon als String (gml:polygon).
    """
    tree = ET.parse(file_path)
    root = tree.getroot()

    # Den Namespace definieren, um korrekt auf die Tags zuzugreifen.
    namespaces = {
        'app': 'http://www.degree.org/app',  # Ersetze mit dem echten Namespace
        'gml': 'http://www.opengis.net/gml/3.2',  # Der Standard-GML Namespace
        'wfs': 'http://www.opengis.net/wfs/2.0' # Der Namespace für WFS, wenn er benötigt wird.
    }

    # Suche nach dem Titel-Element
    for elem in root.findall('.//app:Gebietsname', namespaces):
        if elem.text == title:
            # Wenn der titel gefunden wird, suchen wir nach dem element app:the_geom
            the_geom_elem = elem.find('.//app:the_geom', namespaces)
            if the_geom_elem is not None:
                # Nun extrahieren wir das Polygon innerhalb von app:the_geom
                multi_surface_elem = the_geom_elem.find('.//gml:MultiSurface', namespaces)
                if multi_surface_elem is not None:
                    return multi_surface_elem.text.strip()  # Gibt das Polygon als String zurück
    return None

def send_polygon_to_service(polygon):
    """
    Sendet das Polygon per POST-Request an den externen Dienst.
    :param polygon: Das Polygon als String (gml:polygon).
    :param export_format: Das gewünschte Exportformat (z.B. "WKT", "GeoJSON", "GML").    
    :return: Das WKT des Polygons.
    """
    base_url = "https://geo-api.informationgrid.eu/v1/convert"  # Ersetze mit der tatsächlichen URL des Dienstes

    # URL-Parameter für exportFormat

    query_params = {
        'exportFormat': wkt
    }

    # Die URL mit den Query-Parametern zusammenbauen
    url = f"{base_url}?{urlencode(query_params)}"

    headers = {'Content-Type': 'application/json'}

    # Daten für den POST-Request
    data = {
        'polygon': polygon
    }

    response = requests.post(url, json=data, headers=headers)

    if response.status_code == 200:
        # Extrahiere das WKT aus der Antwort
        return response.json().get('wkt')
    else:
        print(f"Fehler beim Abrufen des WKT: {response.status_code}")
        return None

def process_wkt(wkt):
    """
    Weiterverarbeitung des WKT (z. B. Ausgabe, Speicherung, Analyse).
    :param wkt: Das WKT des Polygons.
    """
    print("Empfangenes WKT:", wkt)
    # Hier kannst du das WKT weiterverarbeiten (z. B. in eine Datei speichern oder analysieren).

def main():
    # Datei und Titel definieren
    file_path = "nsg.xml"  # Pfad deiner XML-Datei
    title = "Oberheide"  # Titel, nach dem du suchst

    # Polygon extrahieren
    polygon = extract_polygon_from_file(file_path, title)

    if polygon:
        print(f"Polygon gefunden!")
        # Polygon an den Dienst senden
        #wkt = send_polygon_to_service(polygon)

        #if wkt:
            # WKT weiterverarbeiten
        #    process_wkt(wkt)
        #else:
        #    print("Fehler beim Abrufen des WKT.")
    else:
        print(f"Kein Polygon für den Titel '{title}' gefunden.")

if __name__ == "__main__":
    main()
