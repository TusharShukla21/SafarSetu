# =========================================================
# SAFAR SETU - EMERGENCY SERVICE
# =========================================================

from database import get_db_connection


def get_all_emergency_services():
    """
    Get all emergency services.
    """

    connection = get_db_connection()

    try:
        services = connection.execute(
            """
            SELECT *
            FROM emergency_services
            ORDER BY category, name
            """
        ).fetchall()

        return services

    finally:
        connection.close()


def get_services_by_category(category):
    """
    Get emergency services belonging
    to a specific category.
    """

    connection = get_db_connection()

    try:
        services = connection.execute(
            """
            SELECT *
            FROM emergency_services
            WHERE LOWER(category) = LOWER(?)
            ORDER BY name
            """,
            (category,)
        ).fetchall()

        return services

    finally:
        connection.close()


def get_service_by_id(service_id):
    """
    Get one emergency service using ID.
    """

    connection = get_db_connection()

    try:
        service = connection.execute(
            """
            SELECT *
            FROM emergency_services
            WHERE id = ?
            """,
            (service_id,)
        ).fetchone()

        return service

    finally:
        connection.close()


def search_emergency_services(search_text):
    """
    Search emergency services by
    name, category, location or address.
    """

    connection = get_db_connection()

    search_pattern = f"%{search_text}%"

    try:
        services = connection.execute(
            """
            SELECT *
            FROM emergency_services
            WHERE name LIKE ?
               OR category LIKE ?
               OR location LIKE ?
               OR address LIKE ?
            ORDER BY category, name
            """,
            (
                search_pattern,
                search_pattern,
                search_pattern,
                search_pattern
            )
        ).fetchall()

        return services

    finally:
        connection.close()


def get_emergency_contacts():
    """
    Get emergency services that have
    a phone number.
    """

    connection = get_db_connection()

    try:
        services = connection.execute(
            """
            SELECT *
            FROM emergency_services
            WHERE phone IS NOT NULL
            AND phone != ''
            ORDER BY category, name
            """
        ).fetchall()

        return services

    finally:
        connection.close()


def get_emergency_summary():
    """
    Create a simple emergency summary
    for the Safar Setu emergency page.
    """

    services = get_all_emergency_services()

    summary = {
        "police": [],
        "ambulance": [],
        "fire": [],
        "other": []
    }

    for service in services:

        category = service["category"].lower()

        if "police" in category:
            summary["police"].append(service)

        elif "ambulance" in category:
            summary["ambulance"].append(service)

        elif "fire" in category:
            summary["fire"].append(service)

        else:
            summary["other"].append(service)

    return summary


def get_primary_emergency_numbers():
    """
    Get important emergency contact numbers
    such as 112, 108 and 101.
    """

    services = get_emergency_contacts()

    numbers = []

    for service in services:

        numbers.append(
            {
                "name": service["name"],
                "category": service["category"],
                "phone": service["phone"]
            }
        )

    return numbers


# =========================================================
# TEST
# =========================================================

if __name__ == "__main__":

    print()
    print("EMERGENCY SERVICE TEST")
    print("-" * 40)

    services = get_all_emergency_services()

    print()
    print("ALL EMERGENCY SERVICES:")

    for service in services:

        print(
            service["name"],
            "|",
            service["category"],
            "|",
            service["phone"]
        )

    print()
    print("EMERGENCY CONTACT NUMBERS:")

    numbers = get_primary_emergency_numbers()

    for number in numbers:

        print(
            number["name"],
            "-",
            number["phone"]
        )

    print()
    print("POLICE SERVICES:")

    police_services = get_services_by_category(
        "Police"
    )

    for service in police_services:

        print(
            service["name"],
            "-",
            service["phone"]
        )