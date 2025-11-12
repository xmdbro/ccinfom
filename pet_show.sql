DROP SCHEMA IF EXISTS pet_show;
CREATE SCHEMA pet_show;
USE pet_show;

CREATE TABLE size_category (
    size_id INT NOT NULL PRIMARY KEY,
    size_name VARCHAR(20) NOT NULL
);

INSERT INTO size_category (size_id, size_name) VALUES
(1, 'Small'),
(2, 'Medium'),
(3, 'Large');

CREATE TABLE owners (
    owner_id INT NOT NULL PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100),
    contact_number VARCHAR(30),
    CONSTRAINT check_contact_info CHECK (email IS NOT NULL OR contact_number IS NOT NULL)
);

INSERT INTO owners (owner_id, first_name, last_name, email, contact_number) VALUES
(1, 'Miguel', 'Santos', 'miguel.santos@example.com', '09171234567'),
(2, 'Anna', 'Reyes', 'anna.reyes@example.com', '09181234567'),
(3, 'Diego', 'Velasco', 'diego.velasco@example.com', '09191234567'),
(4, 'Hannah', 'Lopez', 'h.lopez@example.com', '09201234567'),
(5, 'Rafael', 'DelaCruz', 'rafael.delacruz@example.com', '09211234567'),
(6, 'Sofia', 'Garcia', 'sofia.garcia@example.com', '09221234567'),
(7, 'Ethan', 'Tan', 'ethan.tan@example.com', '09231234567'),
(8, 'Lara', 'Gomez', 'lara.gomez@example.com', '09241234567'),
(9, 'Carlos', 'Mendoza', 'c.mendoza@example.com', '09251234567'),
(10, 'Isabel', 'Paredes', 'isabel.paredes@example.com', '09261234567'),
(11, 'Mark', 'Cruz', 'mark.cruz@example.com', '09271234567'),
(12, 'Jocelyn', 'Lo', 'jocelyn.lo@example.com', '09281234567'),
(13, 'Noah', 'Bautista', 'noah.bautista@example.com', '09291234567'),
(14, 'Maya', 'Ortiz', 'maya.ortiz@example.com', '09301234567'),
(15, 'Paul', 'Serrano', 'paul.serrano@example.com', '09311234567');

CREATE TABLE breeds (
    breed_id INT NOT NULL PRIMARY KEY,
    breed_name VARCHAR(100) NOT NULL,
    size_id INT NOT NULL,
    CONSTRAINT fk_breed_size FOREIGN KEY (size_id) REFERENCES size_category(size_id)
);

INSERT INTO breeds (breed_id, breed_name, size_id) VALUES
(1, 'Chihuahua', 1),
(2, 'Pomeranian', 1),
(3, 'Dachshund', 1),
(4, 'Beagle', 2),
(5, 'Bulldog', 2),
(6, 'Labrador Retriever', 3),
(7, 'Golden Retriever', 3),
(8, 'Border Collie', 2),
(9, 'German Shepherd', 3),
(10, 'Great Dane', 3),
(11, 'Jack Russell Terrier', 1),
(12, 'French Bulldog', 2),
(13, 'Shih Tzu', 1),
(14, 'Poodle (Miniature)', 1),
(15, 'Australian Shepherd', 2);

CREATE TABLE events (
    event_id INT NOT NULL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    date DATE NOT NULL,
    time TIME NOT NULL,
    location VARCHAR(150) NOT NULL,
    max_participants INT NOT NULL,
    registration_deadline DATE NOT NULL,
    type VARCHAR(100) NOT NULL,
    distance_km DECIMAL(5,2),
    time_limit INT,
    status TINYINT(1) NOT NULL, -- 1 = open, 0 = closed
    base_registration_fee DECIMAL(8,2) NOT NULL,
    extra_pet_discount DECIMAL(8,2) NOT NULL,
    min_weight DECIMAL(6,2),
    max_weight DECIMAL(6,2),
    min_size_id INT,
    max_size_id INT,
    CONSTRAINT fk_event_min_size FOREIGN KEY (min_size_id) REFERENCES size_category(size_id),
    CONSTRAINT fk_event_max_size FOREIGN KEY (max_size_id) REFERENCES size_category(size_id)
);

