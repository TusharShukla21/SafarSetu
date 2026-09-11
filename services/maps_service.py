from urllib.parse import quote_plus


# =========================================================
# GOOGLE MAPS LINK SERVICE
# =========================================================

def create_maps_link(place_name, location=None):
    """
    Creates a Google Maps search link.

    No Google Maps API key is required.

    Example:
        create_maps_link("Fort Aguada", "Goa")

    Returns:
        Google Maps search URL
    """

    # -----------------------------------------------------
    # Create search text
    # -----------------------------------------------------

    if location:

        search_text = f"{place_name}, {location}"

    else:

        search_text = place_name


    # -----------------------------------------------------
    # Encode search text
    # -----------------------------------------------------

    encoded_search = quote_plus(
        search_text
    )


    # -----------------------------------------------------
    # Generate Google Maps URL
    # -----------------------------------------------------

    maps_url = (
        "https://www.google.com/maps/search/?api=1"
        f"&query={encoded_search}"
    )


    return maps_url


# =========================================================
# CREATE ROUTE LINK
# =========================================================

def create_route_link(
    source,
    destination,
    travel_mode="driving"
):
    """
    Creates a Google Maps direction/route link.

    travel_mode can be:
        driving
        walking
        bicycling
        transit
    """

    encoded_source = quote_plus(
        source
    )

    encoded_destination = quote_plus(
        destination
    )


    maps_url = (
        "https://www.google.com/maps/dir/?api=1"
        f"&origin={encoded_source}"
        f"&destination={encoded_destination}"
        f"&travelmode={travel_mode}"
    )


    return maps_url


# =========================================================
# CREATE PLACE LINK
# =========================================================

def create_place_link(
    place_name,
    city=None
):
    """
    Creates a Google Maps link for a tourist place.
    """

    if city:

        search_text = (
            f"{place_name}, {city}"
        )

    else:

        search_text = place_name


    return create_maps_link(
        search_text
    )


# =========================================================
# TEST
# =========================================================

if __name__ == "__main__":

    place_link = create_maps_link(
        "Fort Aguada",
        "Goa"
    )

    route_link = create_route_link(
        "Mumbai",
        "Goa"
    )


    print()
    print("PLACE LINK:")
    print(place_link)

    print()

    print("ROUTE LINK:")
    print(route_link)