import sqlite3

from database import get_db_connection, init_database


# =========================================================
# SAFAR SETU - DATABASE SEED DATA
# =========================================================


def clear_demo_data(connection):
    """
    Removes old demo data so seed.py can be safely run again.
    User accounts are NOT deleted.
    """

    connection.execute(
        "DELETE FROM trip_places"
    )

    connection.execute(
        "DELETE FROM trip_stays"
    )

    connection.execute(
        "DELETE FROM trips"
    )

    connection.execute(
        "DELETE FROM business_packages"
    )

    connection.execute(
        "DELETE FROM businesses"
    )

    connection.execute(
        "DELETE FROM stay_offers"
    )

    connection.execute(
        "DELETE FROM transport"
    )

    connection.execute(
        "DELETE FROM places"
    )

    connection.execute(
        "DELETE FROM stays"
    )

    connection.execute(
        "DELETE FROM destinations"
    )

    connection.execute(
        "DELETE FROM emergency_services"
    )


# =========================================================
# DESTINATIONS
# =========================================================

def seed_destinations(connection):

    destinations = [

        (
            "Goa",
            "Goa",
            "India",
            "Goa is a popular tourist destination known for its beaches, forts, waterfalls, food, nightlife and Portuguese heritage.",
            "October to March"
        ),

        (
            "Jaipur",
            "Rajasthan",
            "India",
            "Jaipur is known for its historic forts, palaces, traditional markets and rich Rajasthani culture.",
            "October to March"
        ),

        (
            "Manali",
            "Himachal Pradesh",
            "India",
            "Manali is a mountain destination famous for scenic valleys, snow, adventure activities and beautiful landscapes.",
            "October to June"
        ),

        (
            "Kerala",
            "Kerala",
            "India",
            "Kerala is famous for its backwaters, beaches, hill stations, wildlife and unique cultural experiences.",
            "September to March"
        )

    ]


    connection.executemany(
        """
        INSERT INTO destinations
        (
            name,
            state,
            country,
            description,
            best_time
        )

        VALUES (?, ?, ?, ?, ?)
        """,
        destinations
    )


# =========================================================
# GET DESTINATION ID
# =========================================================

def get_destination_id(connection, name):

    destination = connection.execute(
        """
        SELECT id
        FROM destinations
        WHERE LOWER(name) = LOWER(?)
        """,
        (name,)
    ).fetchone()


    if destination:

        return destination["id"]


    return None


# =========================================================
# PLACES
# =========================================================

