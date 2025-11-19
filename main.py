import sys
from datetime import datetime, date
import mysql.connector
from mysql.connector import Error
from PyQt6.uic import loadUi
from PyQt6 import QtWidgets, QtCore
from PyQt6.QtWidgets import QDialog, QApplication, QWidget, QStackedWidget

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Dlsu1234!',
    'database': 'pet_show'
}

_OWNER_CONTEXT_TEMPLATE = {
    'owner_id': None,
    'username': None,
    'first_name': None,
    'last_name': None,
    'email': None,
    'contact_number': None
}
ACTIVE_OWNER = _OWNER_CONTEXT_TEMPLATE.copy()


def set_active_owner(owner_id, username=None, first_name=None, last_name=None, email=None, contact_number=None):
    """Persist the currently authenticated owner's basic profile."""
    global ACTIVE_OWNER
    ACTIVE_OWNER = {
        'owner_id': owner_id,
        'username': username,
        'first_name': first_name,
        'last_name': last_name,
        'email': email,
        'contact_number': contact_number
    }


def clear_active_owner():
    """Reset the cached owner context (e.g., after logout)."""
    global ACTIVE_OWNER
    ACTIVE_OWNER = _OWNER_CONTEXT_TEMPLATE.copy()


def get_active_owner():
    """Return the active owner's context, if any."""
    if ACTIVE_OWNER.get('owner_id') is None:
        return None
    return ACTIVE_OWNER


def get_active_owner_id():
    """Convenience helper: return the current owner_id or None."""
    owner = get_active_owner()
    return owner['owner_id'] if owner else None


def update_active_owner_details(**kwargs):
    """Update selected fields of the cached owner context."""
    if ACTIVE_OWNER.get('owner_id') is None:
        return
    for key, value in kwargs.items():
        if key in ACTIVE_OWNER and value is not None:
            ACTIVE_OWNER[key] = value
            
def get_db_connection():
    """Open a MySQL connection using the config above."""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        if conn.is_connected():
            conn.autocommit = False
        return conn
    except Error as err:
        print(f"MySQL Connection Error: {err}")
        return None


def to_python_date(value):
    """Try to turn whatever this is into a plain date."""
    if value is None:
        return None
    if isinstance(value, date) and not isinstance(value, datetime):
        return value
    if isinstance(value, datetime):
        return value.date()
    value_str = str(value)
    for fmt in ("%Y-%m-%d", "%Y/%m/%d"):
        try:
            return datetime.strptime(value_str, fmt).date()
        except ValueError:
            continue
    return None


def format_date_string(value):
    """Turn a date-ish value into a nice YYYY-MM-DD string."""
    parsed = to_python_date(value)
    if parsed:
        return parsed.strftime("%Y-%m-%d")
    return str(value) if value not in (None, '') else ''

def setup_database():
   
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            
            # ----------------------------------------------------------------------
                
            # size_category 
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS size_category (
                size_id INTEGER NOT NULL PRIMARY KEY,
                size_name TEXT NOT NULL
            )
            """)
            
            # owners
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS owners (
                owner_id INTEGER NOT NULL PRIMARY KEY,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                email TEXT,
                contact_number TEXT
            )
            """)

            # breeds 
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS breeds (
                breed_id INTEGER NOT NULL PRIMARY KEY,
                breed_name TEXT NOT NULL,
                size_id INTEGER NOT NULL,
                FOREIGN KEY (size_id) REFERENCES size_category(size_id)
            )
            """)
            
            
            # events 
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS events (
                event_id INTEGER NOT NULL PRIMARY KEY,
                name TEXT NOT NULL,
                date TEXT NOT NULL,
                time TEXT NOT NULL,
                location TEXT NOT NULL,
                max_participants INTEGER NOT NULL,
                registration_deadline TEXT NOT NULL,
                type TEXT NOT NULL,
                distance_km REAL,
                time_limit INTEGER,
                status INTEGER NOT NULL, -- 1 = open, 0 = closed
                base_registration_fee REAL NOT NULL,
                extra_pet_discount REAL NOT NULL,
                min_weight REAL,
                max_weight REAL,
                min_size_id INTEGER,
                max_size_id INTEGER,
                FOREIGN KEY (min_size_id) REFERENCES size_category(size_id),
                FOREIGN KEY (max_size_id) REFERENCES size_category(size_id)
            )
            """)

            # pets
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS pets (
                pet_id INTEGER NOT NULL PRIMARY KEY,
                owner_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                actual_size_id INTEGER NOT NULL,
                age INTEGER NOT NULL,
                sex TEXT NOT NULL,
                weight_kg REAL NOT NULL,
                muzzle_required INTEGER NOT NULL,
                notes TEXT,
                FOREIGN KEY (owner_id) REFERENCES owners(owner_id),
                FOREIGN KEY (actual_size_id) REFERENCES size_category(size_id)
            )
            """)
            
            # pet_breed_junction
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS pet_breed_junction (
                pet_id INTEGER NOT NULL,
                breed_id INTEGER NOT NULL,
                PRIMARY KEY (pet_id, breed_id),
                FOREIGN KEY (pet_id) REFERENCES pets(pet_id),
                FOREIGN KEY (breed_id) REFERENCES breeds(breed_id)
            )
            """)

            # event_registration
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS event_registration (
                registration_id INTEGER NOT NULL PRIMARY KEY,
                owner_id INTEGER NOT NULL,
                event_id INTEGER NOT NULL,
                registration_date TEXT NOT NULL,
                total_amount_paid REAL NOT NULL,
                payment_date TEXT NOT NULL,
                payment_time TEXT NOT NULL,
                status TEXT NOT NULL,
                transfer_destination INTEGER NULL,
                cancellation_date TEXT NULL,
                FOREIGN KEY (owner_id) REFERENCES owners(owner_id),
                FOREIGN KEY (event_id) REFERENCES events(event_id),
                FOREIGN KEY (transfer_destination) REFERENCES event_registration(registration_id)
            )
            """)

            # pet_event_entry
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS pet_event_entry (
                entry_id INTEGER NOT NULL PRIMARY KEY,
                registration_id INTEGER NOT NULL,
                pet_id INTEGER NOT NULL,
                event_id INTEGER NOT NULL,
                attendance_status TEXT NOT NULL,
                pet_result REAL NULL,
                UNIQUE (pet_id, event_id),
                FOREIGN KEY (registration_id) REFERENCES event_registration(registration_id),
                FOREIGN KEY (pet_id) REFERENCES pets(pet_id),
                FOREIGN KEY (event_id) REFERENCES events(event_id)
            )
            """)

            # awards
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS awards (
                    award_id INT NOT NULL PRIMARY KEY,
                    pet_id INT,
                    is_special TINYINT(1) NOT NULL,
                    award_name VARCHAR(100) NOT NULL,
                    description TEXT,
                    date DATE NOT NULL,
                    event_id INT NOT NULL,
                    CONSTRAINT fk_award_pet FOREIGN KEY (pet_id) REFERENCES pets(pet_id),
                    CONSTRAINT fk_award_event FOREIGN KEY (event_id) REFERENCES events(event_id)
            )
            """)

            # participation_log
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS participation_log (
                log_id INTEGER NOT NULL PRIMARY KEY,
                registration_id INTEGER NOT NULL,
                action_type TEXT NOT NULL,
                action_date TEXT NOT NULL,
                action_time TEXT NOT NULL,
                original_event_id INTEGER NOT NULL,
                new_event_id INTEGER NULL,
                reason TEXT,
                refund_amount REAL,
                top_up_amount REAL,
                FOREIGN KEY (registration_id) REFERENCES event_registration(registration_id),
                FOREIGN KEY (original_event_id) REFERENCES events(event_id),
                FOREIGN KEY (new_event_id) REFERENCES events(event_id)
            )
            """)
            
            # admin_log
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS admin_log (
                admin_id INT NOT NULL PRIMARY KEY,
                username VARCHAR(50) NOT NULL UNIQUE,
                password VARCHAR(255) NOT NULL,
                first_name VARCHAR(50) NOT NULL,
                last_name VARCHAR(50) NOT NULL
            )
            """)
            
            # owner_log
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS owner_log (
                owner_id INT NOT NULL PRIMARY KEY,
                username VARCHAR(50) NOT NULL UNIQUE,
                password VARCHAR(255) NOT NULL,
                first_name VARCHAR(50) NOT NULL,
                last_name VARCHAR(50) NOT NULL,
                email TEXT,
                contact_number TEXT,
                FOREIGN KEY (owner_id) REFERENCES owners(owner_id)
            )
            """)
           
            # size_category
            cursor.executemany("INSERT IGNORE INTO size_category (size_id, size_name) VALUES (%s, %s)", [
                (1, 'Small'), (2, 'Medium'), (3, 'Large')
            ])
            
            # owners
            cursor.executemany("INSERT IGNORE INTO owners (owner_id, first_name, last_name, email, contact_number) VALUES (%s, %s, %s, %s, %s)", [
                (1, 'Miguel', 'Santos', 'miguel.santos@example.com', '09171234567'), (2, 'Anna', 'Reyes', 'anna.reyes@example.com', '09181234567'), 
                (3, 'Diego', 'Velasco', 'diego.velasco@example.com', '09191234567'), (4, 'Hannah', 'Lopez', 'h.lopez@example.com', '09201234567'), 
                (5, 'Rafael', 'DelaCruz', 'rafael.delacruz@example.com', '09211234567'), (6, 'Sofia', 'Garcia', 'sofia.garcia@example.com', '09221234567'), 
                (7, 'Ethan', 'Tan', 'ethan.tan@example.com', '09231234567'), (8, 'Lara', 'Gomez', 'lara.gomez@example.com', '09241234567'), 
                (9, 'Carlos', 'Mendoza', 'c.mendoza@example.com', '09251234567'), (10, 'Isabel', 'Paredes', 'isabel.paredes@example.com', '09261234567'), 
                (11, 'Mark', 'Cruz', 'mark.cruz@example.com', '09271234567'), (12, 'Jocelyn', 'Lo', 'jocelyn.lo@example.com', '09281234567'), 
                (13, 'Noah', 'Bautista', 'noah.bautista@example.com', '09291234567'), (14, 'Maya', 'Ortiz', 'maya.ortiz@example.com', '09301234567'), 
                (15, 'Paul', 'Serrano', 'paul.serrano@example.com', '09311234567')
            ])

            # breeds
            cursor.executemany("INSERT IGNORE INTO breeds (breed_id, breed_name, size_id) VALUES (%s, %s, %s)", [
                (1, 'Chihuahua', 1), (2, 'Pomeranian', 1), (3, 'Dachshund', 1), (4, 'Beagle', 2), (5, 'Bulldog', 2),
                (6, 'Labrador Retriever', 3), (7, 'Golden Retriever', 3), (8, 'Border Collie', 2), (9, 'German Shepherd', 3),
                (10, 'Great Dane', 3), (11, 'Jack Russell Terrier', 1), (12, 'French Bulldog', 2), (13, 'Shih Tzu', 1),
                (14, 'Poodle (Miniature)', 1), (15, 'Australian Shepherd', 2)
            ])
            
            # events
            cursor.executemany("INSERT IGNORE INTO events (event_id, name, date, time, location, max_participants, registration_deadline, type, distance_km, time_limit, status, base_registration_fee, extra_pet_discount, min_weight, max_weight, min_size_id, max_size_id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", [
                (1, 'Dog Fun Run - Event Starter', '2025-11-21', '07:00:00', 'Greenfield Park, Manila', 150, '2025-11-10', 'Fun Run', 3.00, 60, 1, 300.00, 50.00, None, None, 1, 3),
                (2, 'Dog Agility Course - Tunnels & Jumps', '2025-11-21', '09:00:00', 'Greenfield Park, Manila', 60, '2025-11-10', 'Agility', None, 30, 1, 400.00, 75.00, None, None, 1, 3),
                (3, 'Obedience Challenge', '2025-11-21', '11:00:00', 'Greenfield Park, Manila', 40, '2025-11-10', 'Obedience', None, 20, 1, 250.00, 40.00, None, None, 1, 3),
                (4, 'Best Costume Contest', '2025-11-21', '14:00:00', 'Greenfield Park, Manila', 100, '2025-11-12', 'Fashion', None, None, 1, 200.00, 30.00, None, None, 1, 3),
                (5, 'Dog & Owner Look-Alike', '2025-11-22', '08:00:00', 'Sunset Boulevard', 50, '2025-11-13', 'Fun', None, None, 1, 150.00, 20.00, None, None, 1, 3),
                (6, 'Fastest Fetch Competition', '2025-11-22', '10:00:00', 'Sunset Boulevard', 80, '2025-11-13', 'Competition', None, 10, 1, 180.00, 25.00, None, None, 1, 3),
                (7, 'Dog Talent Show', '2025-11-22', '12:00:00', 'Sunset Boulevard', 60, '2025-11-13', 'Showcase', None, None, 1, 220.00, 30.00, None, None, 1, 3),
                (8, 'Strongest Dog (Tug-of-War) - Weight Classes', '2025-11-22', '15:00:00', 'Sunset Boulevard', 40, '2025-11-15', 'Strength', None, None, 1, 300.00, 50.00, 5.00, 80.00, 2, 3),
                (9, 'Dog Parade / Walkathon', '2025-11-23', '06:30:00', 'Baywalk Promenade', 200, '2025-11-15', 'Parade', 2.00, None, 1, 120.00, 20.00, None, None, 1, 3),
                (10, 'Canine Frisbee Challenge', '2025-11-23', '09:00:00', 'Baywalk Promenade', 60, '2025-11-16', 'Frisbee', None, 30, 1, 260.00, 40.00, None, None, 1, 3),
                (11, 'Photo Booth & Dog Modeling', '2025-11-23', '13:00:00', 'Baywalk Promenade', 120, '2025-11-16', 'Modeling', None, None, 1, 140.00, 20.00, None, None, 1, 3),
                (12, 'Awarding Ceremony - Closing Program', '2025-11-23', '17:00:00', 'Baywalk Main Stage', 500, '2025-11-18', 'Ceremony', None, None, 1, 0.00, 0.00, None, None, 1, 3)
            ])

            # pets
            cursor.executemany("INSERT IGNORE INTO pets (pet_id, owner_id, name, actual_size_id, age, sex, weight_kg, muzzle_required, notes) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)", [
                (1, 1, 'Rico', 3, 4, 'Male', 28.50, 0, 'Loves fetch; friendly with kids'), (2, 1, 'Pip', 1, 2, 'Female', 4.10, 0, 'Tiny, energetic'),
                (3, 2, 'Luna', 1, 2, 'Female', 4.20, 0, 'Very photogenic; short-haired'), (4, 2, 'Mochi', 1, 1, 'Male', 3.60, 0, 'Affectionate lap dog'),
                (5, 3, 'Max', 3, 6, 'Male', 30.00, 0, 'Good at recall'), (6, 4, 'Bella', 2, 3, 'Female', 12.30, 0, 'Agile and fast'),
                (7, 5, 'Bruno', 3, 5, 'Male', 36.00, 1, 'Tug-of-war champion'), (8, 5, 'Fiona', 2, 2, 'Female', 14.50, 0, 'Friendly and playful'),
                (9, 6, 'Milo', 1, 1, 'Male', 3.50, 0, 'Tiny and energetic'), (10, 7, 'Nala', 3, 4, 'Female', 29.00, 0, 'Shepherd mix; high stamina'),
                (11, 7, 'Echo', 2, 3, 'Male', 18.00, 0, 'Smart and attentive'), (12, 8, 'Coco', 1, 7, 'Female', 5.10, 0, 'Great in modeling and photo booths'),
                (13, 9, 'Thor', 3, 3, 'Male', 40.00, 1, 'Large breed; strong pull'), (14, 9, 'Zeus', 3, 2, 'Male', 34.00, 0, 'Playful but strong'),
                (15, 10, 'Daisy', 2, 2, 'Female', 14.00, 0, 'Excellent in agility, loves tunnels'), (16, 11, 'Ollie', 1, 5, 'Male', 6.20, 0, 'Fast fetcher'),
                (17, 11, 'Nibbles', 1, 3, 'Female', 4.90, 0, 'Small and spunky'), (18, 12, 'Gigi', 2, 4, 'Female', 20.00, 0, 'Performs tricks well'),
                (19, 13, 'Poppy', 1, 3, 'Female', 4.80, 0, 'Fashion-forward for costumes'), (20, 13, 'Sprout', 1, 1, 'Male', 3.30, 0, 'Tiny pup'),
                (21, 14, 'Rex', 3, 6, 'Male', 38.50, 1, 'Strong tug-of-war competitor'), (22, 15, 'Buddy', 3, 2, 'Male', 32.00, 0, 'Friendly parade walker'),
                (23, 15, 'Sunny', 2, 4, 'Female', 16.00, 0, 'Good with crowds'), (24, 4, 'Biscuit', 1, 2, 'Female', 5.00, 0, 'Cute costume favorite'),
                (25, 6, 'Gizmo', 1, 2, 'Male', 4.40, 0, 'Quick and curious')
            ])
            
            # Ensure seeded owners have login credentials by default
            cursor.execute("""
                INSERT INTO owner_log (owner_id, username, password, first_name, last_name, email, contact_number)
                SELECT o.owner_id,
                       CONCAT('owner', o.owner_id),
                       'owner123',
                       o.first_name,
                       o.last_name,
                       o.email,
                       o.contact_number
                FROM owners o
                WHERE NOT EXISTS (
                    SELECT 1 FROM owner_log ol WHERE ol.owner_id = o.owner_id
                )
            """)

            # pet_breed_junction
            cursor.executemany("INSERT IGNORE INTO pet_breed_junction (pet_id, breed_id) VALUES (%s, %s)", [
                (1, 6), (2, 14), (3, 14), (4, 1), (5, 6), (6, 4), (7, 9), (8, 5), (9, 1), (10, 9), (11, 8), (12, 2),
                (13, 10), (14, 6), (15, 8), (16, 11), (17, 13), (18, 12), (19, 13), (20, 1), (21, 5), (22, 7), 
                (23, 4), (24, 2), (25, 3)
            ])

            # event_registration
            cursor.executemany("INSERT IGNORE INTO event_registration (registration_id, owner_id, event_id, registration_date, total_amount_paid, payment_date, payment_time, status, transfer_destination, cancellation_date) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", [
                (1, 1, 1, '2025-11-05', 300.00, '2025-11-05', '09:30:00', 'Paid', None, None), (2, 2, 4, '2025-11-06', 200.00, '2025-11-06', '10:10:00', 'Paid', None, None),
                (3, 3, 2, '2025-11-07', 400.00, '2025-11-07', '11:20:00', 'Paid', None, None), (4, 4, 10, '2025-11-07', 260.00, '2025-11-07', '12:00:00', 'Paid', None, None),
                (5, 5, 8, '2025-11-08', 300.00, '2025-11-08', '09:00:00', 'Paid', None, None), (6, 6, 9, '2025-11-09', 120.00, '2025-11-09', '08:30:00', 'Paid', None, None),
                (7, 7, 1, '2025-11-09', 300.00, '2025-11-09', '09:15:00', 'Paid', None, None), (8, 8, 11, '2025-11-10', 140.00, '2025-11-10', '10:00:00', 'Paid', None, None),
                (9, 9, 8, '2025-11-10', 300.00, '2025-11-10', '11:45:00', 'Paid', None, None), (10, 10, 2, '2025-11-11', 400.00, '2025-11-11', '09:50:00', 'Paid', None, None),
                (11, 11, 6, '2025-11-11', 180.00, '2025-11-11', '10:05:00', 'Paid', None, None), (12, 12, 7, '2025-11-12', 220.00, '2025-11-12', '14:30:00', 'Paid', None, None),
                (13, 13, 4, '2025-11-12', 200.00, '2025-11-12', '15:00:00', 'Paid', None, None), (14, 14, 8, '2025-11-13', 300.00, '2025-11-13', '16:20:00', 'Paid', None, None),
                (15, 15, 9, '2025-11-13', 120.00, '2025-11-13', '17:05:00', 'Paid', None, None), (16, 1, 11, '2025-11-14', 140.00, '2025-11-14', '10:00:00', 'Paid', None, None),
                (17, 4, 4, '2025-11-14', 200.00, '2025-11-14', '11:00:00', 'Paid', None, None), (18, 5, 2, '2025-11-14', 400.00, '2025-11-14', '11:30:00', 'Paid', None, None)
            ])

            # pet_event_entry
            cursor.executemany("INSERT IGNORE INTO pet_event_entry (entry_id, registration_id, pet_id, event_id, attendance_status, pet_result) VALUES (%s, %s, %s, %s, %s, %s)", [
                (1, 1, 1, 1, 'Present', 8.7), (2, 2, 3, 4, 'Present', 9.3), (3, 3, 5, 2, 'Present', 9.8), (4, 4, 6, 10, 'Present', 8.9), 
                (5, 5, 7, 8, 'Present', 9.4), (6, 6, 9, 9, 'Present', 8.2), (7, 7, 10, 1, 'Present', 8.6), (8, 8, 12, 11, 'Present', 9.7), 
                (9, 9, 13, 8, 'No Show', 0.0), (10, 10, 15, 2, 'Present', 9.9), (11, 11, 16, 6, 'Present', 9.5), (12, 12, 18, 7, 'Present', 9.1), 
                (13, 13, 19, 4, 'Present', 8.8), (14, 14, 21, 8, 'Present', 9.6), (15, 15, 22, 9, 'Present', 8.4), (16, 16, 2, 11, 'Present', 9.2), 
                (17, 17, 24, 4, 'Present', 8.9), (18, 18, 5, 3, 'Present', 9.0), (19, 3, 8, 2, 'Present', 8.7), (20, 5, 23, 9, 'Present', 8.5)
            ])

            # awards
            cursor.executemany("INSERT IGNORE INTO awards (award_id, pet_id, is_special, award_name, description, date, event_id) VALUES (%s, %s, %s, %s, %s, %s, %s)", [
                (1, None, 0, 'Best Costume - 1st Place', 'Pirate-themed costume, high creativity', '2025-11-21', 4),
                (2, None, 0, 'Best Costume - 2nd Place', 'Colorful tutu and hat', '2025-11-21', 4),
                (3, None, 1, 'Agility - Fastest Run', 'Completed course fastest in novice division', '2025-11-21', 2),
                (4, None, 1, 'Frisbee - Best Catch', 'Long-distance catch accuracy', '2025-11-23', 10),
                (5, None, 1, 'Fun Run - Top Veteran', 'Top among 3-5 year old category', '2025-11-21', 1),
                (6, None, 1, 'Fastest Fetch - Winner', 'Fastest retrieve time', '2025-11-22', 6),
                (7, None, 1, 'Best Talent', 'Multiple tricks performed with style', '2025-11-22', 7),
                (8, None, 0, 'Strongest Dog - Runner Up', 'Excellent tug strength in heavy weight class', '2025-11-22', 8),
                (9, None, 1, 'Parade - Most Cheerful', 'Engaged crowd with playful antics', '2025-11-23', 9),
                (10, None, 1, 'Photo Booth - Most Photogenic', 'Great poses and expressiveness', '2025-11-23', 11),
                (11, None, 1, 'Fun Run - Most Spirited', 'High energy throughout', '2025-11-21', 1),
                (12, None, 0, 'Strongest Dog - Champion', 'Champion of tug-of-war heavy class', '2025-11-22', 8),
                (13, None, 0, 'Obedience - 1st Place', 'Highest obedience score overall', '2025-11-28', 3),
                (14, None, 0, 'Obedience - 2nd Place', 'Very strong performance', '2025-11-28', 3),
                (15, None, 1, 'Look-Alike - Best Pair', 'Dog-owner duo with strongest resemblance', '2025-11-29', 5),
                (16, None, 1, 'Look-Alike - Most Creative', 'Unique coordinated styling', '2025-11-29', 5)
            ])

            # participation_log
            cursor.executemany("INSERT IGNORE INTO participation_log (log_id, registration_id, action_type, action_date, action_time, original_event_id, new_event_id, reason, refund_amount, top_up_amount) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", [
                (1, 1, 'Modified', '2025-11-06', '09:00:00', 1, None, 'Updated emergency contact', 0.00, 0.00), (2, 2, 'Transferred', '2025-11-09', '10:00:00', 4, 11, 'Owner requested transfer to Photo Booth', 0.00, 0.00),
                (3, 3, 'Paid', '2025-11-07', '11:20:00', 2, None, 'Full payment received', 0.00, 0.00), (4, 4, 'Cancelled', '2025-11-10', '12:30:00', 10, None, 'Owner withdrew due to travel', 260.00, 0.00),
                (5, 5, 'Paid', '2025-11-08', '09:00:00', 8, None, 'Paid and confirmed', 0.00, 0.00), (6, 6, 'Paid', '2025-11-09', '08:30:00', 9, None, 'Paid and confirmed', 0.00, 0.00),
                (7, 7, 'Modified', '2025-11-09', '09:20:00', 1, None, 'Added another pet later', 0.00, 0.00), (8, 8, 'Paid', '2025-11-10', '10:05:00', 11, None, 'Payment done at cashier', 0.00, 0.00),
                (9, 9, 'No Show Logged', '2025-11-22', '16:00:00', 8, None, 'Dog did not attend tug-of-war', 0.00, 0.00), (10, 10, 'Transfer Requested', '2025-11-12', '09:55:00', 2, None, 'Owner asked to move to mini agility (pending)', 0.00, 0.00),
                (11, 11, 'Paid', '2025-11-11', '10:05:00', 6, None, '', 0.00, 0.00), (12, 12, 'Paid', '2025-11-12', '14:30:00', 7, None, '', 0.00, 0.00),
                (13, 13, 'Transferred', '2025-11-13', '15:30:00', 4, 2, 'Switched events to agility', 0.00, 200.00), (14, 14, 'Paid', '2025-11-13', '16:20:00', 8, None, '', 0.00, 0.00),
                (15, 15, 'Paid', '2025-11-13', '17:05:00', 9, None, '', 0.00, 0.00)
            ])

            conn.commit()
            print("Database setup complete with 10 tables and initial data.")
        except Error as e:
            print(f"Database setup error: {e}")
        finally:
            if conn:
                conn.close()