INSERT INTO events (event_id, name, date, time, location, max_participants, registration_deadline, type, distance_km, time_limit, status, base_registration_fee, extra_pet_discount, min_weight, max_weight, min_size_id, max_size_id) VALUES
(1, 'Dog Fun Run - Event Starter', '2025-11-21', '07:00:00', 'Greenfield Park, Manila', 150, '2025-11-10', 'Fun Run', 3.00, 60, 1, 300.00, 50.00, NULL, NULL, 1, 3),
(2, 'Dog Agility Course - Tunnels & Jumps', '2025-11-21', '09:00:00', 'Greenfield Park, Manila', 60, '2025-11-10', 'Agility', NULL, 30, 1, 400.00, 75.00, NULL, NULL, 1, 3),
(3, 'Obedience Challenge', '2025-11-21', '11:00:00', 'Greenfield Park, Manila', 40, '2025-11-10', 'Obedience', NULL, 20, 1, 250.00, 40.00, NULL, NULL, 1, 3),
(4, 'Best Costume Contest', '2025-11-21', '14:00:00', 'Greenfield Park, Manila', 100, '2025-11-12', 'Fashion', NULL, NULL, 1, 200.00, 30.00, NULL, NULL, 1, 3),
(5, 'Dog & Owner Look-Alike', '2025-11-22', '08:00:00', 'Sunset Boulevard', 50, '2025-11-13', 'Fun', NULL, NULL, 1, 150.00, 20.00, NULL, NULL, 1, 3),
(6, 'Fastest Fetch Competition', '2025-11-22', '10:00:00', 'Sunset Boulevard', 80, '2025-11-13', 'Competition', NULL, 10, 1, 180.00, 25.00, NULL, NULL, 1, 3),
(7, 'Dog Talent Show', '2025-11-22', '12:00:00', 'Sunset Boulevard', 60, '2025-11-13', 'Showcase', NULL, NULL, 1, 220.00, 30.00, NULL, NULL, 1, 3),
(8, 'Strongest Dog (Tug-of-War) - Weight Classes', '2025-11-22', '15:00:00', 'Sunset Boulevard', 40, '2025-11-15', 'Strength', NULL, NULL, 1, 300.00, 50.00, 5.00, 80.00, 2, 3),
(9, 'Dog Parade / Walkathon', '2025-11-23', '06:30:00', 'Baywalk Promenade', 200, '2025-11-15', 'Parade', 2.00, NULL, 1, 120.00, 20.00, NULL, NULL, 1, 3),
(10, 'Canine Frisbee Challenge', '2025-11-23', '09:00:00', 'Baywalk Promenade', 60, '2025-11-16', 'Frisbee', NULL, 30, 1, 260.00, 40.00, NULL, NULL, 1, 3),
(11, 'Photo Booth & Dog Modeling', '2025-11-23', '13:00:00', 'Baywalk Promenade', 120, '2025-11-16', 'Modeling', NULL, NULL, 1, 140.00, 20.00, NULL, NULL, 1, 3),
(12, 'Awarding Ceremony - Closing Program', '2025-11-23', '17:00:00', 'Baywalk Main Stage', 500, '2025-11-18', 'Ceremony', NULL, NULL, 1, 0.00, 0.00, NULL, NULL, 1, 3);

CREATE TABLE pets (
    pet_id INT NOT NULL PRIMARY KEY,
    owner_id INT NOT NULL,
    name VARCHAR(50) NOT NULL,
    actual_size_id INT NOT NULL,
    age INT NOT NULL,
    sex VARCHAR(6) NOT NULL,
    weight_kg DECIMAL(6,2) NOT NULL,
    muzzle_required TINYINT(1) NOT NULL,
    notes TEXT,
    CONSTRAINT fk_pet_owner FOREIGN KEY (owner_id) REFERENCES owners(owner_id),
    CONSTRAINT fk_pet_size FOREIGN KEY (actual_size_id) REFERENCES size_category(size_id)
);

