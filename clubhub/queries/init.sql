-- First, we drop all things
DROP TRIGGER IF EXISTS set_user_kind_trigger ON Users CASCADE;
DROP FUNCTION IF EXISTS set_user_kind() CASCADE;
DROP VIEW IF EXISTS users_club_membership_view CASCADE;
DROP VIEW IF EXISTS clubs_coordinator_membership_view CASCADE;
DROP VIEW IF EXISTS upcoming_events_clubs_view CASCADE;
DROP VIEW IF EXISTS users_sessions_view CASCADE;
DROP TABLE IF EXISTS Sessions;
DROP TABLE IF EXISTS Sessions CASCADE;
DROP TABLE IF EXISTS Users CASCADE;
DROP TYPE IF EXISTS UserKind CASCADE;
DROP TABLE IF EXISTS CLUBS CASCADE;
DROP TABLE IF EXISTS EVENTS CASCADE;
DROP TABLE IF EXISTS EVENT_PARTICIPATION CASCADE;
DROP TABLE IF EXISTS CLUB_MEMBERSHIP CASCADE;
DROP TRIGGER IF EXISTS set_user_kind_trigger ON Users CASCADE;
DROP FUNCTION IF EXISTS set_user_kind() CASCADE;
DROP TYPE IF EXISTS UserKind CASCADE;


-- then, we create everything

CREATE TYPE UserKind AS ENUM ('coordinator', 'student', 'unapproved','admin');