# --------------------------------------------------------------------------------------------------------------------

class RegisterScreen(QDialog):
    def __init__(self):
        super(RegisterScreen, self).__init__()
        loadUi('./gui/registerscreen.ui', self) 
        clear_active_owner()
        self.loginbutt.clicked.connect(self.gotologin)
        self.exitbutt.clicked.connect(self.quit_application)

    def gotologin(self):
        log = login()
        widget.addWidget(log)
        widget.setCurrentIndex(widget.currentIndex() + 1)

    def quit_application(self):
        app.quit()

# --------------------------------------------------------------------------------------------------------------------

class login(QDialog):
    def __init__(self):
        super(login, self).__init__()
        loadUi('./gui/login.ui', self)
        self.exitbutt.clicked.connect(self.gotoregscreen)
        self.adminlogbutt.clicked.connect(self.gotoadminlog)
        self.ownerlogbutt.clicked.connect(self.ownerlogbut)

    def gotoregscreen(self):
        reg = RegisterScreen()
        widget.addWidget(reg)
        widget.setCurrentIndex(widget.currentIndex() + 1)
    
    def gotoadminlog(self):
        admlog = adminlog()
        widget.addWidget(admlog)
        widget.setCurrentIndex(widget.currentIndex() + 1)
    
    def ownerlogbut(self):
        owlog = ownerlogin()
        widget.addWidget(owlog)
        widget.setCurrentIndex(widget.currentIndex() + 1)
        
# --------------------------------------------------------------------------------------------------------------------
class ownerlogin(QDialog):
    def __init__(self):
        super(ownerlogin, self).__init__()
        loadUi('./gui/ownerlogin.ui', self)
        self.loginbutt.clicked.connect(self.login)
        self.exitbutt.clicked.connect(self.gotoregscreen)
        self.signupbutt.clicked.connect(self.gotoowonersignup)
        self.logerrormes = self.findChild(QtWidgets.QLabel, 'logerrormes')

        # Mask password input like the admin login screen
        self.password.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)

    def gotoregscreen(self):
        reg = RegisterScreen()
        widget.addWidget(reg)
        widget.setCurrentIndex(widget.currentIndex() + 1)
    
    def gotoowonersignup(self):
        owreg = OwnerRegisScreen()
        widget.addWidget(owreg)
        widget.setCurrentIndex(widget.currentIndex() + 1)

    def login(self):
        """Authenticate owner credentials."""
        username = self.username.text().strip()
        password = self.password.text().strip()

        if self.logerrormes:
            self.logerrormes.setText('')

        if not username or not password:
            if self.logerrormes:
                self.logerrormes.setText('Please enter both username and password.')
            return

        conn = get_db_connection()
        if not conn:
            if self.logerrormes:
                self.logerrormes.setText('Database connection failed.')
            return

        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT owner_id, username, first_name, last_name, email, contact_number
                FROM owner_log
                WHERE username = %s AND password = %s
            """, (username, password))

            result = cursor.fetchone()
            if result:
                owner_id, db_username, first_name, last_name, email, contact_number = result
                set_active_owner(
                    owner_id=owner_id,
                    username=db_username,
                    first_name=first_name,
                    last_name=last_name,
                    email=email,
                    contact_number=contact_number
                )
                self.gotommenu()
            else:
                if self.logerrormes:
                    self.logerrormes.setText('Invalid username or password.')
        except Error as err:
            print(f"Owner login error: {err}")
            if self.logerrormes:
                self.logerrormes.setText('Login failed. Please try again.')
        finally:
            if conn:
                conn.close()

    def gotommenu(self):
        mmenu = mainmenu()
        widget.addWidget(mmenu)
        widget.setCurrentIndex(widget.currentIndex() + 1)
        
# --------------------------------------------------------------------------------------------------------------------

class OwnerRegisScreen(QDialog):
    def __init__(self):
        super(OwnerRegisScreen, self).__init__()
        loadUi('./gui/ownerregistration.ui', self)
        self.owregbutt.clicked.connect(self.registerfunc)
        self.exitbutt.clicked.connect(self.gotoregscreen)
        self.owerrormes = self.findChild(QtWidgets.QLabel, 'owerrormes')
        self.password.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)
        
    def gotoregscreen(self):
        reg = RegisterScreen()
        widget.addWidget(reg)
        widget.setCurrentIndex(widget.currentIndex() + 1)
        
    def registerfunc(self):
        username = self.username.text().strip()
        password = self.password.text().strip()
        userfirstname = self.owfirstname.text().strip()
        userlastname = self.owlastname.text().strip()
        useremail = self.owemail.text().strip()
        usernumber = self.ownumber.text().strip()
        
        self.owerrormes.setText('') 

        if not username or not password or not userfirstname or not userlastname:
            self.owerrormes.setText('Please fill in all required fields.')  
            return
        
        if not useremail and not usernumber:
            self.owerrormes.setText('Provide atleast an email address or mobile number.')
            return
        
        conn = get_db_connection()
        
        if conn:
            try:
                cursor = conn.cursor()
                
                # Ensure username is unique
                cursor.execute("SELECT owner_id FROM owner_log WHERE username = %s", (username,))
                if cursor.fetchone():
                    self.owerrormes.setText('Username already exists. Please choose another.')
                    return
                
                # Get owner_id
                cursor.execute("SELECT MAX(owner_id) FROM owners")
                max_id = cursor.fetchone()[0]
                new_owner_id = (max_id if max_id is not None else 0) + 1
                
                # Insert into the database
                sql = "INSERT INTO owners (owner_id, first_name, last_name, email, contact_number) VALUES (%s, %s, %s, %s, %s)"
                data = (new_owner_id, userfirstname, userlastname, useremail or None, usernumber or None)
                
                cursor.execute(sql, data)
                # Store login credentials
                cursor.execute("""
                    INSERT INTO owner_log (owner_id, username, password, first_name, last_name, email, contact_number)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (new_owner_id, username, password, userfirstname, userlastname, useremail, usernumber))
                conn.commit()
                set_active_owner(
                    owner_id=new_owner_id,
                    username=username,
                    first_name=userfirstname,
                    last_name=userlastname,
                    email=useremail,
                    contact_number=usernumber
                )
                print(f"Owner successfully registered with ID: {new_owner_id}")
                self.gotommenu()

            except Error as err:
                print(f"Database INSERT Error (Owner): {err}")
                if conn:
                    conn.rollback()
                self.owerrormes.setText(f'Registration failed: Database Error.')
            except Exception as e:
                print(f"Unexpected Error during registration: {e}")
                if conn:
                    conn.rollback()
                self.owerrormes.setText('An unexpected error occurred.')
            finally:
                if conn:
                    conn.close()
        else:
            self.owerrormes.setText('Database connection failed. Check file access.')

    def gotommenu(self):
        mmenu = mainmenu()
        widget.addWidget(mmenu)
        widget.setCurrentIndex(widget.currentIndex() + 1)
    
# --------------------------------------------------------------------------------------------------------------------

class adminlog(QDialog):
    def __init__(self):
        super(adminlog, self).__init__()
        loadUi('./gui/adminlogscreen.ui', self)
        self.loginbutt.clicked.connect(self.login)
        self.signupbutt.clicked.connect(self.gotoadminsignup)
        self.exitbutt.clicked.connect(self.gotoregscreen)
        self.logerrormes = self.findChild(QtWidgets.QLabel, 'logerrormes')
        
        # Make password field hide characters
        self.password.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)
    
    
    def gotoregscreen(self):
        reg = RegisterScreen()
        widget.addWidget(reg)
        widget.setCurrentIndex(widget.currentIndex() + 1)

    def login(self):
        """Handle admin login."""
        username = self.username.text().strip()
        password = self.password.text().strip()
        
        self.logerrormes.setText('')
        
        if not username or not password:
            self.logerrormes.setText('Please enter both username and password.')
            return
        
        conn = get_db_connection()
        if not conn:
            self.logerrormes.setText('Database connection failed.')
            return
        
        try:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT admin_id, username, first_name, last_name
                FROM admin_log
                WHERE username = %s AND password = %s
            """, (username, password))
            
            result = cursor.fetchone()
            
            if result:
                # Login successful
                self.gotoadminmenu()
            else:
                self.logerrormes.setText('Invalid username or password.')
        except Error as err:
            print(f"Error during login: {err}")
            self.logerrormes.setText('Login failed. Please try again.')
        finally:
            if conn:
                conn.close()

    def gotoadminmenu(self):
        admmn = adminmenu()
        widget.addWidget(admmn)
        widget.setCurrentIndex(widget.currentIndex() + 1)

    def gotoadminsignup(self):
        adsign = adminmsignup()
        widget.addWidget(adsign)
        widget.setCurrentIndex(widget.currentIndex() + 1)
        
# --------------------------------------------------------------------------------------------------------------------
class adminmsignup(QDialog):
    def __init__(self):
        super(adminmsignup, self).__init__()
        loadUi('./gui/adminsignup.ui', self)
        self.signupbutt.clicked.connect(self.signup)
        self.logerrormes = self.findChild(QtWidgets.QLabel, 'logerrormes')
        self.exitbutt.clicked.connect(self.gotoadminscreen)
        
        # Make password field hide characters
        self.password.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)
    
    def gotoadminscreen(self):
        admn = adminlog()
        widget.addWidget(admn)
        widget.setCurrentIndex(widget.currentIndex() + 1)

    def signup(self):
        """Handle admin signup."""
        username = self.username.text().strip()
        password = self.password.text().strip()
        first_name = self.firstname.text().strip()
        last_name = self.lastname.text().strip()
        
        self.logerrormes.setText('')
        
        if not username or not password or not first_name or not last_name:
            self.logerrormes.setText('Please fill in all fields.')
            return
        
        conn = get_db_connection()
        if not conn:
            self.logerrormes.setText('Database connection failed.')
            return
        
        try:
            cursor = conn.cursor()
            
            # Check if username already exists
            cursor.execute("SELECT admin_id FROM admin_log WHERE username = %s", (username,))
            if cursor.fetchone():
                self.logerrormes.setText('Username already exists. Please choose another.')
                conn.close()
                return
            
            # Get next admin_id
            cursor.execute("SELECT MAX(admin_id) FROM admin_log")
            max_admin_id = cursor.fetchone()[0]
            new_admin_id = (max_admin_id if max_admin_id is not None else 0) + 1
            
            # Insert new admin with plain text password
            cursor.execute("""
                INSERT INTO admin_log (admin_id, username, password, first_name, last_name)
                VALUES (%s, %s, %s, %s, %s)
            """, (new_admin_id, username, password, first_name, last_name))
            
            conn.commit()
            
            self.logerrormes.setText('Account created successfully! You can now log in.')
            
            # Clear fields
            self.username.clear()
            self.password.clear()
            self.firstname.clear()
            self.lastname.clear()
            
        except Error as err:
            print(f"Error during signup: {err}")
            if conn:
                conn.rollback()
            self.logerrormes.setText('Signup failed. Please try again.')
        finally:
            if conn:
                conn.close()

    def gotoadminlog(self):
        adlog = adminlog()
        widget.addWidget(adlog)
        widget.setCurrentIndex(widget.currentIndex() + 1)
        
# --------------------------------------------------------------------------------------------------------------------

class adminmenu(QDialog):
    def __init__(self):
        super(adminmenu, self).__init__()
        loadUi('./gui/adminmenu.ui', self)
        self.mmexitbutt.clicked.connect(self.gotoregscreen)
        self.upattendancebutt.clicked.connect(self.gotoupatten)
        self.vieweventawbutt.clicked.connect(self.gotoviewevntaw)
        self.viewattenbuttt.clicked.connect(self.gotoviewatten)
        self.viewpartbutt.clicked.connect(self.gotopartlog)
        self.assscoresawpetbutt.clicked.connect(self.gotoawpetscore)
        
        # Load event status table
        self.load_eventstatus()

    def gotoregscreen(self):
        reg = RegisterScreen()
        widget.addWidget(reg)
        widget.setCurrentIndex(widget.currentIndex() + 1)
    
    def gotoawpetscore(self):
        awpsc = awardpetscore()
        widget.addWidget(awpsc)
        widget.setCurrentIndex(widget.currentIndex() + 1)
    
    def gotoupatten(self):
        upat = updateattendance()
        widget.addWidget(upat)
        widget.setCurrentIndex(widget.currentIndex() + 1)
    
    def gotoviewevntaw(self):
        evnt = vieweventaw()
        widget.addWidget(evnt)
        widget.setCurrentIndex(widget.currentIndex() + 1)

    def gotoviewatten(self):
        attn = eventattendancerep()
        widget.addWidget(attn)
        widget.setCurrentIndex(widget.currentIndex() + 1)

    def gotopartlog(self):
        prtlg = participantlog()
        widget.addWidget(prtlg)
        widget.setCurrentIndex(widget.currentIndex() + 1)
    
    def load_eventstatus(self):
        """Load event status with awarded pets info into the table."""
        conn = get_db_connection()
        if not conn:
            return
    
        try:
            cursor = conn.cursor()

            # Single SQL to retrieve all event/award/pet info
            cursor.execute("""
                SELECT 
                    e.event_id, 
                    e.name, 
                    e.date, 
                    e.time, 
                    e.location,
                    CASE WHEN e.status = 1 THEN 'Open' ELSE 'Closed' END AS status,
                    COALESCE(p.name, 'No winner') AS awarded_pet,
                    COALESCE(a.award_name, 'No award') AS award_name
                FROM events e
                LEFT JOIN awards a ON e.event_id = a.event_id
                LEFT JOIN pets p ON a.pet_id = p.pet_id
                ORDER BY e.event_id, a.award_id;
            """)

            rows = cursor.fetchall()

            # Set up table
            self.eventstatus.setRowCount(len(rows))
            self.eventstatus.setColumnCount(8)
            self.eventstatus.setHorizontalHeaderLabels([
                'Event Id', 'Event Name', 'Event Date', 'Time', 'Location', 
                'Status', 'Awarded Pets', 'Award Name'
            ])

            # Populate table
            for row_index, row in enumerate(rows):
                event_id, name, date, time, location, status, awarded_pet, award_name = row

                formatted_date = format_date_string(date)
                formatted_time = str(time) if time not in (None, '') else ''

                values = [
                    event_id,
                    name,
                    formatted_date,
                    formatted_time,
                    location,
                    status,
                    awarded_pet,
                    award_name
                ]

                for col_index, value in enumerate(values):
                    item = QtWidgets.QTableWidgetItem(str(value))
                    if col_index in [1, 4, 6, 7]:
                        item.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignLeft | QtCore.Qt.AlignmentFlag.AlignVCenter)
                    self.eventstatus.setItem(row_index, col_index, item)

            # Enable wrapping
            self.eventstatus.setWordWrap(True)

            # Resize behavior
            header = self.eventstatus.horizontalHeader()
            if header:
                header.setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Stretch)

            vheader = self.eventstatus.verticalHeader()
            if vheader:
                vheader.setVisible(False)
                vheader.setDefaultSectionSize(40)

        except Error as err:
                print(f"Error loading event status: {err}")
        finally:
                if conn:
                    conn.close()
        
# --------------------------------------------------------------------------------------------------------------------

class updateattendance(QDialog):
    def __init__(self):
        super(updateattendance, self).__init__()
        loadUi('./gui/upattendancestatus.ui', self)
        self.exitbutt.clicked.connect(self.gotoadminmenu)
        self.savebutt.clicked.connect(self.save_attendance)
        self.errormessage = self.findChild(QtWidgets.QLabel, 'errormessage')
        
        # Load events and attendance statuses
        self.load_events()
        self.load_attendance_statuses()
        
        # Connect event selection to load pets and data
        self.events.currentIndexChanged.connect(self.on_event_selected)
        self.pets.currentIndexChanged.connect(self.on_pet_selected)
        
        # Store selected entry_id for updates
        self.selected_entry_id = None
    
    def load_events(self):
        """Grab all events and stick them in the dropdown."""
        conn = get_db_connection()
        if not conn:
            return
        
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT event_id, name 
                FROM events 
                ORDER BY date, time
            """)
            
            events = cursor.fetchall()
            self.events.clear()
            self.events.addItem("Select Event")
            
            for event_id, event_name in events:
                display_text = f"{event_name} (ID: {event_id})"
                self.events.addItem(display_text)
        except Error as err:
            print(f"Error loading events: {err}")
        finally:
            if conn:
                conn.close()
    
    def load_attendance_statuses(self):
        """Load all possible attendance statuses."""
        self.attendancestatus.clear()
        self.attendancestatus.addItem("Select Status")
        self.attendancestatus.addItem("Present")
        self.attendancestatus.addItem("No Show")
        self.attendancestatus.addItem("Registered")
    
    def on_event_selected(self):
        """When an event is selected, load the pets and display data."""
        event_text = self.events.currentText()
        if event_text == "Select Event":
            self.eventstatus.setRowCount(0)
            self.pets.clear()
            return
        
        # Extract event_id
        try:
            event_id = int(event_text.split('(ID: ')[1].split(')')[0])
        except:
            self.eventstatus.setRowCount(0)
            return
        
        # Load pets for this event
        self.load_pets_for_event(event_id)
        
        # Load and display attendance data
        self.load_attendance_data(event_id)
    
    def load_pets_for_event(self, event_id):
        """Load all pets registered for the selected event."""
        conn = get_db_connection()
        if not conn:
            return
        
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT DISTINCT p.pet_id, p.name
                FROM pet_event_entry pee
                JOIN pets p ON pee.pet_id = p.pet_id
                WHERE pee.event_id = %s
                ORDER BY p.name
            """, (event_id,))
            
            pets = cursor.fetchall()
            self.pets.clear()
            self.pets.addItem("Select Pet")
            
            for pet_id, pet_name in pets:
                display_text = f"{pet_name} (ID: {pet_id})"
                self.pets.addItem(display_text)
        except Error as err:
            print(f"Error loading pets: {err}")
        finally:
            if conn:
                conn.close()
    
    def on_pet_selected(self):
        """When a pet is selected, find its entry_id for updating."""
        pet_text = self.pets.currentText()
        event_text = self.events.currentText()
        
        if pet_text == "Select Pet" or event_text == "Select Event":
            self.selected_entry_id = None
            return
        
        try:
            pet_id = int(pet_text.split('(ID: ')[1].split(')')[0])
            event_id = int(event_text.split('(ID: ')[1].split(')')[0])
            
            conn = get_db_connection()
            if conn:
                try:
                    cursor = conn.cursor()
                    cursor.execute("""
                        SELECT entry_id 
                        FROM pet_event_entry 
                        WHERE pet_id = %s AND event_id = %s
                        LIMIT 1
                    """, (pet_id, event_id))
                    
                    result = cursor.fetchone()
                    if result:
                        self.selected_entry_id = result[0]
                finally:
                    conn.close()
        except:
            self.selected_entry_id = None
    
    def load_attendance_data(self, event_id):
        """Load attendance data for the selected event and display in table."""
        conn = get_db_connection()
        if not conn:
            return
        
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT pee.entry_id, pee.pet_id, p.name AS pet_name, pee.attendance_status AS current_status
                FROM pet_event_entry pee
                JOIN pets p ON pee.pet_id = p.pet_id
                WHERE pee.event_id = %s
                ORDER BY p.name
            """, (event_id,))
            
            results = cursor.fetchall()
            
            # Set up table
            self.eventstatus.setRowCount(len(results))
            self.eventstatus.setColumnCount(4)
            self.eventstatus.setHorizontalHeaderLabels([
                'Entry ID', 'Pet ID', 'Pet Name', 'Current Status'
            ])
            
            # Populate table
            for row, data in enumerate(results):
                entry_id = data[0]
                pet_id = data[1]
                pet_name = data[2] or 'Unknown'
                current_status = data[3] or 'Unknown'
                
                values = [str(entry_id), str(pet_id), pet_name, current_status]
                for col, value in enumerate(values):
                    item = QtWidgets.QTableWidgetItem(str(value))
                    if col in [2, 3]:  # Pet Name, Current Status
                        item.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignLeft | QtCore.Qt.AlignmentFlag.AlignVCenter)
                    self.eventstatus.setItem(row, col, item)
            
            # Use same formatting as participantlog - stretch mode with word wrap
            self.eventstatus.setWordWrap(True)
            header = self.eventstatus.horizontalHeader()
            if header:
                header.setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Stretch)
            vheader = self.eventstatus.verticalHeader()
            if vheader:
                vheader.setVisible(False)
                vheader.setDefaultSectionSize(40)
            
        except Error as err:
            print(f"Error loading attendance data: {err}")
            if self.errormessage:
                self.errormessage.setText('Error loading attendance data.')
        finally:
            if conn:
                conn.close()
    
    def save_attendance(self):
        """Update the attendance status for the selected pet and refresh display."""
        if not self.selected_entry_id:
            if self.errormessage:
                self.errormessage.setText('Please select an event and pet first.')
            return
        
        new_status = self.attendancestatus.currentText()
        if new_status == "Select Status":
            if self.errormessage:
                self.errormessage.setText('Please select a new attendance status.')
            return
        
        event_text = self.events.currentText()
        if event_text == "Select Event":
            if self.errormessage:
                self.errormessage.setText('Please select an event.')
            return
        
        try:
            event_id = int(event_text.split('(ID: ')[1].split(')')[0])
        except:
            if self.errormessage:
                self.errormessage.setText('Invalid event selection.')
            return
        
        conn = get_db_connection()
        if not conn:
            if self.errormessage:
                self.errormessage.setText('Database connection failed.')
            return
        
        try:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE pet_event_entry 
                SET attendance_status = %s 
                WHERE entry_id = %s
            """, (new_status, self.selected_entry_id))
            
            conn.commit()
            
            if self.errormessage:
                self.errormessage.setText(f'Attendance status updated to {new_status} successfully!')
            
            # Refresh the display
            self.load_attendance_data(event_id)
            
            # Clear selections
            self.pets.setCurrentIndex(0)
            self.attendancestatus.setCurrentIndex(0)
            self.selected_entry_id = None
            
        except Error as err:
            print(f"Error updating attendance: {err}")
            if conn:
                conn.rollback()
            if self.errormessage:
                self.errormessage.setText('Error updating attendance status.')
        finally:
            if conn:
                conn.close()

    def gotoadminmenu(self):
        admmn = adminmenu()
        widget.addWidget(admmn)
        widget.setCurrentIndex(widget.currentIndex() + 1)
        
# --------------------------------------------------------------------------------------------------------------------

class vieweventaw(QDialog):
    def __init__(self):
        super(vieweventaw, self).__init__()
        loadUi('./gui/eventawardsrep.ui', self)
        self.exitbutt.clicked.connect(self.gotoadminmenu)
        self.errormessage = self.findChild(QtWidgets.QLabel, 'errormessage')
        
        # Load award types into the combo box
        self.load_award_types()
        
        # Connect combo box to update table when selection changes
        self.eventawards.currentIndexChanged.connect(self.load_event_awards)
        
        # Load initial data
        self.load_event_awards()
    
    def load_award_types(self):
        """Fill the Award Type dropdown using is_special categories."""
        self.eventawards.clear()
        self.eventawards.addItem("All Awards")        # show everything
        self.eventawards.addItem("Placement Awards")  # is_special = 0
        self.eventawards.addItem("Special Awards")    # is_special = 1

    def load_event_awards(self):
        """Load events with their winning pets and awards based on selected award type."""
        conn = get_db_connection()
        if not conn:
            return

        try:
            cursor = conn.cursor()
            selected_type = self.eventawards.currentText()

            base_select = """
                SELECT e.event_id,
                       e.name,
                       e.date,
                       e.type,
                       CASE WHEN e.status = 1 THEN 'Open' ELSE 'Closed' END AS event_status,
                       COALESCE(p.name, 'No winner') AS winning_pet,
                       COALESCE(a.award_name, 'No award') AS award_name
                FROM events e
                LEFT JOIN awards a ON a.event_id = e.event_id
                LEFT JOIN pets p ON p.pet_id = a.pet_id
            """

            params = ()
            if selected_type == "Placement Awards":
                query = base_select + " WHERE a.is_special = 0 ORDER BY e.event_id, a.award_id"
                params = ()
            elif selected_type == "Special Awards":
                query = base_select + " WHERE a.is_special = 1 ORDER BY e.event_id, a.award_id"
                params = ()
            else:  # All Awards
                query = base_select + " ORDER BY e.event_id, a.award_id"

            cursor.execute(query, params)
            results = cursor.fetchall()
            
            # Set up table
            self.eventawardsstatus.setRowCount(len(results))
            self.eventawardsstatus.setColumnCount(7)
            self.eventawardsstatus.setHorizontalHeaderLabels([
                'Event Id', 'Event Name', 'Event Date', 'Event Type', 'Status', 'Winning Pet', 'Award Name'
            ])
            
            # Populate table
            for row, data in enumerate(results):
                event_id = data[0]
                event_name = data[1] or 'Event'
                event_date = format_date_string(data[2])
                event_type = data[3] or 'N/A'
                event_status = data[4] or 'Unknown'
                winning_pet = data[5] or 'No winner'
                award_name = data[6] or 'No award'
                
                values = [str(event_id), event_name, event_date, event_type, event_status, winning_pet, award_name]
                for col, value in enumerate(values):
                    item = QtWidgets.QTableWidgetItem(str(value))
                    if col in [1, 4, 5, 6]:  # Event Name, Status, Winning Pet, Award Type
                        item.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignLeft | QtCore.Qt.AlignmentFlag.AlignVCenter)
                    self.eventawardsstatus.setItem(row, col, item)
            
            # Make table look good with word wrap and proper sizing
            self.eventawardsstatus.setWordWrap(True)
            header = self.eventawardsstatus.horizontalHeader()
            if header:
                # Use stretch mode to fill the widget initially, still allows manual resizing
                header.setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Stretch)
            vheader = self.eventawardsstatus.verticalHeader()
            if vheader:
                vheader.setVisible(False)
                vheader.setDefaultSectionSize(40)
            
        except Error as err:
            print(f"Error loading event awards: {err}")
            if self.errormessage:
                self.errormessage.setText('Error loading event awards.')
        finally:
            if conn:
                conn.close()

    def gotoadminmenu(self):
        admmn = adminmenu()
        widget.addWidget(admmn)
        widget.setCurrentIndex(widget.currentIndex() + 1)
        
# --------------------------------------------------------------------------------------------------------------------

class eventattendancerep(QDialog):
    def __init__(self):
        super(eventattendancerep, self).__init__()
        loadUi('./gui/eventattendancerep.ui', self)
        self.exitbutt.clicked.connect(self.gotoadminmenu)
        self.totalpetmess = self.findChild(QtWidgets.QLabel, 'totalpetmess')
        
        # Load events and attendance statuses into dropdowns
        self.load_events()
        self.load_attendance_statuses()
        
        # Connect combo boxes to update table when selection changes
        self.eventawards.currentIndexChanged.connect(self.load_attendance_data)
        self.eventawards_2.currentIndexChanged.connect(self.load_attendance_data)
        
        # Load initial data
        self.load_attendance_data()
    
    def load_events(self):
        """Pull all events from the database and put them in the first dropdown."""
        conn = get_db_connection()
        if not conn:
            return
        
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT event_id, name 
                FROM events 
                ORDER BY date, time
            """)
            
            events = cursor.fetchall()
            self.eventawards.clear()
            self.eventawards.addItem("Select Event")
            
            for event_id, event_name in events:
                display_text = f"{event_name} (ID: {event_id})"
                self.eventawards.addItem(display_text)
        except Error as err:
            print(f"Error loading events: {err}")
        finally:
            if conn:
                conn.close()
    
    def load_attendance_statuses(self):
        """Load all possible attendance statuses into the second dropdown."""
        self.eventawards_2.clear()
        self.eventawards_2.addItem("Select Status")
        self.eventawards_2.addItem("Present")
        self.eventawards_2.addItem("No Show")
        self.eventawards_2.addItem("Registered")
    
    def load_attendance_data(self):
        """Load attendance data based on selected event and status."""
        # Check if both dropdowns have valid selections
        event_text = self.eventawards.currentText()
        status_text = self.eventawards_2.currentText()
        
        if event_text == "Select Event" or status_text == "Select Status":
            self.eventawardsstatus.setRowCount(0)
            self.totalpetmess.setText('')
            return
        
        # Extract event_id from the display text
        try:
            event_id = int(event_text.split('(ID: ')[1].split(')')[0])
        except:
            self.eventawardsstatus.setRowCount(0)
            self.totalpetmess.setText('Invalid event selection.')
            return
        
        conn = get_db_connection()
        if not conn:
            return
        
        try:
            cursor = conn.cursor()
            
            # Query to get attendance data with total count and owner name
            query = """
                SELECT t1.entry_id,
                       p.pet_id,
                       p.name AS pet_name,
                       CONCAT(o.first_name, ' ', o.last_name) AS owner_name,
                       t1.attendance_status,
                       (SELECT COUNT(t2.entry_id)
                        FROM pet_event_entry t2
                        WHERE t2.event_id = t1.event_id
                        AND t2.attendance_status = %s) AS total_status_count
                FROM pet_event_entry t1
                JOIN pets p ON t1.pet_id = p.pet_id
                JOIN owners o ON p.owner_id = o.owner_id
                WHERE t1.event_id = %s
                AND t1.attendance_status = %s
            """
            
            cursor.execute(query, (status_text, event_id, status_text))
            results = cursor.fetchall()
            
            # Set up table
            self.eventawardsstatus.setRowCount(len(results))
            self.eventawardsstatus.setColumnCount(6)
            self.eventawardsstatus.setHorizontalHeaderLabels([
                'Entry ID', 'Pet ID', 'Pet Name', 'Owner Name', 'Attendance Status', 'Total Count'
            ])
            
            total_count = 0
            # Populate table
            for row, data in enumerate(results):
                entry_id = data[0]
                pet_id = data[1]
                pet_name = data[2] or 'Unknown'
                owner_name = data[3] or 'Unknown'
                attendance_status = data[4] or 'Unknown'
                total_status_count = data[5] or 0
                
                if row == 0:
                    total_count = total_status_count
                
                values = [str(entry_id), str(pet_id), pet_name, owner_name, attendance_status, str(total_status_count)]
                for col, value in enumerate(values):
                    item = QtWidgets.QTableWidgetItem(str(value))
                    if col in [2, 3, 4]:  # Pet Name, Owner Name, Attendance Status
                        item.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignLeft | QtCore.Qt.AlignmentFlag.AlignVCenter)
                    self.eventawardsstatus.setItem(row, col, item)
            
            # Update total pets message
            if total_count > 0:
                self.totalpetmess.setText(f'Total pets with {status_text} status: {total_count}')
            else:
                self.totalpetmess.setText(f'No pets found with {status_text} status for this event.')
            
            # Make table look good
            self.eventawardsstatus.setWordWrap(True)
            header = self.eventawardsstatus.horizontalHeader()
            if header:
                # Use stretch mode to fill the widget initially, still allows manual resizing
                header.setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Stretch)
            vheader = self.eventawardsstatus.verticalHeader()
            if vheader:
                vheader.setVisible(False)
                vheader.setDefaultSectionSize(40)
            
        except Error as err:
            print(f"Error loading attendance data: {err}")
            self.totalpetmess.setText('Error loading attendance data.')
        finally:
            if conn:
                conn.close()

    def gotoadminmenu(self):
        admmn = adminmenu()
        widget.addWidget(admmn)
        widget.setCurrentIndex(widget.currentIndex() + 1)
        