INSERT INTO pets (pet_id, owner_id, name, actual_size_id, age, sex, weight_kg, muzzle_required, notes) VALUES
(1, 1, 'Rico', 3, 4, 'Male', 28.50, 0, 'Loves fetch; friendly with kids'),
(2, 1, 'Pip', 1, 2, 'Female', 4.10, 0, 'Tiny, energetic'),
(3, 2, 'Luna', 1, 2, 'Female', 4.20, 0, 'Very photogenic; short-haired'),
(4, 2, 'Mochi', 1, 1, 'Male', 3.60, 0, 'Affectionate lap dog'),
(5, 3, 'Max', 3, 6, 'Male', 30.00, 0, 'Good at recall'),
(6, 4, 'Bella', 2, 3, 'Female', 12.30, 0, 'Agile and fast'),
(7, 5, 'Bruno', 3, 5, 'Male', 36.00, 1, 'Tug-of-war champion'),
(8, 5, 'Fiona', 2, 2, 'Female', 14.50, 0, 'Friendly and playful'),
(9, 6, 'Milo', 1, 1, 'Male', 3.50, 0, 'Tiny and energetic'),
(10, 7, 'Nala', 3, 4, 'Female', 29.00, 0, 'Shepherd mix; high stamina'),
(11, 7, 'Echo', 2, 3, 'Male', 18.00, 0, 'Smart and attentive'),
(12, 8, 'Coco', 1, 7, 'Female', 5.10, 0, 'Great in modeling and photo booths'),
(13, 9, 'Thor', 3, 3, 'Male', 40.00, 1, 'Large breed; strong pull'),
(14, 9, 'Zeus', 3, 2, 'Male', 34.00, 0, 'Playful but strong'),
(15, 10, 'Daisy', 2, 2, 'Female', 14.00, 0, 'Excellent in agility, loves tunnels'),
(16, 11, 'Ollie', 1, 5, 'Male', 6.20, 0, 'Fast fetcher'),
(17, 11, 'Nibbles', 1, 3, 'Female', 4.90, 0, 'Small and spunky'),
(18, 12, 'Gigi', 2, 4, 'Female', 20.00, 0, 'Performs tricks well'),
(19, 13, 'Poppy', 1, 3, 'Female', 4.80, 0, 'Fashion-forward for costumes'),
(20, 13, 'Sprout', 1, 1, 'Male', 3.30, 0, 'Tiny pup'),
(21, 14, 'Rex', 3, 6, 'Male', 38.50, 1, 'Strong tug-of-war competitor'),
(22, 15, 'Buddy', 3, 2, 'Male', 32.00, 0, 'Friendly parade walker'),
(23, 15, 'Sunny', 2, 4, 'Female', 16.00, 0, 'Good with crowds'),
(24, 4, 'Biscuit', 1, 2, 'Female', 5.00, 0, 'Cute costume favorite'),
(25, 6, 'Gizmo', 1, 2, 'Male', 4.40, 0, 'Quick and curious');

CREATE TABLE pet_breed_junction (
    pet_id INT NOT NULL,
    breed_id INT NOT NULL,
    CONSTRAINT pk_pet_breed PRIMARY KEY (pet_id, breed_id),
    CONSTRAINT fk_pbj_pet FOREIGN KEY (pet_id) REFERENCES pets(pet_id),
    CONSTRAINT fk_pbj_breed FOREIGN KEY (breed_id) REFERENCES breeds(breed_id)
);