def seed_places(connection):

    goa = get_destination_id(
        connection,
        "Goa"
    )

    jaipur = get_destination_id(
        connection,
        "Jaipur"
    )

    manali = get_destination_id(
        connection,
        "Manali"
    )

    kerala = get_destination_id(
        connection,
        "Kerala"
    )


    places = [

        # -------------------------------------------------
        # GOA
        # -------------------------------------------------

        (
            goa,
            "Baga Beach",
            "Beaches",
            "One of Goa's most popular beaches, known for water activities and a lively atmosphere.",
            0,
            4.5,
            "Baga, Goa",
            "https://www.google.com/maps/search/?api=1&query=Baga+Beach+Goa",
            ""
        ),

        (
            goa,
            "Fort Aguada",
            "History",
            "Historic Portuguese fort overlooking the Arabian Sea.",
            50,
            4.4,
            "Candolim, Goa",
            "https://www.google.com/maps/search/?api=1&query=Fort+Aguada+Goa",
            ""
        ),

        (
            goa,
            "Dudhsagar Falls",
            "Nature",
            "A spectacular waterfall located in the Western Ghats.",
            500,
            4.6,
            "Mollem, Goa",
            "https://www.google.com/maps/search/?api=1&query=Dudhsagar+Falls+Goa",
            ""
        ),

        (
            goa,
            "Calangute Beach",
            "Beaches",
            "A famous beach offering sightseeing, food and recreational activities.",
            0,
            4.3,
            "Calangute, Goa",
            "https://www.google.com/maps/search/?api=1&query=Calangute+Beach+Goa",
            ""
        ),

        (
            goa,
            "Water Sports",
            "Adventure",
            "Popular adventure activities including parasailing, jet skiing and boat rides.",
            800,
            4.5,
            "North Goa",
            "https://www.google.com/maps/search/?api=1&query=Water+Sports+Goa",
            ""
        ),

        (
            goa,
            "Goan Food Tour",
            "Food",
            "Explore traditional Goan cuisine and local food experiences.",
            600,
            4.4,
            "Panaji, Goa",
            "https://www.google.com/maps/search/?api=1&query=Goan+Food+Tour+Goa",
            ""
        ),

        (
            goa,
            "Panaji",
            "Culture",
            "Explore Goa's capital, colourful streets, churches and Portuguese-influenced architecture.",
            0,
            4.2,
            "Panaji, Goa",
            "https://www.google.com/maps/search/?api=1&query=Panaji+Goa",
            ""
        ),


        # -------------------------------------------------
        # JAIPUR
        # -------------------------------------------------

        (
            jaipur,
            "Amber Fort",
            "History",
            "A historic fort and palace complex showcasing Rajput architecture.",
            200,
            4.6,
            "Amer, Jaipur",
            "https://www.google.com/maps/search/?api=1&query=Amber+Fort+Jaipur",
            ""
        ),

        (
            jaipur,
            "Hawa Mahal",
            "History",
            "Iconic Jaipur landmark famous for its distinctive honeycomb-style windows.",
            50,
            4.5,
            "Jaipur",
            "https://www.google.com/maps/search/?api=1&query=Hawa+Mahal+Jaipur",
            ""
        ),

        (
            jaipur,
            "City Palace",
            "Culture",
            "Historic palace complex representing Jaipur's royal heritage.",
            300,
            4.5,
            "Jaipur",
            "https://www.google.com/maps/search/?api=1&query=City+Palace+Jaipur",
            ""
        ),

        (
            jaipur,
            "Jantar Mantar",
            "History",
            "Historic astronomical observation site and UNESCO World Heritage Site.",
            50,
            4.4,
            "Jaipur",
            "https://www.google.com/maps/search/?api=1&query=Jantar+Mantar+Jaipur",
            ""
        ),


        # -------------------------------------------------
        # MANALI
        # -------------------------------------------------

        (
            manali,
            "Solang Valley",
            "Adventure",
            "Popular destination for adventure activities and mountain views.",
            500,
            4.5,
            "Manali, Himachal Pradesh",
            "https://www.google.com/maps/search/?api=1&query=Solang+Valley+Manali",
            ""
        ),

        (
            manali,
            "Hadimba Temple",
            "Culture",
            "Ancient wooden temple surrounded by cedar forests.",
            0,
            4.5,
            "Manali",
            "https://www.google.com/maps/search/?api=1&query=Hadimba+Temple+Manali",
            ""
        ),

        (
            manali,
            "Rohtang Pass",
            "Nature",
            "High mountain destination offering spectacular Himalayan scenery.",
            500,
            4.6,
            "Near Manali",
            "https://www.google.com/maps/search/?api=1&query=Rohtang+Pass",
            ""
        ),


        # -------------------------------------------------
        # KERALA
        # -------------------------------------------------

        (
            kerala,
            "Alleppey Backwaters",
            "Nature",
            "Famous backwater destination known for houseboats and scenic waterways.",
            1000,
            4.6,
            "Alappuzha, Kerala",
            "https://www.google.com/maps/search/?api=1&query=Alleppey+Backwaters",
            ""
        ),

        (
            kerala,
            "Munnar",
            "Nature",
            "Beautiful hill station known for tea plantations and mountain scenery.",
            0,
            4.7,
            "Munnar, Kerala",
            "https://www.google.com/maps/search/?api=1&query=Munnar+Kerala",
            ""
        ),

        (
            kerala,
            "Varkala Beach",
            "Beaches",
            "Scenic beach destination famous for cliffs and Arabian Sea views.",
            0,
            4.5,
            "Varkala, Kerala",
            "https://www.google.com/maps/search/?api=1&query=Varkala+Beach+Kerala",
            ""
        )

    ]


    connection.executemany(
        """
        INSERT INTO places
        (
            destination_id,
            name,
            category,
            description,
            entry_fee,
            rating,
            location,
            maps_url,
            image_url
        )

        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        places
    )


# =========================================================
# STAYS
# =========================================================

def seed_stays(connection):

    goa = get_destination_id(
        connection,
        "Goa"
    )

    jaipur = get_destination_id(
        connection,
        "Jaipur"
    )

    manali = get_destination_id(
        connection,
        "Manali"
    )

    kerala = get_destination_id(
        connection,
        "Kerala"
    )


    stays = [

        # -------------------------------------------------
        # GOA
        # -------------------------------------------------

        (
            goa,
            "Sea View Dormitory",
            "Dormitory",
            "Budget-friendly dormitory accommodation near popular tourist areas.",
            500,
            4.0,
            "North Goa",
            "",
            "https://www.google.com/maps/search/?api=1&query=North+Goa",
            ""
        ),

        (
            goa,
            "Goa Comfort Hostel",
            "Hostel",
            "Affordable hostel suitable for solo travellers and budget tourists.",
            700,
            4.2,
            "Calangute, Goa",
            "",
            "https://www.google.com/maps/search/?api=1&query=Calangute+Goa",
            ""
        ),

        (
            goa,
            "Palm Stay Hotel",
            "Hotel",
            "Comfortable mid-range hotel for families and couples.",
            1800,
            4.4,
            "Panaji, Goa",
            "",
            "https://www.google.com/maps/search/?api=1&query=Panaji+Goa",
            ""
        ),

        (
            goa,
            "Goa Premium Resort",
            "Resort",
            "Premium resort experience with comfortable rooms and facilities.",
            3500,
            4.6,
            "Candolim, Goa",
            "",
            "https://www.google.com/maps/search/?api=1&query=Candolim+Goa",
            ""
        ),


        # -------------------------------------------------
        # JAIPUR
        # -------------------------------------------------

        (
            jaipur,
            "Pink City Hostel",
            "Hostel",
            "Budget accommodation close to Jaipur's major attractions.",
            600,
            4.2,
            "Jaipur",
            "",
            "https://www.google.com/maps/search/?api=1&query=Jaipur+Rajasthan",
            ""
        ),

        (
            jaipur,
            "Royal Heritage Hotel",
            "Hotel",
            "Mid-range hotel with traditional Rajasthani atmosphere.",
            1800,
            4.4,
            "Jaipur",
            "",
            "https://www.google.com/maps/search/?api=1&query=Jaipur+Rajasthan",
            ""
        ),


        # -------------------------------------------------
        # MANALI
        # -------------------------------------------------

        (
            manali,
            "Mountain View Hostel",
            "Hostel",
            "Budget stay with mountain views.",
            700,
            4.2,
            "Manali",
            "",
            "https://www.google.com/maps/search/?api=1&query=Manali",
            ""
        ),

        (
            manali,
            "Himalayan Comfort Hotel",
            "Hotel",
            "Comfortable accommodation suitable for families and groups.",
            2200,
            4.5,
            "Manali",
            "",
            "https://www.google.com/maps/search/?api=1&query=Manali",
            ""
        ),


        # -------------------------------------------------
        # KERALA
        # -------------------------------------------------

        (
            kerala,
            "Kerala Backpackers Hostel",
            "Hostel",
            "Affordable accommodation for backpackers and young travellers.",
            600,
            4.2,
            "Kerala",
            "",
            "https://www.google.com/maps/search/?api=1&query=Kerala",
            ""
        ),

        (
            kerala,
            "Kerala Heritage Stay",
            "Homestay",
            "Traditional Kerala-style homestay experience.",
            1500,
            4.5,
            "Kerala",
            "",
            "https://www.google.com/maps/search/?api=1&query=Kerala",
            ""
        )

    ]


    connection.executemany(
        """
        INSERT INTO stays
        (
            destination_id,
            name,
            type,
            description,
            price_per_night,
            rating,
            location,
            contact,
            maps_url,
            image_url
        )

        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        stays
    )


