-- First, we drop all things
DROP TABLE IF EXISTS Sessions;
DROP TABLE IF EXISTS Users CASCADE;
DROP TYPE IF EXISTS UserKind CASCADE;


-- then, we create everything

CREATE TYPE UserKind AS ENUM ('coordinator', 'user', 'unapproved',"admin");


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

CREATE TABLE Sessions(
  id BIGSERIAL PRIMARY KEY,
  secret TEXT NOT NULL,

  user_id BIGINT NOT NULL REFERENCES Users(id),

  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  expires_at TIMESTAMPTZ NOT NULL,

  UNIQUE(secret)
);
