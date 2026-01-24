-- Add is_admin column to users table
ALTER TABLE users ADD COLUMN IF NOT EXISTS is_admin BOOLEAN DEFAULT FALSE;

-- Create index for performance
CREATE INDEX IF NOT EXISTS idx_users_is_admin ON users(is_admin);

-- Set existing admin users
UPDATE users SET is_admin = TRUE WHERE email LIKE '%admin%' OR username LIKE '%admin%';

-- Verify the change
SELECT username, email, is_admin FROM users;

SELECT '✅ Migration is_admin terminée!' as message;
