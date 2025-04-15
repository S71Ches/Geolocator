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


# 🧾 Отдача OpenAPI YAML для GPTs
@app.route("/openapi.yaml")
def serve_openapi():
    return send_file("openapi.yaml", mimetype="text/yaml")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
