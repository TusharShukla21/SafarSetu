# =========================================================
# SAFAR SETU - MAIN FLASK APPLICATION
# =========================================================

from datetime import datetime, timedelta
from functools import wraps

from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash,
    jsonify
)

from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)

from config import Config
from database import (
    get_db_connection,
    init_database
)

from services.weather_service import (
    get_current_weather
)

from services.maps_service import (
    create_maps_link,
    create_route_link
)

from services.recommendation_service import (
    generate_recommendations,
    sort_places_by_score
)

from services.hotel_service import (
    get_stays_by_destination,
    get_stays_with_price_comparison,
    get_cheapest_offer
)

from services.transport_service import (
    get_transport_options,
    get_cheapest_transport,
    calculate_transport_cost
)

from services.emergency_service import (
    get_all_emergency_services,
    get_services_by_category
)


# =========================================================
# APP CONFIGURATION
# =========================================================

app = Flask(__name__)

app.config.from_object(Config)

app.secret_key = Config.SECRET_KEY


# =========================================================
# DATABASE INITIALIZATION
# =========================================================

with app.app_context():
    init_database()


# =========================================================
# HELPER FUNCTIONS
# =========================================================

def get_current_user():
    """
    Get the currently logged-in user.
    """

    user_id = session.get("user_id")

    if not user_id:
        return None

    connection = get_db_connection()

    try:
        user = connection.execute(
            """
            SELECT *
            FROM users
            WHERE id = ?
            """,
            (user_id,)
        ).fetchone()

        return user

    finally:
        connection.close()


def login_required(function):
    """
    Allow access only to logged-in users.
    """

    @wraps(function)
    def decorated_function(*args, **kwargs):

        if "user_id" not in session:
            flash(
                "Please login to continue.",
                "warning"
            )
            return redirect(
                url_for("login")
            )

        return function(*args, **kwargs)

    return decorated_function


def tourist_required(function):
    """
    Allow access only to tourist users.
    """

    @wraps(function)
    def decorated_function(*args, **kwargs):

        user = get_current_user()

        if not user:
            flash(
                "Please login first.",
                "warning"
            )
            return redirect(
                url_for("login")
            )

        if user["role"] != "tourist":
            flash(
                "This section is available for tourists.",
                "warning"
            )
            return redirect(
                url_for("home")
            )

        return function(*args, **kwargs)

    return decorated_function


def business_required(function):
    """
    Allow access only to business users.
    """

    @wraps(function)
    def decorated_function(*args, **kwargs):

        user = get_current_user()

        if not user:
            flash(
                "Please login first.",
                "warning"
            )
            return redirect(
                url_for("login")
            )

        if user["role"] != "business":
            flash(
                "This section is available for local businesses.",
                "warning"
            )
            return redirect(
                url_for("home")
            )

        return function(*args, **kwargs)

    return decorated_function


def get_destination_by_name(name):
    """
    Find a destination by name.
    """

    connection = get_db_connection()

    try:
        destination = connection.execute(
            """
            SELECT *
            FROM destinations
            WHERE LOWER(name) = LOWER(?)
            """,
            (name,)
        ).fetchone()

        return destination

    finally:
        connection.close()


def get_destination_by_id(destination_id):
    """
    Find a destination by ID.
    """

    connection = get_db_connection()

    try:
        destination = connection.execute(
            """
            SELECT *
            FROM destinations
            WHERE id = ?
            """,
            (destination_id,)
        ).fetchone()

        return destination

    finally:
        connection.close()


def get_places_by_destination(destination_id):
    """
    Get all tourist places for a destination.
    """

    connection = get_db_connection()

    try:
        places = connection.execute(
            """
            SELECT *
            FROM places
            WHERE destination_id = ?
            ORDER BY rating DESC
            """,
            (destination_id,)
        ).fetchall()

        return places

    finally:
        connection.close()


def get_all_destinations():
    """
    Get all available destinations.
    """

    connection = get_db_connection()

    try:
        destinations = connection.execute(
            """
            SELECT *
            FROM destinations
            ORDER BY name
            """
        ).fetchall()

        return destinations

    finally:
        connection.close()


