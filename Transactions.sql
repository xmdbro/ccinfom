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

-- 4.2. Assign awards to pets after each event will involve the following data & operations:
START TRANSACTION;

-- a. Reading the records of the Pet Record and Events to verify the details.
SELECT p.pet_id, p.name AS pet_name, e.event_id, e.name AS event_name, e.date AS event_date
FROM pets p
JOIN pet_event_entry pee ON p.pet_id = pee.pet_id
JOIN events e ON pee.event_id = e.event_id
WHERE e.event_id = [event_id]
  AND pee.attendance_status = 'Present';

-- b. Reading the results of the event to determine the award recipients.
SELECT pee.pet_id, p.name AS pet_name, pee.pet_result
FROM pet_event_entry pee
JOIN pets p ON pee.pet_id = p.pet_id
WHERE pee.event_id = [event_id]
ORDER BY pee.pet_result DESC -- basically highest scorers(?)
LIMIT [num_winners] -- to get top x or best in x

-- c. Recording a new entry in the Awards and titles table with the awardID, petID, description, date, and eventID.
INSERT INTO awards (awardID, petID, description, date, eventID)
VALUES ([award_id], [petID], [description], CURDATE(), [eventID])

-- OPTIONAL: since there is no log for pets who have received awards, update the notes of the pets(?)
UPDATE pets
SET notes = CONCAT(
  IFNULL(notes, ''),
  'Awarded: ', [award_type],
  ' - ', [description],
  ' (Event: ', [event_name],
  ', Date:', CURDATE(),
  ')'
)
WHERE pet_id = [pet_id];

COMMIT;

-- 4.4. Tracking participant and/or pet withdrawal in an event will involve the following data & operations:
START TRANSACTION;

-- a. Reading the records of the pet_event_entry table to identify the entry of the pet withdrawing from an event.
SELECT entry_id, registration_id
FROM pet_event_entry
WHERE pet_id = [pet_id] AND event_id = [event_id];

-- b. Updating the pet_event_entry record to mark the status as "Withdrawn."
UPDATE pet_event_entry
SET attendance_status = 'Withdrawn'
WHERE entry_id = [entry_id];

-- c. Updating the associated event_registration record to set "Withdrawn" status and cancellation date if there are no other active pets.
UPDATE event_registration
SET status = 'Withdrawn', cancellation_date = CURDATE()
WHERE registration_id = [registration_id] AND 0 = (SELECT COUNT(entry_id)
                                        		       FROM pet_event_entry
                                        		       WHERE registration_id = [registration_id] AND attendance_status NOT IN ('Withdrawn', 'Absent'));

-- d. Recording the withdrawal activity in participation_log table.
INSERT INTO participation_log (registration_id, action_type, action_date, action_time,  original_event_id, reason, refund_amount)
VALUES ([registration_id],'WITHDRAWAL', CURDATE(), CURTIME(), [event_id], [reason], [refund_amount]);

COMMIT;

-- 4.5. Tracking pet attendance in an event will involve the following data & operations:
-- a. Reading the records of the pet_event_entry table to get the list of an event's registered pets whose status is yet to be updated.
SELECT pee.entry_id, pee.pet_id, p.name pet_name, pee.attendance_status current_status
FROM pet_event_entry pee
JOIN pets p ON pee.pet_id = p.pet_id
WHERE pee.event_id = [event_id] AND pee.attendance_status NOT IN ('Withdrawn', 'Present', 'Absent'); -- (initial value can be 'Registered' or 'Pending')

-- b. Updating the pet_event_entry record to mark the attendance_status (e.g., present or absent) for each pet.
-- Present
UPDATE pet_event_entry
SET attendance_status = 'Present'
WHERE entry_id = [entry_id];
-- Absent
UPDATE pet_event_entry
SET attendance_status = 'Absent'
WHERE entry_id = [entry_id];