# =========================================================
# STAY OFFERS
# =========================================================

def seed_stay_offers(connection):

    stays = connection.execute(
        """
        SELECT id, name
        FROM stays
        """
    ).fetchall()


    offers = []


    for stay in stays:

        stay_name = stay["name"]


        if stay_name == "Sea View Dormitory":

            offers.extend([

                (
                    stay["id"],
                    "Safar Setu",
                    500,
                    "",
                ),

                (
                    stay["id"],
                    "Booking Platform A",
                    550,
                    "",
                ),

                (
                    stay["id"],
                    "Booking Platform B",
                    600,
                    "",
                )

            ])


        elif stay_name == "Goa Comfort Hostel":

            offers.extend([

                (
                    stay["id"],
                    "Safar Setu",
                    700,
                    "",
                ),

                (
                    stay["id"],
                    "Booking Platform A",
                    750,
                    "",
                ),

                (
                    stay["id"],
                    "Booking Platform B",
                    820,
                    "",
                )

            ])


        elif stay_name == "Palm Stay Hotel":

            offers.extend([

                (
                    stay["id"],
                    "Safar Setu",
                    1800,
                    "",
                ),

                (
                    stay["id"],
                    "Booking Platform A",
                    1950,
                    "",
                ),

                (
                    stay["id"],
                    "Booking Platform B",
                    2100,
                    "",
                )

            ])


        elif stay_name == "Goa Premium Resort":

            offers.extend([

                (
                    stay["id"],
                    "Safar Setu",
                    3500,
                    "",
                ),

                (
                    stay["id"],
                    "Booking Platform A",
                    3700,
                    "",
                ),

                (
                    stay["id"],
                    "Booking Platform B",
                    3900,
                    "",
                )

            ])


    if offers:

        connection.executemany(
            """
            INSERT INTO stay_offers
            (
                stay_id,
                platform,
                price,
                booking_url
            )

            VALUES (?, ?, ?, ?)
            """,
            offers
        )


# =========================================================
# TRANSPORT
# =========================================================

