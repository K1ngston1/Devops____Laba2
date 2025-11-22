-- migrate:up

DROP TABLE secrets;

-- migrate:down

CREATE TABLE secrets (
    name VARCHAR(255) PRIMARY KEY,
    content BYTEA NOT NULL
);
