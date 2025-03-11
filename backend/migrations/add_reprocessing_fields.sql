-- Add reprocessing fields to emails table
ALTER TABLE emails ADD COLUMN is_dirty BOOLEAN DEFAULT false;
ALTER TABLE emails ADD COLUMN last_reprocessed_at TIMESTAMP WITH TIME ZONE;

-- Ensure all existing emails have is_dirty=false
UPDATE emails SET is_dirty = false WHERE is_dirty IS NULL;

-- Make is_dirty not nullable after setting default value
ALTER TABLE emails ALTER COLUMN is_dirty SET NOT NULL; 