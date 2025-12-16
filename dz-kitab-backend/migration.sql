-- Add new columns
ALTER TABLE users 
ADD COLUMN IF NOT EXISTS first_name VARCHAR,
ADD COLUMN IF NOT EXISTS last_name VARCHAR;

-- Create enum type for university
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'universityenum') THEN
        CREATE TYPE universityenum AS ENUM ('ESTIN', 'ESI', 'EPAU', 'USTHB');
    END IF;
END $$;

-- Add university column
ALTER TABLE users 
ADD COLUMN IF NOT EXISTS university universityenum;

-- Verify the changes
SELECT column_name, data_type, is_nullable 
FROM information_schema.columns 
WHERE table_name = 'users';