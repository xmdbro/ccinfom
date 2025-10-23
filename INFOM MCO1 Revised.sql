CREATE SCHEMA pet_show;

USE pet_show;


CREATE TABLE owners (
    owner_id INT NOT NULL,
    first_name VARCHAR(20),
    last_name VARCHAR(20),
    email VARCHAR(50),
    contact_number INT,
    CONSTRAINT primary_owner_key PRIMARY KEY(owner_id)
);

CREATE TABLE size_category (
    size_id INT NOT NULL,
    size_name VARCHAR(10),
    CONSTRAINT primary_siz_cat_key PRIMARY KEY (size_id)
);

CREATE TABLE breeds (
    breed_id INT NOT NULL,
    breed_name VARCHAR(50),
    size_id INT,
    CONSTRAINT primary_breed_key PRIMARY KEY (breed_id),
    CONSTRAINT fk_breed_size_key FOREIGN KEY(size_id) REFERENCES size_category(size_id)
);

CREATE TABLE events (
    event_id INT NOT NULL,
    name VARCHAR(20) NOT NULL,
    date DATE,
    time TIME,
    location VARCHAR(100) NOT NULL,
    max_participants INT,
    registration_deadline DATE,
    type VARCHAR(100),
    distance_km DECIMAL(4, 2),
    time_limit INT,
    status TINYINT(1),
    base_registration_fee DECIMAL(6,2),
    extra_pet_discount DECIMAL(6,2),
    CONSTRAINT primary_event_key PRIMARY KEY(event_id)
);

CREATE TABLE pets (
    pet_id INT NOT NULL,
    owner_id INT NOT NULL,
    name VARCHAR(20) NOT NULL,
    actual_size_id INT,
    age INT,
    sex VARCHAR(4),
    weight_kg DECIMAL(6,2),
    muzzle_required TINYINT(1),
    notes TEXT,
    CONSTRAINT primary_pet_key PRIMARY KEY(pet_id),
    CONSTRAINT fk_pet_owner_key FOREIGN KEY(owner_id) REFERENCES owners(owner_id),
    CONSTRAINT fk_pet_size_key FOREIGN KEY (actual_size_id) REFERENCES size_category(size_id)
);

CREATE TABLE awards (
    award_id INT NOT NULL,
    pet_id INT NOT NULL,
    type VARCHAR(100),
    description TEXT,
    date DATE,
    event_id INT NOT NULL,
    CONSTRAINT primary_awrd_key PRIMARY KEY (award_id),
    CONSTRAINT fk_awrd_pet_key FOREIGN KEY (pet_id) REFERENCES pets(pet_id),
    CONSTRAINT fk_awrd_event_key FOREIGN KEY(event_id) REFERENCES events(event_id)
);


CREATE TABLE pet_breed_junction (
    pet_id INT NOT NULL,
    breed_id INT NOT NULL,
    CONSTRAINT primary_pet_breed_key PRIMARY KEY (pet_id, breed_id), 
    CONSTRAINT fk_pbj_pet_key FOREIGN KEY (pet_id) REFERENCES pets(pet_id),
    CONSTRAINT fk_pbj_breed_key FOREIGN KEY (breed_id) REFERENCES breeds(breed_id)
);
 
CREATE TABLE event_registration (
    registration_id INT NOT NULL,
    owner_id INT NOT NULL,
    event_id INT NOT NULL,
    registration_date DATE,
    total_amount_paid DECIMAL(6,2),
    payment_date DATE, 
    payment_time TIME, 
    status VARCHAR(20), 
    transfer_destination INT,
    cancellation_date DATE, 
    
    CONSTRAINT primary_reg_key PRIMARY KEY (registration_id),
    CONSTRAINT fk_reg_owner_key FOREIGN KEY (owner_id) REFERENCES owners(owner_id),
    CONSTRAINT fk_reg_event_key FOREIGN KEY (event_id) REFERENCES events(event_id),
    CONSTRAINT fk_reg_transfer_key FOREIGN KEY (transfer_destination) REFERENCES event_registration(registration_id)
);

CREATE TABLE pet_event_entry (
    entry_id INT NOT NULL,
    registration_id INT NOT NULL,
    pet_id INT NOT NULL,
    event_id INT NOT NULL,
    attendance_status VARCHAR(10),
    pet_result DECIMAL(6,2),
    CONSTRAINT primary_entry_key PRIMARY KEY (entry_id),
    CONSTRAINT fk_entry_reg_key FOREIGN KEY (registration_id) REFERENCES event_registration(registration_id),
    CONSTRAINT fk_entry_pet_key FOREIGN KEY (pet_id) REFERENCES pets(pet_id),
    CONSTRAINT fk_entry_event_key FOREIGN KEY (event_id) REFERENCES events(event_id),
    CONSTRAINT unique_pet_event UNIQUE (pet_id, event_id)
);

CREATE TABLE participation_log (
    log_id INT NOT NULL,
    registration_id INT NOT NULL,
    action_type VARCHAR(20),
    action_date DATE,
    action_time TIME,
    original_event_id INT,
    new_event_id INT,
    reason TEXT,
    CONSTRAINT primary_log_key PRIMARY KEY (log_id),
    CONSTRAINT fk_log_reg_key FOREIGN KEY (registration_id) REFERENCES event_registration(registration_id),
    CONSTRAINT fk_log_orig_event_key FOREIGN KEY (original_event_id) REFERENCES events(event_id),
    CONSTRAINT fk_log_new_event_key FOREIGN KEY (new_event_id) REFERENCES events(event_id)
);