def build_trip_alerts(
    budget,
    estimated_cost,
    cheapest_transport=None,
    transport_options=None
):
    """
    Build warnings and suggestions for a planned trip.
    """

    alerts = []

    # ---------------------------------------------------------
    # BUDGET ALERTS
    # ---------------------------------------------------------

    if estimated_cost > budget:
        extra_amount = estimated_cost - budget

        alerts.append(
            {
                "type": "danger",
                "title": "Budget exceeded",
                "message": (
                    f"Your estimated trip cost is ₹{estimated_cost:,.0f}, "
                    f"which is ₹{extra_amount:,.0f} above your budget."
                )
            }
        )

    elif budget > 0 and estimated_cost >= budget * 0.90:
        remaining_amount = budget - estimated_cost

        alerts.append(
            {
                "type": "warning",
                "title": "Budget is almost full",
                "message": (
                    f"Only about ₹{remaining_amount:,.0f} remains "
                    "within your planned budget."
                )
            }
        )

    # ---------------------------------------------------------
    # TRANSPORT AVAILABILITY ALERTS
    # ---------------------------------------------------------

    if cheapest_transport:
        availability = str(
            cheapest_transport["availability"] or ""
        ).strip().lower()

        if availability in {
            "limited",
            "few seats",
            "few seats left",
            "low"
        }:
            alerts.append(
                {
                    "type": "warning",
                    "title": "Limited transport availability",
                    "message": (
                        f"{cheapest_transport['mode']} "
                        f"({cheapest_transport['provider'] or 'provider'}) "
                        "has limited availability. Consider booking early."
                    )
                }
            )

        elif availability in {
            "sold out",
            "unavailable",
            "not available"
        }:
            alerts.append(
                {
                    "type": "danger",
                    "title": "Selected transport is unavailable",
                    "message": (
                        "The cheapest transport option is currently "
                        "unavailable. Please check the other available options."
                    )
                }
            )

    if transport_options:
        available_options = [
            option
            for option in transport_options
            if str(
                option["availability"] or ""
            ).strip().lower()
            not in {
                "sold out",
                "unavailable",
                "not available"
            }
        ]

        if not available_options:
            alerts.append(
                {
                    "type": "danger",
                    "title": "No available transport found",
                    "message": (
                        "All stored transport options for this route "
                        "are currently unavailable. Try another route or mode."
                    )
                }
            )

    elif not cheapest_transport:
        alerts.append(
            {
                "type": "warning",
                "title": "Transport information unavailable",
                "message": (
                    "We could not find a stored transport option for this route. "
                    "Check the Travel section for alternatives."
                )
            }
        )

    # ---------------------------------------------------------
    # SUCCESS / GENERAL STATUS
    # ---------------------------------------------------------

    if estimated_cost <= budget:
        alerts.append(
            {
                "type": "success",
                "title": "Trip fits your budget",
                "message": (
                    f"Your current estimate is ₹{estimated_cost:,.0f} "
                    f"against a budget of ₹{budget:,.0f}."
                )
            }
        )

    return alerts


def get_upcoming_package_alerts(user_id, days=3):
    """
    Get alerts for business packages whose booking deadlines
    are approaching or whose seats are running low.
    """

    connection = get_db_connection()

    try:
        packages = connection.execute(
            """
            SELECT
                business_packages.*,
                businesses.name AS business_name
            FROM business_packages
            JOIN businesses
                ON business_packages.business_id = businesses.id
            WHERE businesses.user_id = ?
            ORDER BY business_packages.booking_deadline
            """,
            (user_id,)
        ).fetchall()

    finally:
        connection.close()

    alerts = []

    today = datetime.now().date()
    deadline_limit = today + timedelta(days=days)

    for package in packages:

        deadline_text = package["booking_deadline"]

        if deadline_text:
            try:
                deadline = datetime.strptime(
                    deadline_text,
                    "%Y-%m-%d"
                ).date()

                if deadline < today:
                    alerts.append(
                        {
                            "type": "danger",
                            "title": "Booking deadline passed",
                            "message": (
                                f"{package['name']} for "
                                f"{package['business_name']} has passed its "
                                "booking deadline."
                            )
                        }
                    )

                elif deadline <= deadline_limit:
                    remaining_days = (
                        deadline - today
                    ).days

                    if remaining_days == 0:
                        deadline_message = (
                            f"{package['name']} booking deadline is today."
                        )
                    elif remaining_days == 1:
                        deadline_message = (
                            f"{package['name']} booking deadline is tomorrow."
                        )
                    else:
                        deadline_message = (
                            f"{package['name']} booking deadline is in "
                            f"{remaining_days} days."
                        )

                    alerts.append(
                        {
                            "type": "warning",
                            "title": "Package deadline approaching",
                            "message": deadline_message
                        }
                    )

            except ValueError:
                pass

        available_seats = package["available_seats"]

        if available_seats is not None:
            try:
                available_seats = int(available_seats)

                if 0 < available_seats <= 5:
                    alerts.append(
                        {
                            "type": "warning",
                            "title": "Low package availability",
                            "message": (
                                f"{package['name']} has only "
                                f"{available_seats} seats remaining."
                            )
                        }
                    )

                elif available_seats <= 0:
                    alerts.append(
                        {
                            "type": "danger",
                            "title": "Package sold out",
                            "message": (
                                f"{package['name']} currently has no "
                                "available seats."
                            )
                        }
                    )

            except (TypeError, ValueError):
                pass

    return alerts