# --------------------------------------------------------------------------------------------------------------------

class participantlog(QDialog):
    def __init__(self):
        super(participantlog, self).__init__()
        loadUi('./gui/participantlog.ui', self)
        self.exitbutt.clicked.connect(self.gotoadminmenu)
        self.owerrormes = self.findChild(QtWidgets.QLabel, 'owerrormes')
        self.editerrormess = self.findChild(QtWidgets.QLabel, 'editerrormess')
        
        # Load participation log data
        self.load_participation_log()
    
    def load_participation_log(self):
        """Pull all participation log stuff and show names instead of those boring IDs."""
        conn = get_db_connection()
        if not conn:
            if self.owerrormes:
                self.owerrormes.setText('Database connection failed.')
            return
        
        try:
            cursor = conn.cursor()
            
            # Grab all the log entries but swap out IDs for actual names
            cursor.execute("""
                SELECT pl.log_id, 
                       CONCAT(o.first_name, ' ', o.last_name) as owner_name,
                       pl.action_type, 
                       pl.action_date, 
                       pl.action_time,
                       e_orig.name as original_event_name,
                       e_new.name as new_event_name,
                       pl.reason, 
                       pl.refund_amount, 
                       pl.top_up_amount
                FROM participation_log pl
                LEFT JOIN event_registration er ON pl.registration_id = er.registration_id
                LEFT JOIN owners o ON er.owner_id = o.owner_id
                LEFT JOIN events e_orig ON pl.original_event_id = e_orig.event_id
                LEFT JOIN events e_new ON pl.new_event_id = e_new.event_id
                ORDER BY pl.action_date DESC, pl.action_time DESC
            """)
            
            logs = cursor.fetchall()
            
            # Set up table
            self.participantlog.setRowCount(len(logs))
            self.participantlog.setColumnCount(10)
            self.participantlog.setHorizontalHeaderLabels([
                'Log ID', 'Owner Name', 'Action Type', 'Action Date', 'Action Time',
                'Original Event', 'New Event', 'Reason', 'Refund Amount', 'Top Up Amount'
            ])
            
            # Populate table
            for row, log in enumerate(logs):
                for col, value in enumerate(log):
                    if value is None:
                        display_value = 'N/A'
                    elif isinstance(value, (int, float)):
                        if col == 8 or col == 9:  # refund_amount or top_up_amount
                            display_value = f"₱{float(value):.2f}" if value else '₱0.00'
                        else:
                            display_value = str(value)
                    else:
                        display_value = str(value)
                    
                    item = QtWidgets.QTableWidgetItem(display_value)
                    # Let text wrap so we can see everything without it getting cut off
                    if col in [1, 2, 5, 6, 7]:  # Owner Name, Action Type, Original Event, New Event, Reason
                        item.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignLeft | QtCore.Qt.AlignmentFlag.AlignVCenter)
                    self.participantlog.setItem(row, col, item)
            
            # Turn on word wrap so long text doesn't get chopped
            self.participantlog.setWordWrap(True)
            
            # Use stretch mode to fill the widget initially, still allows manual resizing
            header = self.participantlog.horizontalHeader()
            if header:
                header.setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Stretch)
            vheader = self.participantlog.verticalHeader()
            if vheader:
                vheader.setVisible(False)
                # Make rows taller so wrapped text fits nicely
                vheader.setDefaultSectionSize(40)
            
        except Error as err:
            print(f"Error loading participation log: {err}")
            if self.owerrormes:
                self.owerrormes.setText('Error loading participation log.')
        finally:
            if conn:
                conn.close()

    def gotoadminmenu(self):
        admmn = adminmenu()
        widget.addWidget(admmn)
        widget.setCurrentIndex(widget.currentIndex() + 1)
        
# --------------------------------------------------------------------------------------------------------------------

