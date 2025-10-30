-- 4.1 Register participant and their pet for an event will involve the following data & operations:
-- a. Reading the records of the Pet Owner and Pet Record to check if they are valid.
-- Check if the pet owner exists and has a valid record
SELECT owner_id, first_name, last_name, email, contact_number
FROM owners
WHERE owner_id = [owner_id];
-- Check if the pet exists and has a valid record
SELECT pet_id, name, actual_size_id, weight_kg, age, sex
FROM pets
WHERE pet_id = [pet_id] AND owner_id = [owner_id];

-- b. Reading the Events record to check for available spots in the selected event.
SELECT event_id, name, date, max_participants, COUNT(pe.entry_id) AS current_participants
FROM events e
LEFT JOIN pet_event_entry pe ON e.event_id = pe.event_id
WHERE e.event_id = [event_id]
GROUP BY e.event_id
HAVING COUNT(pe.entry_id) < e.max_participants;


-- c. Recording the new registration in the Participants-Events Junction table with the participantID, eventID, and registrationDate.
INSERT INTO event_registration (owner_id, event_id, registration_date, total_amount_paid, payment_date, payment_time, status)
VALUES ([owner_id], [event_id], [registration_date], [total_amount_paid], [payment_date], [payment_time], 'Registered');

-- d. Recording the pet's entry in the Pets-Events Junction table with the petID, eventID.
INSERT INTO pet_event_entry (registration_id, pet_id, event_id, attendance_status)
VALUES ([registration_id], [pet_id], [event_id], 'Registered');

-- e. Updating the Events record to increase the participant count for that specific event
UPDATE events
SET max_participants = max_participants - 1
WHERE event_id = [event_id];