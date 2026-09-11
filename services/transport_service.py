# =========================================================
# SAFAR SETU - TRANSPORT SERVICE
# =========================================================

from database import get_db_connection


def get_transport_options(source, destination):
    """
    Get all transport options between
    source and destination.
    """

    connection = get_db_connection()

    try:
        options = connection.execute(
            """
            SELECT *
            FROM transport
            WHERE LOWER(source) = LOWER(?)
            AND LOWER(destination) = LOWER(?)
            ORDER BY price ASC
            """,
            (
                source,
                destination
            )
        ).fetchall()

        return options

    finally:
        connection.close()


def get_transport_by_mode(
    source,
    destination,
    mode
):
    """
    Get transport options for a
    specific travel mode.
    """

    connection = get_db_connection()

    try:
        options = connection.execute(
            """
            SELECT *
            FROM transport
            WHERE LOWER(source) = LOWER(?)
            AND LOWER(destination) = LOWER(?)
            AND LOWER(mode) = LOWER(?)
            ORDER BY price ASC
            """,
            (
                source,
                destination,
                mode
            )
        ).fetchall()

        return options

    finally:
        connection.close()


def get_cheapest_transport(
    source,
    destination
):
    """
    Find the cheapest transport option
    between two locations.
    """

    options = get_transport_options(
        source,
        destination
    )

    if not options:
        return None

    return options[0]


def get_available_transport(
    source,
    destination
):
    """
    Get transport options that are
    currently available.
    """

    options = get_transport_options(
        source,
        destination
    )

    available_options = []

    for option in options:

        availability = option["availability"]

        if not availability:
            available_options.append(option)
            continue

        availability_text = availability.lower()

        if availability_text not in [
            "sold out",
            "unavailable",
            "closed"
        ]:
            available_options.append(option)

    return available_options


def calculate_transport_cost(
    price,
    travellers
):
    """
    Calculate total transport cost
    for all travellers.
    """

    if travellers <= 0:
        travellers = 1

    return price * travellers


def sort_transport_by_price(options):
    """
    Sort transport options from
    cheapest to most expensive.
    """

    return sorted(
        options,
        key=lambda option: option["price"]
    )


def get_transport_summary(
    source,
    destination,
    travellers=1
):
    """
    Create a complete transport summary.
    """

    options = get_transport_options(
        source,
        destination
    )

    if not options:
        return {
            "options": [],
            "cheapest": None,
            "estimated_cost": 0
        }

    cheapest = options[0]

    estimated_cost = calculate_transport_cost(
        cheapest["price"],
        travellers
    )

    return {
        "options": options,
        "cheapest": cheapest,
        "estimated_cost": estimated_cost
    }


# =========================================================
# TEST
# =========================================================

if __name__ == "__main__":

    print()
    print("TRANSPORT SERVICE TEST")
    print("-" * 40)

    source = "Mumbai"
    destination = "Goa"
    travellers = 2

    options = get_transport_options(
        source,
        destination
    )

    print()
    print(
        f"TRANSPORT FROM {source} TO {destination}:"
    )

    for option in options:

        print(
            option["mode"],
            "|",
            option["provider"],
            "| ₹",
            option["price"],
            "|",
            option["duration"],
            "|",
            option["availability"]
        )

    cheapest = get_cheapest_transport(
        source,
        destination
    )

    print()
    print("CHEAPEST OPTION:")

    if cheapest:

        print(
            cheapest["mode"],
            "- ₹",
            cheapest["price"]
        )

        total_cost = calculate_transport_cost(
            cheapest["price"],
            travellers
        )

        print(
            f"Total for {travellers} travellers: ₹{total_cost}"
        )

    else:
        print("No transport options found.")

    print()
    print("AVAILABLE OPTIONS:")

    available = get_available_transport(
        source,
        destination
    )

    for option in available:

        print(
            option["mode"],
            "-",
            option["availability"]
        )