import sys
import sqlite3
from PyQt6.uic import loadUi
from PyQt6 import QtWidgets
from PyQt6.QtWidgets import QDialog, QApplication, QWidget, QStackedWidget

DB_FILE = 'pet_show_portable.db'

def get_db_connection():
    """Establishes connection to the SQLite database file."""
    try:
        # sqlite3.connect creates the file if it is not found.
        conn = sqlite3.connect(DB_FILE) 
        conn.execute("PRAGMA foreign_keys = ON")
        return conn
    except sqlite3.Error as err:
        print(f"SQLite Connection Error: {err}")
        return None

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

            # pets (actual_size_id links to size_category, TINYINT(1) -> INTEGER)
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
                award_id INTEGER NOT NULL PRIMARY KEY,
                pet_id INTEGER NOT NULL,
                type TEXT NOT NULL,
                description TEXT,
                date TEXT NOT NULL,
                event_id INTEGER NOT NULL,
                FOREIGN KEY (pet_id) REFERENCES pets(pet_id),
                FOREIGN KEY (event_id) REFERENCES events(event_id)
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
            
            # ----------------------------------------------------------------------
           
            # size_category
            cursor.executemany("INSERT OR IGNORE INTO size_category (size_id, size_name) VALUES (?, ?)", [
                (1, 'Small'), (2, 'Medium'), (3, 'Large')
            ])
            
            # owners
            cursor.executemany("INSERT OR IGNORE INTO owners (owner_id, first_name, last_name, email, contact_number) VALUES (?, ?, ?, ?, ?)", [
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
            cursor.executemany("INSERT OR IGNORE INTO breeds (breed_id, breed_name, size_id) VALUES (?, ?, ?)", [
                (1, 'Chihuahua', 1), (2, 'Pomeranian', 1), (3, 'Dachshund', 1), (4, 'Beagle', 2), (5, 'Bulldog', 2),
                (6, 'Labrador Retriever', 3), (7, 'Golden Retriever', 3), (8, 'Border Collie', 2), (9, 'German Shepherd', 3),
                (10, 'Great Dane', 3), (11, 'Jack Russell Terrier', 1), (12, 'French Bulldog', 2), (13, 'Shih Tzu', 1),
                (14, 'Poodle (Miniature)', 1), (15, 'Australian Shepherd', 2)
            ])
            
            # events
            cursor.executemany("INSERT OR IGNORE INTO events (event_id, name, date, time, location, max_participants, registration_deadline, type, distance_km, time_limit, status, base_registration_fee, extra_pet_discount, min_weight, max_weight, min_size_id, max_size_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", [
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
            cursor.executemany("INSERT OR IGNORE INTO pets (pet_id, owner_id, name, actual_size_id, age, sex, weight_kg, muzzle_required, notes) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", [
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

            # pet_breed_junction
            cursor.executemany("INSERT OR IGNORE INTO pet_breed_junction (pet_id, breed_id) VALUES (?, ?)", [
                (1, 6), (2, 14), (3, 14), (4, 1), (5, 6), (6, 4), (7, 9), (8, 5), (9, 1), (10, 9), (11, 8), (12, 2),
                (13, 10), (14, 6), (15, 8), (16, 11), (17, 13), (18, 12), (19, 13), (20, 1), (21, 5), (22, 7), 
                (23, 4), (24, 2), (25, 3)
            ])

            # event_registration
            cursor.executemany("INSERT OR IGNORE INTO event_registration (registration_id, owner_id, event_id, registration_date, total_amount_paid, payment_date, payment_time, status, transfer_destination, cancellation_date) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", [
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
            cursor.executemany("INSERT OR IGNORE INTO pet_event_entry (entry_id, registration_id, pet_id, event_id, attendance_status, pet_result) VALUES (?, ?, ?, ?, ?, ?)", [
                (1, 1, 1, 1, 'Present', 8.7), (2, 2, 3, 4, 'Present', 9.3), (3, 3, 5, 2, 'Present', 9.8), (4, 4, 6, 10, 'Present', 8.9), 
                (5, 5, 7, 8, 'Present', 9.4), (6, 6, 9, 9, 'Present', 8.2), (7, 7, 10, 1, 'Present', 8.6), (8, 8, 12, 11, 'Present', 9.7), 
                (9, 9, 13, 8, 'No Show', 0.0), (10, 10, 15, 2, 'Present', 9.9), (11, 11, 16, 6, 'Present', 9.5), (12, 12, 18, 7, 'Present', 9.1), 
                (13, 13, 19, 4, 'Present', 8.8), (14, 14, 21, 8, 'Present', 9.6), (15, 15, 22, 9, 'Present', 8.4), (16, 16, 2, 11, 'Present', 9.2), 
                (17, 17, 24, 4, 'Present', 8.9), (18, 18, 5, 3, 'Present', 9.0), (19, 3, 8, 2, 'Present', 8.7), (20, 5, 23, 9, 'Present', 8.5)
            ])

            # awards
            cursor.executemany("INSERT OR IGNORE INTO awards (award_id, pet_id, type, description, date, event_id) VALUES (?, ?, ?, ?, ?, ?)", [
                (1, 3, 'Best Costume - 1st Place', 'Pirate-themed costume, high creativity', '2025-11-21', 4), (2, 19, 'Best Costume - 2nd Place', 'Colorful tutu and hat', '2025-11-21', 4),
                (3, 5, 'Agility - Fastest Run', 'Completed course fastest in novice division', '2025-11-21', 2), (4, 15, 'Frisbee - Best Catch', 'Long-distance catch accuracy', '2025-11-23', 10),
                (5, 1, 'Fun Run - Top Veteran', 'Top among 3-5 year old category', '2025-11-21', 1), (6, 16, 'Fastest Fetch - Winner', 'Fastest retrieve time', '2025-11-22', 6),
                (7, 18, 'Best Talent', 'Multiple tricks performed with style', '2025-11-22', 7), (8, 7, 'Strongest Dog - Runner Up', 'Excellent tug strength in heavy weight class', '2025-11-22', 8),
                (9, 22, 'Parade - Most Cheerful', 'Engaged crowd with playful antics', '2025-11-23', 9), (10, 12, 'Photo Booth - Most Photogenic', 'Great poses and expressiveness', '2025-11-23', 11),
                (11, 10, 'Fun Run - Most Spirited', 'High energy throughout', '2025-11-21', 1), (12, 21, 'Strongest Dog - Champion', 'Champion of tug-of-war heavy class', '2025-11-22', 8)
            ])

            # participation_log
            cursor.executemany("INSERT OR IGNORE INTO participation_log (log_id, registration_id, action_type, action_date, action_time, original_event_id, new_event_id, reason, refund_amount, top_up_amount) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", [
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
        except sqlite3.Error as e:
            print(f"Database setup error: {e}")
        finally:
            if conn:
                conn.close()

# --------------------------------------------------------------------------------------------------------------------

class RegisterScreen(QDialog):
    def __init__(self):
        super(RegisterScreen, self).__init__()
        loadUi('./gui/registerscreen.ui', self) 
        self.regbutt.clicked.connect(self.gotoownerregistration)

    def gotoownerregistration(self):
        ownerreg = OwnerRegisScreen()
        widget.addWidget(ownerreg)
        widget.setCurrentIndex(widget.currentIndex() + 1)

# --------------------------------------------------------------------------------------------------------------------

class OwnerRegisScreen(QDialog):
    def __init__(self):
        super(OwnerRegisScreen, self).__init__()
        loadUi('./gui/ownerregistration.ui', self)
        self.owregbutt.clicked.connect(self.registerfunc)
        self.owerrormes = self.findChild(QtWidgets.QLabel, 'owerrormes') 
        
    def registerfunc(self):
        userfirstname = self.owfirstname.text().strip()
        userlastname = self.owlastname.text().strip()
        useremail = self.owemail.text().strip()
        usernumber = self.ownumber.text().strip()
        
        self.owerrormes.setText('') 

        if (len(userfirstname) == 0 or len(userlastname) == 0):
            self.owerrormes.setText('Please fill in required fields (First and Last Name).')
            return
            
        conn = get_db_connection()
        
        if conn:
            try:
                cursor = conn.cursor()
                
                # Get the next available owner_id
                cursor.execute("SELECT MAX(owner_id) FROM owners")
                max_id = cursor.fetchone()[0]
                new_owner_id = (max_id if max_id is not None else 0) + 1
                
                # Insert the new owner into the database
                sql = "INSERT INTO owners (owner_id, first_name, last_name, email, contact_number) VALUES (?, ?, ?, ?, ?)"
                data = (new_owner_id, userfirstname, userlastname, useremail, usernumber)
                
                cursor.execute(sql, data)
                conn.commit()
                
                # Verify the insert was successful
                cursor.execute("SELECT owner_id FROM owners WHERE owner_id = ?", (new_owner_id,))
                if cursor.fetchone():
                    print(f"Owner successfully registered with ID: {new_owner_id}")
                    self.gotommenu()
                else:
                    raise sqlite3.Error("Insert verification failed")

            except sqlite3.Error as err:
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

class mainmenu(QDialog):
    def __init__(self):
        super(mainmenu, self).__init__()
        loadUi('./gui/mainmenu.ui', self)
        self.petregbutt.clicked.connect(self.gotopetregis)
        self.eventregbutt.clicked.connect(self.gotoenrollev)
        self.editinbutt.clicked.connect(self.gotoeditinfo)
        self.mmexitbutt.clicked.connect(self.quit_application)

    def quit_application(self):
        app.quit()

    def gotopetregis(self):
        petregis = petregistration()
        widget.addWidget(petregis)
        widget.setCurrentIndex(widget.currentIndex() + 1)
    
    def gotoenrollev(self):
        enrollev = enrollevent()
        widget.addWidget(enrollev)
        widget.setCurrentIndex(widget.currentIndex() + 1)
    
    def gotoeditinfo(self):
        editin = editinf()
        widget.addWidget(editin)
        widget.setCurrentIndex(widget.currentIndex() + 1)

# --------------------------------------------------------------------------------------------------------------------

class petregistration(QDialog):
    def __init__(self):
        super(petregistration, self).__init__()
        loadUi('./gui/petregistration.ui', self)

        self.petsex.addItems(['Male', 'Female', 'Unknown'])
        self.petsize.addItems(['Small', 'Medium', 'Large', 'Extra Large']) 

        self.petexitbutt.clicked.connect(self.gotommenu)
        self.petregisterbutt.clicked.connect(self.petregisfunc)
        self.petregiserr = self.findChild(QtWidgets.QLabel, 'petregiserr') 
        
    def petregisfunc(self):
        petname = self.petname.text().strip()
        petage = self.petage.value()
        petsex = self.petsex.currentText().strip()
        petweight = self.petweight.value()
        petsize_name = self.petsize.currentText().strip()
        petbreed = self.petbreed.text().strip()
        petnotes = self.petnotes.toPlainText().strip()

        self.petregiserr.setText('') 

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
                
                cursor.execute("SELECT MAX(owner_id) FROM owners")
                current_owner_id = cursor.fetchone()[0]
                
                if current_owner_id is None:
                    self.petregiserr.setText('Error: No owner found. Please register an owner first.')
                    return

                
                cursor.execute("SELECT MAX(pet_id) FROM pets")
                max_pet_id = cursor.fetchone()[0]
                new_pet_id = (max_pet_id if max_pet_id is not None else 0) + 1
                
                
                sql_breed_lookup = "SELECT breed_id FROM breeds WHERE breed_name = ?"
                cursor.execute(sql_breed_lookup, (petbreed,))
                breed_result = cursor.fetchone()

                if breed_result:
                    breed_id = breed_result[0]
                else:
                    
                    cursor.execute("SELECT MAX(breed_id) FROM breeds")
                    max_breed_id = cursor.fetchone()[0]
                    new_breed_id = max(16, (max_breed_id if max_breed_id is not None else 0) + 1)
                    
                    sql_insert_breed = "INSERT INTO breeds (breed_id, breed_name, size_id) VALUES (?, ?, ?)"
                    cursor.execute(sql_insert_breed, (new_breed_id, petbreed, 3)) 
                    
                    breed_id = new_breed_id
                
                sql_pet = """
                INSERT INTO pets 
                (pet_id, owner_id, name, actual_size_id, age, sex, weight_kg, muzzle_required, notes) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """
                data_pet = (
                    new_pet_id, 
                    current_owner_id, 
                    petname, 
                    actual_size_id,
                    petage, 
                    petsex, 
                    petweight, 
                    muzzle_required, 
                    petnotes
                )
                
                cursor.execute(sql_pet, data_pet)

                sql_junction = "INSERT INTO pet_breed_junction (pet_id, breed_id) VALUES (?, ?)"
                data_junction = (new_pet_id, breed_id)
                
                cursor.execute(sql_junction, data_junction)
                
                conn.commit()
                
                cursor.execute("SELECT pet_id FROM pets WHERE pet_id = ?", (new_pet_id,))
                if cursor.fetchone():
                    print(f"Pet successfully registered with ID: {new_pet_id}")
                    self.gotopetregistered()
                else:
                    raise sqlite3.Error("Insert verification failed")
                
            except sqlite3.Error as err:
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
    def __init__(self):
        super(enrollevent, self).__init__()
        loadUi('./gui/enrollevent.ui', self)
        self.enrollevexitbutt.clicked.connect(self.gotommenu)
        self.enrolevbutt.clicked.connect(self.gotoeventenroll)
        
    def enrollevnt(self):
        # Future function to handle event enrollment logic
        pass

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
    def __init__(self):
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
        self.current_owner_id = None
        self.loadownerdata()
        self.loadpets()
        
    def loadownerdata(self):
        """Load the current owner's information into the form fields."""
        conn = get_db_connection()
        if conn:
            try:
                cursor = conn.cursor()
                
                # Get the most recently registered owner
                cursor.execute("SELECT MAX(owner_id) FROM owners")
                result = cursor.fetchone()
                
                if result and result[0] is not None:
                    self.current_owner_id = result[0]
                    
                    # Get owner details
                    cursor.execute("""
                        SELECT first_name, last_name, email, contact_number 
                        FROM owners 
                        WHERE owner_id = ?
                    """, (self.current_owner_id,))
                    
                    owner_data = cursor.fetchone()
                    
                    if owner_data:
                        self.editfirst.setText(owner_data[0] or '')
                        self.editlast.setText(owner_data[1] or '')
                        self.editemail.setText(owner_data[2] or '')
                        self.editnum.setText(owner_data[3] or '')
                else:
                    self.owerrormes.setText('No owner found. Please register first.')
                    
            except sqlite3.Error as err:
                print(f"Error loading owner data: {err}")
                self.owerrormes.setText('Error loading owner data.')
            finally:
                if conn:
                    conn.close()
        else:
            self.owerrormes.setText('Database connection failed.')
    
    def loadpets(self):
        """Load pets for the current owner into the table."""
        if self.current_owner_id is None:
            return
            
        conn = get_db_connection()
        if conn:
            try:
                cursor = conn.cursor()
                
                # Get all pets for this owner with breed information
                cursor.execute("""
                    SELECT p.pet_id, p.name, p.age, p.sex, p.weight_kg, 
                           GROUP_CONCAT(b.breed_name, ', ') as breeds,
                           sc.size_name
                    FROM pets p
                    LEFT JOIN pet_breed_junction pbj ON p.pet_id = pbj.pet_id
                    LEFT JOIN breeds b ON pbj.breed_id = b.breed_id
                    LEFT JOIN size_category sc ON p.actual_size_id = sc.size_id
                    WHERE p.owner_id = ?
                    GROUP BY p.pet_id
                    ORDER BY p.pet_id
                """, (self.current_owner_id,))
                
                pets = cursor.fetchall()
                
                # Set up table
                self.petlist.setRowCount(len(pets))
                self.petlist.setColumnCount(7)
                self.petlist.setHorizontalHeaderLabels(['ID', 'Name', 'Age', 'Sex', 'Weight (kg)', 'Breed', 'Size'])
                
                # Populate table
                for row, pet in enumerate(pets):
                    for col, value in enumerate(pet):
                        item = QtWidgets.QTableWidgetItem(str(value) if value is not None else '')
                        self.petlist.setItem(row, col, item)
                
                # Resize columns to fit content
                self.petlist.resizeColumnsToContents()
                
            except sqlite3.Error as err:
                print(f"Error loading pets: {err}")
                self.editerrormess.setText('Error loading pets.')
            finally:
                if conn:
                    conn.close()
    
    def saveownerinfo(self):
        """Save the owner's information to the database."""
        if self.current_owner_id is None:
            self.owerrormes.setText('No owner selected.')
            return
        
        first_name = self.editfirst.text().strip()
        last_name = self.editlast.text().strip()
        email = self.editemail.text().strip()
        contact_number = self.editnum.text().strip()
        
        self.owerrormes.setText('')
        
        # Validate required fields
        if not first_name or not last_name:
            self.owerrormes.setText('First and Last name are required.')
            return
        
        conn = get_db_connection()
        if conn:
            try:
                cursor = conn.cursor()
                
                # Update owner information
                sql = """
                    UPDATE owners 
                    SET first_name = ?, last_name = ?, email = ?, contact_number = ?
                    WHERE owner_id = ?
                """
                cursor.execute(sql, (first_name, last_name, email, contact_number, self.current_owner_id))
                conn.commit()
                
                # Verify the update was successful
                cursor.execute("SELECT owner_id FROM owners WHERE owner_id = ? AND first_name = ? AND last_name = ?",
                             (self.current_owner_id, first_name, last_name))
                if cursor.fetchone():
                    print(f"Owner information successfully updated for ID: {self.current_owner_id}")
                    self.owerrormes.setText('Owner information saved successfully!')
                else:
                    raise sqlite3.Error("Update verification failed")
                    
            except sqlite3.Error as err:
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
        """Show a combo box to select a pet to edit."""
        if self.current_owner_id is None:
            self.editerrormess.setText('No owner found. Please register first.')
            return
        
        # Get list of pets for this owner
        conn = get_db_connection()
        if not conn:
            self.editerrormess.setText('Database connection failed.')
            return
        
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT pet_id, name 
                FROM pets 
                WHERE owner_id = ?
                ORDER BY pet_id
            """, (self.current_owner_id,))
            
            pets = cursor.fetchall()
            
            if not pets:
                self.editerrormess.setText('No pets found to edit.')
                conn.close()
                return
            
            # Create a dialog with combo box
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
                    # Navigate to edit pet screen
                    editpet = editpetscreen(selected_pet_id, self.current_owner_id)
                    widget.addWidget(editpet)
                    widget.setCurrentIndex(widget.currentIndex() + 1)
            
        except sqlite3.Error as err:
            print(f"Error loading pets for selection: {err}")
            self.editerrormess.setText('Error loading pets.')
        finally:
            if conn:
                conn.close()
    
    def deletepet(self):
        """Delete the selected pet from the database."""
        selected_row = self.petlist.currentRow()
        if selected_row < 0:
            self.editerrormess.setText('Please select a pet to delete.')
            return
        
        pet_id_item = self.petlist.item(selected_row, 0)
        if not pet_id_item:
            self.editerrormess.setText('Could not identify selected pet.')
            return
        
        pet_id = int(pet_id_item.text())
        pet_name = self.petlist.item(selected_row, 1).text() if self.petlist.item(selected_row, 1) else 'Unknown'
        
        # Confirm deletion (you could add a confirmation dialog here)
        conn = get_db_connection()
        if conn:
            try:
                cursor = conn.cursor()
                
                # Delete from pet_breed_junction first (foreign key constraint)
                cursor.execute("DELETE FROM pet_breed_junction WHERE pet_id = ?", (pet_id,))
                
                # Delete from pet_event_entry
                cursor.execute("DELETE FROM pet_event_entry WHERE pet_id = ?", (pet_id,))
                
                # Delete from awards
                cursor.execute("DELETE FROM awards WHERE pet_id = ?", (pet_id,))
                
                # Delete the pet
                cursor.execute("DELETE FROM pets WHERE pet_id = ?", (pet_id,))
                
                conn.commit()
                
                print(f"Pet {pet_name} (ID: {pet_id}) successfully deleted.")
                self.editerrormess.setText(f'Pet {pet_name} deleted successfully.')
                
                # Reload the pets table
                self.loadpets()
                
            except sqlite3.Error as err:
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
        
    def saveinf(self):
        """Save all information and navigate to success screen."""
        # Save owner info first
        self.saveownerinfo()
        
        # Check if save was successful (no error message means success)
        if not self.owerrormes.text() or 'successfully' in self.owerrormes.text():
            self.gotoinfoedited()
        else:
            # If there was an error, don't navigate away
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
        
        # Connect buttons
        self.petexitbutt.clicked.connect(self.gotoeditinf)
        self.peteditbutt.clicked.connect(self.savepetinfo)
        
        # Get error label
        self.petregiserr = self.findChild(QtWidgets.QLabel, 'petregiserr')
        
        # Load pet data
        self.loadpetdata()
        
    def loadpetdata(self):
        """Load the pet's current information into the form fields."""
        conn = get_db_connection()
        if conn:
            try:
                cursor = conn.cursor()
                
                # Get pet details
                cursor.execute("""
                    SELECT p.name, p.age, p.sex, p.weight_kg, p.actual_size_id, 
                           p.muzzle_required, p.notes, sc.size_name
                    FROM pets p
                    LEFT JOIN size_category sc ON p.actual_size_id = sc.size_id
                    WHERE p.pet_id = ?
                """, (self.pet_id,))
                
                pet_data = cursor.fetchone()
                
                if pet_data:
                    # Set pet information
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
                    
                    # Set muzzle required
                    if pet_data[5] == 1:
                        self.muzzleyes.setChecked(True)
                    else:
                        self.muzzleno.setChecked(True)
                    
                    self.petnotes.setPlainText(pet_data[6] or '')
                    
                    # Get breed
                    cursor.execute("""
                        SELECT b.breed_name 
                        FROM breeds b
                        JOIN pet_breed_junction pbj ON b.breed_id = pbj.breed_id
                        WHERE pbj.pet_id = ?
                        LIMIT 1
                    """, (self.pet_id,))
                    
                    breed_result = cursor.fetchone()
                    if breed_result:
                        self.petbreed.setText(breed_result[0] or '')
                    
                    # Get owner name for display
                    cursor.execute("""
                        SELECT first_name, last_name 
                        FROM owners 
                        WHERE owner_id = ?
                    """, (self.owner_id,))
                    
                    owner_result = cursor.fetchone()
                    if owner_result:
                        owner_name = f"{owner_result[0]} {owner_result[1]}"
                        self.owerusername.setText(owner_name)
                
            except sqlite3.Error as err:
                print(f"Error loading pet data: {err}")
                self.petregiserr.setText('Error loading pet data.')
            finally:
                if conn:
                    conn.close()
        else:
            self.petregiserr.setText('Database connection failed.')
    
    def savepetinfo(self):
        """Save the updated pet information to the database."""
        petname = self.petname.text().strip()
        petage = self.petage.value()
        petsex = self.petsex.currentText().strip()
        petweight = self.petweight.value()
        petsize_name = self.petsize.currentText().strip()
        petbreed = self.petbreed.text().strip()
        petnotes = self.petnotes.toPlainText().strip()
        
        self.petregiserr.setText('')
        
        # Validate required fields
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
                
                # Update pet information
                sql_pet = """
                    UPDATE pets 
                    SET name = ?, actual_size_id = ?, age = ?, sex = ?, 
                        weight_kg = ?, muzzle_required = ?, notes = ?
                    WHERE pet_id = ?
                """
                cursor.execute(sql_pet, (
                    petname, actual_size_id, petage, petsex, 
                    petweight, muzzle_required, petnotes, self.pet_id
                ))
                
                # Handle breed update
                sql_breed_lookup = "SELECT breed_id FROM breeds WHERE breed_name = ?"
                cursor.execute(sql_breed_lookup, (petbreed,))
                breed_result = cursor.fetchone()
                
                if breed_result:
                    breed_id = breed_result[0]
                else:
                    # Create new breed if it doesn't exist
                    cursor.execute("SELECT MAX(breed_id) FROM breeds")
                    max_breed_id = cursor.fetchone()[0]
                    new_breed_id = max(16, (max_breed_id if max_breed_id is not None else 0) + 1)
                    
                    sql_insert_breed = "INSERT INTO breeds (breed_id, breed_name, size_id) VALUES (?, ?, ?)"
                    cursor.execute(sql_insert_breed, (new_breed_id, petbreed, 3))
                    breed_id = new_breed_id
                
                # Update pet_breed_junction (delete old, insert new)
                cursor.execute("DELETE FROM pet_breed_junction WHERE pet_id = ?", (self.pet_id,))
                cursor.execute("INSERT INTO pet_breed_junction (pet_id, breed_id) VALUES (?, ?)", 
                             (self.pet_id, breed_id))
                
                conn.commit()
                
                # Verify the update was successful
                cursor.execute("SELECT pet_id FROM pets WHERE pet_id = ? AND name = ?",
                             (self.pet_id, petname))
                if cursor.fetchone():
                    print(f"Pet information successfully updated for ID: {self.pet_id}")
                    self.petregiserr.setText('Pet information saved successfully!')
                    # Return to editinf screen after a short delay or immediately
                    self.gotoeditinf()
                else:
                    raise sqlite3.Error("Update verification failed")
                
            except sqlite3.Error as err:
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

# Main Application Entry Point
if __name__ == '__main__':
    # 1. Ensure the SQLite database and all 10 tables with data are ready
    setup_database() 
    
    # 2. Run the PyQt application
    app = QApplication(sys.argv)
    registerscreen = RegisterScreen()
    widget = QStackedWidget()

    widget.addWidget(registerscreen)
    widget.setFixedHeight(526)
    widget.setFixedWidth(808)
    widget.show()

    try:
        sys.exit(app.exec())
    except Exception as e:
        print(f'Exiting with error: {e}')