--    TABLES  --
CREATE TABLE USERS(
  user_id BIGSERIAL PRIMARY KEY,
  name TEXT NOT NULL,
  username TEXT NOT NULL UNIQUE,
  email TEXT NOT NULL UNIQUE,
  mobile TEXT NOT NULL,

  password_hash TEXT NOT NULL,

  user_kind UserKind NOT NULL,
  last_login TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE TABLE CLUBS(
  club_id BIGSERIAL PRIMARY KEY,
  name TEXT NOT NULL,
  description TEXT NOT NULL,
  validity Text NOT NULL,--pending/approved/rejected
  user_id BIGINT NOT NULL REFERENCES Users(user_id), -- Added foreign key constraint
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);


CREATE TABLE EVENTS(
  event_id BIGSERIAL PRIMARY KEY,
  name TEXT NOT NULL,
  description TEXT NOT NULL,
  date TIMESTAMPTZ NOT NULL,
  venue TEXT NOT NULL,
  
  club_id BIGINT NOT NULL REFERENCES Clubs(club_id),
  
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE EVENT_PARTICIPATION(
  event_id BIGINT NOT NULL REFERENCES Events(event_id),
  user_id BIGINT NOT NULL REFERENCES Users(user_id),
  PRIMARY KEY(event_id, user_id),

  status TEXT NOT NULL,--pending/approved/rejected
  
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE CLUB_MEMBERSHIP(
  club_id BIGINT NOT NULL REFERENCES Clubs(club_id),
  user_id BIGINT NOT NULL REFERENCES Users(user_id),
  PRIMARY KEY(club_id, user_id),

  status TEXT NOT NULL,--pending/approved/rejected
  
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE Sessions(
  id BIGSERIAL PRIMARY KEY,
  secret TEXT NOT NULL,

  user_id INT NOT NULL REFERENCES Users(user_id),

  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  expires_at TIMESTAMPTZ NOT NULL,

  UNIQUE(secret)
);

--    FUNCTIONS AND TRIGGERS  --
CREATE OR REPLACE FUNCTION set_user_kind()
RETURNS TRIGGER AS $$
BEGIN
  IF NEW.user_kind IS NOT NULL THEN
    RAISE EXCEPTION 'user_kind cannot be set explicitly';
  END IF;
  IF NOT EXISTS (SELECT 1 FROM USERS) THEN 
    NEW.user_kind = 'admin';
  ELSE
    NEW.user_kind = 'unapproved';
  END IF;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE TRIGGER set_user_kind_trigger
BEFORE INSERT ON USERS
FOR EACH ROW 
EXECUTE FUNCTION set_user_kind();

-- Function to set club_id when a new club is made
CREATE OR REPLACE FUNCTION set_club_id()
RETURNS TRIGGER AS $$
BEGIN
  IF NEW.club_id IS NULL THEN
    NEW.club_id = 1;
  NEW.club_id = (SELECT MAX(club_id) FROM CLUBS) + 1;
  END IF;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to execute the set_club_id function before inserting into Clubs table
CREATE OR REPLACE TRIGGER set_club_id_trigger
BEFORE INSERT ON CLUBS
FOR EACH ROW 
EXECUTE FUNCTION set_club_id();

CREATE OR REPLACE FUNCTION approve_event_participation()
RETURNS TRIGGER AS $$
BEGIN
  -- Check if the user is a member of the club associated with the event
  IF EXISTS (
    SELECT 1 FROM CLUB_MEMBERSHIP
    WHERE club_id = (SELECT club_id FROM Events WHERE event_id = NEW.event_id) AND user_id = NEW.user_id AND status = 'approved'
  ) THEN
    -- If the user is a member of the club, approve their participation
    NEW.status = 'approved';
  END IF;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to execute the approve_event_participation function before inserting into Event_Participation table
CREATE OR REPLACE TRIGGER approve_event_participation_trigger
BEFORE INSERT ON EVENT_PARTICIPATION
FOR EACH ROW
EXECUTE FUNCTION approve_event_participation();


-- Function to check if the user has reached the maximum club membership limit
CREATE OR REPLACE FUNCTION check_club_membership_limit()
RETURNS TRIGGER AS $$
DECLARE
    club_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO club_count
    FROM CLUB_MEMBERSHIP
    WHERE user_id = NEW.user_id AND status = 'approved';

    IF club_count >= 3 THEN
        RAISE EXCEPTION 'User has reached the maximum club membership limit';
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to execute the check_club_membership_limit function before inserting into CLUB_MEMBERSHIP table
CREATE TRIGGER check_club_membership_limit_trigger
BEFORE INSERT ON CLUB_MEMBERSHIP
FOR EACH ROW
EXECUTE FUNCTION check_club_membership_limit();

-- Function to update the updated_at column with the current timestamp
CREATE OR REPLACE FUNCTION updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to execute the updated_at function after inserting, updating, or deleting rows in the Users table
CREATE TRIGGER updated_at_trigger
AFTER INSERT OR UPDATE OR DELETE ON Users
FOR EACH STATEMENT
EXECUTE FUNCTION updated_at();


--trigger to add another unapproved user once admin has been made for testing
CREATE OR REPLACE FUNCTION check_entries()
RETURNS TRIGGER AS $$
BEGIN
  IF (SELECT COUNT(*) FROM USERS) = 1 THEN 
    FOR i IN 2..10 LOOP
      INSERT INTO USERS(name, username, email, mobile, password_hash)
      VALUES ('User' || i, 'user' || i, 'user' || i || '@example.com', '1234567890', 'placeholder_hash');
    END LOOP;
  END IF;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER after_insert_users
AFTER INSERT ON USERS
FOR EACH ROW
EXECUTE FUNCTION check_entries();

-- Function to add one club to the database upon initialization
CREATE OR REPLACE FUNCTION add_initial_club()
RETURNS VOID AS $$
BEGIN
  IF (SELECT COUNT(*) FROM USERS) < 2 OR EXISTS (SELECT 1 FROM CLUBS WHERE name = 'Club Name') THEN
    RETURN;
  END IF;

  INSERT INTO CLUBS (name, description, coordinator_id)
  VALUES ('Club Name', 'Club Description', (SELECT user_id FROM USERS LIMIT 1));
END;
$$ LANGUAGE plpgsql;

-- Function to assign the first user in the users table a membership to the club
CREATE OR REPLACE FUNCTION assign_membership_to_first_user()
RETURNS VOID AS $$
BEGIN
  IF (SELECT COUNT(*) FROM USERS) < 2 OR EXISTS (SELECT 1 FROM CLUB_MEMBERSHIP WHERE user_id = (SELECT user_id FROM USERS ORDER BY user_id LIMIT 1)) THEN
    RETURN;
  END IF;

  INSERT INTO CLUB_MEMBERSHIP (club_id, user_id, status, created_at, updated_at)
  SELECT 1, user_id, 'approved', NOW(), NOW()
  FROM USERS
  ORDER BY user_id
  LIMIT 1;
END;
$$ LANGUAGE plpgsql;
-- Create Views 
CREATE VIEW users_club_membership_view AS
SELECT 
    u.user_id,
    u.name,
    u.username,
    u.email,
    u.mobile,
    cm.club_id,
    cm.status as membership_status
FROM USERS u
JOIN CLUB_MEMBERSHIP cm ON u.user_id = cm.user_id;

CREATE VIEW clubs_coordinator_membership_view AS
SELECT
    c.club_id,
    c.name as club_name,
    u.name as coordinator_name,
    COUNT(cm.user_id) as membership_count
FROM CLUBS c
JOIN USERS u ON c.user_id = u.user_id
LEFT JOIN CLUB_MEMBERSHIP cm ON c.club_id = cm.club_id
GROUP BY c.club_id, u.name;

CREATE VIEW upcoming_events_clubs_view AS
SELECT 
    e.event_id,
    e.name as event_name,
    e.description as event_description,
    e.date as event_date,
    e.venue as event_venue,
    c.club_id,
    c.name as club_name,
    ep.user_id,
    ep.status as participation_status
FROM EVENTS e
JOIN CLUBS c ON e.club_id = c.club_id
JOIN EVENT_PARTICIPATION ep ON e.event_id = ep.event_id
WHERE e.date > NOW();

CREATE VIEW users_sessions_view AS
SELECT 
    u.user_id,
    u.name,
    u.username,
    u.email,
    u.mobile,
    s.id as session_id,
    s.secret,
    s.expires_at
FROM USERS u
JOIN Sessions s ON u.user_id = s.user_id;
