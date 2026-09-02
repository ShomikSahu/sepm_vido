import urllib.request
import zlib
import os

def plantuml_encode(plantuml_text):
    utf8_bytes = plantuml_text.encode('utf-8')
    compressed = zlib.compress(utf8_bytes)[2:-4]
    
    plantuml_alphabet = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz-_'
    
    def encode_6bit(b):
        return plantuml_alphabet[b & 0x3f]

    res = []
    i = 0
    while i < len(compressed):
        c1 = compressed[i]
        c2 = compressed[i+1] if i+1 < len(compressed) else 0
        c3 = compressed[i+2] if i+2 < len(compressed) else 0
        
        b1 = c1 >> 2
        b2 = ((c1 & 0x3) << 4) | (c2 >> 4)
        b3 = ((c2 & 0xf) << 2) | (c3 >> 6)
        b4 = c3 & 0x3f
        
        res.append(encode_6bit(b1))
        res.append(encode_6bit(b2))
        if i + 1 < len(compressed):
            res.append(encode_6bit(b3))
        if i + 2 < len(compressed):
            res.append(encode_6bit(b4))
        i += 3
    return ''.join(res)

def render_puml(puml_text, output_png_path):
    encoded = plantuml_encode(puml_text)
    url = f"http://www.plantuml.com/plantuml/png/{encoded}"
    print(f"Fetching PlantUML PNG from {url} ...")
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req) as response:
        png_data = response.read()
    os.makedirs(os.path.dirname(output_png_path), exist_ok=True)
    with open(output_png_path, "wb") as f:
        f.write(png_data)
    print(f"Saved PNG to {output_png_path} ({len(png_data)} bytes)")

use_case_puml = """@startuml
left to right direction
skinparam packageStyle rectangle
hide circle
skinparam classAttributeIconSize 0

actor User

rectangle "Volcanic Image/Data Observatory (VIDO)" {
    usecase "UC-01 Browse Celestial Systems" as UC1
    usecase "UC-02 Search & Filter Observations" as UC2
    usecase "UC-03 Inspect Metadata Payloads" as UC3
    usecase "UC-04 Associate Observations with Events" as UC4
    usecase "UC-05 Explore Synchronized Timeline" as UC5
    usecase "UC-06 Explore Spatial Coordinates" as UC6
}

User -- UC1
User -- UC2
User -- UC3
User -- UC4
User -- UC5
User -- UC6
@enduml
"""

class_puml = """@startuml
hide circle
skinparam classAttributeIconSize 0

class CelestialBody {
    id
    name
    coordinate_convention
    mean_radius
}

class VolcanicSystem {
    id
    name
    region
    elevation
    status
    latitude
    longitude
}

class ObservationSource {
    id
    name
    source_type
}

class Observation {
    id
    timestamp
    latitude
    longitude
    metadata
}

class VolcanicEvent {
    id
    name
    start_time
    end_time
    vei
}

class ObservationEventLink {
    id
    relationship_type
    temporal_offset_hours
}

CelestialBody "1" -- "*" VolcanicSystem
VolcanicSystem "1" -- "*" Observation
ObservationSource "1" -- "*" Observation
Observation "1" -- "*" ObservationEventLink
VolcanicEvent "1" -- "*" ObservationEventLink
@enduml
"""

if __name__ == "__main__":
    os.makedirs("docs/plantuml", exist_ok=True)
    with open("docs/plantuml/use_case_diagram.puml", "w") as f:
        f.write(use_case_puml)
    with open("docs/plantuml/class_diagram.puml", "w") as f:
        f.write(class_puml)
    
    render_puml(use_case_puml, "docs/plantuml/use_case_diagram.png")
    render_puml(class_puml, "docs/plantuml/class_diagram.png")