# =========================================================
# BASIC ROUTES
# =========================================================

@app.route("/")
def index():
    """
    Landing page.
    """

    if "user_id" in session:
        return redirect(
            url_for("home")
        )

    return redirect(
        url_for("login")
    )


@app.route("/health")
def health():
    """
    Simple application health check.
    """

    return jsonify(
        {
            "status": "success",
            "message": "Safar Setu is running."
        }
    )


# =========================================================
# AUTHENTICATION
# =========================================================

@app.route("/signup", methods=["GET", "POST"])
def signup():

    if request.method == "POST":

        name = request.form.get(
            "name",
            ""
        ).strip()

        email = request.form.get(
            "email",
            ""
        ).strip().lower()

        password = request.form.get(
            "password",
            ""
        )

        confirm_password = request.form.get(
            "confirm_password",
            ""
        )

        if not name or not email or not password:
            flash(
                "Please fill all required fields.",
                "danger"
            )
            return render_template(
                "signup.html"
            )

        if password != confirm_password:
            flash(
                "Passwords do not match.",
                "danger"
            )
            return render_template(
                "signup.html"
            )

        if len(password) < 6:
            flash(
                "Password must contain at least 6 characters.",
                "danger"
            )
            return render_template(
                "signup.html"
            )

        connection = get_db_connection()

        try:

            existing_user = connection.execute(
                """
                SELECT id
                FROM users
                WHERE LOWER(email) = LOWER(?)
                """,
                (email,)
            ).fetchone()

            if existing_user:

                flash(
                    "An account with this email already exists.",
                    "danger"
                )

                return render_template(
                    "signup.html"
                )

            password_hash = generate_password_hash(
                password
            )

            cursor = connection.execute(
                """
                INSERT INTO users
                (
                    name,
                    email,
                    password
                )
                VALUES (?, ?, ?)
                """,
                (
                    name,
                    email,
                    password_hash
                )
            )

            connection.commit()

            session.clear()

            session["user_id"] = cursor.lastrowid

            return redirect(
                url_for("role")
            )

        except Exception as error:

            connection.rollback()

            print(
                "Signup error:",
                error
            )

            flash(
                "Something went wrong during signup.",
                "danger"
            )

            return render_template(
                "signup.html"
            )

        finally:
            connection.close()

    return render_template(
        "signup.html"
    )


@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form.get(
            "email",
            ""
        ).strip().lower()

        password = request.form.get(
            "password",
            ""
        )

        if not email or not password:

            flash(
                "Please enter email and password.",
                "danger"
            )

            return render_template(
                "login.html"
            )

        connection = get_db_connection()

        try:

            user = connection.execute(
                """
                SELECT *
                FROM users
                WHERE LOWER(email) = LOWER(?)
                """,
                (email,)
            ).fetchone()

        finally:
            connection.close()

        if not user:

            flash(
                "Invalid email or password.",
                "danger"
            )

            return render_template(
                "login.html"
            )

        if not check_password_hash(
            user["password"],
            password
        ):

            flash(
                "Invalid email or password.",
                "danger"
            )

            return render_template(
                "login.html"
            )

        session.clear()

        session["user_id"] = user["id"]

        if user["role"]:

            session["role"] = user["role"]

            return redirect(
                url_for("home")
            )

        return redirect(
            url_for("role")
        )

    return render_template(
        "login.html"
    )


@app.route("/logout")
def logout():

    session.clear()

    flash(
        "You have been logged out.",
        "success"
    )

    return redirect(
        url_for("login")
    )


# =========================================================
# ROLE SELECTION
# =========================================================

