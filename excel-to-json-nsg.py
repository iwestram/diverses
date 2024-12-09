import pandas as pd
import json
from datetime import datetime
import os
from wkt_erzeugen import wkt_for_title
import uuid

# Excel-Datei einlesen
excel_file = 'nsg-normal.xlsx'  # Pfad zur Excel-Datei
df = pd.read_excel(excel_file)

# Erstellen eines Ordners, um die JSON-Dateien zu speichern
output_folder = 'json_output'
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# Funktion zur Umwandlung des referenceDate in ein gültiges ISO-8601-Datum
def format_reference_date(date):
    if pd.isna(date):
        return None  # Falls leer, gebe None zurück
    if isinstance(date, pd.Timestamp):  # Wenn es ein Pandas Timestamp ist, formatiere es
        return date.isoformat()+"Z"
#    return str(date).replace(" ", "T")+"Z"  # Wenn es bereits ein String ist, gebe ihn direkt zurück
    if isinstance(date, datetime):        
        return date.isoformat()+"Z"
    return datetime.strptime(date, '%Y-%m-%d %H:%M:%S').isoformat()+"Z"

json_files = []

# Durch jede Zeile iterieren und JSON-Dokumente erstellen
for index, row in df.iterrows():

    myuuid = uuid.uuid4()
    # Zum Testen einen Stopp einbauen
    if index > 10:
        break

    # Wenn der Titel in Spalte A leer ist, füge Verweise aus Spalte D (title) und Spalte E (url) hinzu
    if pd.isna(row['A']):
        previous_json = json_files[-1]  # Wir holen das zuletzt erstellte JSON-Dokument
        previous_json['resources']['draft']['references'].append({
            "url": row['E'],
            "type": {"key": "9990"},
            "title": row['D'],
            "urlDataType": {"key": "21"}
        })
        continue

    # Erstellen des Basis-JSON-Dokuments
    json_data = {
        "_export_date": datetime.now().isoformat(),
        "_version": "1.1.0",
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
                    "spatialSystems": [{"key": "25833"}],
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
               "subType" : {
                    "key" : "5"
                },
                "extraInfo": {"legalBasicsDescriptions": []},
                "qualities": [],
                "identifier" : str(myuuid),
                # "isOpenData": "true",
                "references": [],
                "resolution": [],
                "dataQuality": {"completenessOmission": {}},
                "description": row['D'],
                "distribution": {"format": []},
                "pointOfContact": [{"ref" : "dbb25aa5-14cc-4d2f-b78c-7c9b0f43c7f5", "type" : {"key" : "7"}}, {"ref" : "dbb25aa5-14cc-4d2f-b78c-7c9b0f43c7f5","type" : {"key" : "12"}}],
                "dataQualityInfo": {"lineage": {"source": {"processStep": {"description": []}, "descriptions": []}}},
                "topicCategories": [{"key": "7"}],
                "keywords": {"gemet": [], "umthes": [],
                "free": [{"label": "Naturschutzgebiet"}]},
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
            "type": {"key": "5302"},
            "title": "Verordnung",
        })

    # Wenn ein Raumbezug (Spalte E) angegeben ist, rufe das WKT ab und füge es hinzu
    if not pd.isna(row['A']):
        wkt = wkt_for_title(row['A'])
        if wkt:
            json_data['resources']['draft']['spatial']['references'].append({
                "wkt": wkt,
                "type": "wkt",
                "title": row['A'],
                "value": None
            })

    # Schreibe das JSON-Dokument in eine Datei
    json_files.append(json_data)

for file_counter, json_file in enumerate(json_files):
    file_name = f"{json_file['resources']['draft']['title']}.json"
    # Stelle sicher, dass der Dateiname keine ungültigen Zeichen enthält
    file_name = file_name.replace("/", "_").replace("\\", "_").replace(":", "_").replace("\"", "")
    # Speicherort und vollständiger Dateiname
    file_path = os.path.join(output_folder, file_name)
    with open(file_path, 'w', encoding='utf-8') as f:
        print(file_name)
    #    if file_name == "Dammühlenfließniederung.json":
    #        print(json_file)
        json.dump(json_file, f, indent=4, ensure_ascii=False)
        print(f"JSON-Dokument gespeichert: {file_path}")

print(f"Fertig! {file_counter + 1} JSON-Dokumente wurden erstellt.")