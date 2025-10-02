CREATE SCHEMA pet_show;

USE pet_show;

#EVENTS TABLE CREATION
CREATE TABLE events (eventID INT NOT NULL, 
					name VARCHAR(20) NOT NULL, 
                    date DATE, 
                    time TIME, 
                    location VARCHAR(100) NOT NULL, 
                    maxParticipants INT, 
                    registrationDeadline DATE, 
                    eventType VARCHAR(100), 
                    distanceInKM DECIMAL(4, 2), 
                    timeLimit INT, 
                    breedCategory VARCHAR(50), 
                    status BOOLEAN,
                    CONSTRAINT primary_event_key PRIMARY KEY(eventID));
                    
#PET OWNER TABLE CREATION
CREATE TABLE pet_owner (participantID INT NOT NULL, 
					   firstName VARCHAR(20) NOT NULL,
                       lastName VARCHAR(20) NOT NULL, 
                       email VARCHAR(20), 
                       number INT NOT NULL, 
                       totalPets INT,
                       CONSTRAINT primary_par_key PRIMARY KEY(participantID));
                       
#PET RECORD TABLE CREATION
CREATE TABLE pet_record (petID INT NOT NULL, 
						 participantID INT NOT NULL, 
                         name VARCHAR(20) NOT NULL, 
                         breed VARCHAR(30), 
                         age INT, 
                         sex VARCHAR(4), 
                         weightInKg DECIMAL(6,2), 
                         muzzleRequired BOOLEAN, 
                         notes TEXT, 
                         CONSTRAINT primary_pet_key PRIMARY KEY(petID),
                         CONSTRAINT pet_foreign_owner_key FOREIGN KEY(participantID) REFERENCES pet_owner(participantID));
                         
#AWARDS AND TITLES TABLE CREATION
CREATE TABLE awrd_title (awardID INT NOT NULL, 
						 petID INT NOT NULL, 
                         type VARCHAR(100), 
                         description TEXT, 
                         date DATE, 
                         eventID INT NOT NULL,
                         CONSTRAINT primary_awrd_key PRIMARY KEY (awardID),
                         CONSTRAINT awrd_foreign_pet_key FOREIGN KEY (petID) REFERENCES pet_record(petID),
                         CONSTRAINT awrd_foreign_event_key FOREIGN KEY(eventID) REFERENCES events(eventID));
                         
#PARTICIPANTS-EVENTS JUNCTION TABLE CREATION
CREATE TABLE participant_event (participantID INT NOT NULL,
								eventID INT NOT NULL,
								registrationDate DATE NOT NULL,
								CONSTRAINT primary_par_event_key PRIMARY KEY (participantID, eventID),
								CONSTRAINT par_event_foreign_participant_key FOREIGN KEY (participantID) REFERENCES pet_owner(participantID),
								CONSTRAINT par_event_foreign_event_key FOREIGN KEY (eventID) REFERENCES events(eventID));
#PETS-EVENTS JUNCTION TABLE CREATION
CREATE TABLE pet_event (petID INT NOT NULL,
						eventID INT NOT NULL,
						attendanceStatus VARCHAR(10) CHECK (attendanceStatus IN ('Present', 'Absent', 'Registered')),
						-- (time, score, rank)
						petResult DECIMAL(5, 2), 
						CONSTRAINT primary_pet_event_key PRIMARY KEY (petID, eventID),
						CONSTRAINT pet_event_foreign_pet_key FOREIGN KEY (petID) REFERENCES pet_record(petID),
						CONSTRAINT pet_event_foreign_event_key FOREIGN KEY (eventID) REFERENCES events(eventID));