class awardpetscore(QDialog):
    def __init__(self):
        super(awardpetscore, self).__init__()
        loadUi('./gui/awardgivingpetscore.ui', self)
        self.petexitbutt.clicked.connect(self.gotoadminmenu)
        self.savebutt.clicked.connect(self.save_score_and_award)
        self.message = self.findChild(QtWidgets.QLabel, 'message')
        
        # Load events and awards
        self.load_events()
        
        # Connect event selection to load pets and display data
        self.pastevents.currentIndexChanged.connect(self.on_event_selected)
        self.petswhoparticipated.currentIndexChanged.connect(self.on_pet_selected)
        
        # Set score limit to 10.00
        self.doubleSpinBox.setMaximum(10.00)
        self.doubleSpinBox.setMinimum(0.00)
        self.doubleSpinBox.setDecimals(2)
        
        # Store selected pet_id and entry_id
        self.selected_pet_id = None
        self.selected_entry_id = None
        
        # Get label for current pet score
        self.pet_score_label = self.findChild(QtWidgets.QLabel, "petscorelabel")
        if self.pet_score_label:
            self.pet_score_label.raise_()          # bring to front
            self.pet_score_label.show()            # ensure visible
            self.pet_score_label.setStyleSheet(
              'color: rgb(40,52,84); background: rgba(255,255,255,180); font: 700 12pt "Berlin Sans FB Demi"; padding: 2px;'
            )
            
        self.petswhoparticipated.currentIndexChanged.connect(self.update_selected_pet_score)
        self.pastevents.currentIndexChanged.connect(self.update_selected_pet_score)
        
        self.update_selected_pet_score()
    
    def load_events(self):
        """Grab all events and put them in the dropdown."""
        conn = get_db_connection()
        if not conn:
            return
        
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT event_id, name 
                FROM events 
                ORDER BY date DESC, time DESC
            """)
            
            events = cursor.fetchall()
            self.pastevents.clear()
            self.pastevents.addItem("Select Event")
            
            for event_id, event_name in events:
                display_text = f"{event_name} (ID: {event_id})"
                self.pastevents.addItem(display_text)
        except Error as err:
            print(f"Error loading events: {err}")
        finally:
            if conn:
                conn.close()
    
    def load_awards(self, event_id: int):
        """Load awards for this event into dropdown, only special awards."""
        self.awards.clear()
        self.awards.addItem("Select Award")
        self.awards.addItem("Remove Award for this Pet")

        conn = get_db_connection()
        if not conn:
            return
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT DISTINCT award_name
                FROM awards
                WHERE event_id = %s AND is_special = 1
                ORDER BY award_name
            """, (event_id,))
            for (name,) in cursor.fetchall():
                if name:
                    self.awards.addItem(name)
        except Error as err:
            print(f"Error loading awards for event: {err}")
        finally:
            if conn:
                conn.close()
    
    def is_placement_event(self, event_id: int) -> bool:
        """Return True if this event uses placement awards (is_special=0)."""
        conn = get_db_connection()
        if not conn:
            return False
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT COUNT(*) 
                FROM awards 
                WHERE event_id = %s AND is_special = 0
            """, (event_id,))
            count = cursor.fetchone()[0] or 0
            return count > 0
        except Error as err:
            print(f"Error checking event award type: {err}")
            return False
        finally:
            if conn:
                conn.close()

    def on_event_selected(self):
        """When an event is selected, load pets and display data."""
        event_text = self.pastevents.currentText()
        if event_text == "Select Event":
            self.eventstatus.setRowCount(0)
            self.petswhoparticipated.clear()
            self.current_event_id = None
            self.current_event_is_placement = False
            # Enable everything by default
            self.doubleSpinBox.setEnabled(True)
            self.awards.setEnabled(True)
            return

        try:
            event_id = int(event_text.split('(ID: ')[1].split(')')[0])
        except:
            self.eventstatus.setRowCount(0)
            self.current_event_id = None
            self.current_event_is_placement = False
            return

        self.current_event_id = event_id
        # Decide if this is a placement event (has placement‑type awards)
        self.current_event_is_placement = self.is_placement_event(event_id)

        # UI rules:
        # placement event → score enabled, awards dropdown disabled
        # special event   → awards enabled, score disabled
        if self.current_event_is_placement:
            self.doubleSpinBox.setEnabled(True)
            self.awards.setEnabled(False)
            self.awards.clear()
            self.awards.addItem("Select Award")
        else:
            self.doubleSpinBox.setEnabled(False)
            self.doubleSpinBox.setValue(0.00)
            self.awards.setEnabled(True)
            self.load_awards(event_id)

        # Load pets and table as before
        self.load_pets_for_event(event_id)
        self.load_event_data(event_id)
    
    def load_pets_for_event(self, event_id):
        """Load all pets registered for the selected event."""
        conn = get_db_connection()
        if not conn:
            return
        
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT DISTINCT p.pet_id, p.name
                FROM pet_event_entry pee
                JOIN pets p ON pee.pet_id = p.pet_id
                WHERE pee.event_id = %s
                ORDER BY p.name
            """, (event_id,))
            
            pets = cursor.fetchall()
            self.petswhoparticipated.clear()
            self.petswhoparticipated.addItem("Select Pet")
            
            for pet_id, pet_name in pets:
                display_text = f"{pet_name} (ID: {pet_id})"
                self.petswhoparticipated.addItem(display_text)
        except Error as err:
            print(f"Error loading pets: {err}")
        finally:
            if conn:
                conn.close()
    
    def on_pet_selected(self):
        """When a pet is selected, store its ID for saving."""
        pet_text = self.petswhoparticipated.currentText()
        event_text = self.pastevents.currentText()
        
        if pet_text == "Select Pet" or event_text == "Select Event":
            self.selected_pet_id = None
            self.selected_entry_id = None
            return
        
        try:
            pet_id = int(pet_text.split('(ID: ')[1].split(')')[0])
            event_id = int(event_text.split('(ID: ')[1].split(')')[0])
            
            conn = get_db_connection()
            if conn:
                try:
                    cursor = conn.cursor()
                    cursor.execute("""
                        SELECT entry_id 
                        FROM pet_event_entry 
                        WHERE pet_id = %s AND event_id = %s
                        LIMIT 1
                    """, (pet_id, event_id))
                    
                    result = cursor.fetchone()
                    if result:
                        self.selected_entry_id = result[0]
                        self.selected_pet_id = pet_id
                finally:
                    conn.close()
        except:
            self.selected_pet_id = None
            self.selected_entry_id = None
    
    def load_event_data(self, event_id):
        """Load event data with pets registered and display in table."""
        conn = get_db_connection()
        if not conn:
            return
        
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT e.event_id, e.name, p.pet_id, p.name AS pets_registered
                FROM events e
                LEFT JOIN pet_event_entry pee ON e.event_id = pee.event_id
                LEFT JOIN pets p ON pee.pet_id = p.pet_id
                WHERE e.event_id = %s
                ORDER BY p.name
            """, (event_id,))
            
            results = cursor.fetchall()
            
            # Set up table
            self.eventstatus.setRowCount(len(results))
            self.eventstatus.setColumnCount(4)
            self.eventstatus.setHorizontalHeaderLabels([
                'Event ID', 'Event Name', 'Pet ID', 'Pet Name'
            ])
            
            # Populate table
            for row, data in enumerate(results):
                event_id_val = data[0]
                event_name = data[1] or 'Event'
                pet_id = data[2] if data[2] is not None else 'N/A'
                pet_name = data[3] if data[3] is not None else 'No pets registered'
                
                values = [str(event_id_val), event_name, str(pet_id), pet_name]
                for col, value in enumerate(values):
                    item = QtWidgets.QTableWidgetItem(str(value))
                    if col in [1, 3]:  # Event Name, Pet Name
                        item.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignLeft | QtCore.Qt.AlignmentFlag.AlignVCenter)
                    self.eventstatus.setItem(row, col, item)
            
            # Use stretch mode to fill the widget
            self.eventstatus.setWordWrap(True)
            header = self.eventstatus.horizontalHeader()
            if header:
                header.setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Stretch)
            vheader = self.eventstatus.verticalHeader()
            if vheader:
                vheader.setVisible(False)
                vheader.setDefaultSectionSize(40)
            
        except Error as err:
            print(f"Error loading event data: {err}")
            if self.message:
                self.message.setText('Error loading event data.')
        finally:
            if conn:
                conn.close()
    
    def save_score_and_award(self):
        """Save score or special award for the selected pet, depending on event type."""
        if self.selected_entry_id is None or self.selected_pet_id is None:
            if self.message:
                self.message.setText('Please select an event and pet first.')
            return

        event_text = self.pastevents.currentText()
        if event_text == "Select Event" or not self.current_event_id:
            if self.message:
                self.message.setText('Please select an event.')
            return

        event_id = self.current_event_id
        
        conn = get_db_connection()
        if not conn:
            if self.message:
                self.message.setText('Database connection failed.')
            return
        
        try:
            cursor = conn.cursor()
            
            # Update pet_result in pet_event_entry
            if self.current_event_is_placement:
                # Placement event: update score only
                # 1) Save this pet's score
                score = self.doubleSpinBox.value()
                cursor.execute("""
                    UPDATE pet_event_entry
                    SET pet_result = %s
                    WHERE entry_id = %s
                """, (score, self.selected_entry_id))

                # 2) Recompute rankings (highest score first)
                cursor.execute("""
                    SELECT pee.pet_id
                    FROM pet_event_entry pee
                    WHERE pee.event_id = %s
                      AND pee.pet_result IS NOT NULL
                    ORDER BY pee.pet_result DESC
                """, (event_id,))
                ranking = cursor.fetchall()

                # 3) Update 1st place / champion (top of the ranking)
                if len(ranking) >= 1:
                    win_pet_id = ranking[0][0]
                    cursor.execute("""
                        UPDATE awards
                        SET pet_id = %s
                        WHERE event_id = %s
                          AND is_special = 0
                          AND (
                                award_name LIKE '%1st%' OR
                                award_name LIKE '%Champion%'
                              )
                    """, (win_pet_id, event_id))

                # 4) Update 2nd place / runner‑up (second in the ranking)
                if len(ranking) >= 2:
                    win2_pet_id = ranking[1][0]
                    cursor.execute("""
                        SELECT award_id
                        FROM awards
                        WHERE event_id = %s
                          AND is_special = 0
                          AND (
                                award_name LIKE '%2nd%' OR
                                award_name LIKE '%Runner Up%'
                            )
                        LIMIT 1
                    """, (event_id,))

                    row = cursor.fetchone()

                    if row:
                        award_id = row[0]
                        cursor.execute("""
                            UPDATE awards
                            SET pet_id = %s
                            WHERE award_id = %s
                        """, (win2_pet_id, award_id))

                conn.commit()
                if self.message:
                    self.message.setText(
                        f'Score {score:.2f} saved and placements updated based on current rankings.'
                    )
                if self.pet_score_label:
                    self.pet_score_label.setText(f"Pet score: {score:.2f}")
            else:
                # Special event: award only, no score
                award_name = self.awards.currentText()
                if award_name == "Select Award":
                    if self.message:
                        self.message.setText('Please select an award type for this special event.')
                    return
                
                # Special event: Remove Award
                if award_name == "Remove Award for this Pet":
                    cursor.execute("""
                        UPDATE awards
                        SET pet_id = NULL
                        WHERE event_id = %s
                          AND is_special = 1
                          AND pet_id = %s
                    """, (event_id, self.selected_pet_id))
                    conn.commit()
                    if self.message:
                        self.message.setText(f'Award removed successfully for this pet.')
                    if self.pet_score_label:
                        self.pet_score_label.setText(f"Pet score: N/A")
                    return

                from datetime import datetime
                now = datetime.now()
                award_date = now.strftime("%Y-%m-%d")

                # 1) Try to find an existing placeholder award for this event & name
                cursor.execute("""
                    SELECT award_id
                    FROM awards
                    WHERE event_id = %s
                      AND award_name = %s
                      AND pet_id IS NULL
                    LIMIT 1
                """, (event_id, award_name))
                row = cursor.fetchone()

                if row:
                    # 2) Update that row in place: fill in pet_id and other fields
                    award_id = row[0]
                    cursor.execute("""
                        UPDATE awards
                        SET pet_id = %s,
                            is_special = 1,
                            description = 'Special award',
                            date = %s
                        WHERE award_id = %s
                    """, (self.selected_pet_id, award_date, award_id))

                conn.commit()
                if self.message:
                    self.message.setText(f'Award \"{award_name}\" saved successfully for this pet.')
                    
                if self.pet_score_label:
                    self.pet_score_label.setText(f"Pet score: N/A")
                    
            # refresh table and reset selection
            self.load_event_data(event_id)
            self.petswhoparticipated.setCurrentIndex(0)
            self.awards.setCurrentIndex(0)
            self.doubleSpinBox.setValue(0.00)
            self.selected_pet_id = None
            self.selected_entry_id = None
                
        except Error as err:
            print(f"Error saving score/award: {err}")
            if conn:
                conn.rollback()
            if self.message:
                self.message.setText('Error saving score or award.')
        finally:
            if conn:
                conn.close()
                
    def update_selected_pet_score(self):
        ev_text = self.pastevents.currentText()
        pt_text = self.petswhoparticipated.currentText()

        # Guard: nothing selected yet
        if ev_text == "Select Event" or pt_text in ("", "Select Pet"):
            self.doubleSpinBox.setValue(0.0)
            if self.pet_score_label:
                self.pet_score_label.setText("Pet score: 0.00")
            return

        # Extract IDs from "Name (ID: N)"
        try:
            event_id = int(ev_text.split("(ID: ")[1].split(")")[0])
            pet_id   = int(pt_text.split("(ID: ")[1].split(")")[0])
        except Exception:
            self.doubleSpinBox.setValue(0.0)
            if self.pet_score_label:
                self.pet_score_label.setText("Pet score: 0.00")
            return

        # Look up the score and display it
        conn = get_db_connection()
        if not conn:
            if self.pet_score_label:
                self.pet_score_label.setText("Pet score: (DB error)")
            return

        try:
            cur = conn.cursor()
            cur.execute("""
                SELECT pet_result
                FROM pet_event_entry
                WHERE event_id = %s AND pet_id = %s
                LIMIT 1
            """, (event_id, pet_id))
            row = cur.fetchone()
            score = float(row[0]) if row and row[0] is not None else 0.0

            self.doubleSpinBox.setValue(score)
            if self.pet_score_label:
                self.pet_score_label.setText(f"Pet score: {score:.2f}")
        except Error as err:
            print("load score error:", err)
            if self.pet_score_label:
                self.pet_score_label.setText("Pet score: (error)")
        finally:
            conn.close()

    def gotoadminmenu(self):
        admmn = adminmenu()
        widget.addWidget(admmn)
        widget.setCurrentIndex(widget.currentIndex() + 1)
        
# --------------------------------------------------------------------------------------------------------------------

class mainmenu(QDialog):
    def __init__(self, owner_context=None):
        super(mainmenu, self).__init__()
        loadUi('./gui/mainmenu.ui', self)
        self.owner_context = owner_context or get_active_owner()
        if not self.owner_context:
            print("Warning: main menu opened without an active owner; owner-specific actions may fail.")
        self.petregbutt.clicked.connect(self.gotopetregis)
        self.eventregbutt.clicked.connect(self.gotoenrollev)
        self.editinbutt.clicked.connect(self.gotoeditinfo)
        self.eventsbutt.clicked.connect(self.gotoevents)
        self.entrybutt.clicked.connect(self.gotoentries)
        self.statusbutt.clicked.connect(self.gotostatus)
        self.mmexitbutt.clicked.connect(self.gotoregscreen)
        self.calendarWidget.selectionChanged.connect(self.on_date_selected)
        
        # Set up the mini "what's happening today" table
        self.load_date_summary()
    
    def on_date_selected(self):
        """When the calendar changes, refresh the summary table."""
        self.load_date_summary()
    
    def load_date_summary(self):
        "Grab events and basic stats for the currently selected date."
        selected_date = self.calendarWidget.selectedDate()
        date_str = selected_date.toString("yyyy-MM-dd")
        
        conn = get_db_connection()
        if not conn:
            return
        
        try:
            cursor = conn.cursor()
            all_rows = []
            
            # 1. Get events on this date
            cursor.execute("""
                SELECT name, time
                FROM events
                WHERE date = %s
                ORDER BY time
            """, (date_str,))
            
            events = cursor.fetchall()
            if events:
                all_rows.append(("--- EVENTS ON THIS DATE ---", ""))
                for event_name, event_time in events:
                    all_rows.append((f"Event: {event_name}", f"Time: {event_time}"))
                all_rows.append(("", ""))  # Empty row
            
            # 2. New registrations 
            cursor.execute("""
                SELECT COUNT(DISTINCT er.registration_id) as total_registrations,
                       COUNT(DISTINCT er.owner_id) as total_participants,
                       COUNT(DISTINCT pee.pet_id) as total_pets
                FROM event_registration er
                JOIN pet_event_entry pee ON er.registration_id = pee.registration_id
                WHERE er.registration_date = %s AND er.status = 'Paid'
            """, (date_str,))
            
            reg_result = cursor.fetchone()
            if reg_result and reg_result[0] > 0:
                all_rows.append(("--- NEW REGISTRATIONS ---", ""))
                all_rows.append((f"Total Registrations: {reg_result[0]}", ""))
                all_rows.append((f"Total Participants: {reg_result[1]}", ""))
                all_rows.append((f"Total Pets: {reg_result[2]}", ""))
                all_rows.append(("", ""))  # Empty row
            
            # 3. Transfers 
            cursor.execute("""
                SELECT COUNT(DISTINCT pl.registration_id) as total_transfers,
                       COUNT(DISTINCT er.owner_id) as total_participants,
                       COUNT(DISTINCT pee.pet_id) as total_pets
                FROM participation_log pl
                JOIN event_registration er ON pl.registration_id = er.registration_id
                JOIN pet_event_entry pee ON er.registration_id = pee.registration_id
                WHERE pl.action_type = 'Transferred' AND pl.action_date = %s
            """, (date_str,))
            
            transfer_result = cursor.fetchone()
            if transfer_result and transfer_result[0] > 0:
                all_rows.append(("--- TRANSFERS ---", ""))
                all_rows.append((f"Total Transfers: {transfer_result[0]}", ""))
                all_rows.append((f"Participants: {transfer_result[1]}", ""))
                all_rows.append((f"Pets: {transfer_result[2]}", ""))
                all_rows.append(("", ""))  # Empty row
            
            # 4. Withdrawals 
            cursor.execute("""
                SELECT COUNT(DISTINCT pl.registration_id) as total_withdrawals,
                       COUNT(DISTINCT er.owner_id) as total_participants
                FROM participation_log pl
                JOIN event_registration er ON pl.registration_id = er.registration_id
                WHERE pl.action_type = 'Cancelled' AND pl.action_date = %s
            """, (date_str,))
            
            withdrawal_result = cursor.fetchone()
            if withdrawal_result and withdrawal_result[0] > 0:
                # Since pet_event_entry is deleted on withdrawal, we approximate pet count
                # Each registration typically has at least one pet
                total_withdrawals = withdrawal_result[0]
                total_participants = withdrawal_result[1]
                # Use number of withdrawals as proxy for pets (each withdrawal = at least 1 pet)
                total_pets = total_withdrawals
                
                all_rows.append(("--- WITHDRAWALS ---", ""))
                all_rows.append((f"Total Withdrawals: {total_withdrawals}", ""))
                all_rows.append((f"Participants: {total_participants}", ""))
                all_rows.append((f"Pets: {total_pets}", ""))
                all_rows.append(("", ""))  # Empty row
            
            # 5. Awards summary
            cursor.execute("""
                SELECT e.name as event_name, a.award_name, COUNT(*) as award_count
                FROM awards a
                JOIN events e ON a.event_id = e.event_id
                WHERE a.date = %s
                GROUP BY e.name, a.award_name
                ORDER BY e.name, a.award_name
            """, (date_str,))
            
            awards = cursor.fetchall()
            if awards:
                all_rows.append(("--- AWARDS ---", ""))
                current_event = None
                for event_name, award_name, award_count in awards:
                    if event_name != current_event:
                        if current_event is not None:
                            all_rows.append(("", ""))
                        all_rows.append((f"Event: {event_name}", ""))
                        current_event = event_name
                    all_rows.append((f"  {award_name}: {award_count}", ""))
            
            # Populate table
            if not all_rows:
                all_rows.append(("No events or activities", f"on {date_str}"))
            
            self.eventontheday.setRowCount(len(all_rows))
            self.eventontheday.setColumnCount(2)
            self.eventontheday.setHorizontalHeaderLabels(['Information', 'Details'])
            
            for row, (col1, col2) in enumerate(all_rows):
                item1 = QtWidgets.QTableWidgetItem(col1)
                item2 = QtWidgets.QTableWidgetItem(col2)
                self.eventontheday.setItem(row, 0, item1)
                self.eventontheday.setItem(row, 1, item2)
            
            # Resize columns
            self.eventontheday.resizeColumnsToContents()
            header = self.eventontheday.horizontalHeader()
            if header:
                header.setStretchLastSection(True)
                header.setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Stretch)
            vheader = self.eventontheday.verticalHeader()
            if vheader:
                vheader.setVisible(False)
                vheader.setDefaultSectionSize(28)
            
        except Error as err:
            print(f"Error loading date summary: {err}")
        finally:
            if conn:
                conn.close()

    def gotoregscreen(self):
        clear_active_owner()
        reg = RegisterScreen()
        widget.addWidget(reg)
        widget.setCurrentIndex(widget.currentIndex() + 1)

    def gotoentries(self):
        entrs= entries()
        widget.addWidget(entrs)
        widget.setCurrentIndex(widget.currentIndex() + 1)

    def gotoevents(self):
        evs = viewevents()
        widget.addWidget(evs)
        widget.setCurrentIndex(widget.currentIndex() + 1)

    def gotostatus(self):
        status_screen = yourstatuss(self.owner_context)
        widget.addWidget(status_screen)
        widget.setCurrentIndex(widget.currentIndex() + 1)

    def gotopetregis(self):
        petregis = petregistration(self.owner_context)
        widget.addWidget(petregis)
        widget.setCurrentIndex(widget.currentIndex() + 1)
    
    def gotoenrollev(self):
        enrollev = enrollevent(self.owner_context)
        widget.addWidget(enrollev)
        widget.setCurrentIndex(widget.currentIndex() + 1)
    
    def gotoeditinfo(self):
        editin = editinf(self.owner_context)
        widget.addWidget(editin)
        widget.setCurrentIndex(widget.currentIndex() + 1)

# --------------------------------------------------------------------------------------------------------------------

class petregistration(QDialog):
    def __init__(self, owner_context=None):
        super(petregistration, self).__init__()
        loadUi('./gui/petregistration.ui', self)

        self.petsex.addItems(['Male', 'Female', 'Unknown'])
        self.petsize.addItems(['Small', 'Medium', 'Large', 'Extra Large']) 

        # Load breeds into combo box
        self.load_breeds()
        
        # Connect breed combo box to handle "Other" option
        self.petbreed.currentIndexChanged.connect(self.on_breed_selected)
        
        # Make the combo box editable so users can type custom breed names when "Other" is selected
        self.petbreed.setEditable(True)

        self.petexitbutt.clicked.connect(self.gotommenu)
        self.petregisterbutt.clicked.connect(self.petregisfunc)
        self.petregiserr = self.findChild(QtWidgets.QLabel, 'petregiserr')
        self.owner_context = owner_context or get_active_owner()
        self.owner_id = self.owner_context['owner_id'] if self.owner_context else None
        
        # Highlight muzzle choice
        self.muzzleyes  = self.findChild(QtWidgets.QRadioButton, 'muzzleyes')
        self.muzzleno   = self.findChild(QtWidgets.QRadioButton, 'muzzleno')
        self.muzzleyes.toggled.connect(self._update_muzzle_highlight)
        self.muzzleno.toggled.connect(self._update_muzzle_highlight)
        self._update_muzzle_highlight()
        
        if self.muzzleyes and self.muzzleno:
            self.muzzleyes.toggled.connect(self._update_muzzle_highlight)
            self.muzzleno.toggled.connect(self._update_muzzle_highlight)
            self._update_muzzle_highlight()
            
    def _update_muzzle_highlight(self):
        off = ("QRadioButton { color: rgb(40,52,84); background: transparent; "
               "font: 700 10pt 'Berlin Sans FB Demi'; padding: 2px 6px; border-radius: 6px; }")
        on  = ("QRadioButton { color: white; background: rgb(251,176,59); "
               "font: 700 10pt 'Berlin Sans FB Demi'; padding: 2px 6px; border-radius: 6px; }")

        if self.muzzleyes.isChecked():
            self.muzzleyes.setStyleSheet(on)
            self.muzzleno.setStyleSheet(off)
        elif self.muzzleno.isChecked():
            self.muzzleyes.setStyleSheet(off)
            self.muzzleno.setStyleSheet(on)
        else:
            self.muzzleyes.setStyleSheet(off)
            self.muzzleno.setStyleSheet(off)

    def load_breeds(self):
        """Grab all breeds from the database and add them to the combo box, plus "Other" option."""
        conn = get_db_connection()
        if not conn:
            return
        
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT DISTINCT breed_name 
                FROM breeds 
                ORDER BY breed_name
            """)
            
            breeds = cursor.fetchall()
            self.petbreed.clear()
            
            # Add all breeds
            for breed in breeds:
                if breed[0]:
                    self.petbreed.addItem(breed[0])
            
            # Add "Other" option at the end
            self.petbreed.addItem("Other")
        except Error as err:
            print(f"Error loading breeds: {err}")
        finally:
            if conn:
                conn.close()
    
    def on_breed_selected(self):
        """Handle when breed selection changes - if "Other" is selected, clear the text so user can type."""
        if self.petbreed.currentText() == "Other":
            # Clear the text so user can type their custom breed
            self.petbreed.setEditText("") 
        
    def petregisfunc(self):
        petname = self.petname.text().strip()
        petage = self.petage.value()
        petsex = self.petsex.currentText().strip()
        petweight = self.petweight.value()
        petsize_name = self.petsize.currentText().strip()
        petbreed = self.petbreed.currentText().strip()  # Changed from .text() to .currentText() for combo box
        petnotes = self.petnotes.toPlainText().strip()

        self.petregiserr.setText('') 

        # Handle "Other" breed option - get the custom breed name from the editable combo box
        if petbreed == "Other" or (petbreed == "" and self.petbreed.currentIndex() == self.petbreed.count() - 1):
            # User selected "Other" - get the text they typed
            custom_breed = self.petbreed.currentText().strip()
            if not custom_breed or custom_breed == "Other":
                self.petregiserr.setText('Please enter a custom breed name when "Other" is selected.')
                return
            petbreed = custom_breed  # Use the custom breed name
        
        if not petname or petage == 0 or not petbreed:
            self.petregiserr.setText('Please fill in Pet Name, Age (must be > 0), and Breed.')
            return
        
        muzzle_required = 1 if self.muzzleyes.isChecked() else 0 
        
        size_map = {'Small': 1, 'Medium': 2, 'Large': 3, 'Extra Large': 3}
        actual_size_id = size_map.get(petsize_name, 3) 

        conn = get_db_connection()
        if conn:
            try:
                cursor = conn.cursor()
                owner_id = self.owner_id or get_active_owner_id()
                if owner_id is None:
                    self.petregiserr.setText('Please log in as an owner before registering pets.')
                    return

                cursor.execute("SELECT MAX(pet_id) FROM pets")
                max_pet_id = cursor.fetchone()[0]
                new_pet_id = (max_pet_id if max_pet_id is not None else 0) + 1
                

                sql_breed_lookup = "SELECT breed_id FROM breeds WHERE breed_name = %s"
                cursor.execute(sql_breed_lookup, (petbreed,))
                breed_result = cursor.fetchone()

                if breed_result:
                    breed_id = breed_result[0]
                else:
                    
                    cursor.execute("SELECT MAX(breed_id) FROM breeds")
                    max_breed_id = cursor.fetchone()[0]
                    new_breed_id = max(16, (max_breed_id if max_breed_id is not None else 0) + 1)
                    
                    sql_insert_breed = "INSERT INTO breeds (breed_id, breed_name, size_id) VALUES (%s, %s, %s)"
                    cursor.execute(sql_insert_breed, (new_breed_id, petbreed, 3)) 
                    
                    breed_id = new_breed_id
                
                sql_pet = """
                INSERT INTO pets 
                (pet_id, owner_id, name, actual_size_id, age, sex, weight_kg, muzzle_required, notes) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                data_pet = (
                    new_pet_id, 
                    owner_id, 
                    petname, 
                    actual_size_id,
                    petage, 
                    petsex, 
                    petweight, 
                    muzzle_required, 
                    petnotes
                )
                
                cursor.execute(sql_pet, data_pet)

                sql_junction = "INSERT INTO pet_breed_junction (pet_id, breed_id) VALUES (%s, %s)"
                data_junction = (new_pet_id, breed_id)
                
                cursor.execute(sql_junction, data_junction)
                
                conn.commit()
                
                cursor.execute("SELECT pet_id FROM pets WHERE pet_id = %s", (new_pet_id,))
                if cursor.fetchone():
                    print(f"Pet successfully registered with ID: {new_pet_id}")
                    self.gotopetregistered()
                else:
                    raise Error("Insert verification failed")
                
            except Error as err:
                print(f"Database INSERT Error (Pet): {err}")
                if conn:
                    conn.rollback()
                self.petregiserr.setText(f'Registration failed: Database Error.')
            except Exception as e:
                print(f"Unexpected Error during pet registration: {e}")
                if conn:
                    conn.rollback()
                self.petregiserr.setText('An unexpected error occurred.')
            finally:
                if conn:
                    conn.close()
        else:
            self.petregiserr.setText('Database connection failed.')

    def gotopetregistered(self):
        pregistrd = petrgistrd()
        widget.addWidget(pregistrd)
        widget.setCurrentIndex(widget.currentIndex() + 1)

    def gotommenu(self):
        mmenu = mainmenu()
        widget.addWidget(mmenu)
        widget.setCurrentIndex(widget.currentIndex() + 1)

# --------------------------------------------------------------------------------------------------------------------

class petrgistrd(QDialog):
    def __init__(self):
        super(petrgistrd, self).__init__()
        loadUi('./gui/petregistered!.ui', self)
        self.sucpetregbackbutt.clicked.connect(self.gotommenu)

    def gotommenu(self):
        mmenu = mainmenu()
        widget.addWidget(mmenu)
        widget.setCurrentIndex(widget.currentIndex() + 1)
        
# --------------------------------------------------------------------------------------------------------------------

class enrollevent(QDialog):
    def __init__(self, owner_context=None):
        super(enrollevent, self).__init__()
        loadUi('./gui/enrollevent.ui', self)
        self.enrollevexitbutt.clicked.connect(self.gotommenu)
        self.enrolevbutt.clicked.connect(self.enrollevnt)
        
        
        self.petregiserr = self.findChild(QtWidgets.QLabel, 'petregiserr')
        self.petwarningsize = self.findChild(QtWidgets.QLabel, 'petwarningsize')
        self.enrollsummary = self.findChild(QtWidgets.QLabel, 'enrollsummary')
        self.enrollattstat = self.findChild(QtWidgets.QLabel, 'enrollattstat')
        self.owerusername = self.findChild(QtWidgets.QLabel, 'owerusername')
        
        # Keep track of which owner/pet/event we're dealing with
        self.owner_context = owner_context or get_active_owner()
        self.current_owner_id = self.owner_context['owner_id'] if self.owner_context else None
        self.selected_pet_id = None
        self.event_data = {}
        
        # Default registration date to "today" so user doesn't have to pick
        from datetime import date
        self.enrollregdate.setDate(date.today())
        
        # Hook up dropdowns so we react when user changes stuff
        self.enrollselev.currentIndexChanged.connect(self.on_event_selected)
        self.selectpetbutt.currentIndexChanged.connect(self.on_pet_selected)
        
        # Load initial data for owner, events, and pets
        self.load_owner_data()
        self.load_events()
        self.load_pets()
        
    def load_owner_data(self):
        "Load the active owner's name for display."
        if self.current_owner_id is None:
            self.owerusername.setText('Please log in as an owner first.')
            return
        conn = get_db_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT first_name, last_name 
                    FROM owners 
                    WHERE owner_id = %s
                """, (self.current_owner_id,))
                owner_data = cursor.fetchone()
                if owner_data:
                    owner_name = f"{owner_data[0]} {owner_data[1]}"
                    self.owerusername.setText(owner_name)
            except Error as err:
                print(f"Error loading owner data: {err}")
            finally:
                if conn:
                    conn.close()
    
    def load_events(self):
        """Pull all open events into the event dropdown."""
        conn = get_db_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT event_id, name, date, time, location, type, 
                           base_registration_fee, extra_pet_discount,
                           min_size_id, max_size_id, min_weight, max_weight,
                           registration_deadline
                    FROM events 
                    WHERE status = 1
                    ORDER BY date, time
                """)
                
                events = cursor.fetchall()
                self.enrollselev.clear()
                self.event_dict = {}
                
                for event in events:
                    event_id = event[0]
                    event_name = event[1]
                    display_text = event_name
                    self.enrollselev.addItem(display_text)
                    self.event_dict[display_text] = {
                        'event_id': event_id,
                        'name': event[1],
                        'date': event[2],
                        'time': event[3],
                        'location': event[4],
                        'type': event[5],
                        'base_fee': event[6],
                        'extra_pet_discount': event[7],
                        'min_size_id': event[8],
                        'max_size_id': event[9],
                        'min_weight': event[10],
                        'max_weight': event[11],
                        'registration_deadline': event[12]
                    }
            except Error as err:
                print(f"Error loading events: {err}")
                self.petregiserr.setText('Error loading events.')
            finally:
                if conn:
                    conn.close()
    
    def load_pets(self):
        """Put all this owner's pets into the pet dropdown."""
        if self.current_owner_id is None:
            return
            
        conn = get_db_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT p.pet_id, p.name, p.actual_size_id, p.weight_kg,
                           sc.size_name
                    FROM pets p
                    LEFT JOIN size_category sc ON p.actual_size_id = sc.size_id
                    WHERE p.owner_id = %s
                    ORDER BY p.name
                """, (self.current_owner_id,))
                
                pets = cursor.fetchall()
                self.selectpetbutt.clear()
                self.pet_dict = {}
                
                for pet in pets:
                    pet_id = pet[0]
                    pet_name = pet[1]
                    display_text = f"{pet_name}"
                    self.selectpetbutt.addItem(display_text)
                    self.pet_dict[display_text] = {
                        'pet_id': pet_id,
                        'name': pet[1],
                        'size_id': pet[2],
                        'weight_kg': pet[3],
                        'size_name': pet[4]
                    }
            except Error as err:
                print(f"Error loading pets: {err}")
                self.petregiserr.setText('Error loading pets.')
            finally:
                if conn:
                    conn.close()
    
    def on_event_selected(self):
        """When the event changes, update summary and size checks."""
        selected_text = self.enrollselev.currentText()
        if not selected_text or selected_text not in self.event_dict:
            return
        
        self.event_data = self.event_dict[selected_text]
        self.selected_event_id = self.event_data['event_id']
        
        # Update summary
        self.update_summary()
        
        # Check pet size if a pet is selected
        if self.selectpetbutt.currentText():
            self.check_pet_size_compatibility()
    
    def on_pet_selected(self):
        """When the pet changes, update summary and size checks."""
        selected_text = self.selectpetbutt.currentText()
        if not selected_text or selected_text not in self.pet_dict:
            return
        
        self.selected_pet_id = self.pet_dict[selected_text]['pet_id']
        
        # Update summary
        self.update_summary()
        
        # Check size compatibility if an event is selected
        if self.enrollselev.currentText():
            self.check_pet_size_compatibility()
    
    def check_pet_size_compatibility(self):
        """Rough check if this pet fits the event's size/weight rules."""
        if not self.enrollselev.currentText() or not self.selectpetbutt.currentText():
            self.petwarningsize.setText('')
            return
        
        event_text = self.enrollselev.currentText()
        pet_text = self.selectpetbutt.currentText()
        
        if event_text not in self.event_dict or pet_text not in self.pet_dict:
            return
        
        event = self.event_dict[event_text]
        pet = self.pet_dict[pet_text]
        
        pet_size_id = pet['size_id']
        event_min_size = event['min_size_id']
        event_max_size = event['max_size_id']
        pet_weight = pet['weight_kg']
        event_min_weight = event['min_weight']
        event_max_weight = event['max_weight']
        
        warnings = []
        
        # Check size compatibility
        if event_min_size and pet_size_id < event_min_size:
            warnings.append(f"Pet size ({pet['size_name']}) is smaller than required minimum")
        if event_max_size and pet_size_id > event_max_size:
            warnings.append(f"Pet size ({pet['size_name']}) is larger than required maximum")
        
        # Check weight compatibility
        if event_min_weight and pet_weight < event_min_weight:
            warnings.append(f"Pet weight ({pet_weight} kg) is below minimum ({event_min_weight} kg)")
        if event_max_weight and pet_weight > event_max_weight:
            warnings.append(f"Pet weight ({pet_weight} kg) exceeds maximum ({event_max_weight} kg)")
        
        if warnings:
            self.petwarningsize.setText(' | '.join(warnings))
        else:
            self.petwarningsize.setText('✓ Pet size and weight are compatible')
    
    def update_summary(self):
        """Refresh the little summary box for the current selection."""
        if not self.enrollselev.currentText():
            self.enrollsummary.setText('')
            self.enrollattstat.setText('')
            self.enrollpayment.clear()
            self.statuspart.clear()
            return
        
        event_text = self.enrollselev.currentText()
        if event_text not in self.event_dict:
            return
        
        event = self.event_dict[event_text]
        reg_date = self.enrollregdate.date().toString("yyyy-MM-dd")
        
        # Build summary text we show in the label
        summary_parts = []
        summary_parts.append(f"Event: {event['name']}")
        summary_parts.append(f"Date: {event['date']} at {event['time']}")
        summary_parts.append(f"Location: {event['location']}")
        summary_parts.append(f"Type: {event['type']}")
        
        if self.selectpetbutt.currentText():
            pet_text = self.selectpetbutt.currentText()
            if pet_text in self.pet_dict:
                pet = self.pet_dict[pet_text]
                summary_parts.append(f"Pet: {pet['name']}")
        
        summary_parts.append(f"Registration Date: {reg_date}")
        
        self.enrollsummary.setText('\n'.join(summary_parts))
        
        # Just show a simple status line for now
        self.enrollattstat.setText("Status: Registered")
        
        # Recompute payment and participants
        self.calculate_payment()
    
    def calculate_payment(self):
        """Figure out how much to pay and show it."""
        self.enrollpayment.clear()
        self.statuspart.clear()
        
        if not self.enrollselev.currentText():
            return
        
        event = self.event_dict[self.enrollselev.currentText()]
        base_fee = event['base_fee']
        discount = event['extra_pet_discount']
        event_id = event['event_id']
        
        # See how many of this owner's pets already joined this event
        conn = get_db_connection()
        if conn:
            try:
                cursor = conn.cursor()
                
                # Get owner name
                owner_name = "Unknown"
                if self.current_owner_id:
                    cursor.execute("""
                        SELECT first_name, last_name 
                        FROM owners 
                        WHERE owner_id = %s
                    """, (self.current_owner_id,))
                    owner_result = cursor.fetchone()
                    if owner_result:
                        owner_name = f"{owner_result[0]} {owner_result[1]}"
                
                # Get pet name
                pet_name = "Not selected"
                if self.selectpetbutt.currentText():
                    pet_text = self.selectpetbutt.currentText()
                    if pet_text in self.pet_dict:
                        pet_name = self.pet_dict[pet_text]['name']
                
                # Add event and enrollment information
                self.enrollpayment.addItem(f"Event: {event['name']}")
                self.enrollpayment.addItem(f"Event Date: {event['date']} at {event['time']}")
                self.enrollpayment.addItem(f"Owner: {owner_name}")
                self.enrollpayment.addItem(f"Pet: {pet_name}")
                self.enrollpayment.addItem("")  # Empty line separator
                
                cursor.execute("""
                    SELECT COUNT(DISTINCT pee.pet_id)
                    FROM event_registration er
                    JOIN pet_event_entry pee ON er.registration_id = pee.registration_id
                    WHERE er.owner_id = %s AND er.event_id = %s AND er.status = 'Paid'
                """, (self.current_owner_id, event_id))
                
                existing_pets_count = cursor.fetchone()[0] or 0
                
                # Calculate total
                if existing_pets_count == 0:
                    # First pet pays full price
                    total = base_fee
                    self.enrollpayment.addItem(f"Base Registration Fee: ₱{base_fee:.2f}")
                else:
                    # Additional pets get discount
                    total = base_fee - discount
                    self.enrollpayment.addItem(f"Base Registration Fee: ₱{base_fee:.2f}")
                    self.enrollpayment.addItem(f"Extra Pet Discount: -₱{discount:.2f}")
                
                self.enrollpayment.addItem(f"Total Amount: ₱{total:.2f}")
                
                # Count total participants for this event (all owners)
                cursor.execute("""
                    SELECT COUNT(DISTINCT pee.pet_id)
                    FROM event_registration er
                    JOIN pet_event_entry pee ON er.registration_id = pee.registration_id
                    WHERE er.event_id = %s AND er.status = 'Paid'
                """, (event_id,))
                
                total_participants = cursor.fetchone()[0] or 0
                max_participants = event.get('max_participants', 0)
                available_spots = max(0, max_participants - total_participants)
                
                # Participation status - only show participants and available spots
                self.statuspart.addItem(f"Participants: {total_participants}")
                self.statuspart.addItem(f"Available Spots: {available_spots}")
                
            except Error as err:
                print(f"Error calculating payment: {err}")
            finally:
                if conn:
                    conn.close()
        
    def enrollevnt(self):
        """Handle event enrollment logic."""
        self.petregiserr.setText('')
        self.petwarningsize.setText('')
        
        # Validate selections
        if not self.enrollselev.currentText():
            self.petregiserr.setText('Please select an event.')
            return
        
        if not self.selectpetbutt.currentText():
            self.petregiserr.setText('Please select a pet.')
            return
        
        if self.current_owner_id is None:
            self.petregiserr.setText('No owner found. Please register first.')
            return
        
        event_text = self.enrollselev.currentText()
        pet_text = self.selectpetbutt.currentText()
        
        if event_text not in self.event_dict or pet_text not in self.pet_dict:
            self.petregiserr.setText('Invalid selection.')
            return
        
        event = self.event_dict[event_text]
        pet = self.pet_dict[pet_text]
        
        # Check if pet is already registered for this event
        conn = get_db_connection()
        if conn:
            try:
                cursor = conn.cursor()
                
                # Check for existing registration (only check for active Paid registrations)
                # This allows re-enrollment after withdrawal since we delete pet_event_entry on withdrawal
                cursor.execute("""
                    SELECT COUNT(*) 
                    FROM pet_event_entry pee
                    JOIN event_registration er ON pee.registration_id = er.registration_id
                    WHERE pee.pet_id = %s AND pee.event_id = %s AND er.status = 'Paid'
                """, (pet['pet_id'], event['event_id']))
                
                if cursor.fetchone()[0] > 0:
                    self.petregiserr.setText('This pet is already registered for this event. You can register for other events though!')
                    conn.close()
                    return
                
                # Check event deadline
                reg_qdate = self.enrollregdate.date()
                reg_date_obj = reg_qdate.toPyDate()
                reg_date = reg_date_obj.strftime("%Y-%m-%d")
                deadline = event.get('registration_deadline')
                
                deadline_date = to_python_date(deadline)
                if deadline:
                    # Get deadline from database
                    cursor.execute("""
                        SELECT registration_deadline 
                        FROM events 
                        WHERE event_id = %s
                    """, (event['event_id'],))
                    deadline_result = cursor.fetchone()
                    if deadline_result and deadline_result[0]:
                        deadline = deadline_result[0]
                        deadline_date = to_python_date(deadline)
                if deadline_date and reg_date_obj > deadline_date:
                    deadline_text = deadline_date.strftime("%Y-%m-%d")
                    self.petregiserr.setText(f'Registration deadline ({deadline_text}) has passed.')
                    conn.close()
                    return
                
                # Get next registration ID
                cursor.execute("SELECT MAX(registration_id) FROM event_registration")
                max_reg_id = cursor.fetchone()[0]
                new_reg_id = (max_reg_id if max_reg_id is not None else 0) + 1
                
                # Calculate payment
                cursor.execute("""
                    SELECT COUNT(DISTINCT pee.pet_id)
                    FROM event_registration er
                    JOIN pet_event_entry pee ON er.registration_id = pee.registration_id
                    WHERE er.owner_id = %s AND er.event_id = %s AND er.status = 'Paid'
                """, (self.current_owner_id, event['event_id']))
                
                existing_pets_count = cursor.fetchone()[0] or 0
                
                if existing_pets_count == 0:
                    total_amount = event['base_fee']
                else:
                    total_amount = event['base_fee'] - event['extra_pet_discount']
                
                # Get current date and time for payment
                from datetime import datetime
                now = datetime.now()
                payment_date = now.strftime("%Y-%m-%d")
                payment_time = now.strftime("%H:%M:%S")
                
                # Insert registration
                cursor.execute("""
                    INSERT INTO event_registration 
                    (registration_id, owner_id, event_id, registration_date, 
                     total_amount_paid, payment_date, payment_time, status)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (new_reg_id, self.current_owner_id, event['event_id'], reg_date,
                      total_amount, payment_date, payment_time, 'Paid'))
                
                # Get next entry ID
                cursor.execute("SELECT MAX(entry_id) FROM pet_event_entry")
                max_entry_id = cursor.fetchone()[0]
                new_entry_id = (max_entry_id if max_entry_id is not None else 0) + 1
                
                # Insert pet event entry
                cursor.execute("""
                    INSERT INTO pet_event_entry 
                    (entry_id, registration_id, pet_id, event_id, attendance_status)
                    VALUES (%s, %s, %s, %s, %s)
                """, (new_entry_id, new_reg_id, pet['pet_id'], event['event_id'], 'Registered'))
                
                # Log to participation_log
                cursor.execute("SELECT MAX(log_id) FROM participation_log")
                max_log_id = cursor.fetchone()[0]
                new_log_id = (max_log_id if max_log_id is not None else 0) + 1
                
                action_date = now.strftime("%Y-%m-%d")
                action_time = now.strftime("%H:%M:%S")
                
                cursor.execute("""
                    INSERT INTO participation_log
                    (log_id, registration_id, action_type, action_date, action_time,
                     original_event_id, new_event_id, reason, refund_amount, top_up_amount)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (new_log_id, new_reg_id, 'Paid', action_date, action_time,
                      event['event_id'], None, 'New registration', 0.00, 0.00))
                
                conn.commit()
                
                print(f"Successfully enrolled pet {pet['name']} in event {event['name']}")
                self.gotoeventenroll()
                
            except Error as err:
                print(f"Database INSERT Error (Enrollment): {err}")
                if conn:
                    conn.rollback()
                self.petregiserr.setText('Registration failed: Database Error.')
            except Exception as e:
                print(f"Unexpected Error during enrollment: {e}")
                if conn:
                    conn.rollback()
                self.petregiserr.setText('An unexpected error occurred.')
            finally:
                if conn:
                    conn.close()
        else:
            self.petregiserr.setText('Database connection failed.')

    def gotommenu(self):
        mmenu = mainmenu()
        widget.addWidget(mmenu)
        widget.setCurrentIndex(widget.currentIndex() + 1)

    def gotoeventenroll(self):
        eventrolled = evenrolled()
        widget.addWidget(eventrolled)
        widget.setCurrentIndex(widget.currentIndex() + 1)
        