@app.route("/role", methods=["GET", "POST"])
@login_required
def role():

    if request.method == "POST":

        selected_role = request.form.get(
            "role"
        )

        if selected_role not in [
            "tourist",
            "business"
        ]:

            flash(
                "Please select a valid role.",
                "danger"
            )

            return render_template(
                "role.html"
            )

        user_id = session["user_id"]

        connection = get_db_connection()

        try:

            connection.execute(
                """
                UPDATE users
                SET role = ?
                WHERE id = ?
                """,
                (
                    selected_role,
                    user_id
                )
            )

            connection.commit()

        finally:
            connection.close()

        session["role"] = selected_role

        return redirect(
            url_for("home")
        )

    return render_template(
        "role.html"
    )


# =========================================================
# HOME
# =========================================================

@app.route("/home")
@login_required
def home():

    user = get_current_user()

    destinations = get_all_destinations()

    return render_template(
        "home.html",
        user=user,
        destinations=destinations
    )


# =========================================================
# PROFILE
# =========================================================

@app.route("/profile")
@login_required
def profile():

    user = get_current_user()

    return render_template(
        "profile.html",
        user=user
    )


# =========================================================
# PLAN A TRIP
# =========================================================

@app.route("/plan-trip", methods=["GET", "POST"])
@tourist_required
def plan_trip():

    destinations = get_all_destinations()

    if request.method == "POST":

        source = request.form.get(
            "source",
            ""
        ).strip()

        destination_name = request.form.get(
            "destination",
            ""
        ).strip()

        start_date = request.form.get(
            "start_date",
            ""
        )

        end_date = request.form.get(
            "end_date",
            ""
        )

        travellers_text = request.form.get(
            "travellers",
            "1"
        )

        budget_text = request.form.get(
            "budget",
            "0"
        )

        interests = request.form.getlist(
            "interests"
        )

        try:
            travellers = int(
                travellers_text
            )
        except ValueError:
            travellers = 0

        try:
            budget = float(
                budget_text
            )
        except ValueError:
            budget = 0

        if not source:
            flash(
                "Please enter your starting location.",
                "danger"
            )
            return render_template(
                "plan_trip.html",
                destinations=destinations
            )

        if not destination_name:
            flash(
                "Please select a destination.",
                "danger"
            )
            return render_template(
                "plan_trip.html",
                destinations=destinations
            )

        if travellers <= 0:
            flash(
                "Number of travellers must be at least 1.",
                "danger"
            )
            return render_template(
                "plan_trip.html",
                destinations=destinations
            )

        if budget <= 0:
            flash(
                "Please enter a valid budget.",
                "danger"
            )
            return render_template(
                "plan_trip.html",
                destinations=destinations
            )

        destination = get_destination_by_name(
            destination_name
        )

        if not destination:

            flash(
                "Destination not found.",
                "danger"
            )

            return render_template(
                "plan_trip.html",
                destinations=destinations
            )

        # -------------------------------------------------
        # DATE VALIDATION
        # -------------------------------------------------

        try:

            start = datetime.strptime(
                start_date,
                "%Y-%m-%d"
            )

            end = datetime.strptime(
                end_date,
                "%Y-%m-%d"
            )

            if end < start:

                flash(
                    "End date cannot be before start date.",
                    "danger"
                )

                return render_template(
                    "plan_trip.html",
                    destinations=destinations
                )

            trip_days = (
                end - start
            ).days + 1

            if trip_days > Config.MAX_TRIP_DAYS:

                flash(
                    f"Trip cannot be longer than {Config.MAX_TRIP_DAYS} days.",
                    "danger"
                )

                return render_template(
                    "plan_trip.html",
                    destinations=destinations
                )

            nights = max(
                trip_days - 1,
                1
            )

        except ValueError:

            flash(
                "Please enter valid travel dates.",
                "danger"
            )

            return render_template(
                "plan_trip.html",
                destinations=destinations
            )

        # -------------------------------------------------
        # TRANSPORT
        # -------------------------------------------------

        transport_options = get_transport_options(
            source,
            destination["name"]
        )

        cheapest_transport = get_cheapest_transport(
            source,
            destination["name"]
        )

        if cheapest_transport:

            travel_cost = calculate_transport_cost(
                cheapest_transport["price"],
                travellers
            )

        else:

            travel_cost = 0

        # -------------------------------------------------
        # STAYS
        # -------------------------------------------------

        stays = get_stays_by_destination(
            destination["id"]
        )

        stay_cost = 0

        if stays:

            cheapest_stay = min(
                stays,
                key=lambda stay: stay["price_per_night"]
            )

            rooms = max(
                (travellers + 1) // 2,
                1
            )

            stay_cost = (
                cheapest_stay["price_per_night"]
                * nights
                * rooms
            )

        else:

            cheapest_stay = None
            rooms = 1

        # -------------------------------------------------
        # FOOD ESTIMATE
        # -------------------------------------------------

        food_cost_per_person = 500

        food_cost = (
            food_cost_per_person
            * travellers
            * trip_days
        )

        # -------------------------------------------------
        # LOCAL TRAVEL ESTIMATE
        # -------------------------------------------------

        local_travel_cost_per_person = 200

        local_travel_cost = (
            local_travel_cost_per_person
            * travellers
            * trip_days
        )

        # -------------------------------------------------
        # PLACES
        # -------------------------------------------------

        places = get_places_by_destination(
            destination["id"]
        )

        sorted_places = sort_places_by_score(
            places,
            interests
        )

        # -------------------------------------------------
        # RECOMMENDATIONS
        # -------------------------------------------------

        recommendations = generate_recommendations(
            sorted_places,
            interests,
            budget,
            travel_cost,
            stay_cost,
            food_cost,
            local_travel_cost
        )

        estimated_cost = (
            travel_cost
            + stay_cost
            + food_cost
            + local_travel_cost
            + recommendations["activity_cost"]
        )

        # -------------------------------------------------
        # BUDGET STATUS
        # -------------------------------------------------

        if estimated_cost <= budget:

            budget_status = "within_budget"

        else:

            budget_status = "over_budget"

        # -------------------------------------------------
        # TRIP ALERTS
        # -------------------------------------------------

        trip_alerts = build_trip_alerts(
            budget=budget,
            estimated_cost=estimated_cost,
            cheapest_transport=cheapest_transport,
            transport_options=transport_options
        )

        # -------------------------------------------------
        # WEATHER
        # -------------------------------------------------

        weather = get_current_weather(
            destination["name"]
        )

        # -------------------------------------------------
        # MAP LINK
        # -------------------------------------------------

        destination_maps_url = create_maps_link(
            destination["name"],
            destination["state"]
        )

        # -------------------------------------------------
        # SAVE TRIP
        # -------------------------------------------------

        connection = get_db_connection()

        try:

            cursor = connection.execute(
                """
                INSERT INTO trips
                (
                    user_id,
                    source,
                    destination,
                    start_date,
                    end_date,
                    travellers,
                    budget,
                    estimated_cost
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    session["user_id"],
                    source,
                    destination["name"],
                    start_date,
                    end_date,
                    travellers,
                    budget,
                    estimated_cost
                )
            )

            trip_id = cursor.lastrowid

            # Save recommended places

            for index, place in enumerate(
                recommendations["places"],
                start=1
            ):

                connection.execute(
                    """
                    INSERT INTO trip_places
                    (
                        trip_id,
                        place_id,
                        visit_date,
                        visit_order
                    )
                    VALUES (?, ?, ?, ?)
                    """,
                    (
                        trip_id,
                        place["id"],
                        None,
                        index
                    )
                )

            # Save cheapest stay

            if cheapest_stay:

                connection.execute(
                    """
                    INSERT INTO trip_stays
                    (
                        trip_id,
                        stay_id,
                        rooms
                    )
                    VALUES (?, ?, ?)
                    """,
                    (
                        trip_id,
                        cheapest_stay["id"],
                        rooms
                    )
                )

            connection.commit()

        except Exception as error:

            connection.rollback()

            print(
                "Trip save error:",
                error
            )

            flash(
                "Trip could not be saved.",
                "danger"
            )

            return render_template(
                "plan_trip.html",
                destinations=destinations
            )

        finally:
            connection.close()

        return render_template(
            "trip_result.html",
            trip_id=trip_id,
            source=source,
            destination=destination,
            start_date=start_date,
            end_date=end_date,
            trip_days=trip_days,
            nights=nights,
            travellers=travellers,
            budget=budget,
            estimated_cost=estimated_cost,
            budget_status=budget_status,
            transport_options=transport_options,
            cheapest_transport=cheapest_transport,
            travel_cost=travel_cost,
            stays=stays,
            cheapest_stay=cheapest_stay,
            stay_cost=stay_cost,
            rooms=rooms,
            food_cost=food_cost,
            local_travel_cost=local_travel_cost,
            places=places,
            recommendations=recommendations,
            weather=weather,
            destination_maps_url=destination_maps_url,
            trip_alerts=trip_alerts
        )

    return render_template(
        "plan_trip.html",
        destinations=destinations
    )


# =========================================================
# MY TRIPS
# =========================================================

@app.route("/my-trips")
@tourist_required
def my_trips():

    connection = get_db_connection()

    try:

        trips = connection.execute(
            """
            SELECT *
            FROM trips
            WHERE user_id = ?
            ORDER BY created_at DESC
            """,
            (session["user_id"],)
        ).fetchall()

    finally:
        connection.close()

    return render_template(
        "my_trips.html",
        trips=trips
    )


# =========================================================
# STAY
# =========================================================

@app.route("/stay")
@tourist_required
def stay():

    destination_name = request.args.get(
        "destination",
        ""
    ).strip()

    budget_text = request.args.get(
        "budget",
        ""
    ).strip()

    destination = None
    stays = []

    if destination_name:

        destination = get_destination_by_name(
            destination_name
        )

        if destination:

            budget = None

            if budget_text:

                try:
                    budget = float(
                        budget_text
                    )
                except ValueError:
                    budget = None

            stays = get_stays_with_price_comparison(
                destination["id"],
                budget
            )

    return render_template(
        "stay.html",
        destination=destination,
        stays=stays
    )


@app.route("/stay/<int:stay_id>/offers")
@tourist_required
def stay_offers(stay_id):

    connection = get_db_connection()

    try:

        stay_data = connection.execute(
            """
            SELECT *
            FROM stays
            WHERE id = ?
            """,
            (stay_id,)
        ).fetchone()

        offers = connection.execute(
            """
            SELECT *
            FROM stay_offers
            WHERE stay_id = ?
            ORDER BY price ASC
            """,
            (stay_id,)
        ).fetchall()

    finally:
        connection.close()

    if not stay_data:

        flash(
            "Stay not found.",
            "danger"
        )

        return redirect(
            url_for("stay")
        )

    cheapest_offer = get_cheapest_offer(
        stay_id
    )

    return render_template(
        "stay.html",
        destination=None,
        stays=[
            {
                "stay": stay_data,
                "offers": offers,
                "cheapest_offer": cheapest_offer
            }
        ]
    )


# =========================================================
# TRAVEL
# =========================================================

@app.route("/travel")
@tourist_required
def travel():

    source = request.args.get(
        "source",
        ""
    ).strip()

    destination = request.args.get(
        "destination",
        ""
    ).strip()

    options = []

    cheapest = None

    if source and destination:

        options = get_transport_options(
            source,
            destination
        )

        cheapest = get_cheapest_transport(
            source,
            destination
        )

    return render_template(
        "travel.html",
        source=source,
        destination=destination,
        options=options,
        cheapest=cheapest
    )


# =========================================================
# PLACES
# =========================================================

@app.route("/places")
@tourist_required
def places():

    destination_name = request.args.get(
        "destination",
        ""
    ).strip()

    destination = None
    places_data = []

    if destination_name:

        destination = get_destination_by_name(
            destination_name
        )

        if destination:

            places_data = get_places_by_destination(
                destination["id"]
            )

            places_data = sort_places_by_score(
                places_data,
                []
            )

    return render_template(
        "places.html",
        destination=destination,
        places=places_data
    )


# =========================================================
# MAP ROUTES
# =========================================================

@app.route("/map-link")
@login_required
def map_link():

    place = request.args.get(
        "place",
        ""
    ).strip()

    location = request.args.get(
        "location",
        ""
    ).strip()

    if not place:

        return redirect(
            url_for("home")
        )

    maps_url = create_maps_link(
        place,
        location
    )

    return redirect(
        maps_url
    )


@app.route("/route-link")
@login_required
def route_link():

    source = request.args.get(
        "source",
        ""
    ).strip()

    destination = request.args.get(
        "destination",
        ""
    ).strip()

    mode = request.args.get(
        "mode",
        "driving"
    ).strip()

    if not source or not destination:

        return redirect(
            url_for("home")
        )

    maps_url = create_route_link(
        source,
        destination,
        mode
    )

    return redirect(
        maps_url
    )


# =========================================================
# EMERGENCY
# =========================================================

@app.route("/emergency")
@login_required
def emergency():

    services = get_all_emergency_services()

    police = get_services_by_category(
        "Police"
    )

    return render_template(
        "emergency.html",
        services=services,
        police=police
    )


# =========================================================
# BUSINESS DASHBOARD
# =========================================================

@app.route("/business")
@business_required
def business():

    connection = get_db_connection()

    try:

        businesses = connection.execute(
            """
            SELECT *
            FROM businesses
            WHERE user_id = ?
            ORDER BY created_at DESC
            """,
            (session["user_id"],)
        ).fetchall()

    finally:
        connection.close()

    return render_template(
        "business.html",
        businesses=businesses
    )


# =========================================================
# ADD BUSINESS
# =========================================================

@app.route(
    "/business/add",
    methods=["GET", "POST"]
)
@business_required
def add_business():

    if request.method == "POST":

        name = request.form.get(
            "name",
            ""
        ).strip()

        category = request.form.get(
            "category",
            ""
        ).strip()

        description = request.form.get(
            "description",
            ""
        ).strip()

        location = request.form.get(
            "location",
            ""
        ).strip()

        phone = request.form.get(
            "phone",
            ""
        ).strip()

        email = request.form.get(
            "email",
            ""
        ).strip()

        website = request.form.get(
            "website",
            ""
        ).strip()

        price_info = request.form.get(
            "price_info",
            ""
        ).strip()

        image_url = request.form.get(
            "image_url",
            ""
        ).strip()

        if not name or not category or not location:

            flash(
                "Business name, category and location are required.",
                "danger"
            )

            return render_template(
                "add_business.html"
            )

        maps_url = create_maps_link(
            name,
            location
        )

        connection = get_db_connection()

        try:

            connection.execute(
                """
                INSERT INTO businesses
                (
                    user_id,
                    name,
                    category,
                    description,
                    location,
                    phone,
                    email,
                    website,
                    price_info,
                    maps_url,
                    image_url
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    session["user_id"],
                    name,
                    category,
                    description,
                    location,
                    phone,
                    email,
                    website,
                    price_info,
                    maps_url,
                    image_url
                )
            )

            connection.commit()

        finally:
            connection.close()

        flash(
            "Business added successfully.",
            "success"
        )

        return redirect(
            url_for("business")
        )

    return render_template(
        "add_business.html"
    )