def seed_transport(connection):

    transport = [

        # -------------------------------------------------
        # MUMBAI → GOA
        # -------------------------------------------------

        (
            "Mumbai",
            "Goa",
            "Train",
            "Indian Railways",
            1200,
            "10 hours",
            "Available",
            "",
            "",
            ""
        ),

        (
            "Mumbai",
            "Goa",
            "Bus",
            "Bus Service",
            900,
            "12 hours",
            "Available",
            "",
            "",
            ""
        ),

        (
            "Mumbai",
            "Goa",
            "Flight",
            "Airline",
            3500,
            "1 hour 10 minutes",
            "Limited Seats",
            "",
            "",
            ""
        ),

        (
            "Mumbai",
            "Goa",
            "Own Car",
            "Self Drive",
            2800,
            "11 hours",
            "Available",
            "",
            "",
            ""
        ),

        (
            "Mumbai",
            "Goa",
            "Taxi",
            "Cab Service",
            7000,
            "11 hours",
            "Available",
            "",
            "",
            ""
        ),


        # -------------------------------------------------
        # DELHI → JAIPUR
        # -------------------------------------------------

        (
            "Delhi",
            "Jaipur",
            "Train",
            "Indian Railways",
            600,
            "5 hours",
            "Available",
            "",
            "",
            ""
        ),

        (
            "Delhi",
            "Jaipur",
            "Bus",
            "Bus Service",
            500,
            "6 hours",
            "Available",
            "",
            "",
            ""
        ),

        (
            "Delhi",
            "Jaipur",
            "Flight",
            "Airline",
            2500,
            "1 hour",
            "Limited Seats",
            "",
            "",
            ""
        ),


        # -------------------------------------------------
        # DELHI → MANALI
        # -------------------------------------------------

        (
            "Delhi",
            "Manali",
            "Bus",
            "Volvo Bus",
            1200,
            "12 hours",
            "Available",
            "",
            "",
            ""
        ),

        (
            "Delhi",
            "Manali",
            "Taxi",
            "Cab Service",
            7000,
            "11 hours",
            "Available",
            "",
            "",
            ""
        ),


        # -------------------------------------------------
        # MUMBAI → KERALA
        # -------------------------------------------------

        (
            "Mumbai",
            "Kerala",
            "Flight",
            "Airline",
            5000,
            "2 hours",
            "Available",
            "",
            "",
            ""
        ),

        (
            "Mumbai",
            "Kerala",
            "Train",
            "Indian Railways",
            1800,
            "24 hours",
            "Available",
            "",
            "",
            ""
        )

    ]


    connection.executemany(
        """
        INSERT INTO transport
        (
            source,
            destination,
            mode,
            provider,
            price,
            duration,
            availability,
            booking_url,
            departure_time,
            arrival_time
        )

        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        transport
    )


# =========================================================
# EMERGENCY SERVICES
# =========================================================

def seed_emergency_services(connection):

    services = [

        (
            "Police Emergency",
            "Police",
            "112",
            "India",
            "Emergency Police Assistance",
            ""
        ),

        (
            "Ambulance",
            "Ambulance",
            "108",
            "India",
            "Emergency Medical Assistance",
            ""
        ),

        (
            "Fire Brigade",
            "Fire",
            "101",
            "India",
            "Fire and Rescue Services",
            ""
        ),

        (
            "National Emergency",
            "Emergency",
            "112",
            "India",
            "Unified Emergency Number",
            ""
        ),

        (
            "Tourist Helpline",
            "Tourism",
            "1363",
            "India",
            "Tourist assistance and information",
            ""
        )

    ]


    connection.executemany(
        """
        INSERT INTO emergency_services
        (
            name,
            category,
            phone,
            location,
            address,
            maps_url
        )

        VALUES (?, ?, ?, ?, ?, ?)
        """,
        services
    )


# =========================================================
# MAIN SEED FUNCTION
# =========================================================

def seed_database():

    print()
    print("========================================")
    print("       SAFAR SETU DATABASE SETUP")
    print("========================================")
    print()


    # Make sure tables exist
    init_database()


    connection = get_db_connection()


    try:

        print("Clearing old demo data...")

        clear_demo_data(
            connection
        )


        print("Adding destinations...")

        seed_destinations(
            connection
        )


        print("Adding tourist places...")

        seed_places(
            connection
        )


        print("Adding stays...")

        seed_stays(
            connection
        )


        print("Adding stay offers...")

        seed_stay_offers(
            connection
        )


        print("Adding transport options...")

        seed_transport(
            connection
        )


        print("Adding emergency services...")

        seed_emergency_services(
            connection
        )


        connection.commit()


        print()
        print("========================================")
        print("       DATABASE SEEDING COMPLETE")
        print("========================================")
        print()


    except Exception as error:

        connection.rollback()

        print()
        print("DATABASE SEEDING FAILED")
        print(error)
        print()

        raise


    finally:

        connection.close()


# =========================================================
# RUN
# =========================================================

if __name__ == "__main__":

    seed_database()