# --------------------------------------------------------------------------------------------------------------------

class evenrolled(QDialog):
    def __init__(self):
        super(evenrolled, self).__init__()
        loadUi('./gui/eventenrolled.ui', self)
        self.eventenrolledbutt.clicked.connect(self.gotommenu)

    def gotommenu(self):
        mmenu = mainmenu()
        widget.addWidget(mmenu)
        widget.setCurrentIndex(widget.currentIndex() + 1)

# --------------------------------------------------------------------------------------------------------------------

class editinf(QDialog):
    def __init__(self, owner_context=None):
        super(editinf, self).__init__()
        loadUi('./gui/editinfo.ui', self)
        self.editexitbutt.clicked.connect(self.gotommenu)
        self.saveinfobutt.clicked.connect(self.saveinf)
        self.oweditsavebutt.clicked.connect(self.saveownerinfo)
        self.editpetbutt.clicked.connect(self.editpet)
        self.delpetbutt.clicked.connect(self.deletepet)
        
        # Get error message labels
        self.owerrormes = self.findChild(QtWidgets.QLabel, 'owerrormes')
        self.editerrormess = self.findChild(QtWidgets.QLabel, 'editerrormess')
        
        # Load current owner and pet data
        self.owner_context = owner_context or get_active_owner()
        self.current_owner_id = self.owner_context['owner_id'] if self.owner_context else None
        self.loadownerdata()
        self.loadpets()
        
    def loadownerdata(self):
        """Load the latest owner's info into the text fields."""
        if self.current_owner_id is None:
            self.owerrormes.setText('No owner found. Please log in first.')
            return
        conn = get_db_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT first_name, last_name, email, contact_number 
                    FROM owners 
                    WHERE owner_id = %s
                """, (self.current_owner_id,))
                
                owner_data = cursor.fetchone()
                
                if owner_data:
                    self.editfirst.setText(owner_data[0] or '')
                    self.editlast.setText(owner_data[1] or '')
                    self.editemail.setText(owner_data[2] or '')
                    self.editnum.setText(owner_data[3] or '')
                else:
                    self.owerrormes.setText('Owner record not found. Please re-login.')
                    
            except Error as err:
                print(f"Error loading owner data: {err}")
                self.owerrormes.setText('Error loading owner data.')
            finally:
                if conn:
                    conn.close()
        else:
            self.owerrormes.setText('Database connection failed.')
    
    def loadpets(self):
        """Show this owner's pets in the table."""
        if self.current_owner_id is None:
            return
            
        conn = get_db_connection()
        if conn:
            try:
                cursor = conn.cursor()
                
                # Grab all pets for this owner, plus breed and size
                cursor.execute("""
                    SELECT p.pet_id, p.name, p.age, p.sex, p.weight_kg, 
                           GROUP_CONCAT(b.breed_name SEPARATOR ', ') as breeds,
                           sc.size_name
                    FROM pets p
                    LEFT JOIN pet_breed_junction pbj ON p.pet_id = pbj.pet_id
                    LEFT JOIN breeds b ON pbj.breed_id = b.breed_id
                    LEFT JOIN size_category sc ON p.actual_size_id = sc.size_id
                    WHERE p.owner_id = %s
                    GROUP BY p.pet_id
                    ORDER BY p.pet_id
                """, (self.current_owner_id,))
                
                pets = cursor.fetchall()
                
                # Basic table setup
                self.petlist.setRowCount(len(pets))
                self.petlist.setColumnCount(7)
                self.petlist.setHorizontalHeaderLabels(['ID', 'Name', 'Age', 'Sex', 'Weight (kg)', 'Breed', 'Size'])
                
                # Fill the rows
                for row, pet in enumerate(pets):
                    for col, value in enumerate(pet):
                        item = QtWidgets.QTableWidgetItem(str(value) if value is not None else '')
                        self.petlist.setItem(row, col, item)
                
                # Make columns wide enough so stuff is readable
                self.petlist.resizeColumnsToContents()
                
            except Error as err:
                print(f"Error loading pets: {err}")
                self.editerrormess.setText('Error loading pets.')
            finally:
                if conn:
                    conn.close()
    
    def saveownerinfo(self):
        """Save whatever the user typed for this owner."""
        if self.current_owner_id is None:
            self.owerrormes.setText('No owner selected.')
            return
        
        first_name = self.editfirst.text().strip()
        last_name = self.editlast.text().strip()
        email = self.editemail.text().strip()
        contact_number = self.editnum.text().strip()
        
        self.owerrormes.setText('')
        
        # Make sure we at least have a first + last name
        if not first_name or not last_name:
            self.owerrormes.setText('First and Last name are required.')
            return
        
        conn = get_db_connection()
        if conn:
            try:
                cursor = conn.cursor()
                
                # Save updated owner fields
                sql = """
                    UPDATE owners 
                    SET first_name = %s, last_name = %s, email = %s, contact_number = %s
                    WHERE owner_id = %s
                """
                cursor.execute(sql, (first_name, last_name, email, contact_number, self.current_owner_id))
                conn.commit()
                
                # Double-check that the update really went through
                cursor.execute("SELECT owner_id FROM owners WHERE owner_id = %s AND first_name = %s AND last_name = %s",
                             (self.current_owner_id, first_name, last_name))
                if cursor.fetchone():
                    print(f"Owner information successfully updated for ID: {self.current_owner_id}")
                    self.owerrormes.setText('Owner information saved successfully!')
                    update_active_owner_details(
                        first_name=first_name,
                        last_name=last_name,
                        email=email,
                        contact_number=contact_number
                    )
                else:
                    raise Error("Update verification failed")
                    
            except Error as err:
                print(f"Database UPDATE Error (Owner): {err}")
                if conn:
                    conn.rollback()
                self.owerrormes.setText('Failed to save owner information.')
            except Exception as e:
                print(f"Unexpected Error during owner update: {e}")
                if conn:
                    conn.rollback()
                self.owerrormes.setText('An unexpected error occurred.')
            finally:
                if conn:
                    conn.close()
        else:
            self.owerrormes.setText('Database connection failed.')
    
    def editpet(self):
        """Pop up a small window to pick which pet to edit."""
        if self.current_owner_id is None:
            self.editerrormess.setText('No owner found. Please register first.')
            return
        
        # Get all pets for this owner so we can list them
        conn = get_db_connection()
        if not conn:
            self.editerrormess.setText('Database connection failed.')
            return
        
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT pet_id, name 
                FROM pets 
                WHERE owner_id = %s
                ORDER BY name
            """, (self.current_owner_id,))
            
            pets = cursor.fetchall()
            
            if not pets:
                self.editerrormess.setText('No pets found to edit.')
                conn.close()
                return
            
            # Tiny dialog with a combo box so user can pick a pet
            dialog = QDialog(self)
            dialog.setWindowTitle("Select Pet to Edit")
            dialog.setModal(True)
            layout = QtWidgets.QVBoxLayout()
            
            label = QtWidgets.QLabel("Select a pet to edit:")
            layout.addWidget(label)
            
            combo = QtWidgets.QComboBox()
            pet_dict = {}
            for pet_id, pet_name in pets:
                display_text = f"{pet_name} (ID: {pet_id})"
                combo.addItem(display_text)
                pet_dict[display_text] = pet_id
            
            layout.addWidget(combo)
            
            button_box = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.StandardButton.Ok | QtWidgets.QDialogButtonBox.StandardButton.Cancel)
            button_box.accepted.connect(dialog.accept)
            button_box.rejected.connect(dialog.reject)
            layout.addWidget(button_box)
            
            dialog.setLayout(layout)
            
            if dialog.exec() == 1:  # QDialog.DialogCode.Accepted
                selected_text = combo.currentText()
                selected_pet_id = pet_dict.get(selected_text)
                
                if selected_pet_id:
                    # Go to the full edit-pet screen
                    editpet = editpetscreen(selected_pet_id, self.current_owner_id)
                    widget.addWidget(editpet)
                    widget.setCurrentIndex(widget.currentIndex() + 1)
            
        except Error as err:
            print(f"Error loading pets for selection: {err}")
            self.editerrormess.setText('Error loading pets.')
        finally:
            if conn:
                conn.close()
    
    def deletepet(self):
        """Pop up a small window to pick which pet to delete."""
        if self.current_owner_id is None:
            self.editerrormess.setText('No owner found. Please register first.')
            return
        
        # Same idea: list the pets for this owner
        conn = get_db_connection()
        if not conn:
            self.editerrormess.setText('Database connection failed.')
            return
        
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT pet_id, name 
                FROM pets 
                WHERE owner_id = %s
                ORDER BY name
            """, (self.current_owner_id,))
            
            pets = cursor.fetchall()
            
            if not pets:
                self.editerrormess.setText('No pets found to delete.')
                conn.close()
                return
            
            # Small dialog with a dropdown of pets
            dialog = QDialog(self)
            dialog.setWindowTitle("Select Pet to Delete")
            dialog.setModal(True)
            layout = QtWidgets.QVBoxLayout()
            
            label = QtWidgets.QLabel("Select a pet to delete:")
            layout.addWidget(label)
            
            combo = QtWidgets.QComboBox()
            pet_dict = {}
            for pet_id, pet_name in pets:
                display_text = f"{pet_name} (ID: {pet_id})"
                combo.addItem(display_text)
                pet_dict[display_text] = pet_id
            
            layout.addWidget(combo)
            
            button_box = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.StandardButton.Ok | QtWidgets.QDialogButtonBox.StandardButton.Cancel)
            button_box.accepted.connect(dialog.accept)
            button_box.rejected.connect(dialog.reject)
            layout.addWidget(button_box)
            
            dialog.setLayout(layout)
            
            pet_id = None
            pet_name = None
            
            if dialog.exec() == 1:  # QDialog.DialogCode.Accepted
                selected_text = combo.currentText()
                pet_id = pet_dict.get(selected_text)
                
                if not pet_id:
                    conn.close()
                    return
                
                # Pull just the name part from the text we showed
                pet_name = selected_text.split(' (ID:')[0] if ' (ID:' in selected_text else 'Unknown'
            
            conn.close()
            
            # Actually delete the pet (and related rows) using a fresh connection
            if pet_id and pet_name:
                conn = get_db_connection()
                if conn:
                    try:
                        cursor = conn.cursor()
                        
                        # Clear out breed links first (keeps FK happy)
                        cursor.execute("DELETE FROM pet_breed_junction WHERE pet_id = %s", (pet_id,))
                        
                        # Then any event entries
                        cursor.execute("DELETE FROM pet_event_entry WHERE pet_id = %s", (pet_id,))
                        
                        # And any awards tied to this pet
                        cursor.execute("DELETE FROM awards WHERE pet_id = %s", (pet_id,))
                        
                        # Finally, remove the pet itself
                        cursor.execute("DELETE FROM pets WHERE pet_id = %s", (pet_id,))
                        
                        conn.commit()
                        
                        print(f"Pet {pet_name} (ID: {pet_id}) successfully deleted.")
                        self.editerrormess.setText(f'Pet {pet_name} deleted successfully.')
                        
                        # Refresh the pets table on screen
                        self.loadpets()
                        
                    except Error as err:
                        print(f"Database DELETE Error (Pet): {err}")
                        if conn:
                            conn.rollback()
                        self.editerrormess.setText('Failed to delete pet.')
                    except Exception as e:
                        print(f"Unexpected Error during pet deletion: {e}")
                        if conn:
                            conn.rollback()
                        self.editerrormess.setText('An unexpected error occurred.')
                    finally:
                        if conn:
                            conn.close()
                else:
                    self.editerrormess.setText('Database connection failed.')
            
        except Error as err:
            print(f"Error loading pets for selection: {err}")
            self.editerrormess.setText('Error loading pets.')
            if conn:
                conn.close()
        except Exception as e:
            print(f"Unexpected error: {e}")
            if conn:
                conn.close()
        
    def saveinf(self):
        """Save everything on this page, then move to the success screen."""
        # Try saving owner info first
        self.saveownerinfo()
        
        # If there are no error messages, we assume it went fine
        if not self.owerrormes.text() or 'successfully' in self.owerrormes.text():
            self.gotoinfoedited()
        else:
            # If something went wrong, stay here and show a hint
            self.editerrormess.setText('Please fix errors before saving.')

    def gotommenu(self):
        mmenu = mainmenu()
        widget.addWidget(mmenu)
        widget.setCurrentIndex(widget.currentIndex() + 1)

    def gotoinfoedited(self):    
        infoedtd = infoedited()
        widget.addWidget(infoedtd)
        widget.setCurrentIndex(widget.currentIndex() + 1)
        
