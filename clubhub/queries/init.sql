CREATE TYPE UserKind AS ENUM ('coordinator', 'user', 'unapproved');


CREATE TABLE Users(
  id BIGSERIAL PRIMARY KEY,
  username TEXT NOT NULL,
  email TEXT NOT NULL,
  mobile TEXT NOT NULL,

  password_hash TEXT NOT NULL,

  is_admin BOOLEAN NOT NULL,

  user_kind UserKind NOT NULL,

  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()  
);

