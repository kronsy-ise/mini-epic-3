-- First, we drop all things
DROP TRIGGER IF EXISTS set_user_kind_trigger ON Users CASCADE;
DROP FUNCTION IF EXISTS set_user_kind() CASCADE;
DROP TABLE IF EXISTS Sessions;
DROP TABLE IF EXISTS Users CASCADE;
DROP TYPE IF EXISTS UserKind CASCADE;
DROP TABLE IF EXISTS CLUBS CASCADE;
DROP TABLE IF EXISTS EVENTS CASCADE;
DROP TABLE IF EXISTS EVENT_PARTICIPATION CASCADE;
DROP TABLE IF EXISTS CLUB_MEMBERSHIP CASCADE;
DROP TRIGGER IF EXISTS set_user_kind_trigger ON Users CASCADE;
DROP FUNCTION IF EXISTS set_user_kind() CASCADE;
DROP TABLE IF EXISTS USERS CASCADE;
DROP TABLE IF EXISTS Sessions;
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

  status TEXT NOT NULL,
  
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE CLUB_MEMBERSHIP(
  club_id BIGINT NOT NULL REFERENCES Clubs(club_id),
  user_id BIGINT NOT NULL REFERENCES Users(user_id),
  PRIMARY KEY(club_id, user_id),

  status TEXT NOT NULL,
  
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
  RETURN NEW;
  END IF;
END;
$$ LANGUAGE plpgsql;

-- Trigger to execute the set_club_id function before inserting into Clubs table
CREATE OR REPLACE TRIGGER set_club_id_trigger
BEFORE INSERT ON CLUBS
FOR EACH ROW 
EXECUTE FUNCTION set_club_id();

-- Function to approve event participation and add user to club_membership if status is approved
CREATE OR REPLACE FUNCTION approve_event_participation()
RETURNS TRIGGER AS $$
BEGIN
  IF NEW.status = 'approved' THEN
    -- Add user to club_membership
    INSERT INTO CLUB_MEMBERSHIP(club_id, user_id, status, created_at, updated_at)
    VALUES (NEW.club_id, NEW.user_id, 'approved', NOW(), NOW());
  ELSE
    -- Check if the user is a member of the club
    IF EXISTS (
      SELECT 1 FROM CLUB_MEMBERSHIP
      WHERE club_id = NEW.club_id AND user_id = NEW.user_id AND status = 'approved'
    ) THEN
      NEW.status = 'approved';
    END IF;
  END IF;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to execute the approve_event_participation function before inserting into Event_Participation table
CREATE OR REPLACE TRIGGER approve_event_participation_trigger
BEFORE INSERT ON EVENT_PARTICIPATION
FOR EACH ROW
EXECUTE FUNCTION approve_event_participation();

-- Function to set the coordinator_id to the user_id
CREATE OR REPLACE FUNCTION set_club_coordinator()
RETURNS TRIGGER AS $$
BEGIN
  NEW.coordinator_id = NEW.user_id;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to execute the set_club_coordinator function before inserting into Clubs table
CREATE TRIGGER set_club_coordinator_trigger
BEFORE INSERT ON CLUBS
FOR EACH ROW
EXECUTE FUNCTION set_club_coordinator();

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
    INSERT INTO USERS(name, username, email, mobile, password_hash)
    VALUES ('User1', 'user1', 'user1@example.com', '1234567890', 'placeholder_hash');
  END IF;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER after_insert_users
AFTER INSERT ON USERS
FOR EACH ROW
EXECUTE FUNCTION check_entries();


-- Create Views 