# --------------------------------------------------------------------------------------------------------------------

class editpetscreen(QDialog):
    def __init__(self, pet_id, owner_id):
        super(editpetscreen, self).__init__()
        loadUi('./gui/editpet.ui', self)
        
        self.pet_id = pet_id
        self.owner_id = owner_id
        
        # Set up combo boxes
        self.petsex.addItems(['Male', 'Female', 'Unknown'])
        self.petsize.addItems(['Small', 'Medium', 'Large', 'Extra Large'])

        # Load breeds into combo box
        self.load_breeds()

        # Connect breed combo box to handle "Other" option
        self.petbreed.currentIndexChanged.connect(self.on_breed_selected)
        
        # Connect buttons
        self.petexitbutt.clicked.connect(self.gotoeditinf)
        self.peteditbutt.clicked.connect(self.savepetinfo)
        
        # Get error label
        self.petregiserr = self.findChild(QtWidgets.QLabel, 'petregiserr')
        
        # Load pet data
        self.loadpetdata()
        
        # Highlight muzzle choice
        self.muzzleyes  = self.findChild(QtWidgets.QRadioButton, 'muzzleyes')
        self.muzzleno   = self.findChild(QtWidgets.QRadioButton, 'muzzleno')
        self.muzzleyes.toggled.connect(self.update_muzzle_highlight_edit)
        self.muzzleno.toggled.connect(self.update_muzzle_highlight_edit)
        self.update_muzzle_highlight_edit()
        
        if self.muzzleyes and self.muzzleno:
            self.muzzleyes.toggled.connect(self.update_muzzle_highlight_edit)
            self.muzzleno.toggled.connect(self.update_muzzle_highlight_edit)
            self.update_muzzle_highlight_edit()
            
    def update_muzzle_highlight_edit(self):
        off = ("QRadioButton { color: rgb(40,52,84); background: transparent; "
               "font: 700 10pt 'Berlin Sans FB Demi'; padding: 2px 6px; border-radius: 6px; }")
        on  = ("QRadioButton { color: white; background: rgb(251,176,59); "
               "font: 700 10pt 'Berlin Sans FB Demi'; padding: 2px 6px; border-radius: 6px; }")

        if self.muzzleyes.isChecked():
            self.muzzleyes.setStyleSheet(on)
            self.muzzleno.setStyleSheet(off)
        elif self.muzzleno.isChecked():
            self.muzzleyes.setStyleSheet(off)
            self.muzzleno.setStyleSheet(on)
        else:
            self.muzzleyes.setStyleSheet(off)
            self.muzzleno.setStyleSheet(off)
    

    def load_breeds(self):
        """Grab all breeds from the database and add them to the combo box, plus "Other" option."""
        conn = get_db_connection()
        if not conn:
            return
        
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT DISTINCT breed_name 
                FROM breeds 
                ORDER BY breed_name
            """)
            
            breeds = cursor.fetchall()
            self.petbreed.clear()
            
            # Add all breeds
            for breed in breeds:
                if breed[0]:
                    self.petbreed.addItem(breed[0])
            
            # Add "Other" option at the end
            self.petbreed.addItem("Other")
        except Error as err:
            print(f"Error loading breeds: {err}")
        finally:
            if conn:
                conn.close()
    
    def on_breed_selected(self):
        """Handle when breed selection changes - if "Other" is selected, clear the text so user can type."""
        if self.petbreed.currentText() == "Other":
            # Clear the text so user can type their custom breed
            self.petbreed.setEditText("") 
        
    def loadpetdata(self):
        """Load this pet's current info into the form so we can tweak it."""
        conn = get_db_connection()
        if conn:
            try:
                cursor = conn.cursor()
                
                # First, pull the main pet details
                cursor.execute("""
                    SELECT p.name, p.age, p.sex, p.weight_kg, p.actual_size_id, 
                           p.muzzle_required, p.notes, sc.size_name
                    FROM pets p
                    LEFT JOIN size_category sc ON p.actual_size_id = sc.size_id
                    WHERE p.pet_id = %s
                """, (self.pet_id,))
                
                pet_data = cursor.fetchone()
                
                if pet_data:
                    # Push basic pet info into the widgets
                    self.petname.setText(pet_data[0] or '')
                    self.petage.setValue(pet_data[1] or 0)
                    
                    # Set sex
                    sex_index = self.petsex.findText(pet_data[2] or 'Unknown')
                    if sex_index >= 0:
                        self.petsex.setCurrentIndex(sex_index)
                    
                    self.petweight.setValue(pet_data[3] or 0.0)
                    
                    # Set size
                    size_name = pet_data[7] or 'Large'
                    size_index = self.petsize.findText(size_name)
                    if size_index >= 0:
                        self.petsize.setCurrentIndex(size_index)
                    
                    # Flip the muzzle radio buttons
                    if pet_data[5] == 1:
                        self.muzzleyes.setChecked(True)
                    else:
                        self.muzzleno.setChecked(True)
                    
                    self.petnotes.setPlainText(pet_data[6] or '')
                    
                    # Now grab the breed and set it in the combo box
                    cursor.execute("""
                        SELECT b.breed_name 
                        FROM breeds b
                        JOIN pet_breed_junction pbj ON b.breed_id = pbj.breed_id
                        WHERE pbj.pet_id = %s
                        LIMIT 1
                    """, (self.pet_id,))
                    
                    breed_result = cursor.fetchone()
                    if breed_result:
                        breed_name = breed_result[0] or ''
                        # Set the combo box text to the breed name
                        self.petbreed.setCurrentText(breed_name)
                    
                    # Show the owner name at the top
                    cursor.execute("""
                        SELECT first_name, last_name 
                        FROM owners 
                        WHERE owner_id = %s
                    """, (self.owner_id,))
                    
                    owner_result = cursor.fetchone()
                    if owner_result:
                        owner_name = f"{owner_result[0]} {owner_result[1]}"
                        self.owerusername.setText(owner_name)
                
            except Error as err:
                print(f"Error loading pet data: {err}")
                self.petregiserr.setText('Error loading pet data.')
            finally:
                if conn:
                    conn.close()
        else:
            self.petregiserr.setText('Database connection failed.')
    
    def savepetinfo(self):
        """Save updated pet info back into the database."""
        petname = self.petname.text().strip()
        petage = self.petage.value()
        petsex = self.petsex.currentText().strip()
        petweight = self.petweight.value()
        petsize_name = self.petsize.currentText().strip()
        petbreed = self.petbreed.currentText().strip()
        petnotes = self.petnotes.toPlainText().strip()
        
        self.petregiserr.setText('')
        
        # Handle "Other" logic
        if petbreed == "Other" or (petbreed == "" and self.petbreed.currentIndex() == self.petbreed.count() - 1):
            self.petregiserr.setText('Please enter a custom breed name.')
            return

        # Quick sanity check on required fields
        if not petname or petage == 0 or not petbreed:
            self.petregiserr.setText('Please fill in Pet Name, Age (must be > 0), and Breed.')
            return
        
        muzzle_required = 1 if self.muzzleyes.isChecked() else 0
        
        size_map = {'Small': 1, 'Medium': 2, 'Large': 3, 'Extra Large': 3}
        actual_size_id = size_map.get(petsize_name, 3)
        
        conn = get_db_connection()
        if conn:
            try:
                cursor = conn.cursor()
                
                # Update the core pet record
                sql_pet = """
                    UPDATE pets 
                    SET name = %s, actual_size_id = %s, age = %s, sex = %s, 
                        weight_kg = %s, muzzle_required = %s, notes = %s
                    WHERE pet_id = %s
                """
                cursor.execute(sql_pet, (
                    petname, actual_size_id, petage, petsex, 
                    petweight, muzzle_required, petnotes, self.pet_id
                ))
                
                # Deal with the breed: reuse if it exists, otherwise make a new one
                sql_breed_lookup = "SELECT breed_id FROM breeds WHERE breed_name = %s"
                cursor.execute(sql_breed_lookup, (petbreed,))
                breed_result = cursor.fetchone()
                
                if breed_result:
                    breed_id = breed_result[0]
                else:
                    # No existing breed, so we add it
                    cursor.execute("SELECT MAX(breed_id) FROM breeds")
                    max_breed_id = cursor.fetchone()[0]
                    new_breed_id = max(16, (max_breed_id if max_breed_id is not None else 0) + 1)
                    
                    sql_insert_breed = "INSERT INTO breeds (breed_id, breed_name, size_id) VALUES (%s, %s, %s)"
                    cursor.execute(sql_insert_breed, (new_breed_id, petbreed, 3))
                    breed_id = new_breed_id
                
                # Reset the breed link for this pet
                cursor.execute("DELETE FROM pet_breed_junction WHERE pet_id = %s", (self.pet_id,))
                cursor.execute("INSERT INTO pet_breed_junction (pet_id, breed_id) VALUES (%s, %s)", 
                             (self.pet_id, breed_id))
                
                conn.commit()
                
                # Just make sure the update really stuck
                cursor.execute("SELECT pet_id FROM pets WHERE pet_id = %s AND name = %s",
                             (self.pet_id, petname))
                if cursor.fetchone():
                    print(f"Pet information successfully updated for ID: {self.pet_id}")
                    self.petregiserr.setText('Pet information saved successfully!')
                    # Return to editinf screen after a short delay or immediately
                    self.gotoeditinf()
                else:
                    raise Error("Update verification failed")
                
            except Error as err:
                print(f"Database UPDATE Error (Pet): {err}")
                if conn:
                    conn.rollback()
                self.petregiserr.setText('Failed to save pet information.')
            except Exception as e:
                print(f"Unexpected Error during pet update: {e}")
                if conn:
                    conn.rollback()
                self.petregiserr.setText('An unexpected error occurred.')
            finally:
                if conn:
                    conn.close()
        else:
            self.petregiserr.setText('Database connection failed.')
    
    def gotoeditinf(self):
        """Return to the edit info screen."""
        editin = editinf()
        widget.addWidget(editin)
        widget.setCurrentIndex(widget.currentIndex() + 1)
        
# --------------------------------------------------------------------------------------------------------------------

class infoedited(QDialog):
    def __init__(self):
        super(infoedited, self).__init__()
        loadUi('./gui/infoedited!.ui', self)
        self.infoeditedbackbutt.clicked.connect(self.gotommenu)

    def gotommenu(self):
        mmenu = mainmenu()
        widget.addWidget(mmenu)
        widget.setCurrentIndex(widget.currentIndex() + 1)

# --------------------------------------------------------------------------------------------------------------------

class viewevents(QDialog):
    def __init__(self):
        super(viewevents, self).__init__()
        loadUi('./gui/viewevents.ui', self)
        self.veventexitbutt.clicked.connect(self.gotommenu)
        
        # Grab the labels we use for quick error messages
        self.owerrormes = self.findChild(QtWidgets.QLabel, 'owerrormes')
        self.editerrormess = self.findChild(QtWidgets.QLabel, 'editerrormess')
        
        # Fill the table with events
        self.load_events()

    def load_events(self):
        """Pull all events from the DB and show them in the table."""
        conn = get_db_connection()
        if conn:
            try:
                cursor = conn.cursor()
                
                # Get all events plus their size ranges (if any)
                cursor.execute("""
                    SELECT e.event_id, e.name, e.date, e.time, e.location, 
                           e.type, e.max_participants, e.registration_deadline,
                           e.status, e.base_registration_fee, e.extra_pet_discount,
                           e.distance_km, e.time_limit, e.min_weight, e.max_weight,
                           sc_min.size_name as min_size, sc_max.size_name as max_size
                    FROM events e
                    LEFT JOIN size_category sc_min ON e.min_size_id = sc_min.size_id
                    LEFT JOIN size_category sc_max ON e.max_size_id = sc_max.size_id
                    ORDER BY e.date, e.time
                """)
                
                events = cursor.fetchall()
                
                # Set up table with columns we want to show
                self.eventlist.setRowCount(len(events))
                self.eventlist.setColumnCount(15)
                self.eventlist.setHorizontalHeaderLabels([
                    'ID', 'Name', 'Date', 'Time', 'Location', 'Type', 
                    'Status', 'Max Participants', 'Deadline', 'Base Fee', 
                    'Extra Pet Discount', 'Distance (km)', 'Time Limit (min)', 
                    'Weight Range', 'Size Range'
                ])
                
                # Populate table
                for row, event in enumerate(events):
                    event_id = event[0]
                    name = event[1] or ''
                    date_value = event[2]
                    date_str = format_date_string(date_value)
                    time_value = event[3]
                    time_str = str(time_value) if time_value not in (None, '') else ''
                    location = event[4] or ''
                    event_type = event[5] or ''
                    max_participants = int(event[6]) if event[6] is not None else 0
                    deadline_str = format_date_string(event[7])
                    status = 'Open' if event[8] == 1 else 'Closed'
                    base_fee = float(event[9]) if event[9] is not None else 0.0
                    discount = float(event[10]) if event[10] is not None else 0.0
                    distance = event[11] if event[11] is not None else 'N/A'
                    time_limit = event[12] if event[12] is not None else 'N/A'
                    
                    # Weight range
                    min_weight = float(event[13]) if event[13] is not None else None
                    max_weight = float(event[14]) if event[14] is not None else None
                    if min_weight is not None or max_weight is not None:
                        min_weight_text = f"{min_weight:.2f}" if min_weight is not None else 'Any'
                        max_weight_text = f"{max_weight:.2f}" if max_weight is not None else 'Any'
                        weight_range = f"{min_weight_text}-{max_weight_text} kg"
                    else:
                        weight_range = 'Any'
                    
                    # Size range
                    min_size = event[15] or ''
                    max_size = event[16] or ''
                    if min_size or max_size:
                        size_range = f"{min_size if min_size else 'Any'}-{max_size if max_size else 'Any'}"
                    else:
                        size_range = 'Any'
                    
                    # Set items in table
                    self.eventlist.setItem(row, 0, QtWidgets.QTableWidgetItem(str(event_id)))
                    self.eventlist.setItem(row, 1, QtWidgets.QTableWidgetItem(name))
                    self.eventlist.setItem(row, 2, QtWidgets.QTableWidgetItem(date_str))
                    self.eventlist.setItem(row, 3, QtWidgets.QTableWidgetItem(time_str))
                    self.eventlist.setItem(row, 4, QtWidgets.QTableWidgetItem(location))
                    self.eventlist.setItem(row, 5, QtWidgets.QTableWidgetItem(event_type))
                    self.eventlist.setItem(row, 6, QtWidgets.QTableWidgetItem(status))
                    self.eventlist.setItem(row, 7, QtWidgets.QTableWidgetItem(str(max_participants)))
                    self.eventlist.setItem(row, 8, QtWidgets.QTableWidgetItem(deadline_str))
                    self.eventlist.setItem(row, 9, QtWidgets.QTableWidgetItem(f"₱{base_fee:.2f}"))
                    self.eventlist.setItem(row, 10, QtWidgets.QTableWidgetItem(f"₱{discount:.2f}"))
                    self.eventlist.setItem(row, 11, QtWidgets.QTableWidgetItem(str(distance)))
                    self.eventlist.setItem(row, 12, QtWidgets.QTableWidgetItem(str(time_limit)))
                    self.eventlist.setItem(row, 13, QtWidgets.QTableWidgetItem(weight_range))
                    self.eventlist.setItem(row, 14, QtWidgets.QTableWidgetItem(size_range))
                
                # Resize columns to fit content
                self.eventlist.resizeColumnsToContents()
                
                # Set alternating row colors for better readability
                self.eventlist.setAlternatingRowColors(True)
                
            except Error as err:
                print(f"Error loading events: {err}")
                if self.owerrormes:
                    self.owerrormes.setText('Error loading events.')
                if self.editerrormess:
                    self.editerrormess.setText('Error loading events.')
            finally:
                if conn:
                    conn.close()
        else:
            if self.owerrormes:
                self.owerrormes.setText('Database connection failed.')
            if self.editerrormess:
                self.editerrormess.setText('Database connection failed.')

    def gotommenu(self):
        mmenu = mainmenu()
        widget.addWidget(mmenu)
        widget.setCurrentIndex(widget.currentIndex() + 1)

# --------------------------------------------------------------------------------------------------------------------

