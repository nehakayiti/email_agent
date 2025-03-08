-- Create email_trash_events table for storing events for ML training

CREATE TABLE IF NOT EXISTS email_trash_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email_id UUID NOT NULL REFERENCES emails(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    event_type VARCHAR(50) NOT NULL,
    sender_email VARCHAR NOT NULL,
    sender_domain VARCHAR NOT NULL,
    subject VARCHAR,
    snippet TEXT,
    keywords VARCHAR[],
    is_auto_categorized BOOLEAN DEFAULT FALSE,
    categorization_source VARCHAR(20),
    confidence_score FLOAT,
    email_metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
);

-- Create indexes for efficient querying
CREATE INDEX IF NOT EXISTS ix_email_trash_events_user_id ON email_trash_events(user_id);
CREATE INDEX IF NOT EXISTS ix_email_trash_events_email_id ON email_trash_events(email_id);
CREATE INDEX IF NOT EXISTS ix_email_trash_events_event_type ON email_trash_events(event_type);
CREATE INDEX IF NOT EXISTS ix_email_trash_events_sender_domain ON email_trash_events(sender_domain);
CREATE INDEX IF NOT EXISTS ix_email_trash_events_created_at ON email_trash_events(created_at);
CREATE INDEX IF NOT EXISTS ix_email_trash_events_categorization_source ON email_trash_events(categorization_source); 