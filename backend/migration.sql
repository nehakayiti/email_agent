BEGIN;

CREATE TABLE alembic_version (
    version_num VARCHAR(32) NOT NULL, 
    CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)
);

-- Running upgrade  -> 0ab192bd5eea

CREATE TABLE users (
    id UUID NOT NULL, 
    email VARCHAR NOT NULL, 
    name VARCHAR, 
    created_at TIMESTAMP WITH TIME ZONE NOT NULL, 
    last_sign_in TIMESTAMP WITH TIME ZONE, 
    credentials JSON, 
    PRIMARY KEY (id)
);

CREATE UNIQUE INDEX ix_users_email ON users (email);

CREATE TABLE email_categories (
    id SERIAL NOT NULL, 
    name VARCHAR NOT NULL, 
    display_name VARCHAR NOT NULL, 
    description VARCHAR, 
    priority INTEGER, 
    is_system BOOLEAN, 
    created_at TIMESTAMP WITH TIME ZONE, 
    PRIMARY KEY (id), 
    CONSTRAINT uq_category_name_system UNIQUE (name, is_system)
);

CREATE INDEX ix_email_categories_id ON email_categories (id);

CREATE INDEX idx_email_category_name ON email_categories (name);

CREATE TABLE category_keywords (
    id SERIAL NOT NULL, 
    category_id INTEGER NOT NULL, 
    keyword VARCHAR NOT NULL, 
    is_regex BOOLEAN, 
    weight INTEGER, 
    user_id UUID, 
    PRIMARY KEY (id), 
    FOREIGN KEY(category_id) REFERENCES email_categories (id) ON DELETE CASCADE, 
    FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE CASCADE
);

CREATE INDEX ix_category_keywords_id ON category_keywords (id);

CREATE INDEX idx_category_keyword ON category_keywords (keyword);

CREATE INDEX idx_category_keyword_category ON category_keywords (category_id);

CREATE INDEX idx_category_keyword_user ON category_keywords (user_id);

CREATE TABLE sender_rules (
    id SERIAL NOT NULL, 
    category_id INTEGER NOT NULL, 
    pattern VARCHAR NOT NULL, 
    is_domain BOOLEAN, 
    weight INTEGER, 
    user_id UUID, 
    created_at TIMESTAMP WITHOUT TIME ZONE, 
    updated_at TIMESTAMP WITHOUT TIME ZONE, 
    rule_metadata JSON, 
    PRIMARY KEY (id), 
    CONSTRAINT unique_sender_rule_per_domain UNIQUE (pattern, is_domain, user_id), 
    FOREIGN KEY(category_id) REFERENCES email_categories (id) ON DELETE CASCADE, 
    FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE CASCADE
);

CREATE INDEX ix_sender_rules_id ON sender_rules (id);

CREATE TABLE emails (
    id UUID NOT NULL, 
    user_id UUID NOT NULL, 
    gmail_id VARCHAR NOT NULL, 
    thread_id VARCHAR NOT NULL, 
    subject VARCHAR, 
    from_email VARCHAR, 
    received_at TIMESTAMP WITH TIME ZONE, 
    snippet VARCHAR, 
    labels VARCHAR[], 
    is_read BOOLEAN, 
    is_processed BOOLEAN, 
    importance_score INTEGER, 
    category VARCHAR, 
    raw_data JSON, 
    created_at TIMESTAMP WITH TIME ZONE, 
    is_dirty BOOLEAN, 
    last_reprocessed_at TIMESTAMP WITH TIME ZONE, 
    PRIMARY KEY (id), 
    FOREIGN KEY(user_id) REFERENCES users (id)
);

CREATE INDEX ix_emails_user_id_received_at ON emails (user_id, received_at);

CREATE INDEX ix_emails_gmail_id ON emails (gmail_id);

CREATE INDEX ix_emails_category ON emails (category);

CREATE TABLE categorization_feedback (
    id UUID NOT NULL, 
    email_id UUID NOT NULL, 
    user_id UUID NOT NULL, 
    original_category VARCHAR, 
    new_category VARCHAR NOT NULL, 
    feedback_timestamp TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
    feedback_metadata JSON, 
    PRIMARY KEY (id), 
    FOREIGN KEY(email_id) REFERENCES emails (id), 
    FOREIGN KEY(user_id) REFERENCES users (id)
);

CREATE INDEX ix_categorization_feedback_id ON categorization_feedback (id);

CREATE TABLE email_categorization_decisions (
    id UUID NOT NULL, 
    email_id UUID NOT NULL, 
    category_to VARCHAR NOT NULL, 
    confidence_score FLOAT NOT NULL, 
    decision_type VARCHAR NOT NULL, 
    decision_factors JSON, 
    created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
    updated_at TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
    PRIMARY KEY (id), 
    FOREIGN KEY(email_id) REFERENCES emails (id)
);

CREATE INDEX ix_email_categorization_decisions_id ON email_categorization_decisions (id);

