import threading
from dotenv import load_dotenv
load_dotenv()  # This will load environment variables from a .env file
from app import app, connect_to_gps_server


if __name__ == "__main__":
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
        app.shutdown_server()