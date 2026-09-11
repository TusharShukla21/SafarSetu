import os

from dotenv import load_dotenv


# =========================================================
# LOAD ENVIRONMENT VARIABLES
# =========================================================

load_dotenv()


# =========================================================
# APPLICATION CONFIGURATION
# =========================================================

class Config:

    # Flask secret key
    SECRET_KEY = os.getenv(
        "SECRET_KEY",
        "safar-setu-development-secret-key"
    )

    # SQLite database
    DATABASE = os.path.join(
        os.path.dirname(__file__),
        "database.db"
    )

    # Weather API
    WEATHER_API_KEY = os.getenv(
        "WEATHER_API_KEY",
        ""
    )

    # Google Maps API
    # Currently not required.
    # Maps will use direct Google Maps links.
    GOOGLE_MAPS_API_KEY = os.getenv(
        "GOOGLE_MAPS_API_KEY",
        ""
    )

    # Application name
    APP_NAME = "Safar Setu"

    # Maximum trip duration
    MAX_TRIP_DAYS = 30