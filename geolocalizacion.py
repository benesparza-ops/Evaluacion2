import requests
import urllib.parse

geocode_url = "https://graphhopper.com/api/1/geocode?"
route_url = "https://graphhopper.com/api/1/route?"
key = "32db2b79-a8fb-4a00-b20f-5c93c8fcab65"


def geocodificar(localizacion, key):
    while localizacion == "":
        localizacion = input("Por favor, ingrese una localización válida: ")

    url = (
        geocode_url
        + urllib.parse.urlencode({"q": localizacion, "limit": "1", "key": key})
    )
    reply = requests.get(url)
    json_data = reply.json()
    json_status = reply.status_code

    if json_status == 200 and len(json_data["hits"]) != 0:
        lat = json_data["hits"][0]["point"]["lat"]
        lng = json_data["hits"][0]["point"]["lng"]
        nombre = json_data["hits"][0]["name"]
        pais = json_data["hits"][0].get("country", "")
        estado = json_data["hits"][0].get("state", "")

        if estado != "" and pais != "":
            nuevo_nombre = f"{nombre}, {estado}, {pais}"
        elif pais != "":
            nuevo_nombre = f"{nombre}, {pais}"
        else:
            nuevo_nombre = nombre

        return json_status, lat, lng, nuevo_nombre
    else:
        print(
            f"\n[ERROR] Estado HTTP {json_status}: No se encontró '{localizacion}'."
        )
        return json_status, None, None, localizacion


while True:
    print("\n" + "=" * 60)
    print("      SISTEMA DE GEOLOCALIZACIÓN Y RUTAS - BIBLIOTECA")
    print("=" * 60)

    origen = input(
        "\nIngrese la ciudad de Origen (o 's' / 'salir' para finalizar): "
    ).strip()
    if origen.lower() in ["s", "salir"]:
        print(
            "\n¡Gracias por utilizar el sistema de geolocalización! Hasta luego."
        )
        break

    destino = input(
        "Ingrese la ciudad de Destino (o 's' / 'salir' para finalizar): "
    ).strip()
    if destino.lower() in ["s", "salir"]:
        print(
            "\n¡Gracias por utilizar el sistema de geolocalización! Hasta luego."
        )
        break

    status_orig, lat_orig, lng_orig, nombre_orig = geocodificar(origen, key)
    if status_orig != 200 or lat_orig is None:
        continue

    status_dest, lat_dest, lng_dest, nombre_dest = geocodificar(destino, key)
    if status_dest != 200 or lat_dest is None:
        continue

    print("\n" + "-" * 60)
    print(f" Calculando ruta: {nombre_orig} ---> {nombre_dest}")
    print("-" * 60)

    opciones_ruta = [
        ("point", f"{lat_orig},{lng_orig}"),
        ("point", f"{lat_dest},{lng_dest}"),
        ("vehicle", "car"),
        ("locale", "es"),
        ("key", key),
    ]

    url_ruta = route_url + urllib.parse.urlencode(opciones_ruta)
    respuesta_ruta = requests.get(url_ruta)
    status_ruta = respuesta_ruta.status_code
    datos_ruta = respuesta_ruta.json()

    print(f"Estado de la respuesta de ruta (HTTP): {status_ruta}")

    if status_ruta == 200:
        distancia_m = datos_ruta["paths"][0]["distance"]
        tiempo_ms = datos_ruta["paths"][0]["time"]

        distancia_km = distancia_m / 1000
        distancia_mili = distancia_km * 0.621371

        segundos = int((tiempo_ms / 1000) % 60)
        minutos = int((tiempo_ms / (1000 * 60)) % 60)
        horas = int((tiempo_ms / (1000 * 60 * 60)))

        print(
            f"Distancia Total : {distancia_km:.2f} km ({distancia_mili:.2f} millas)"
        )
        print(
            f"Tiempo Estimado : {horas:02d}h {minutos:02d}m {segundos:02d}s"
        )

        print("\nINSTRUCCIONES DE NAVEGACIÓN PASO A PASO (NARRATIVA):")
        print("-" * 60)

        instrucciones = datos_ruta["paths"][0]["instructions"]
        for i, paso in enumerate(instrucciones, 1):
            texto = paso["text"]
            dist_paso_km = paso["distance"] / 1000
            print(f"{i:02d}. {texto} ({dist_paso_km:.2f} km)")
    else:
        print(
            "\n[ERROR] No se pudo calcular la ruta entre las ubicaciones indicadas."
        )
