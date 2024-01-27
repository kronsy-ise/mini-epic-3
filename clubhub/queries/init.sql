-- First, we drop all things
DROP TRIGGER IF EXISTS set_user_kind_trigger ON Users CASCADE;
DROP FUNCTION IF EXISTS set_user_kind() CASCADE;
DROP TABLE IF EXISTS Sessions;
DROP TABLE IF EXISTS Users CASCADE;
DROP TYPE IF EXISTS UserKind CASCADE;


-- then, we create everything

CREATE TYPE UserKind AS ENUM ('coordinator', 'user', 'unapproved','admin');


CREATE TABLE Users(
  id BIGSERIAL PRIMARY KEY,
  name TEXT NOT NULL,
  username TEXT NOT NULL,
  email TEXT NOT NULL,
  mobile TEXT NOT NULL,

  password_hash TEXT NOT NULL,

  user_kind UserKind NOT NULL,

  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

  UNIQUE(email),
  UNIQUE(username)
);

CREATE OR REPLACE FUNCTION set_user_kind()
RETURNS TRIGGER AS $$
BEGIN
  IF NEW.user_kind IS NOT NULL THEN
    RAISE EXCEPTION 'user_kind cannot be set explicitly';
  END IF;
  IF NOT EXISTS (SELECT 1 FROM Users) THEN 
    NEW.user_kind = 'admin';
  ELSE
    NEW.user_kind = 'unapproved';
  END IF;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE TRIGGER set_user_kind_trigger
BEFORE INSERT ON Users
FOR EACH ROW 
EXECUTE FUNCTION set_user_kind();

CREATE TABLE Sessions(
  id BIGSERIAL PRIMARY KEY,
  secret TEXT NOT NULL,

  user_id BIGINT NOT NULL REFERENCES Users(id),

  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  expires_at TIMESTAMPTZ NOT NULL,

  UNIQUE(secret)
);
