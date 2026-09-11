# =========================================================
# SAFAR SETU - HOTEL / STAY SERVICE
# =========================================================

from database import get_db_connection


def get_stays_by_destination(destination_id):
    """
    Get all stays available for a destination.
    """

    connection = get_db_connection()

    try:
        stays = connection.execute(
            """
            SELECT *
            FROM stays
            WHERE destination_id = ?
            ORDER BY rating DESC, price_per_night ASC
            """,
            (destination_id,)
        ).fetchall()

        return stays

    finally:
        connection.close()


def get_stay_by_id(stay_id):
    """
    Get a single stay using its ID.
    """

    connection = get_db_connection()

    try:
        stay = connection.execute(
            """
            SELECT *
            FROM stays
            WHERE id = ?
            """,
            (stay_id,)
        ).fetchone()

        return stay

    finally:
        connection.close()


def get_stays_within_budget(
    destination_id,
    budget_per_night
):
    """
    Get stays whose nightly price
    is within the given budget.
    """

    connection = get_db_connection()

    try:
        stays = connection.execute(
            """
            SELECT *
            FROM stays
            WHERE destination_id = ?
            AND price_per_night <= ?
            ORDER BY rating DESC, price_per_night ASC
            """,
            (
                destination_id,
                budget_per_night
            )
        ).fetchall()

        return stays

    finally:
        connection.close()


def get_stay_offers(stay_id):
    """
    Get all available platform offers
    for a particular stay.
    """

    connection = get_db_connection()

    try:
        offers = connection.execute(
            """
            SELECT *
            FROM stay_offers
            WHERE stay_id = ?
            ORDER BY price ASC
            """,
            (stay_id,)
        ).fetchall()

        return offers

    finally:
        connection.close()


def get_cheapest_offer(stay_id):
    """
    Find the cheapest booking platform
    for a particular stay.
    """

    connection = get_db_connection()

    try:
        offer = connection.execute(
            """
            SELECT *
            FROM stay_offers
            WHERE stay_id = ?
            ORDER BY price ASC
            LIMIT 1
            """,
            (stay_id,)
        ).fetchone()

        return offer

    finally:
        connection.close()


def compare_stay_prices(stay_id):
    """
    Compare prices of a stay across
    different booking platforms.
    """

    stay = get_stay_by_id(stay_id)

    if not stay:
        return None

    offers = get_stay_offers(stay_id)

    cheapest_offer = None

    if offers:
        cheapest_offer = offers[0]

    return {
        "stay": stay,
        "offers": offers,
        "cheapest_offer": cheapest_offer
    }


def get_stays_with_price_comparison(
    destination_id,
    budget_per_night=None
):
    """
    Get stays along with their
    platform-wise price comparison.
    """

    if budget_per_night is not None:
        stays = get_stays_within_budget(
            destination_id,
            budget_per_night
        )
    else:
        stays = get_stays_by_destination(
            destination_id
        )

    results = []

    for stay in stays:

        offers = get_stay_offers(
            stay["id"]
        )

        cheapest_offer = None

        if offers:
            cheapest_offer = offers[0]

        results.append(
            {
                "stay": stay,
                "offers": offers,
                "cheapest_offer": cheapest_offer
            }
        )

    return results


def calculate_total_stay_cost(
    price_per_night,
    nights,
    rooms=1
):
    """
    Calculate total stay cost.
    """

    if nights <= 0:
        return 0

    if rooms <= 0:
        rooms = 1

    return (
        price_per_night
        * nights
        * rooms
    )


def find_best_stay(
    destination_id,
    budget_per_night=None
):
    """
    Find the best stay based on
    rating and price.
    """

    if budget_per_night is not None:
        stays = get_stays_within_budget(
            destination_id,
            budget_per_night
        )
    else:
        stays = get_stays_by_destination(
            destination_id
        )

    if not stays:
        return None

    return stays[0]


# =========================================================
# TEST
# =========================================================

if __name__ == "__main__":

    print()
    print("HOTEL SERVICE TEST")
    print("-" * 40)

    # Goa destination ID from seed data
    stays = get_stays_by_destination(1)

    print()
    print("GOA STAYS:")

    for stay in stays:
        print(
            stay["name"],
            "- ₹",
            stay["price_per_night"]
        )

    print()
    print("PRICE COMPARISON:")

    comparison = get_stays_with_price_comparison(1)

    for item in comparison:

        stay = item["stay"]
        cheapest = item["cheapest_offer"]

        print()
        print("Stay:", stay["name"])

        if cheapest:
            print(
                "Cheapest:",
                cheapest["platform"],
                "- ₹",
                cheapest["price"]
            )
        else:
            print("No platform offers available.")