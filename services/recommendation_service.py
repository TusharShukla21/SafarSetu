# =========================================================
# SAFAR SETU - RECOMMENDATION SERVICE
# =========================================================


# =========================================================
# FILTER PLACES BY INTEREST
# =========================================================

def filter_places_by_interest(places, interests):
    """
    Filters places according to user's selected interests.

    Example interests:
        ["Beaches", "Food", "Nature"]

    Returns:
        List of matching places.
    """

    # If user has not selected any interest,
    # return all places.

    if not interests:
        return list(places)


    recommended = []


    for place in places:

        category = place["category"]


        if category in interests:

            recommended.append(place)


    return recommended


# =========================================================
# CALCULATE ACTIVITY BUDGET
# =========================================================

def calculate_activity_budget(
    total_budget,
    travel_cost,
    stay_cost,
    food_cost,
    local_travel_cost
):
    """
    Calculates how much money is available
    for tourist activities.
    """

    activity_budget = (

        total_budget

        - travel_cost

        - stay_cost

        - food_cost

        - local_travel_cost

    )


    # Activity budget should never be negative.

    if activity_budget < 0:

        activity_budget = 0


    return activity_budget


# =========================================================
# SELECT PLACES WITHIN BUDGET
# =========================================================

def select_places_within_budget(
    places,
    activity_budget,
    max_places=6
):
    """
    Selects the highest-rated places while keeping
    activity cost within the available budget.
    """

    # Sort by rating from highest to lowest.

    sorted_places = sorted(
        places,
        key=lambda place: place["rating"],
        reverse=True
    )


    selected_places = []

    total_activity_cost = 0


    for place in sorted_places:

        # Stop after desired number of places.

        if len(selected_places) >= max_places:

            break


        entry_fee = place["entry_fee"]


        # Check if this place fits the budget.

        if (
            total_activity_cost + entry_fee
            <= activity_budget
        ):

            selected_places.append(
                place
            )

            total_activity_cost += entry_fee


    return selected_places, total_activity_cost


# =========================================================
# ADD FREE PLACES IF POSSIBLE
# =========================================================

def add_free_places(
    selected_places,
    all_places,
    max_places=6
):
    """
    Adds free places when the selected list is small.

    This helps the tourist get more places to visit
    without increasing the activity budget.
    """

    selected_ids = set()


    for place in selected_places:

        selected_ids.add(
            place["id"]
        )


    for place in all_places:

        if len(selected_places) >= max_places:

            break


        if place["id"] in selected_ids:

            continue


        if place["entry_fee"] == 0:

            selected_places.append(
                place
            )

            selected_ids.add(
                place["id"]
            )


    return selected_places


# =========================================================
# FINAL RECOMMENDATION FUNCTION
# =========================================================

def generate_recommendations(
    places,
    interests,
    total_budget,
    travel_cost,
    stay_cost,
    food_cost,
    local_travel_cost,
    max_places=6
):
    """
    Main recommendation engine.

    It considers:

    1. User interests
    2. Available activity budget
    3. Place rating
    4. Entry fees
    5. Maximum number of places

    Returns:

        recommended_places
        activity_cost
        activity_budget
    """


    # -----------------------------------------------------
    # Calculate activity budget
    # -----------------------------------------------------

    activity_budget = calculate_activity_budget(

        total_budget,

        travel_cost,

        stay_cost,

        food_cost,

        local_travel_cost

    )


    # -----------------------------------------------------
    # Filter according to interests
    # -----------------------------------------------------

    filtered_places = filter_places_by_interest(

        places,

        interests

    )


    # -----------------------------------------------------
    # If no matching interests found,
    # use all available places
    # -----------------------------------------------------

    if not filtered_places:

        filtered_places = list(
            places
        )


    # -----------------------------------------------------
    # Select places within budget
    # -----------------------------------------------------

    selected_places, activity_cost = (
        select_places_within_budget(

            filtered_places,

            activity_budget,

            max_places

        )
    )


    # -----------------------------------------------------
    # Add free places if there is room
    # -----------------------------------------------------

    selected_places = add_free_places(

        selected_places,

        filtered_places,

        max_places

    )


    return {

        "places": selected_places,

        "activity_cost": activity_cost,

        "activity_budget": activity_budget

    }


# =========================================================
# SIMPLE PLACE SCORING
# =========================================================

def calculate_place_score(
    place,
    interests
):
    """
    Calculates a simple recommendation score.

    Higher score = better recommendation.

    This is intentionally simple for the prototype.
    """

    score = 0


    # -----------------------------------------------------
    # Rating score
    # -----------------------------------------------------

    rating = place["rating"]

    score += rating * 10


    # -----------------------------------------------------
    # Interest match
    # -----------------------------------------------------

    if (
        interests
        and place["category"] in interests
    ):

        score += 20


    # -----------------------------------------------------
    # Free-entry bonus
    # -----------------------------------------------------

    if place["entry_fee"] == 0:

        score += 5


    return score


# =========================================================
# SORT PLACES BY SMART SCORE
# =========================================================

def sort_places_by_score(
    places,
    interests
):
    """
    Sorts places according to recommendation score.
    """

    scored_places = []


    for place in places:

        score = calculate_place_score(

            place,

            interests

        )


        scored_places.append(
            (
                score,
                place
            )
        )


    # Highest score first.

    scored_places.sort(
        key=lambda item: item[0],
        reverse=True
    )


    return [
        item[1]
        for item in scored_places
    ]