class yourstatuss(QDialog):
    def __init__(self, owner_context=None):
        super(yourstatuss, self).__init__()
        loadUi('./gui/status.ui', self)
        self.exitbutt.clicked.connect(self.gotommenu)
        self.owerrormes = self.findChild(QtWidgets.QLabel, 'owerrormes')
        self.editerrormess = self.findChild(QtWidgets.QLabel, 'editerrormess')
        self.status_table = self.findChild(QtWidgets.QTableWidget, 'yourstatus')
        self.owner_context = owner_context or get_active_owner()
        self.current_owner_id = self.owner_context['owner_id'] if self.owner_context else None
        self.owner_name = ''
        self.configure_table()
        self.load_owner_data()
        self.populate_status_table()

    def configure_table(self):
        if not self.status_table:
            return
        headers = ['Owner', 'Pet', 'Breed', 'Size', 'Event', 'Event Date', 'Event Time', 'Status']
        self.status_table.setColumnCount(len(headers))
        self.status_table.setHorizontalHeaderLabels(headers)
        header = self.status_table.horizontalHeader()
        if header:
            header.setStretchLastSection(True)
            header.setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Stretch)
        vheader = self.status_table.verticalHeader()
        if vheader:
            vheader.setVisible(False)
            vheader.setDefaultSectionSize(28)

    def load_owner_data(self):
        if self.current_owner_id is None:
            if self.owerrormes:
                self.owerrormes.setText('Please log in to view your status.')
            return
        conn = get_db_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT first_name, last_name 
                    FROM owners 
                    WHERE owner_id = %s
                """, (self.current_owner_id,))
                owner_data = cursor.fetchone()
                if owner_data:
                    self.owner_name = f"{owner_data[0]} {owner_data[1]}".strip()
                else:
                    if self.owerrormes:
                        self.owerrormes.setText('Owner record not found. Please re-login.')
            except Error as err:
                print(f"Error loading owner data (status): {err}")
                if self.owerrormes:
                    self.owerrormes.setText('Error loading owner data.')
            finally:
                conn.close()
        else:
            if self.owerrormes:
                self.owerrormes.setText('Database connection failed.')

    def populate_status_table(self):
        if not self.status_table:
            return
        if self.current_owner_id is None:
            self.status_table.setRowCount(0)
            return

        conn = get_db_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT o.first_name, o.last_name,
                           p.name AS pet_name,
                           GROUP_CONCAT(DISTINCT b.breed_name SEPARATOR ', ') AS breeds,
                           sc.size_name,
                           e.name AS event_name,
                           e.date,
                           e.time,
                           COALESCE(er.status, 'Not Registered') AS status_text
                    FROM owners o
                    LEFT JOIN pets p ON p.owner_id = o.owner_id
                    LEFT JOIN pet_breed_junction pbj ON p.pet_id = pbj.pet_id
                    LEFT JOIN breeds b ON pbj.breed_id = b.breed_id
                    LEFT JOIN size_category sc ON p.actual_size_id = sc.size_id
                    LEFT JOIN pet_event_entry pee ON p.pet_id = pee.pet_id
                    LEFT JOIN events e ON pee.event_id = e.event_id
                    LEFT JOIN event_registration er ON pee.registration_id = er.registration_id
                    WHERE o.owner_id = %s
                    GROUP BY o.owner_id, p.pet_id, pee.event_id, er.status, e.date, e.time
                    ORDER BY (e.date IS NULL), e.date, p.name
                """, (self.current_owner_id,))
                rows = cursor.fetchall()

                if rows:
                    self.status_table.setRowCount(len(rows))
                    for row_idx, row in enumerate(rows):
                        owner_name = f"{row[0]} {row[1]}".strip() or (self.owner_name or 'Owner')
                        pet_name = row[2] or 'No pet'
                        breed = row[3] or 'N/A'
                        size = row[4] or 'N/A'
                        event_name = row[5] or 'Not enrolled'
                        event_date = format_date_string(row[6])
                        event_time = str(row[7]) if row[7] not in (None, '') else ''
                        status_text = row[8] or 'Pending'

                        values = [owner_name, pet_name, breed, size, event_name, event_date, event_time, status_text]
                        for col, value in enumerate(values):
                            self.status_table.setItem(row_idx, col, QtWidgets.QTableWidgetItem(str(value)))
                else:
                    self.status_table.setRowCount(1)
                    self.status_table.setItem(0, 0, QtWidgets.QTableWidgetItem(self.owner_name or 'Owner'))
                    self.status_table.setItem(0, 1, QtWidgets.QTableWidgetItem('No pets registered yet.'))
                    for col in range(2, self.status_table.columnCount()):
                        self.status_table.setItem(0, col, QtWidgets.QTableWidgetItem('N/A'))

            except Error as err:
                print(f"Error loading status data: {err}")
                if self.owerrormes:
                    self.owerrormes.setText('Failed to load status information.')
            finally:
                conn.close()
        else:
            if self.owerrormes:
                self.owerrormes.setText('Database connection failed.')

    def gotommenu(self):
        mmenu = mainmenu()
        widget.addWidget(mmenu)
        widget.setCurrentIndex(widget.currentIndex() + 1)

# --------------------------------------------------------------------------------------------------------------------

class entries(QDialog):
    def __init__(self):
        super(entries, self).__init__()
        loadUi('./gui/entries.ui', self)
        self.entriestexitbutt.clicked.connect(self.gotommenu)
        self.transferbutt.clicked.connect(self.gototransfer)
        self.withdrawbutt.clicked.connect(self.gotowithdraw)
        
        # Quick handles for labels we might update
        self.owerrormes = self.findChild(QtWidgets.QLabel, 'owerrormes')
        
        # When event changes in the dropdown, refresh the details
        self.vieweventsel.currentIndexChanged.connect(self.on_event_selected)
        
        # Initially load all visible events into the dropdown
        self.load_events()
        
    def load_events(self):
        """Grab all open events and stuff them into the dropdown."""
        conn = get_db_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT event_id, name, date, time
                    FROM events 
                    WHERE status = 1
                    ORDER BY date, time
                """)
                
                events = cursor.fetchall()
                self.vieweventsel.clear()
                self.event_dict = {}
                
                for event in events:
                    event_id = event[0]
                    event_name = event[1]
                    display_text = event_name
                    self.vieweventsel.addItem(display_text)
                    self.event_dict[display_text] = {
                        'event_id': event_id,
                        'name': event[1],
                        'date': event[2],
                        'time': event[3]
                    }
            except Error as err:
                print(f"Error loading events: {err}")
                self.owerrormes.setText('Error loading events.')
            finally:
                if conn:
                    conn.close()
    
    def on_event_selected(self):
        """When you pick an event, show its date and list of participants."""
        selected_text = self.vieweventsel.currentText()
        if not selected_text or selected_text not in self.event_dict:
            self.eventdate.clear()
            self.eventsparticipants.setRowCount(0)
            return
        
        event = self.event_dict[selected_text]
        event_id = event['event_id']
        
        # Show the date and time in the small list widget
        self.eventdate.clear()
        self.eventdate.addItem(f"Date: {event['date']}")
        self.eventdate.addItem(f"Time: {event['time']}")
        
        # Then load everyone registered for this event
        self.load_participants(event_id)
    
    def load_participants(self, event_id):
        """Fill the participants table for the chosen event."""
        conn = get_db_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT o.first_name, o.last_name, o.email, o.contact_number,
                           p.name as pet_name, p.age, p.sex, p.weight_kg,
                           sc.size_name, er.registration_date, er.total_amount_paid,
                           pee.attendance_status
                    FROM event_registration er
                    JOIN owners o ON er.owner_id = o.owner_id
                    JOIN pet_event_entry pee ON er.registration_id = pee.registration_id
                    JOIN pets p ON pee.pet_id = p.pet_id
                    LEFT JOIN size_category sc ON p.actual_size_id = sc.size_id
                    WHERE er.event_id = %s AND er.status = 'Paid'
                    ORDER BY er.registration_date, o.last_name, o.first_name
                """, (event_id,))
                
                participants = cursor.fetchall()
                
                # Set up table
                self.eventsparticipants.setRowCount(len(participants))
                self.eventsparticipants.setColumnCount(12)
                self.eventsparticipants.setHorizontalHeaderLabels([
                    'Owner First Name', 'Owner Last Name', 'Email', 'Contact',
                    'Pet Name', 'Age', 'Sex', 'Weight (kg)', 'Size',
                    'Registration Date', 'Amount Paid', 'Status'
                ])
                
                # Populate table
                for row, participant in enumerate(participants):
                    for col, value in enumerate(participant):
                        item = QtWidgets.QTableWidgetItem(str(value) if value is not None else '')
                        self.eventsparticipants.setItem(row, col, item)
                
                # Resize columns to fit content
                self.eventsparticipants.resizeColumnsToContents()
                
            except Error as err:
                print(f"Error loading participants: {err}")
                self.owerrormes.setText('Error loading participants.')
            finally:
                if conn:
                    conn.close()
        else:
            self.owerrormes.setText('Database connection failed.')

    def gotommenu(self):
        mmenu = mainmenu()
        widget.addWidget(mmenu)
        widget.setCurrentIndex(widget.currentIndex() + 1)

    def gotowithdraw(self):
        """Navigate to withdraw screen, passing selected event info if available."""
        selected_text = self.vieweventsel.currentText()
        if selected_text and selected_text in self.event_dict:
            event_id = self.event_dict[selected_text]['event_id']
            withd = withdraw(event_id)
        else:
            withd = withdraw()
        widget.addWidget(withd)
        widget.setCurrentIndex(widget.currentIndex() + 1)
    
    def gototransfer(self):
        """Navigate to transfer screen, passing selected event info if available."""
        selected_text = self.vieweventsel.currentText()
        if selected_text and selected_text in self.event_dict:
            event_id = self.event_dict[selected_text]['event_id']
            trnsfr = transfer(event_id)
        else:
            trnsfr = transfer()
        widget.addWidget(trnsfr)
        widget.setCurrentIndex(widget.currentIndex() + 1)

# --------------------------------------------------------------------------------------------------------------------


