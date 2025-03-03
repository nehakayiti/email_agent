-- SQL script to create the email_operations table for tracking pending operations
-- This addresses the sync issue when changes in EA aren't reflected in Gmail

-- Create the email_operations table
CREATE TABLE IF NOT EXISTS email_operations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email_id UUID NOT NULL REFERENCES emails(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    operation_type VARCHAR(50) NOT NULL,
    operation_data JSONB NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    error_message TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    retries INTEGER DEFAULT 0
);

-- Create indexes for efficient querying
CREATE INDEX IF NOT EXISTS ix_email_operations_status ON email_operations(status);
CREATE INDEX IF NOT EXISTS ix_email_operations_user_id ON email_operations(user_id);
CREATE INDEX IF NOT EXISTS ix_email_operations_email_id ON email_operations(email_id);
CREATE INDEX IF NOT EXISTS ix_email_operations_created_at ON email_operations(created_at);
CREATE INDEX IF NOT EXISTS ix_email_operations_operation_type ON email_operations(operation_type);

-- Create an operation to sync any emails already in trash
INSERT INTO email_operations (
    email_id,
    user_id,
    operation_type,
    operation_data,
    status
)
SELECT 
    id, 
    user_id, 
    'delete', 
    jsonb_build_object(
        'add_labels', jsonb_build_array('TRASH'),
        'remove_labels', jsonb_build_array('INBOX')
    ), 
    'pending'
FROM 
    emails
WHERE 
    category = 'trash' 
    AND 'TRASH' = ANY(labels) 
    AND id NOT IN (
        SELECT email_id FROM email_operations WHERE operation_type = 'delete'
    );

-- Update script complete
SELECT 'Email operations table created successfully' as result; 