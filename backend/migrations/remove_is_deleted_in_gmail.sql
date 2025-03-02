-- Migration to remove is_deleted_in_gmail column
-- This migration removes the is_deleted_in_gmail column and adds the TRASH label to emails that were marked as deleted
-- Run this with psql:
-- psql -U your_user -d your_database -f remove_is_deleted_in_gmail.sql

-- Start a transaction
BEGIN;

-- First, ensure all emails that had is_deleted_in_gmail=true have the TRASH label
UPDATE emails 
SET 
    labels = CASE 
        WHEN is_deleted_in_gmail = true AND NOT (labels @> ARRAY['TRASH']) THEN 
            array_append(COALESCE(labels, ARRAY[]::varchar[]), 'TRASH')
        ELSE 
            labels
    END,
    category = CASE 
        WHEN is_deleted_in_gmail = true AND category != 'trash' THEN 
            'trash'
        ELSE 
            category
    END
WHERE is_deleted_in_gmail = true;

-- Remove the is_deleted_in_gmail column
ALTER TABLE emails DROP COLUMN is_deleted_in_gmail;

-- Commit the transaction
COMMIT; 