# =========================================================
# EDIT BUSINESS
# =========================================================

@app.route(
    "/business/edit/<int:business_id>",
    methods=["GET", "POST"]
)
@business_required
def edit_business(business_id):

    connection = get_db_connection()

    try:

        business_data = connection.execute(
            """
            SELECT *
            FROM businesses
            WHERE id = ?
            AND user_id = ?
            """,
            (
                business_id,
                session["user_id"]
            )
        ).fetchone()

    finally:
        connection.close()

    if not business_data:

        flash(
            "Business not found.",
            "danger"
        )

        return redirect(
            url_for("business")
        )

    if request.method == "POST":

        name = request.form.get(
            "name",
            ""
        ).strip()

        category = request.form.get(
            "category",
            ""
        ).strip()

        description = request.form.get(
            "description",
            ""
        ).strip()

        location = request.form.get(
            "location",
            ""
        ).strip()

        phone = request.form.get(
            "phone",
            ""
        ).strip()

        email = request.form.get(
            "email",
            ""
        ).strip()

        website = request.form.get(
            "website",
            ""
        ).strip()

        price_info = request.form.get(
            "price_info",
            ""
        ).strip()

        image_url = request.form.get(
            "image_url",
            ""
        ).strip()

        maps_url = create_maps_link(
            name,
            location
        )

        connection = get_db_connection()

        try:

            connection.execute(
                """
                UPDATE businesses
                SET
                    name = ?,
                    category = ?,
                    description = ?,
                    location = ?,
                    phone = ?,
                    email = ?,
                    website = ?,
                    price_info = ?,
                    maps_url = ?,
                    image_url = ?
                WHERE id = ?
                AND user_id = ?
                """,
                (
                    name,
                    category,
                    description,
                    location,
                    phone,
                    email,
                    website,
                    price_info,
                    maps_url,
                    image_url,
                    business_id,
                    session["user_id"]
                )
            )

            connection.commit()

        finally:
            connection.close()

        flash(
            "Business updated successfully.",
            "success"
        )

        return redirect(
            url_for("business")
        )

    return render_template(
        "edit_business.html",
        business=business_data
    )


