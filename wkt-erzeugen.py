import os
import requests
import xml.etree.ElementTree as ET
from urllib.parse import urlencode


# Den Namespace definieren, um korrekt auf die Tags zuzugreifen.
namespaces = {
    'app': 'http://www.deegree.org/app',  # Ersetze mit dem echten Namespace
    'gml': 'http://www.opengis.net/gml/3.2',  # Der Standard-GML Namespace
    'wfs': 'http://www.opengis.net/wfs/2.0' # Der Namespace für WFS, wenn er benötigt wird.
}
for prefix, uri in namespaces.items():
    ET.register_namespace(prefix, uri)


def extract_geometry_from_file(file_path, title):
    """
    Extrahiert die Geometrie aus der XML-Datei anhand des Titels.
    :param file_path: Der Pfad zur Textdatei.
    :param title: Der Titel (app:Gebietsname), nach dem gesucht werden soll.
    :return: Die Geometrie als String (gml:*).
    """
    tree = ET.parse(file_path)
    geometry_elem = tree.find(f'.//app:nsg[app:Gebietsname = "{title}"]/app:the_geom/*', namespaces)

    if geometry_elem is not None:
        return ET.tostring(geometry_elem, encoding='unicode') # Gibt die Geometrie als String zurück
    return None

def send_geometry_to_service(geometry):
    """
    Sendet die Geometrie per POST-Request an den externen Dienst.
    :param geometry: Die Geometrie als String (gml:*).
    :param export_format: Das gewünschte Exportformat (z.B. "WKT", "GeoJSON", "GML").
    :return: Das WKT der Geometrie.
    """
    base_url = "https://geo-api.informationgrid.eu/v1/convert"  # Ersetze mit der tatsächlichen URL des Dienstes
    query_params = {
        'exportFormat': 'wkt'
    }
    headers = {'Content-Type': 'application/xml'}
    auth = (os.environ["API_USER"], os.environ["API_PASSWORD"])

    response = requests.post(base_url, params=query_params, data=geometry, headers=headers, auth=auth)
    try:
        response.raise_for_status()
    except:
        print(f"Fehler beim Abrufen des WKT: {response.status_code}")
        return None
    # Extrahiere das WKT aus der Antwort
    return response.text

def process_wkt(wkt):
    """
    Weiterverarbeitung des WKT (z. B. Ausgabe, Speicherung, Analyse).
    :param wkt: Das WKT der Geometrie.
    """
    print("Empfangenes WKT:", wkt)
    # Hier kannst du das WKT weiterverarbeiten (z. B. in eine Datei speichern oder analysieren).

def main():
    # Prüfen, ob die Umgebungsvariablen API_USER und API_PASSWORD gesetzt sind
    if "API_USER" not in os.environ or "API_PASSWORD" not in os.environ:
        print("Umgebungsvariablen API_USER und API_PASSWORD müssen gesetzt sein.")
        exit()

    # Datei und Titel definieren
    file_path = "nsg.xml"  # Pfad deiner XML-Datei
    title = "Oberheide"  # Titel, nach dem du suchst

    # Geometrie extrahieren
    geometry = extract_geometry_from_file(file_path, title)

    if geometry:
        print(f"Geometrie gefunden!")
        # Geometrie an den Dienst senden
        wkt = send_geometry_to_service(geometry)

        if wkt:
            # WKT weiterverarbeiten
           process_wkt(wkt)
        else:
           print("Fehler beim Abrufen des WKT.")
    else:
        print(f"Keine Geometrie für den Titel '{title}' gefunden.")

if __name__ == "__main__":
    main()
