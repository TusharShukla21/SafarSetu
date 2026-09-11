PRAGMA foreign_keys = ON;


-- =========================================================
-- USERS
-- =========================================================

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    role TEXT CHECK (role IN ('tourist', 'business') OR role IS NULL),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- =========================================================
-- DESTINATIONS
-- =========================================================

CREATE TABLE IF NOT EXISTS destinations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    state TEXT,
    country TEXT DEFAULT 'India',
    description TEXT,
    best_time TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- =========================================================
-- PLACES
-- =========================================================

CREATE TABLE IF NOT EXISTS places (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    destination_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    category TEXT NOT NULL,
    description TEXT,
    entry_fee REAL DEFAULT 0,
    rating REAL DEFAULT 0,
    location TEXT,
    maps_url TEXT,
    image_url TEXT,

    FOREIGN KEY (destination_id)
        REFERENCES destinations(id)
        ON DELETE CASCADE
);


-- =========================================================
-- STAYS
-- =========================================================

CREATE TABLE IF NOT EXISTS stays (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    destination_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    type TEXT NOT NULL,
    description TEXT,
    price_per_night REAL NOT NULL,
    rating REAL DEFAULT 0,
    location TEXT,
    contact TEXT,
    maps_url TEXT,
    image_url TEXT,

    FOREIGN KEY (destination_id)
        REFERENCES destinations(id)
        ON DELETE CASCADE
);


-- =========================================================
-- STAY OFFERS
-- =========================================================

CREATE TABLE IF NOT EXISTS stay_offers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    stay_id INTEGER NOT NULL,
    platform TEXT NOT NULL,
    price REAL NOT NULL,
    booking_url TEXT,
    checked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (stay_id)
        REFERENCES stays(id)
        ON DELETE CASCADE
);


-- =========================================================
-- TRANSPORT
-- =========================================================

CREATE TABLE IF NOT EXISTS transport (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source TEXT NOT NULL,
    destination TEXT NOT NULL,
    mode TEXT NOT NULL,
    provider TEXT,
    price REAL NOT NULL,
    duration TEXT,
    availability TEXT,
    booking_url TEXT,
    departure_time TEXT,
    arrival_time TEXT
);


-- =========================================================
-- BUSINESSES
-- =========================================================

CREATE TABLE IF NOT EXISTS businesses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    category TEXT NOT NULL,
    description TEXT,
    location TEXT NOT NULL,
    phone TEXT,
    email TEXT,
    website TEXT,
    price_info TEXT,
    maps_url TEXT,
    image_url TEXT,
    status TEXT DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE CASCADE
);


-- =========================================================
-- BUSINESS PACKAGES
-- =========================================================

CREATE TABLE IF NOT EXISTS business_packages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    business_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    start_date TEXT NOT NULL,
    end_date TEXT NOT NULL,
    price REAL NOT NULL,
    available_seats INTEGER DEFAULT 0,
    booking_deadline TEXT,
    inclusions TEXT,
    exclusions TEXT,
    contact TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (business_id)
        REFERENCES businesses(id)
        ON DELETE CASCADE
);


-- =========================================================
-- TRIPS
-- =========================================================

CREATE TABLE IF NOT EXISTS trips (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    source TEXT NOT NULL,
    destination TEXT NOT NULL,
    start_date TEXT NOT NULL,
    end_date TEXT NOT NULL,
    travellers INTEGER NOT NULL,
    budget REAL NOT NULL,
    estimated_cost REAL,
    status TEXT DEFAULT 'planned',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE CASCADE
);


-- =========================================================
-- TRIP PLACES
-- =========================================================

CREATE TABLE IF NOT EXISTS trip_places (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    trip_id INTEGER NOT NULL,
    place_id INTEGER NOT NULL,
    visit_date TEXT,
    visit_order INTEGER,

    FOREIGN KEY (trip_id)
        REFERENCES trips(id)
        ON DELETE CASCADE,

    FOREIGN KEY (place_id)
        REFERENCES places(id)
        ON DELETE CASCADE
);


-- =========================================================
-- TRIP STAYS
-- =========================================================

CREATE TABLE IF NOT EXISTS trip_stays (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    trip_id INTEGER NOT NULL,
    stay_id INTEGER NOT NULL,
    rooms INTEGER DEFAULT 1,

    FOREIGN KEY (trip_id)
        REFERENCES trips(id)
        ON DELETE CASCADE,

    FOREIGN KEY (stay_id)
        REFERENCES stays(id)
        ON DELETE CASCADE
);


-- =========================================================
-- EMERGENCY SERVICES
-- =========================================================

CREATE TABLE IF NOT EXISTS emergency_services (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    category TEXT NOT NULL,
    phone TEXT,
    location TEXT,
    address TEXT,
    maps_url TEXT
);


-- =========================================================
-- INDEXES
-- =========================================================

CREATE INDEX IF NOT EXISTS idx_places_destination
ON places(destination_id);

CREATE INDEX IF NOT EXISTS idx_stays_destination
ON stays(destination_id);

CREATE INDEX IF NOT EXISTS idx_stay_offers_stay
ON stay_offers(stay_id);

CREATE INDEX IF NOT EXISTS idx_businesses_user
ON businesses(user_id);

CREATE INDEX IF NOT EXISTS idx_business_packages_business
ON business_packages(business_id);

CREATE INDEX IF NOT EXISTS idx_trips_user
ON trips(user_id);

CREATE INDEX IF NOT EXISTS idx_trip_places_trip
ON trip_places(trip_id);

CREATE INDEX IF NOT EXISTS idx_trip_stays_trip
ON trip_stays(trip_id);