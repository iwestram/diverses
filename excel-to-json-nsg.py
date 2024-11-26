import pandas as pd
#import requests
import json
from datetime import datetime
import os

# Funktion zum Abrufen von WKT-Daten basierend auf einem Titel
#def get_wkt_from_external_service(title):
#    try:
#        # Beispiel-URL für den externen Dienst (dies muss angepasst werden)
#        url = f"https://example.com/api/get_wkt?title={title}"
#        response = requests.get(url)
#        response.raise_for_status()  # Sicherstellen, dass der Request erfolgreich war
#        data = response.json()
#        return data.get("wkt", None)  # WKT aus der Antwort extrahieren
#    except Exception as e:
#        print(f"Fehler beim Abrufen von WKT für {title}: {e}")
#        return None

# Excel-Datei einlesen
excel_file = 'neueVersion-ohneAlphabet-ohneAenderung-ohnedoppeltesDatum.xlsx'  # Pfad zur Excel-Datei
df = pd.read_excel(excel_file)

# Erstellen eines Ordners, um die JSON-Dateien zu speichern
output_folder = 'json_output_4'
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# Initialisierung der letzten JSON-Dokumente
previous_json = None

# Zähler für Dateien, die keinen Titel in Spalte A haben
file_counter = 1

# Funktion zur Umwandlung des referenceDate in ein gültiges ISO-8601-Datum
def format_reference_date(date):
    if pd.isna(date):
        return None  # Falls leer, gebe None zurück
    if isinstance(date, pd.Timestamp):  # Wenn es ein Pandas Timestamp ist, formatiere es
        return date.isoformat()
    return str(date)  # Wenn es bereits ein String ist, gebe ihn direkt zurück

json_files = []

# Durch jede Zeile iterieren und JSON-Dokumente erstellen
for index, row in df.iterrows():

    # Wenn der Titel in Spalte A leer ist, füge Verweise aus Spalte D (title) und Spalte E (url) hinzu
    if pd.isna(row['A']):
        previous_json = json_files[-1]  # Wir holen das zuletzt erstellte JSON-Dokument
        previous_json['resources']['draft']['references'].append({
            "url": row['E'],
            "type": {"key": "9990"},
            "title": row['D'],
            "referenceType": "url",
            "urlDataType": {"key": "21"}
        })
        continue

    # Erstellen des Basis-JSON-Dokuments
    json_data = {
        "_export_date": datetime.now().isoformat(),
        "_version": "1.2.0",
        "_profile": "ingrid",
        "resources": {
            "draft": {
                "dataset": {
                    "languages": ["150"]
                },
                "lineage": {
                    "statement": "Naturschutzgebiete in Brandenburg"
                },
                "spatial": {
                    "references": [],
                    "spatialSystems": [{"key": "84"}],
                    "verticalExtent": {"unitOfMeasure": None}
                },
                "keywords": {
                    "free": [],
                    "gemet": [],
                    "umthes": []
                },
                "metadata": {
                    "language": {"key": "150"},
                    "characterSet": None
                },
                "resource": {
                    "useConstraints": [{"title": {"key": "26"}}],
                    "accessConstraints": []
                },
                "temporal": {
                    "events": [{"referenceDate": format_reference_date(row['C']),
                                "referenceDateType": {"key": "1"}}],
                    "status": None,
                    "resourceDateType": None
                },
                "extraInfo": {"legalBasicsDescriptions": []},
                "qualities": [],
                "properties": {"subType": {"key": "5"}},
                "references": [],
                "resolution": [],
                "dataQuality": {"completenessOmission": {}},
                "description": row['D'],
                "distribution": {"format": []},
                "pointOfContact": [],
                "dataQualityInfo": {"lineage": {"source": {"processStep": {"description": []}, "descriptions": []}}},
                "topicCategories": [{"key": "7"}],
                "advProductGroups": [],
                "graphicOverviews": [],
                "digitalTransferOptions": [],
                "maintenanceInformation": {"maintenanceAndUpdateFrequency": None, "userDefinedMaintenanceFrequency": {"unit": None}},
                "portrayalCatalogueInfo": {"citation": []},
                "spatialRepresentationType": [],
                "featureCatalogueDescription": {"citation": [], "featureTypes": []},
                "absoluteExternalPositionalAccuracy": {},
                "title": row['A'],
                "_type": "InGridGeoDataset"
            }
        }
    }

    # Füge den URL-Verweis hinzu
    if not pd.isna(row['B']):
        json_data['resources']['draft']['references'].append({
            "url": row['B'],
            "type": {"key": "9999"},
            "title": "Verordnung",
            "referenceType": "url"
        })

    # Wenn ein Raumbezug (Spalte E) angegeben ist, rufe das WKT ab und füge es hinzu
    #if not pd.isna(row['E']):
    #    wkt = get_wkt_from_external_service(row['E'])
    #    if wkt:
    #        json_data['resources']['draft']['spatial']['references'].append({
    #            "wkt": wkt,
    #            "type": "wkt",
    #            "title": row['E'],
    #            "value": None
    #        })

    # Speichere das aktuelle JSON-Dokument in eine Datei
    if pd.notna(row['A']):
        # Verwende den Titel aus Spalte A als Dateinamen
        file_name = f"{row['A']}.json"
    else:
        # Wenn der Titel leer ist, verwende einen fortlaufenden Zähler
        file_name = f"document_{file_counter}.json"
        file_counter += 1

    # Schreibe das JSON-Dokument in eine Datei
    json_files.append(json_data)

for file_counter, json_file in enumerate(json_files):
    # Stelle sicher, dass der Dateiname keine ungültigen Zeichen enthält
    file_name = file_name.replace("/", "_").replace("\\", "_").replace(":", "_").replace("\"", "")
    # Speicherort und vollständiger Dateiname
    file_path = os.path.join(output_folder, file_name)
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(json_file, f, indent=4, ensure_ascii=False)
        print(f"JSON-Dokument gespeichert: {file_path}")

print(f"Fertig! {file_counter + 1} JSON-Dokumente wurden erstellt.")