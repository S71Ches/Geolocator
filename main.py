from flask import Flask, request, jsonify, send_file  # добавили send_file
import requests

app = Flask(__name__)

GOOGLE_MAPS_API_KEY = "AIzaSyBl4AG5rWjlbUtdQytBcCtqP0nBUWcNpD8"

# 🔍 Получить координаты по адресу
@app.route("/get-coordinates", methods=["GET"])
def get_coordinates():
    address = request.args.get("address")

    if not address:
        return jsonify({"error": "Missing address"}), 400

    print(f"[DEBUG] Получен адрес от GPTs: {address}")

    url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {
        "address": address,
        "key": GOOGLE_MAPS_API_KEY,
    }

    response = requests.get(url, params=params)
    print(f"[DEBUG] Запрос в Google: {response.url}")
    data = response.json()
    print(f"[DEBUG] Ответ от Google: {data}")

    if data["status"] != "OK":
        return jsonify({"error": "Geocoding failed", "status": data["status"]}), 500

    location = data["results"][0]["geometry"]["location"]
    return jsonify({
        "lat": location["lat"],
        "lon": location["lng"]
    })

# 📍 Получить адрес по координатам
@app.route("/get-location", methods=["GET"])
def get_location():
    lat = request.args.get("lat")
    lon = request.args.get("lon")

    print(f"[DEBUG] Получен запрос от GPTs с параметрами: lat={lat}, lon={lon}")

    if not lat or not lon:
        return jsonify({"error": "Missing coordinates"}), 400

    url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {
        "latlng": f"{lat},{lon}",
        "key": GOOGLE_MAPS_API_KEY,
        "result_type": "street_address"
    }

    response = requests.get(url, params=params)
    print(f"[DEBUG] Запрос в Google: {response.url}")
    data = response.json()
    print(f"[DEBUG] Ответ от Google: {data}")

    if data["status"] != "OK":
        return jsonify({"error": "Geocoding failed", "status": data["status"]}), 500

    address = data["results"][0]["formatted_address"]
    return jsonify({"address": address})


# ➡️ Построить маршрут между точками через Google Directions API
@app.route("/get-route", methods=["GET"])
def get_route():
    origin = request.args.get("origin")  # например "49.033,36.229"
    destination = request.args.get("destination")  # например "49.067,36.254"
    mode = request.args.get("mode", "driving")  # по умолчанию driving

    if not origin or not destination:
        return jsonify({"error": "Missing origin or destination"}), 400

    print(f"[DEBUG] Построение маршрута от {origin} до {destination}, режим {mode}")

    url = "https://maps.googleapis.com/maps/api/directions/json"
    params = {
        "origin": origin,
        "destination": destination,
        "mode": mode,
        "key": GOOGLE_MAPS_API_KEY,
    }

    response = requests.get(url, params=params)
    print(f"[DEBUG] Запрос в Google: {response.url}")
    data = response.json()
    print(f"[DEBUG] Ответ от Google: {data}")

    if data["status"] != "OK":
        return jsonify({"error": "Directions API failed", "status": data["status"]}), 500

    route = data["routes"][0]["legs"][0]

    steps = []
    for step in route["steps"]:
        instruction = step.get("html_instructions", "")
        distance_step = step.get("distance", {}).get("value", 0)
        steps.append({
            "instruction": instruction,
            "distance": distance_step
        })

    return jsonify({
        "distance": route["distance"]["value"],
        "duration": route["duration"]["value"],
        "steps": steps
    })




# 🌳 Найти интересные места рядом с точкой через Google Places API
@app.route("/find-places", methods=["GET"])
def find_places():
    location = request.args.get("location")  # например "49.033,36.229"
    radius = request.args.get("radius", 1000)  # радиус поиска в метрах, по умолчанию 1000
    place_type = request.args.get("type", "tourist_attraction")  # тип места

    if not location:
        return jsonify({"error": "Missing location"}), 400

    print(f"[DEBUG] Поиск мест возле {location} с радиусом {radius}м, тип {place_type}")

    url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    params = {
        "location": location,
        "radius": radius,
        "type": place_type,
        "key": GOOGLE_MAPS_API_KEY,
    }

    response = requests.get(url, params=params)
    print(f"[DEBUG] Запрос в Google: {response.url}")
    data = response.json()
    print(f"[DEBUG] Ответ от Google: {data}")

    if data.get("status") != "OK":
        return jsonify({"error": "Places API failed", "status": data.get("status")}), 500

    places = []
    for result in data.get("results", []):
        place = {
            "name": result.get("name"),
            "address": result.get("vicinity"),
            "location": {
                "lat": result["geometry"]["location"]["lat"],
                "lng": result["geometry"]["location"]["lng"]
            }
        }
        places.append(place)

    return jsonify({"places": places})


# ⛰️ Получить профиль высот вдоль маршрута через Google Elevation API
@app.route("/get-elevation", methods=["GET"])
def get_elevation():
    path = request.args.get("path")  # список точек через |

    if not path:
        return jsonify({"error": "Missing path parameter"}), 400

    print(f"[DEBUG] Запрос профиля высот для пути: {path}")

    url = "https://maps.googleapis.com/maps/api/elevation/json"
    params = {
        "path": path,
        "samples": 100,  # количество точек выборки по пути
        "key": GOOGLE_MAPS_API_KEY,
    }

    response = requests.get(url, params=params)
    print(f"[DEBUG] Запрос в Google: {response.url}")
    data = response.json()
    print(f"[DEBUG] Ответ от Google: {data}")

    if data.get("status") != "OK":
        return jsonify({"error": "Elevation API failed", "status": data.get("status")}), 500

    elevations = []
    for result in data.get("results", []):
        elevation_point = {
            "location": {
                "lat": result["location"]["lat"],
                "lng": result["location"]["lng"],
            },
            "elevation": result["elevation"]
        }
        elevations.append(elevation_point)

    return jsonify({"elevations": elevations})


# ☀️ Получить прогноз погоды по координатам на указанную дату через Google Weather API
@app.route("/get-weather", methods=["GET"])
def get_weather():
    lat = request.args.get("lat")
    lon = request.args.get("lon")
    date = request.args.get("date")  # формат YYYY-MM-DD

    if not lat or not lon or not date:
        return jsonify({"error": "Missing lat, lon or date parameters"}), 400

    print(f"[DEBUG] Запрос погоды для координат: {lat}, {lon} на дату {date}")

    # Пример для Google Weather API (Environment Data)
    url = f"https://weather.googleapis.com/v1/weather:lookup"
    params = {
        "location.latitude": lat,
        "location.longitude": lon,
        "timestamp": f"{date}T12:00:00Z",  # фиксируем время для точности
        "key": GOOGLE_MAPS_API_KEY,
    }

    response = requests.get(url, params=params)
    print(f"[DEBUG] Запрос в Google Weather: {response.url}")
    data = response.json()
    print(f"[DEBUG] Ответ от Google Weather: {data}")

    if "currentWeather" not in data:
        return jsonify({"error": "Weather API failed or unsupported response"}), 500

    weather = data["currentWeather"]

    return jsonify({
        "temperature": weather.get("temperature", 0),
        "condition": weather.get("conditions", "unknown"),
        "precipitation": weather.get("precipitationIntensity", 0),
        "wind_speed": weather.get("windSpeed", 0)
    })


# 🧾 Отдача OpenAPI YAML для GPTs
@app.route("/openapi.yaml")
def serve_openapi():
    return send_file("openapi.yaml", mimetype="text/yaml")


# 👋 Пинг для Render'а
@app.route("/", methods=["GET"])
def wake():
    return jsonify({"status": "awake"}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
