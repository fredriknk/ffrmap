import socket
import threading
import random
import time
from geopy.distance import geodesic
from datetime import datetime
import pynmea2
import os

# Constants for the simulation
START_LAT = 59.664024053333335
START_LON = 10.762923273333334
LENGTH = 10  # meters
SPEED = 1.  # m/s (equivalent to 1.08 km/h)
STOPTIME = 10  # seconds
# Your TCP server's IP and port
TCP_IP = os.getenv('TCP_IP', '127.0.0.1')
TCP_PORT = int(os.getenv('TCP_PORT', '9001'))
JITTER_RANGE = 0.00000002  # Range in degrees for GPS jitter

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((TCP_IP, TCP_PORT))
server_socket.listen(5)
print(f"GPS Rover Simulator running at {TCP_IP}:{TCP_PORT}")

def simulate_movement(conn):
    current_position = (START_LAT, START_LON)
    while True:
        # Choose a random bearing between 0 and 360 degrees
        bearing = random.uniform(0, 360)

        # Calculate number of steps and time per step
        steps = LENGTH / SPEED
        time_per_step = 1.0

        for _ in range(int(steps)):
            # Simulate the GPS fixed interval
            time.sleep(time_per_step)

            # Calculate the new position based on speed and bearing
            new_position = geodesic(meters=SPEED * time_per_step).destination(current_position, bearing)
            current_position = (new_position.latitude, new_position.longitude)

            # Send updated position
            send_gga_sentence(conn, current_position)

        # Simulate standing still with jitter
        for _ in range(int(STOPTIME)):
            time.sleep(1)  # Simulate a position update every second
            # Apply jitter
            jittered_position = (
                current_position[0] + random.uniform(-JITTER_RANGE, JITTER_RANGE),
                current_position[1] + random.uniform(-JITTER_RANGE, JITTER_RANGE)
            )
            # Send jittered position
            send_gga_sentence(conn, jittered_position)

def send_gga_sentence(conn, position):
    lat_deg = int(position[0])
    lat_min = (position[0] - lat_deg) * 60
    lon_deg = int(position[1])
    lon_min = (position[1] - lon_deg) * 60
    current_utc_time = datetime.utcnow().strftime('%H%M%S')

    gga = pynmea2.GGA('GP', 'GGA', (
        current_utc_time,
        '%02d%07.4f' % (lat_deg, lat_min), 'N',
        '%03d%07.4f' % (lon_deg, lon_min), 'E',
        '8',  # GPS Quality Indicator (1 = Fix)
        '05',  # Number of satellites in use
        '1.2',  # Horizontal dilution of position
        '10.1', 'M',  # Altitude, Meters, above mean sea level
        '0.0', 'M',  # Height of geoid (mean sea level) above WGS84 ellipsoid
        '',  # Time in seconds since last DGPS update
        '',  # DGPS station ID number
    ))
    gga_sentence = str(gga)
    conn.sendall(gga_sentence.encode())

def handle_client(connection, client_address):
    try:
        print('Connection from', client_address)
        simulate_movement(connection)
    except Exception as e:
        print(f"Error with {client_address}: {e}")
    finally:
        connection.close()

def accept_connections():
    while True:
        print('Waiting for a connection...')
        connection, client_address = server_socket.accept()
        # Use a thread to handle connection so that the main server can accept other connections
        client_thread = threading.Thread(target=handle_client, args=(connection, client_address))
        client_thread.daemon = True
        client_thread.start()

if __name__ == "__main__":
    # Start the TCP server thread
    server_thread = threading.Thread(target=accept_connections, daemon=True)
    server_thread.start()

    try:
        # Prevent the main thread from exiting
        input("Press Enter to stop the simulator...\n")
    finally:
        server_socket.close()
        print("GPS Rover Simulator stopped.")