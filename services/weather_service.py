import requests

from config import Config


# =========================================================
# OPENWEATHER API
# =========================================================

WEATHER_URL = (
    "https://api.openweathermap.org/data/2.5/weather"
)


# =========================================================
# GET CURRENT WEATHER
# =========================================================

def get_current_weather(city):
    """
    Fetches current weather information for a city.

    Returns:
        Dictionary containing weather information
        or None if the request fails.
    """

    # -----------------------------------------------------
    # Check API key
    # -----------------------------------------------------

    if not Config.WEATHER_API_KEY:

        print(
            "Weather API key is not configured."
        )

        return None


    # -----------------------------------------------------
    # API parameters
    # -----------------------------------------------------

    params = {

        "q": city,

        "appid": Config.WEATHER_API_KEY,

        "units": "metric"

    }


    try:

        # -------------------------------------------------
        # API request
        # -------------------------------------------------

        response = requests.get(

            WEATHER_URL,

            params=params,

            timeout=10

        )


        # -------------------------------------------------
        # Check response
        # -------------------------------------------------

        if response.status_code != 200:

            print(
                "Weather API Error:",
                response.status_code
            )

            return None


        data = response.json()


        # -------------------------------------------------
        # Extract useful information
        # -------------------------------------------------

        weather = {

            "city":
                data.get(
                    "name",
                    city
                ),

            "country":
                data.get(
                    "sys",
                    {}
                ).get(
                    "country",
                    ""
                ),

            "temperature":
                round(
                    data.get(
                        "main",
                        {}
                    ).get(
                        "temp",
                        0
                    )
                ),

            "feels_like":
                round(
                    data.get(
                        "main",
                        {}
                    ).get(
                        "feels_like",
                        0
                    )
                ),

            "humidity":
                data.get(
                    "main",
                    {}
                ).get(
                    "humidity",
                    0
                ),

            "pressure":
                data.get(
                    "main",
                    {}
                ).get(
                    "pressure",
                    0
                ),

            "condition":
                data.get(
                    "weather",
                    [{}]
                )[0].get(
                    "main",
                    "Unknown"
                ),

            "description":
                data.get(
                    "weather",
                    [{}]
                )[0].get(
                    "description",
                    "Weather information unavailable"
                ),

            "wind_speed":
                data.get(
                    "wind",
                    {}
                ).get(
                    "speed",
                    0
                ),

            "visibility":
                data.get(
                    "visibility",
                    0
                )

        }


        return weather


    # -----------------------------------------------------
    # Network error
    # -----------------------------------------------------

    except requests.RequestException as error:

        print(
            "Weather request failed:",
            error
        )

        return None


    # -----------------------------------------------------
    # Unexpected error
    # -----------------------------------------------------

    except Exception as error:

        print(
            "Weather processing failed:",
            error
        )

        return None
