Signup (Register) endpoint
📌 Endpoint
POST /register


auth

📥 Request body (what frontend sends)

Tell him to send JSON like this (based on User model):

{
  "email": "user@email.com",
  "username": "user123",
  "password": "123456",
  "full_name": "User Name",
  "phone_number": "0550123456"
}
Login endpoint
📌 Endpoint
POST /login


auth

📥 Request body
{
  "email": "user@email.com",
  "password": "123456"
}
id (int)
email (string, unique)
username (string, unique)
hashed_password (string)
full_name (string)
phone_number (string, optional)
is_active (boolean)
created_at (datetime)