CREATE TABLE email_operations (
    id UUID NOT NULL, 
    email_id UUID NOT NULL, 
    user_id UUID NOT NULL, 
    operation_type VARCHAR(50) NOT NULL, 
    operation_data JSONB NOT NULL, 
    status VARCHAR(20) NOT NULL, 
    error_message TEXT, 
    created_at TIMESTAMP WITH TIME ZONE NOT NULL, 
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL, 
    retries INTEGER, 
    PRIMARY KEY (id), 
    FOREIGN KEY(email_id) REFERENCES emails (id) ON DELETE CASCADE, 
    FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE CASCADE
);

CREATE INDEX ix_email_operations_status ON email_operations (status);

CREATE INDEX ix_email_operations_user_id ON email_operations (user_id);

CREATE INDEX ix_email_operations_email_id ON email_operations (email_id);

CREATE INDEX ix_email_operations_created_at ON email_operations (created_at);

CREATE INDEX ix_email_operations_operation_type ON email_operations (operation_type);

CREATE TABLE email_trash_events (
    id UUID NOT NULL, 
    email_id UUID NOT NULL, 
    user_id UUID NOT NULL, 
    event_type VARCHAR(50) NOT NULL, 
    sender_email VARCHAR NOT NULL, 
    sender_domain VARCHAR NOT NULL, 
    subject VARCHAR, 
    snippet TEXT, 
    keywords VARCHAR[], 
    is_auto_categorized BOOLEAN, 
    categorization_source VARCHAR(20), 
    confidence_score FLOAT, 
    email_metadata JSONB, 
    created_at TIMESTAMP WITH TIME ZONE NOT NULL, 
    PRIMARY KEY (id), 
    FOREIGN KEY(email_id) REFERENCES emails (id) ON DELETE CASCADE, 
    FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE CASCADE
);

CREATE INDEX ix_email_trash_events_user_id ON email_trash_events (user_id);

CREATE INDEX ix_email_trash_events_email_id ON email_trash_events (email_id);

CREATE INDEX ix_email_trash_events_event_type ON email_trash_events (event_type);

CREATE INDEX ix_email_trash_events_sender_domain ON email_trash_events (sender_domain);

CREATE INDEX ix_email_trash_events_created_at ON email_trash_events (created_at);

CREATE INDEX ix_email_trash_events_categorization_source ON email_trash_events (categorization_source);

CREATE TABLE email_syncs (
    id UUID NOT NULL, 
    user_id UUID NOT NULL, 
    last_fetched_at TIMESTAMP WITH TIME ZONE NOT NULL, 
    last_history_id VARCHAR, 
    sync_cadence INTEGER NOT NULL, 
    created_at TIMESTAMP WITH TIME ZONE NOT NULL, 
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL, 
    PRIMARY KEY (id), 
    UNIQUE (user_id), 
    FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE CASCADE
);

CREATE INDEX ix_email_syncs_user_id ON email_syncs (user_id);

CREATE INDEX ix_email_syncs_last_fetched_at ON email_syncs (last_fetched_at);

CREATE TYPE syncdirection AS ENUM ('GMAIL_TO_EA', 'EA_TO_GMAIL', 'BI_DIRECTIONAL');

CREATE TYPE synctype AS ENUM ('MANUAL', 'AUTOMATIC');

CREATE TYPE syncstatus AS ENUM ('SUCCESS', 'ERROR');

CREATE TABLE sync_details (
    id SERIAL NOT NULL, 
    user_id UUID NOT NULL, 
    account_email VARCHAR NOT NULL, 
    direction syncdirection NOT NULL, 
    sync_type synctype NOT NULL, 
    sync_started_at TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
    sync_completed_at TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
    duration_sec FLOAT NOT NULL, 
    status syncstatus NOT NULL, 
    error_message TEXT, 
    emails_synced INTEGER NOT NULL, 
    changes_detected INTEGER NOT NULL, 
    changes_applied INTEGER NOT NULL, 
    pending_ea_changes JSON, 
    backend_version VARCHAR, 
    data_freshness_sec INTEGER, 
    PRIMARY KEY (id)
);

CREATE INDEX ix_sync_details_user_id ON sync_details (user_id);

INSERT INTO alembic_version (version_num) VALUES ('0ab192bd5eea') RETURNING alembic_version.version_num;

-- Running upgrade 0ab192bd5eea -> d4ad63c70b05

UPDATE alembic_version SET version_num='d4ad63c70b05' WHERE alembic_version.version_num = '0ab192bd5eea';

-- Running upgrade d4ad63c70b05 -> 92cdd3d6b9f8

UPDATE alembic_version SET version_num='92cdd3d6b9f8' WHERE alembic_version.version_num = 'd4ad63c70b05';

-- Running upgrade 92cdd3d6b9f8 -> 44e9bb081149

DROP TABLE IF EXISTS test_table CASCADE;;

UPDATE alembic_version SET version_num='44e9bb081149' WHERE alembic_version.version_num = '92cdd3d6b9f8';

COMMIT;

