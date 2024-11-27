import requests
import xml.etree.ElementTree as ET

def extract_polygon_from_file(file_path, title):
    """
    Extrahiert das Polygon aus der XML-Datei anhand des Titels.
    :param file_path: Der Pfad zur Textdatei.
    :param title: Der Titel (app:Gebietsname), nach dem gesucht werden soll.
    :return: Das Polygon als String (gml:polygon).
    """
    tree = ET.parse(file_path)
    root = tree.getroot()

    # Den Namespace definieren, um korrekt auf die Tags zuzugreifen
    namespaces = {
        'app': 'http://www.degree.org/app',  # Ersetze mit dem echten Namespace
        'gml': 'http://www.opengis.net/gml'  # Der Standard-GML Namespace
    }

    # Suche nach dem Titel-Element
    for elem in root.findall('.//app:Gebietsname', namespaces):
        if elem.text == title:
            # Finde das zugehörige Polygon
            polygon_elem = elem.find('.//gml:polygon', namespaces)
            if polygon_elem is not None:
                return polygon_elem.text.strip()  # Gibt das Polygon als String zurück
    return None

def send_polygon_to_service(polygon):
    """
    Sendet das Polygon per POST-Request an den externen Dienst.
    :param polygon: Das Polygon als String (gml:polygon).
    :return: Das WKT des Polygons.
    """
    url = "https://geo-api.informationgrid.eu/v1/convert"  # Ersetze mit der tatsächlichen URL des Dienstes
    headers = {'Content-Type': 'application/json'}

    # Daten für den POST-Request
    data = {
        'polygon': polygon;
        'exportFormat': wkt;
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
        # Polygon an den Dienst senden
        wkt = send_polygon_to_service(polygon)

        if wkt:
            # WKT weiterverarbeiten
            process_wkt(wkt)
        else:
            print("Fehler beim Abrufen des WKT.")
    else:
        print(f"Kein Polygon für den Titel '{title}' gefunden.")

if __name__ == "__main__":
    main()