class transfer(QDialog):
    def __init__(self, preselected_event_id=None, owner_context=None):
        super(transfer, self).__init__()
        loadUi('./gui/transfer.ui', self)
        self.transexit.clicked.connect(self.gotoentries)
        self.tranferconbuut.clicked.connect(self.process_transfer)
        
        # Grab some handy labels so we can show messages
        self.petregiserr = self.findChild(QtWidgets.QLabel, 'petregiserr')
        self.petwarningsize = self.findChild(QtWidgets.QLabel, 'petwarningsize')
        self.owerusername = self.findChild(QtWidgets.QLabel, 'owerusername')
        
        # Stuff we keep around while you're on this screen
        self.owner_context = owner_context or get_active_owner()
        self.current_owner_id = self.owner_context['owner_id'] if self.owner_context else None
        self.selected_registration_id = None
        self.selected_pet_id = None
        self.selected_pet_ids = []  # Store all pet IDs for the registration
        self.event_from_dict = {}
        self.event_to_dict = {}
        
        # React when user changes either of the dropdowns
        self.eventfrom.currentIndexChanged.connect(self.on_event_from_selected)
        self.transferto.currentIndexChanged.connect(self.on_event_to_selected)
        
        # Kick things off by loading owner details and their events
        self.load_owner_data()
        self.load_enrolled_events(preselected_event_id)
    
    def load_owner_data(self):
        """Get the active owner and show their name at the top."""
        if self.current_owner_id is None:
            self.owerusername.setText('Please log in as an owner first.')
            return
        conn = get_db_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT first_name, last_name 
                    FROM owners 
                    WHERE owner_id = %s
                """, (self.current_owner_id,))
                
                owner_data = cursor.fetchone()
                if owner_data:
                    owner_name = f"{owner_data[0]} {owner_data[1]}"
                    self.owerusername.setText(owner_name)
            except Error as err:
                print(f"Error loading owner data: {err}")
            finally:
                if conn:
                    conn.close()
    
    def load_enrolled_events(self, preselected_event_id=None):
        """List the events this owner is currently paid/enrolled in."""
        if self.current_owner_id is None:
            return
        
        conn = get_db_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT DISTINCT er.registration_id, er.event_id, e.name, e.date, e.time,
                           e.base_registration_fee, e.extra_pet_discount
                    FROM event_registration er
                    JOIN events e ON er.event_id = e.event_id
                    WHERE er.owner_id = %s AND er.status = 'Paid'
                    ORDER BY e.date, e.time
                """, (self.current_owner_id,))
                
                registrations = cursor.fetchall()
                self.eventfrom.clear()
                self.event_from_dict = {}
                
                for reg in registrations:
                    reg_id = reg[0]
                    event_id = reg[1]
                    event_name = reg[2]
                    # Use registration_id to make display text unique for multiple transfers
                    display_text = f"{event_name} (Reg #{reg_id})"
                    self.eventfrom.addItem(display_text)
                    self.event_from_dict[display_text] = {
                        'registration_id': reg_id,
                        'event_id': event_id,
                        'name': reg[2],
                        'date': reg[3],
                        'time': reg[4],
                        'base_fee': reg[5],
                        'extra_pet_discount': reg[6]
                    }
                
                # If there's only one option, just auto-select it for convenience
                if len(registrations) == 1:
                    # Always select the first (and only) item
                    index = 0
                    # Use QTimer to ensure combo box is fully populated before selection
                    from PyQt6.QtCore import QTimer
                    QTimer.singleShot(0, lambda: self._select_event_from(index))
                elif preselected_event_id:
                    # If we came here from Entries with a specific event, pick that one
                    for text, data in self.event_from_dict.items():
                        if data['event_id'] == preselected_event_id:
                            index = self.eventfrom.findText(text)
                            if index >= 0:
                                from PyQt6.QtCore import QTimer
                                QTimer.singleShot(0, lambda idx=index: self._select_event_from(idx))
                            break
                
            except Error as err:
                print(f"Error loading enrolled events: {err}")
                self.petregiserr.setText('Error loading enrolled events.')
            finally:
                if conn:
                    conn.close()
    
    def _select_event_from(self, index):
        """Tiny helper to safely set the combo index and trigger the handler."""
        if index >= 0 and index < self.eventfrom.count():
            # Temporarily disconnect so we don't fire the slot twice
            try:
                self.eventfrom.currentIndexChanged.disconnect()
            except:
                pass  # Signal might not be connected yet
            
            self.eventfrom.setCurrentIndex(index)
            
            # Put the signal back
            self.eventfrom.currentIndexChanged.connect(self.on_event_from_selected)
            
            # And now manually load the data for that selection
            self.on_event_from_selected()
    
    def on_event_from_selected(self):
        """When the 'from' event changes, refresh pet list and details."""
        selected_text = self.eventfrom.currentText()
        if not selected_text or selected_text not in self.event_from_dict:
            self.petandowner.clear()
            self.currententry.clear()
            self.transferto.clear()
            self.newevent.clear()
            self.petwarningsize.setText('')
            return
        
        event_data = self.event_from_dict[selected_text]
        self.selected_registration_id = event_data['registration_id']
        event_id = event_data['event_id']
        
        # Show owner + pets for this registration
        self.load_pets_and_owners()
        
        # Fill the 'transfer to' dropdown, skipping events we can't move to
        self.load_transferable_events()
        
        # Show a quick summary for the current event
        self.display_current_entry(event_data)
    
    def load_pets_and_owners(self):
        """Show which pets (and owner) are attached to this registration."""
        if not self.selected_registration_id:
            self.petandowner.clear()
            return
        
        conn = get_db_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT DISTINCT o.first_name, o.last_name, p.name as pet_name, p.pet_id
                    FROM event_registration er
                    JOIN owners o ON er.owner_id = o.owner_id
                    JOIN pet_event_entry pee ON er.registration_id = pee.registration_id
                    JOIN pets p ON pee.pet_id = p.pet_id
                    WHERE er.registration_id = %s
                    ORDER BY p.name
                """, (self.selected_registration_id,))
                
                results = cursor.fetchall()
                self.petandowner.clear()
                self.selected_pet_ids = []  # track every pet ID in this registration
                
                if results:
                    # Owner is the same for all rows, so we just use the first
                    owner_first, owner_last, _, _ = results[0]
                    owner_name = f"{owner_first} {owner_last}"
                    self.petandowner.addItem(f"Owner: {owner_name}")
                    self.petandowner.addItem("")  # Empty line
                    
                    # Add each pet on its own line
                    for owner_first, owner_last, pet_name, pet_id in results:
                        self.petandowner.addItem(f"Pet: {pet_name}")
                        self.selected_pet_ids.append(pet_id)
                    
                    print(f"Loaded {len(self.selected_pet_ids)} pets for owner {owner_name}")
                else:
                    self.petandowner.addItem("No pets found for this registration")
                
                # Default to the first pet if we ever need a single one
                if self.selected_pet_ids:
                    self.selected_pet_id = self.selected_pet_ids[0]
                
            except Error as err:
                print(f"Error loading pets and owners: {err}")
                self.petregiserr.setText(f'Error loading pets: {err}')
            finally:
                if conn:
                    conn.close()
        else:
            self.petregiserr.setText('Database connection failed.')
    
    def load_transferable_events(self):
        """Figure out which other events we can move this entry to."""
        # Start by noting the current event so we can skip it
        current_event_id = None
        if self.eventfrom.currentText() and self.eventfrom.currentText() in self.event_from_dict:
            current_event_id = self.event_from_dict[self.eventfrom.currentText()]['event_id']
        
        # Also note any events this pet is already in so we don't double-book
        pet_ids_to_check = self.selected_pet_ids if hasattr(self, 'selected_pet_ids') and self.selected_pet_ids else []
        if hasattr(self, 'selected_pet_id') and self.selected_pet_id and self.selected_pet_id not in pet_ids_to_check:
            pet_ids_to_check.append(self.selected_pet_id)
        
        conn = get_db_connection()
        if conn:
            try:
                cursor = conn.cursor()
                
                # Query all open events, except the one we're currently in
                if current_event_id:
                    cursor.execute("""
                        SELECT event_id, name, date, time, base_registration_fee,
                               extra_pet_discount, max_participants
                        FROM events 
                        WHERE status = 1 AND event_id != %s
                        ORDER BY date, time
                    """, (current_event_id,))
                else:
                    cursor.execute("""
                        SELECT event_id, name, date, time, base_registration_fee,
                               extra_pet_discount, max_participants
                        FROM events 
                        WHERE status = 1
                        ORDER BY date, time
                    """)
                
                events = cursor.fetchall()
                self.transferto.clear()
                self.event_to_dict = {}
                
                # Build a set of events where these pets are already registered
                already_registered_events = set()
                if pet_ids_to_check:
                    placeholders = ','.join(['%s'] * len(pet_ids_to_check))
                    cursor.execute(f"""
                        SELECT DISTINCT pee.event_id
                        FROM pet_event_entry pee
                        JOIN event_registration er ON pee.registration_id = er.registration_id
                        WHERE pee.pet_id IN ({placeholders}) AND er.status = 'Paid'
                    """, pet_ids_to_check)
                    already_registered_events = {row[0] for row in cursor.fetchall()}
                
                for event in events:
                    event_id = event[0]
                    event_name = event[1]
                    
                    # Skip events that already have this pet, unless it's the current one
                    if event_id in already_registered_events and event_id != current_event_id:
                        continue
                    
                    display_text = event_name
                    self.transferto.addItem(display_text)
                    self.event_to_dict[display_text] = {
                        'event_id': event_id,
                        'name': event[1],
                        'date': event[2],
                        'time': event[3],
                        'base_fee': event[4],
                        'extra_pet_discount': event[5],
                        'max_participants': event[6]
                    }
                
                print(f"Loaded {len(self.event_to_dict)} transferable events")
                
            except Error as err:
                print(f"Error loading transferable events: {err}")
                self.petregiserr.setText(f'Error loading events: {err}')
            finally:
                if conn:
                    conn.close()
        else:
            self.petregiserr.setText('Database connection failed.')
    
    def display_current_entry(self, event_data):
        """Show a simple summary for the current event/registration."""
        self.currententry.clear()
        
        if not self.selected_registration_id:
            return
        
        self.currententry.addItem(f"Event: {event_data['name']}")
        self.currententry.addItem(f"Date: {event_data['date']} at {event_data['time']}")
        self.currententry.addItem(f"Base Fee: ₱{event_data['base_fee']:.2f}")
        
        # Also show how much was actually paid and when
        conn = get_db_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT total_amount_paid, registration_date
                    FROM event_registration
                    WHERE registration_id = %s
                """, (self.selected_registration_id,))
                
                result = cursor.fetchone()
                if result:
                    self.currententry.addItem("")  # Empty line
                    self.currententry.addItem(f"Amount Paid: ₱{result[0]:.2f}")
                    self.currententry.addItem(f"Registration Date: {result[1]}")
                else:
                    self.currententry.addItem("Registration details not found")
            except Error as err:
                print(f"Error loading registration details: {err}")
                self.currententry.addItem(f"Error: {err}")
            finally:
                if conn:
                    conn.close()
        else:
            self.currententry.addItem("Database connection failed")
    
    def on_event_to_selected(self):
        """When the 'to' event changes, show the new event info and any extra payment."""
        selected_text = self.transferto.currentText()
        if not selected_text:
            self.newevent.clear()
            self.petwarningsize.setText('')
            return
        
        if selected_text not in self.event_to_dict:
            self.newevent.clear()
            self.petwarningsize.setText('Event not found in dictionary.')
            print(f"Warning: '{selected_text}' not found in event_to_dict")
            print(f"Available events: {list(self.event_to_dict.keys())}")
            return
        
        event_data = self.event_to_dict[selected_text]
        
        # Show the details of the event we're moving to
        self.display_new_event(event_data)
        
        # See if we need to top up the payment and put a note in the label
        if self.selected_registration_id:
            conn = get_db_connection()
            if conn:
                try:
                    cursor = conn.cursor()
                    cursor.execute("""
                        SELECT total_amount_paid
                        FROM event_registration
                        WHERE registration_id = %s
                    """, (self.selected_registration_id,))
                    
                    result = cursor.fetchone()
                    if result:
                        current_amount = result[0]
                        new_fee = event_data['base_fee']
                        
                        if new_fee > current_amount:
                            additional = new_fee - current_amount
                            self.petwarningsize.setText(f"Additional ₱{additional:.2f} to be processed. Do you wish to proceed?")
                        elif new_fee < current_amount:
                            difference = current_amount - new_fee
                            new_total = current_amount - difference
                            self.petwarningsize.setText(f"Fee reduction: ₱{difference:.2f}. New total: ₱{new_total:.2f}. Do you wish to proceed?")
                        else:
                            self.petwarningsize.setText('No additional payment required.')
                    else:
                        self.petwarningsize.setText('Could not retrieve current payment amount.')
                except Error as err:
                    print(f"Error calculating payment: {err}")
                    self.petwarningsize.setText(f'Error: {err}')
                finally:
                    if conn:
                        conn.close()
        else:
            self.petwarningsize.setText('No registration selected.')
    
    def display_new_event(self, event_data):
        """Show new event info plus any extra payment we might need."""
        self.newevent.clear()
        
        if not event_data:
            self.newevent.addItem("No event data available")
            return
        
        self.newevent.addItem(f"Event: {event_data['name']}")
        self.newevent.addItem(f"Date: {event_data['date']} at {event_data['time']}")
        self.newevent.addItem(f"Base Fee: ₱{event_data['base_fee']:.2f}")
        self.newevent.addItem(f"Max Participants: {event_data['max_participants']}")
        
        # Work out the extra amount if the new event is pricier
        if self.selected_registration_id:
            conn = get_db_connection()
            if conn:
                try:
                    cursor = conn.cursor()
                    cursor.execute("""
                        SELECT total_amount_paid
                        FROM event_registration
                        WHERE registration_id = %s
                    """, (self.selected_registration_id,))
                    
                    result = cursor.fetchone()
                    if result:
                        current_amount = result[0]
                        new_fee = event_data['base_fee']
                        
                        self.newevent.addItem("")  # Empty line
                        if new_fee > current_amount:
                            additional = new_fee - current_amount
                            self.newevent.addItem(f"Additional Payment Required: ₱{additional:.2f}")
                            self.newevent.addItem(f"New Total: ₱{current_amount + additional:.2f}")
                        elif new_fee < current_amount:
                            # New event costs less - subtract the difference
                            difference = current_amount - new_fee
                            new_total = current_amount - difference
                            self.newevent.addItem(f"Fee Reduction: ₱{difference:.2f}")
                            self.newevent.addItem(f"New Total: ₱{new_total:.2f}")
                        else:
                            self.newevent.addItem("No additional payment required")
                            self.newevent.addItem(f"Total: ₱{current_amount:.2f}")
                    else:
                        self.newevent.addItem("")  # Empty line
                        self.newevent.addItem("Could not retrieve current payment")
                except Error as err:
                    print(f"Error calculating additional price: {err}")
                    self.newevent.addItem("")  # Empty line
                    self.newevent.addItem(f"Error: {err}")
                finally:
                    if conn:
                        conn.close()
        else:
            self.newevent.addItem("")  # Empty line
            self.newevent.addItem("No registration selected")
    
    def process_transfer(self):
        """Actually move the registration over to the new event."""
        self.petregiserr.setText('')
        
        if not self.eventfrom.currentText() or not self.transferto.currentText():
            self.petregiserr.setText('Please select both source and destination events.')
            return
        
        event_from_text = self.eventfrom.currentText()
        event_to_text = self.transferto.currentText()
        
        if event_from_text not in self.event_from_dict or event_to_text not in self.event_to_dict:
            self.petregiserr.setText('Invalid event selection.')
            return
        
        event_from = self.event_from_dict[event_from_text]
        event_to = self.event_to_dict[event_to_text]
        
        # Check if additional payment is needed
        conn = get_db_connection()
        if conn:
            try:
                cursor = conn.cursor()
                
                # Get current amount paid
                cursor.execute("""
                    SELECT total_amount_paid
                    FROM event_registration
                    WHERE registration_id = %s
                """, (self.selected_registration_id,))
                
                result = cursor.fetchone()
                if not result:
                    self.petregiserr.setText('Registration not found.')
                    conn.close()
                    return
                
                current_amount = result[0]
                new_fee = event_to['base_fee']
                
                # Calculate the fee difference
                fee_difference = new_fee - current_amount
                
                # Calculate new total amount
                if fee_difference > 0:
                    # New event costs more - add the additional fees
                    new_total_amount = current_amount + fee_difference
                    additional = fee_difference
                    # Show confirmation dialog
                    from PyQt6.QtWidgets import QMessageBox
                    reply = QMessageBox.question(
                        self, 
                        'Additional Payment Required',
                        f'Additional ₱{additional:.2f} to be processed. Do you wish to proceed?',
                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                    )
                    
                    if reply != QMessageBox.StandardButton.Yes:
                        return
                elif fee_difference < 0:
                    # New event costs less - subtract the difference
                    new_total_amount = current_amount + fee_difference  # fee_difference is negative, so this subtracts
                    additional = 0.00
                else:
                    # Same price
                    new_total_amount = current_amount
                    additional = 0.00
                
                # Update payment with new total amount
                from datetime import datetime
                now = datetime.now()
                payment_date = now.strftime("%Y-%m-%d")
                payment_time = now.strftime("%H:%M:%S")
                
                cursor.execute("""
                    UPDATE event_registration
                    SET total_amount_paid = %s, payment_date = %s, payment_time = %s
                    WHERE registration_id = %s
                """, (new_total_amount, payment_date, payment_time, self.selected_registration_id))
                
                # Update event_registration to new event
                cursor.execute("""
                    UPDATE event_registration
                    SET event_id = %s
                    WHERE registration_id = %s
                """, (event_to['event_id'], self.selected_registration_id))
                
                # Delete the original pet_event_entry entries (remove previous entry)
                if hasattr(self, 'selected_pet_ids') and self.selected_pet_ids:
                    for pet_id in self.selected_pet_ids:
                        cursor.execute("""
                            DELETE FROM pet_event_entry
                            WHERE registration_id = %s AND pet_id = %s AND event_id = %s
                        """, (self.selected_registration_id, pet_id, event_from['event_id']))
                else:
                    # Fallback to single pet
                    cursor.execute("""
                        DELETE FROM pet_event_entry
                        WHERE registration_id = %s AND pet_id = %s AND event_id = %s
                    """, (self.selected_registration_id, self.selected_pet_id, event_from['event_id']))
                
                # Create new pet_event_entry entries for the new event
                # Get the starting entry ID once
                cursor.execute("SELECT MAX(entry_id) FROM pet_event_entry")
                max_entry_id = cursor.fetchone()[0]
                next_entry_id = (max_entry_id if max_entry_id is not None else 0) + 1
                
                if hasattr(self, 'selected_pet_ids') and self.selected_pet_ids:
                    for idx, pet_id in enumerate(self.selected_pet_ids):
                        new_entry_id = next_entry_id + idx
                        
                        cursor.execute("""
                            INSERT INTO pet_event_entry
                            (entry_id, registration_id, pet_id, event_id, attendance_status)
                            VALUES (%s, %s, %s, %s, %s)
                        """, (new_entry_id, self.selected_registration_id, pet_id, event_to['event_id'], 'Registered'))
                else:
                    # Fallback to single pet
                    cursor.execute("""
                        INSERT INTO pet_event_entry
                        (entry_id, registration_id, pet_id, event_id, attendance_status)
                        VALUES (%s, %s, %s, %s, %s)
                    """, (next_entry_id, self.selected_registration_id, self.selected_pet_id, event_to['event_id'], 'Registered'))
                
                # Log the transfer
                cursor.execute("SELECT MAX(log_id) FROM participation_log")
                max_log_id = cursor.fetchone()[0]
                new_log_id = (max_log_id if max_log_id is not None else 0) + 1
                
                from datetime import datetime
                now = datetime.now()
                action_date = now.strftime("%Y-%m-%d")
                action_time = now.strftime("%H:%M:%S")
                
                # Calculate refund and top-up amounts
                refund_amount = abs(fee_difference) if fee_difference < 0 else 0.00
                top_up_amount = fee_difference if fee_difference > 0 else 0.00
                
                cursor.execute("""
                    INSERT INTO participation_log
                    (log_id, registration_id, action_type, action_date, action_time,
                     original_event_id, new_event_id, reason, refund_amount, top_up_amount)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (new_log_id, self.selected_registration_id, 'Transferred', action_date, action_time,
                      event_from['event_id'], event_to['event_id'], 'Event transfer', 
                      refund_amount, top_up_amount))
                
                conn.commit()
                
                self.petregiserr.setText('Transfer successful!')
                print(f"Successfully transferred registration {self.selected_registration_id} from event {event_from['event_id']} to {event_to['event_id']}")
                
                # Reload enrolled events to reflect the transfer
                # This allows multiple transfers to work correctly
                self.load_enrolled_events()
                
                # Clear the transfer to selection since event has changed
                self.transferto.clear()
                self.newevent.clear()
                self.petwarningsize.setText('Transfer completed. Please select a new event to transfer to if needed.')
                
            except Error as err:
                print(f"Database UPDATE Error (Transfer): {err}")
                if conn:
                    conn.rollback()
                self.petregiserr.setText('Transfer failed: Database Error.')
            except Exception as e:
                print(f"Unexpected Error during transfer: {e}")
                if conn:
                    conn.rollback()
                self.petregiserr.setText('An unexpected error occurred.')
            finally:
                if conn:
                    conn.close()
        else:
            self.petregiserr.setText('Database connection failed.')

    def gotoentries(self):
        entrs = entries()
        widget.addWidget(entrs)
        widget.setCurrentIndex(widget.currentIndex() + 1)

# --------------------------------------------------------------------------------------------------------------------

class withdraw(QDialog):
    def __init__(self, preselected_event_id=None, owner_context=None):
        super(withdraw, self).__init__()
        loadUi('./gui/withdraw.ui', self)
        self.withexit.clicked.connect(self.gotoentries)
        self.withdrawbutt.clicked.connect(self.process_withdrawal)
        
        # Get UI components
        self.petregiserr = self.findChild(QtWidgets.QLabel, 'petregiserr')
        self.warningwithdrawal = self.findChild(QtWidgets.QLabel, 'warningwithdrawal')
        self.owerusername = self.findChild(QtWidgets.QLabel, 'owerusername')
        self.currententry = self.findChild(QtWidgets.QListWidget, 'currententry')
        
        # Store data
        self.owner_context = owner_context or get_active_owner()
        self.current_owner_id = self.owner_context['owner_id'] if self.owner_context else None
        self.selected_registration_id = None
        self.selected_pet_ids = []
        self.event_from_dict = {}
        
        # Connect combo box signals
        self.withdrawfrom.currentIndexChanged.connect(self.on_event_from_selected)
        
        # Load data
        self.load_owner_data()
        self.load_enrolled_events(preselected_event_id)
    
    def load_owner_data(self):
        """Grab the active owner and show their name on top."""
        if self.current_owner_id is None:
            self.owerusername.setText('Please log in as an owner first.')
            return
        conn = get_db_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT first_name, last_name 
                    FROM owners 
                    WHERE owner_id = %s
                """, (self.current_owner_id,))
                
                owner_data = cursor.fetchone()
                if owner_data:
                    owner_name = f"{owner_data[0]} {owner_data[1]}"
                    self.owerusername.setText(owner_name)
            except Error as err:
                print(f"Error loading owner data: {err}")
            finally:
                if conn:
                    conn.close()
    
    def load_enrolled_events(self, preselected_event_id=None):
        """List events this owner is currently signed up (and paid) for."""
        if self.current_owner_id is None:
            return
        
        conn = get_db_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT DISTINCT er.registration_id, er.event_id, e.name, e.date, e.time,
                           e.base_registration_fee, e.extra_pet_discount
                    FROM event_registration er
                    JOIN events e ON er.event_id = e.event_id
                    WHERE er.owner_id = %s AND er.status = 'Paid'
                    ORDER BY e.date, e.time
                """, (self.current_owner_id,))
                
                registrations = cursor.fetchall()
                self.withdrawfrom.clear()
                self.event_from_dict = {}
                
                for reg in registrations:
                    reg_id = reg[0]
                    event_id = reg[1]
                    event_name = reg[2] or 'Event'
                    event_date = to_python_date(reg[3])
                    event_time = str(reg[4]) if reg[4] not in (None, '') else ''
                    event_date_text = format_date_string(event_date if event_date else reg[3])
                    base_fee = float(reg[5]) if reg[5] is not None else 0.0
                    extra_discount = float(reg[6]) if reg[6] is not None else 0.0
                    display_text = f"{event_name} (Reg #{reg_id})"
                    self.withdrawfrom.addItem(display_text)
                    self.event_from_dict[display_text] = {
                        'registration_id': reg_id,
                        'event_id': event_id,
                        'name': event_name,
                        'date': event_date,
                        'date_text': event_date_text,
                        'time': event_time,
                        'base_fee': base_fee,
                        'extra_pet_discount': extra_discount
                    }
                
                # If there’s only one choice, just auto-pick it for the user
                if len(registrations) == 1:
                    # Always select the first (and only) item
                    index = 0
                    # Use QTimer to ensure combo box is fully populated before selection
                    from PyQt6.QtCore import QTimer
                    QTimer.singleShot(0, lambda: self._select_withdraw_from(index))
                elif preselected_event_id:
                    # If Entries passed in an event, try to highlight that one
                    for text, data in self.event_from_dict.items():
                        if data['event_id'] == preselected_event_id:
                            index = self.withdrawfrom.findText(text)
                            if index >= 0:
                                from PyQt6.QtCore import QTimer
                                QTimer.singleShot(0, lambda idx=index: self._select_withdraw_from(idx))
                            break
                
            except Error as err:
                print(f"Error loading enrolled events: {err}")
                if self.petregiserr:
                    self.petregiserr.setText('Error loading enrolled events.')
            finally:
                if conn:
                    conn.close()
    
    def _select_withdraw_from(self, index):
        """Helper to safely set the index and run the handler once."""
        if index >= 0 and index < self.withdrawfrom.count():
            # Disconnect so we don't trigger twice while we change the index
            try:
                self.withdrawfrom.currentIndexChanged.disconnect()
            except:
                pass  # Signal might not be connected yet
            
            self.withdrawfrom.setCurrentIndex(index)
            
            # Put the connection back
            self.withdrawfrom.currentIndexChanged.connect(self.on_event_from_selected)
            
            # And then manually refresh the UI
            self.on_event_from_selected()
    
    def on_event_from_selected(self):
        """When the event changes, reload the pets and the summary."""
        selected_text = self.withdrawfrom.currentText()
        if not selected_text or selected_text not in self.event_from_dict:
            self.currententry.clear()
            self.warningwithdrawal.setText('')
            return
        
        event_data = self.event_from_dict[selected_text]
        self.selected_registration_id = event_data['registration_id']
        
        # Keep track of which pets are tied to this registration
        self.load_pets_and_owners()
        
        # Show the breakdown, including any possible refund
        self.display_current_entry_with_refund(event_data)
    
    def load_pets_and_owners(self):
        """Record which pets go with the current registration."""
        if not self.selected_registration_id:
            self.currententry.clear()
            return
        
        conn = get_db_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT DISTINCT o.first_name, o.last_name, p.name as pet_name, p.pet_id
                    FROM event_registration er
                    JOIN owners o ON er.owner_id = o.owner_id
                    JOIN pet_event_entry pee ON er.registration_id = pee.registration_id
                    JOIN pets p ON pee.pet_id = p.pet_id
                    WHERE er.registration_id = %s
                    ORDER BY p.name
                """, (self.selected_registration_id,))
                
                results = cursor.fetchall()
                self.selected_pet_ids = []
                
                if results:
                    for owner_first, owner_last, pet_name, pet_id in results:
                        self.selected_pet_ids.append(pet_id)
                
            except Error as err:
                print(f"Error loading pets and owners: {err}")
            finally:
                if conn:
                    conn.close()
    
    def calculate_refund(self, event_date, amount_paid):
        """Roughly figure out how much can be refunded based on how close the event is."""
        from datetime import datetime, date
        
        # Parse event date
        event_dt = to_python_date(event_date)
        if not event_dt:
            event_dt = date.today()
        
        # Get today's date
        today = date.today()
        
        # Calculate days until event
        days_until = (event_dt - today).days
        
        # Calculate refund based on policy
        if days_until >= 14:
            # 14+ days: 100% refund
            refund_percentage = 1.0
            refund_amount = amount_paid
            refund_text = "100% refund (14+ days before event)"
        elif days_until >= 4:
            # 13-4 days: 50% refund
            refund_percentage = 0.5
            refund_amount = amount_paid * 0.5
            refund_text = f"50% refund ({days_until} days before event)"
        else:
            # 3 days or less: 0% refund
            refund_percentage = 0.0
            refund_amount = 0.0
            refund_text = f"0% refund ({days_until} days before event - less than 4 days)"
        
        return {
            'days_until': days_until,
            'refund_percentage': refund_percentage,
            'refund_amount': refund_amount,
            'refund_text': refund_text
        }
    
    def display_current_entry_with_refund(self, event_data):
        """Show the current event details plus a quick refund breakdown."""
        self.currententry.clear()
        
        if not self.selected_registration_id:
            return
        
        event_name = event_data.get('name', 'Event')
        event_date_text = format_date_string(event_data.get('date'))
        event_time = event_data.get('time') or ''
        base_fee = float(event_data.get('base_fee', 0.0))
        self.currententry.addItem(f"Event: {event_name}")
        self.currententry.addItem(f"Event Date: {event_date_text} at {event_time}")
        self.currententry.addItem(f"Base Fee: ₱{base_fee:.2f}")
        
        # Get actual amount paid and registration details
        conn = get_db_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT total_amount_paid, registration_date, payment_date
                    FROM event_registration
                    WHERE registration_id = %s
                """, (self.selected_registration_id,))
                
                result = cursor.fetchone()
                if result:
                    amount_paid = float(result[0]) if result[0] is not None else 0.0
                    reg_date = format_date_string(result[1])
                    payment_date = format_date_string(result[2])
                    
                    self.currententry.addItem("")  # Empty line
                    self.currententry.addItem(f"Amount Paid: ₱{amount_paid:.2f}")
                    self.currententry.addItem(f"Registration Date: {reg_date}")
                    self.currententry.addItem(f"Payment Date: {payment_date}")
                    
                    # Calculate refund
                    refund_info = self.calculate_refund(event_data.get('date'), amount_paid)
                    
                    self.currententry.addItem("")  # Empty line
                    self.currententry.addItem("--- Refund Calculation ---")
                    self.currententry.addItem(f"Days until event: {refund_info['days_until']}")
                    self.currententry.addItem(f"Refund Policy: {refund_info['refund_text']}")
                    self.currententry.addItem("")  # Empty line
                    self.currententry.addItem(f"Refund Amount: ₱{refund_info['refund_amount']:.2f}")
                    
                    # Update warning label
                    if refund_info['refund_amount'] > 0:
                        self.warningwithdrawal.setText(f"Refund: ₱{refund_info['refund_amount']:.2f} will be processed.")
                    else:
                        self.warningwithdrawal.setText("No refund available (less than 4 days before event).")
                else:
                    self.currententry.addItem("Registration details not found")
            except Error as err:
                print(f"Error loading registration details: {err}")
                self.currententry.addItem(f"Error: {err}")
            finally:
                if conn:
                    conn.close()
        else:
            self.currententry.addItem("Database connection failed")
    
    def process_withdrawal(self):
        """Handle the actual withdrawal and log it."""
        if not self.petregiserr:
            self.petregiserr = self.findChild(QtWidgets.QLabel, 'petregiserr')
        
        if self.petregiserr:
            self.petregiserr.setText('')
        
        if not self.withdrawfrom.currentText():
            if self.petregiserr:
                self.petregiserr.setText('Please select a registration to withdraw.')
            return
        
        selected_text = self.withdrawfrom.currentText()
        if selected_text not in self.event_from_dict:
            if self.petregiserr:
                self.petregiserr.setText('Invalid registration selection.')
            return
        
        event_data = self.event_from_dict[selected_text]
        
        # Get refund information
        conn = get_db_connection()
        if conn:
            try:
                cursor = conn.cursor()
                
                # Get current amount paid and event date
                cursor.execute("""
                    SELECT er.total_amount_paid, e.date
                    FROM event_registration er
                    JOIN events e ON er.event_id = e.event_id
                    WHERE er.registration_id = %s
                """, (self.selected_registration_id,))
                
                result = cursor.fetchone()
                if not result:
                    if self.petregiserr:
                        self.petregiserr.setText('Registration not found.')
                    conn.close()
                    return
                
                amount_paid = float(result[0]) if result[0] is not None else 0.0
                event_date = result[1]
                
                # Calculate refund
                refund_info = self.calculate_refund(event_date, amount_paid)
                
                # Show confirmation dialog
                from PyQt6.QtWidgets import QMessageBox
                confirmation_msg = f"Are you sure you want to withdraw from this event?\n\n"
                confirmation_msg += f"Event: {event_data['name']}\n"
                confirmation_msg += f"Date: {format_date_string(event_date)}\n"
                confirmation_msg += f"Amount Paid: ₱{amount_paid:.2f}\n"
                confirmation_msg += f"Refund: ₱{refund_info['refund_amount']:.2f}\n\n"
                confirmation_msg += f"({refund_info['refund_text']})"
                
                reply = QMessageBox.question(
                    self, 
                    'Confirm Withdrawal',
                    confirmation_msg,
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                
                if reply != QMessageBox.StandardButton.Yes:
                    return
                
                # Delete pet_event_entry records first (to allow re-enrollment)
                if hasattr(self, 'selected_pet_ids') and self.selected_pet_ids:
                    for pet_id in self.selected_pet_ids:
                        cursor.execute("""
                            DELETE FROM pet_event_entry
                            WHERE registration_id = %s AND pet_id = %s
                        """, (self.selected_registration_id, pet_id))
                
                # Update registration status to Cancelled (keep record for audit, but mark as cancelled)
                from datetime import datetime
                now = datetime.now()
                cancellation_date = now.strftime("%Y-%m-%d")
                
                cursor.execute("""
                    UPDATE event_registration
                    SET status = %s, cancellation_date = %s
                    WHERE registration_id = %s
                """, ('Cancelled', cancellation_date, self.selected_registration_id))
                
                # Log the cancellation
                cursor.execute("SELECT MAX(log_id) FROM participation_log")
                max_log_id = cursor.fetchone()[0]
                new_log_id = (max_log_id if max_log_id is not None else 0) + 1
                
                action_date = now.strftime("%Y-%m-%d")
                action_time = now.strftime("%H:%M:%S")
                
                cursor.execute("""
                    INSERT INTO participation_log
                    (log_id, registration_id, action_type, action_date, action_time,
                     original_event_id, new_event_id, reason, refund_amount, top_up_amount)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (new_log_id, self.selected_registration_id, 'Cancelled', action_date, action_time,
                      event_data['event_id'], None, 'Owner withdrew from event', 
                      refund_info['refund_amount'], 0.00))
                
                conn.commit()
                
                if self.petregiserr:
                    refund_amt = refund_info['refund_amount']
                    self.petregiserr.setText(f"Withdrawal successful! Refund: ₱{refund_amt:.2f}")
                print(f"Successfully withdrew registration {self.selected_registration_id} from event {event_data['event_id']}")
                
                # Reload enrolled events to reflect the withdrawal
                self.load_enrolled_events()
                self.currententry.clear()
                if self.warningwithdrawal:
                    self.warningwithdrawal.setText('Withdrawal completed.')
                
            except Error as err:
                print(f"Database UPDATE Error (Withdrawal): {err}")
                if conn:
                    conn.rollback()
                if self.petregiserr:
                    self.petregiserr.setText('Withdrawal failed: Database Error.')
            except Exception as e:
                print(f"Unexpected Error during withdrawal: {e}")
                if conn:
                    conn.rollback()
                if self.petregiserr:
                    self.petregiserr.setText('An unexpected error occurred.')
            finally:
                if conn:
                    conn.close()
        else:
            if self.petregiserr:
                self.petregiserr.setText('Database connection failed.')

    def gotoentries(self):
        entrs = entries()
        widget.addWidget(entrs)
        widget.setCurrentIndex(widget.currentIndex() + 1)

# --------------------------------------------------------------------------------------------------------------------

class status(QDialog):
    def __init__(self):
        super(status, self).__init__()
        loadUi('./gui/status.ui', self)
        self.exitbutt.clicked.connect(self.gotommenu)

    def gotommenu(self):
        mmenu = mainmenu()
        widget.addWidget(mmenu)
        widget.setCurrentIndex(widget.currentIndex() + 1)

# --------------------------------------------------------------------------------------------------------------------

# Main Application Entry Point
if __name__ == '__main__':
    # 1. Ensure the SQLite database and all 10 tables with data are ready
    setup_database() 
    
    # 2. Run the PyQt application
    app = QApplication(sys.argv)
    registerscreen = RegisterScreen()
    widget = QStackedWidget()

    widget.addWidget(registerscreen)
    widget.setFixedHeight(796)
    widget.setFixedWidth(1246)
    widget.show()

    try:
        sys.exit(app.exec())
    except Exception as e:
        print(f'Exiting with error: {e}')
