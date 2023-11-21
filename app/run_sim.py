import threading
import rover_simulator
from app import app, connect_to_gps_server


if __name__ == "__main__":
    # Start the TCP server thread
    rover_thread = threading.Thread(target=rover_simulator.accept_connections, daemon=True)
    rover_thread.start()
    # Start the GPS server connection thread
    gps_thread = threading.Thread(target=connect_to_gps_server, daemon=True)
    gps_thread.start()

    # Start the Flask application
    flask_thread = threading.Thread(target=lambda: app.run(debug=True, use_reloader=False))
    flask_thread.start()
    try:
        # Prevent the main thread from exiting
        input("Press Enter to stop the simulator...\n")
    except (KeyboardInterrupt, SystemExit):
        print("Stopping the simulator...")
        flask_thread.terminate()
        gps_thread.terminate()
        rover_thread.terminate()
        app.shutdown_server()