# =========================================================
# BUSINESS PACKAGES
# =========================================================

@app.route(
    "/business/<int:business_id>/packages",
    methods=["GET", "POST"]
)
@business_required
def business_packages(business_id):

    connection = get_db_connection()

    try:

        business_data = connection.execute(
            """
            SELECT *
            FROM businesses
            WHERE id = ?
            AND user_id = ?
            """,
            (
                business_id,
                session["user_id"]
            )
        ).fetchone()

    finally:
        connection.close()

    if not business_data:

        flash(
            "Business not found.",
            "danger"
        )

        return redirect(
            url_for("business")
        )

    if request.method == "POST":

        name = request.form.get(
            "name",
            ""
        ).strip()

        description = request.form.get(
            "description",
            ""
        ).strip()

        start_date = request.form.get(
            "start_date",
            ""
        ).strip()

        end_date = request.form.get(
            "end_date",
            ""
        ).strip()

        price_text = request.form.get(
            "price",
            ""
        ).strip()

        seats_text = request.form.get(
            "available_seats",
            "0"
        ).strip()

        booking_deadline = request.form.get(
            "booking_deadline",
            ""
        ).strip()

        inclusions = request.form.get(
            "inclusions",
            ""
        ).strip()

        exclusions = request.form.get(
            "exclusions",
            ""
        ).strip()

        contact = request.form.get(
            "contact",
            ""
        ).strip()

        if not name or not start_date or not end_date or not price_text:
            flash(
                "Package name, dates and price are required.",
                "danger"
            )

            return redirect(
                url_for(
                    "business_packages",
                    business_id=business_id
                )
            )

        try:
            start = datetime.strptime(
                start_date,
                "%Y-%m-%d"
            )

            end = datetime.strptime(
                end_date,
                "%Y-%m-%d"
            )

            if end < start:
                flash(
                    "Package end date cannot be before start date.",
                    "danger"
                )

                return redirect(
                    url_for(
                        "business_packages",
                        business_id=business_id
                    )
                )

            price = float(price_text)

            if price < 0:
                raise ValueError

            available_seats = int(seats_text)

            if available_seats < 0:
                raise ValueError

            if booking_deadline:
                deadline = datetime.strptime(
                    booking_deadline,
                    "%Y-%m-%d"
                )

                if deadline > start:
                    flash(
                        "Booking deadline cannot be after the package start date.",
                        "danger"
                    )

                    return redirect(
                        url_for(
                            "business_packages",
                            business_id=business_id
                        )
                    )

        except ValueError:
            flash(
                "Please enter valid package dates, price and available seats.",
                "danger"
            )

            return redirect(
                url_for(
                    "business_packages",
                    business_id=business_id
                )
            )

        connection = get_db_connection()

        try:
            connection.execute(
                """
                INSERT INTO business_packages
                (
                    business_id,
                    name,
                    description,
                    start_date,
                    end_date,
                    price,
                    available_seats,
                    booking_deadline,
                    inclusions,
                    exclusions,
                    contact
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    business_id,
                    name,
                    description,
                    start_date,
                    end_date,
                    price,
                    available_seats,
                    booking_deadline or None,
                    inclusions,
                    exclusions,
                    contact
                )
            )

            connection.commit()

        except Exception as error:
            connection.rollback()

            print(
                "Package save error:",
                error
            )

            flash(
                "Package could not be added.",
                "danger"
            )

            return redirect(
                url_for(
                    "business_packages",
                    business_id=business_id
                )
            )

        finally:
            connection.close()

        flash(
            "Package added successfully.",
            "success"
        )

        return redirect(
            url_for(
                "business_packages",
                business_id=business_id
            )
        )

    connection = get_db_connection()

    try:
        packages = connection.execute(
            """
            SELECT *
            FROM business_packages
            WHERE business_id = ?
            ORDER BY start_date
            """,
            (business_id,)
        ).fetchall()
    finally:
        connection.close()

    return render_template(
        "business_packages.html",
        business=business_data,
        packages=packages
    )


# =========================================================
# BUSINESS ALERTS
# =========================================================

@app.route("/business/alerts")
@business_required
def business_alerts():

    alerts = get_upcoming_package_alerts(
        session["user_id"]
    )

    return jsonify(
        {
            "status": "success",
            "alerts": alerts,
            "count": len(alerts)
        }
    )


# =========================================================
# ERROR HANDLERS
# =========================================================

@app.errorhandler(404)
def page_not_found(error):

    return render_template(
        "errors/404.html"
    ), 404


@app.errorhandler(500)
def internal_server_error(error):

    return render_template(
        "errors/500.html"
    ), 500


# =========================================================
# RUN APPLICATION
# =========================================================

if __name__ == "__main__":

    print()
    print("=" * 50)
    print("SAFAR SETU")
    print("=" * 50)
    print("Application starting...")
    print("Health check: http://127.0.0.1:5000/health")
    print("Main application: http://127.0.0.1:5000/")
    print("=" * 50)
    print()

    app.run(
        debug=True,
        host="127.0.0.1",
        port=5000
    )