INSERT INTO pet_breed_junction (pet_id, breed_id) VALUES
(1, 6),  -- Rico: Labrador
(2, 14), -- Pip: Poodle (Miniature)
(3, 14), -- Luna: Poodle (Miniature)
(4, 1),  -- Mochi: Chihuahua
(5, 6),  -- Max: Labrador
(6, 4),  -- Bella: Beagle
(7, 9),  -- Bruno: German Shepherd
(8, 5),  -- Fiona: Bulldog (medium)
(9, 1),  -- Milo: Chihuahua
(10, 9), -- Nala: German Shepherd / mix
(11, 8), -- Echo: Border Collie
(12, 2), -- Coco: Pomeranian
(13, 10),-- Thor: Great Dane
(14, 6), -- Zeus: Labrador
(15, 8), -- Daisy: Border Collie
(16, 11),-- Ollie: Jack Russell Terrier
(17, 13),-- Nibbles: Shih Tzu
(18, 12),-- Gigi: French Bulldog
(19, 13),-- Poppy: Shih Tzu
(20, 1), -- Sprout: Chihuahua
(21, 5), -- Rex: Bulldog
(22, 7), -- Buddy: Golden Retriever
(23, 4), -- Sunny: Beagle
(24, 2), -- Biscuit: Pomeranian
(25, 3); -- Gizmo: Dachshund

CREATE TABLE event_registration (
    registration_id INT NOT NULL PRIMARY KEY,
    owner_id INT NOT NULL,
    event_id INT NOT NULL,
    registration_date DATE NOT NULL,
    total_amount_paid DECIMAL(8,2) NOT NULL,
    payment_date DATE NOT NULL,
    payment_time TIME NOT NULL,
    status VARCHAR(20) NOT NULL,
    transfer_destination INT NULL,
    cancellation_date DATE NULL,
    CONSTRAINT fk_reg_owner FOREIGN KEY (owner_id) REFERENCES owners(owner_id),
    CONSTRAINT fk_reg_event FOREIGN KEY (event_id) REFERENCES events(event_id),
    CONSTRAINT fk_reg_transfer FOREIGN KEY (transfer_destination) REFERENCES event_registration(registration_id)
);

INSERT INTO event_registration (registration_id, owner_id, event_id, registration_date, total_amount_paid, payment_date, payment_time, status, transfer_destination, cancellation_date) VALUES
(1, 1, 1, '2025-11-05', 300.00, '2025-11-05', '09:30:00', 'Paid', NULL, NULL),
(2, 2, 4, '2025-11-06', 200.00, '2025-11-06', '10:10:00', 'Paid', NULL, NULL),
(3, 3, 2, '2025-11-07', 400.00, '2025-11-07', '11:20:00', 'Paid', NULL, NULL),
(4, 4, 10, '2025-11-07', 260.00, '2025-11-07', '12:00:00', 'Paid', NULL, NULL),
(5, 5, 8, '2025-11-08', 300.00, '2025-11-08', '09:00:00', 'Paid', NULL, NULL),
(6, 6, 9, '2025-11-09', 120.00, '2025-11-09', '08:30:00', 'Paid', NULL, NULL),
(7, 7, 1, '2025-11-09', 300.00, '2025-11-09', '09:15:00', 'Paid', NULL, NULL),
(8, 8, 11, '2025-11-10', 140.00, '2025-11-10', '10:00:00', 'Paid', NULL, NULL),
(9, 9, 8, '2025-11-10', 300.00, '2025-11-10', '11:45:00', 'Paid', NULL, NULL),
(10, 10, 2, '2025-11-11', 400.00, '2025-11-11', '09:50:00', 'Paid', NULL, NULL),
(11, 11, 6, '2025-11-11', 180.00, '2025-11-11', '10:05:00', 'Paid', NULL, NULL),
(12, 12, 7, '2025-11-12', 220.00, '2025-11-12', '14:30:00', 'Paid', NULL, NULL),
(13, 13, 4, '2025-11-12', 200.00, '2025-11-12', '15:00:00', 'Paid', NULL, NULL),
(14, 14, 8, '2025-11-13', 300.00, '2025-11-13', '16:20:00', 'Paid', NULL, NULL),
(15, 15, 9, '2025-11-13', 120.00, '2025-11-13', '17:05:00', 'Paid', NULL, NULL),
(16, 1, 11, '2025-11-14', 140.00, '2025-11-14', '10:00:00', 'Paid', NULL, NULL),
(17, 4, 4, '2025-11-14', 200.00, '2025-11-14', '11:00:00', 'Paid', NULL, NULL),
(18, 5, 2, '2025-11-14', 400.00, '2025-11-14', '11:30:00', 'Paid', NULL, NULL);

