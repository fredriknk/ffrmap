from flask import Flask, jsonify, render_template, Response
import os
import threading
import socket
import pynmea2
from datetime import datetime
import requests
import random

app = Flask(__name__)

# Your TCP server's IP and port
TCP_IP = os.getenv('TCP_IP', '127.0.0.1')
TCP_PORT = int(os.getenv('TCP_PORT', '9001'))

# Authentication credentials from environment variables
AUTH_USERNAME = os.getenv('AUTH_USERNAME')
AUTH_PASSWORD = os.getenv('AUTH_PASSWORD')

# The URL to fetch images from
IMAGE_URL = os.getenv('IMAGE_URL', 'http://192.168.0.20/dms?')

print("Starting server at {}:{}".format(TCP_IP, TCP_PORT))
# The latest GPS coordinates
latest_coords = None

@app.route('/')
def index():
    return render_template('map.html')

@app.route('/mapnik')
def mapnik():  # Changed function name to 'mapnik'
    return render_template('Mapnik.html')

@app.route('/coords')
def get_coords():
    return jsonify([latest_coords])

@app.route('/image')
def get_image():
    try:
        # Generate a random number and append it to the URL
        random_number = random.random()
        url_with_param = f"{IMAGE_URL}nowprofileid=4&{random_number}"

        response = requests.get(url_with_param, auth=(AUTH_USERNAME, AUTH_PASSWORD))
        response.raise_for_status()
        return Response(response.content, mimetype=response.headers['Content-Type'])
    except requests.RequestException as e:
        return jsonify({'error': str(e)}), 500
def connect_to_gps_server():
    global latest_coords
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((TCP_IP, TCP_PORT))
    print(f"Connected to GPS server at {TCP_IP}:{TCP_PORT}")

    try:
        while True:
            data = s.recv(4096).decode('ascii', errors='ignore')
            if not data:
                raise ConnectionError("Connection lost.")
            # Assuming data is in NMEA format
            for line in data.strip().split('\n'):
                gps_data = parse_gps_data(line)
                if gps_data:
                    # Add a timestamp to the gps_data dictionary
                    timestamp = datetime.utcnow().isoformat() + 'Z'  # Adding 'Z' to indicate UTC time
                    latest_coords = {
                        'latitude': gps_data.latitude,
                        'longitude': gps_data.longitude,
                        'sattelites': gps_data.num_sats,
                        'fix_quality': gps_data.gps_qual,
                        'timestamp': timestamp
                    }
    except Exception as e:
        print(f"Error: {e}")
    finally:
        s.close()
        print("Connection closed.")

def parse_gps_data(nmea_data):
    try:
        msg = pynmea2.parse(nmea_data)
        if hasattr(msg, 'latitude') and hasattr(msg, 'longitude'):
            return msg
    except pynmea2.ParseError as e:
        print(f"Parse error: {e}")
    return None

if __name__ == "__main__":
    threading.Thread(target=connect_to_gps_server, daemon=True).start()
    app.run(debug=True, use_reloader=False)