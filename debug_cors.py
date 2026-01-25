import requests
import random

url = "https://dz-kitab-backend.vercel.app/auth/register"
origin = "https://dz-kitab-frontend.vercel.app"

print(f"--- TESTING PREFLIGHT (OPTIONS) ---")
headers_options = {
    "Origin": origin,
    "Access-Control-Request-Method": "POST",
    "Access-Control-Request-Headers": "content-type"
}

uid = random.randint(1000, 9999)
data = {
    "username": f"testuser_{uid}",
    "email": f"test_{uid}@example.com",
    "password": "Password123!", # Valid password
    "full_name": "Debug User"
}

headers_post = {
    "Origin": origin,
    "Content-Type": "application/json"
}

results = []
results.append(f"--- TESTING PREFLIGHT (OPTIONS) ---")
try:
    res_opt = requests.options(url, headers=headers_options)
    results.append(f"Status: {res_opt.status_code}")
    results.append("Headers:")
    for k, v in res_opt.headers.items():
        results.append(f"  {k}: {v}")
except Exception as e:
    results.append(f"Preflight error: {e}")

results.append(f"\n--- TESTING REGISTRATION (POST) ---")
try:
    res_post = requests.post(url, json=data, headers=headers_post)
    results.append(f"Status: {res_post.status_code}")
    results.append(f"Response Body: {res_post.text}")
    results.append("Headers:")
    for k, v in res_post.headers.items():
        results.append(f"  {k}: {v}")
except Exception as e:
    results.append(f"Post error: {e}")

with open("debug_cors_results.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(results))
print("Results written to debug_cors_results.txt")
