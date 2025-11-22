-- migrate:up

CREATE TABLE conversions (
    uuid UUID PRIMARY KEY,
    encrypted_content BYTEA NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- migrate:down

DROP TABLE conversions;