CREATE TABLE pet_event_entry (
    entry_id INT NOT NULL PRIMARY KEY,
    registration_id INT NOT NULL,
    pet_id INT NOT NULL,
    event_id INT NOT NULL,
    attendance_status VARCHAR(20) NOT NULL,
    pet_result DECIMAL(8,2) NULL,
    CONSTRAINT fk_entry_reg FOREIGN KEY (registration_id) REFERENCES event_registration(registration_id),
    CONSTRAINT fk_entry_pet FOREIGN KEY (pet_id) REFERENCES pets(pet_id),
    CONSTRAINT fk_entry_event FOREIGN KEY (event_id) REFERENCES events(event_id),
    CONSTRAINT unique_pet_event UNIQUE (pet_id, event_id)
);

INSERT INTO pet_event_entry (entry_id, registration_id, pet_id, event_id, attendance_status, pet_result) VALUES
(1, 1, 1, 1, 'Present', 8.7),     -- Rico in Dog Fun Run
(2, 2, 3, 4, 'Present', 9.3),     -- Luna in Costume Contest
(3, 3, 5, 2, 'Present', 9.8),     -- Max in Agility
(4, 4, 6, 10, 'Present', 8.9),    -- Bella in Frisbee
(5, 5, 7, 8, 'Present', 9.4),     -- Bruno in Tug-of-War
(6, 6, 9, 9, 'Present', 8.2),     -- Milo in Parade
(7, 7, 10, 1, 'Present', 8.6),    -- Nala in Dog Fun Run
(8, 8, 12, 11, 'Present', 9.7),   -- Coco in Photo Booth
(9, 9, 13, 8, 'No Show', 0.0),    -- Thor registered for Tug but no-show
(10, 10, 15, 2, 'Present', 9.9),  -- Daisy in Agility
(11, 11, 16, 6, 'Present', 9.5),  -- Ollie in Fastest Fetch
(12, 12, 18, 7, 'Present', 9.1),  -- Gigi in Talent Show
(13, 13, 19, 4, 'Present', 8.8),  -- Poppy in Costume Contest
(14, 14, 21, 8, 'Present', 9.6),  -- Rex in Tug-of-War
(15, 15, 22, 9, 'Present', 8.4),  -- Buddy in Parade
(16, 16, 2, 11, 'Present', 9.2),  -- Pip in Photo Booth
(17, 17, 24, 4, 'Present', 8.9),  -- Biscuit in Costume Contest
(18, 18, 5, 3, 'Present', 9.0),   -- Max now in Obedience Challenge
(19, 3, 8, 2, 'Present', 8.7),    -- Fiona in Agility
(20, 5, 23, 9, 'Present', 8.5);   -- Sunny in Parade
-- just to note, numbers here are just averaged from 6 to 10, assuming that each event only has a rating of highest average score (1-10)

CREATE TABLE awards (
    award_id INT NOT NULL PRIMARY KEY,
    pet_id INT NOT NULL,
    type VARCHAR(100) NOT NULL,
    description TEXT,
    date DATE NOT NULL,
    event_id INT NOT NULL,
    CONSTRAINT fk_award_pet FOREIGN KEY (pet_id) REFERENCES pets(pet_id),
    CONSTRAINT fk_award_event FOREIGN KEY (event_id) REFERENCES events(event_id)
);

INSERT INTO awards (award_id, pet_id, type, description, date, event_id) VALUES
(1, 3, 'Best Costume - 1st Place', 'Pirate-themed costume, high creativity', '2025-11-21', 4),
(2, 19, 'Best Costume - 2nd Place', 'Colorful tutu and hat', '2025-11-21', 4),
(3, 5, 'Agility - Fastest Run', 'Completed course fastest in novice division', '2025-11-21', 2),
(4, 15, 'Frisbee - Best Catch', 'Long-distance catch accuracy', '2025-11-23', 10),
(5, 1, 'Fun Run - Top Veteran', 'Top among 3-5 year old category', '2025-11-21', 1),
(6, 16, 'Fastest Fetch - Winner', 'Fastest retrieve time', '2025-11-22', 6),
(7, 18, 'Best Talent', 'Multiple tricks performed with style', '2025-11-22', 7),
(8, 7, 'Strongest Dog - Runner Up', 'Excellent tug strength in heavy weight class', '2025-11-22', 8),
(9, 22, 'Parade - Most Cheerful', 'Engaged crowd with playful antics', '2025-11-23', 9),
(10, 12, 'Photo Booth - Most Photogenic', 'Great poses and expressiveness', '2025-11-23', 11),
(11, 10, 'Fun Run - Most Spirited', 'High energy throughout', '2025-11-21', 1),
(12, 21, 'Strongest Dog - Champion', 'Champion of tug-of-war heavy class', '2025-11-22', 8);

CREATE TABLE participation_log (
    log_id INT NOT NULL PRIMARY KEY,
    registration_id INT NOT NULL,
    action_type VARCHAR(50) NOT NULL,
    action_date DATE NOT NULL,
    action_time TIME NOT NULL,
    original_event_id INT NOT NULL,
    new_event_id INT NULL,
    reason TEXT,
    refund_amount DECIMAL(8,2),
    top_up_amount DECIMAL(8,2),
    CONSTRAINT fk_log_reg FOREIGN KEY (registration_id) REFERENCES event_registration(registration_id),
    CONSTRAINT fk_log_orig_event FOREIGN KEY (original_event_id) REFERENCES events(event_id),
    CONSTRAINT fk_log_new_event FOREIGN KEY (new_event_id) REFERENCES events(event_id)
);

INSERT INTO participation_log (log_id, registration_id, action_type, action_date, action_time, original_event_id, new_event_id, reason, refund_amount, top_up_amount) VALUES
(1, 1, 'Modified', '2025-11-06', '09:00:00', 1, NULL, 'Updated emergency contact', 0.00, 0.00),
(2, 2, 'Transferred', '2025-11-09', '10:00:00', 4, 11, 'Owner requested transfer to Photo Booth', 0.00, 0.00),
(3, 3, 'Paid', '2025-11-07', '11:20:00', 2, NULL, 'Full payment received', 0.00, 0.00),
(4, 4, 'Cancelled', '2025-11-10', '12:30:00', 10, NULL, 'Owner withdrew due to travel', 260.00, 0.00),
(5, 5, 'Paid', '2025-11-08', '09:00:00', 8, NULL, 'Paid and confirmed', 0.00, 0.00),
(6, 6, 'Paid', '2025-11-09', '08:30:00', 9, NULL, 'Paid and confirmed', 0.00, 0.00),
(7, 7, 'Modified', '2025-11-09', '09:20:00', 1, NULL, 'Added another pet later', 0.00, 0.00),
(8, 8, 'Paid', '2025-11-10', '10:05:00', 11, NULL, 'Payment done at cashier', 0.00, 0.00),
(9, 9, 'No Show Logged', '2025-11-22', '16:00:00', 8, NULL, 'Dog did not attend tug-of-war', 0.00, 0.00),
(10, 10, 'Transfer Requested', '2025-11-12', '09:55:00', 2, NULL, 'Owner asked to move to mini agility (pending)', 0.00, 0.00),
(11, 11, 'Paid', '2025-11-11', '10:05:00', 6, NULL, '', 0.00, 0.00),
(12, 12, 'Paid', '2025-11-12', '14:30:00', 7, NULL, '', 0.00, 0.00),
(13, 13, 'Transferred', '2025-11-13', '15:30:00', 4, 2, 'Switched events to agility', 0.00, 200.00),
(14, 14, 'Paid', '2025-11-13', '16:20:00', 8, NULL, '', 0.00, 0.00),
(15, 15, 'Paid', '2025-11-13', '17:05:00', 9, NULL, '', 0.00, 0.00);