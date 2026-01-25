import requests
import sys
import time

# Production URL from previous deployment
BACKEND_URL = "https://dz-kitab-backend.vercel.app"
FRONTEND_URL = "https://dz-kitab-frontend.vercel.app"

def check_endpoint(name, url):
    print(f"Checking {name} ({url})...")
    try:
        start = time.time()
        response = requests.get(url, timeout=10)
        elapsed = time.time() - start
        
        print(f"  Status: {response.status_code}")
        print(f"  Time: {elapsed:.2f}s")
        
        if response.status_code == 200:
            print(f"  ✅ Success")
            return response.json() if "json" in response.headers.get("Content-Type", "") else response.text
        else:
            print(f"  ❌ Failed: {response.text[:200]}")
            return None
    except Exception as e:
        print(f"  ❌ Error: {str(e)}")
        return None

print("--- STARTING PRODUCTION VERIFICATION ---")

# 1. Check Root
check_endpoint("Backend Root", f"{BACKEND_URL}/")

# 2. Check Health (DB Connection)
health_data = check_endpoint("Backend Health", f"{BACKEND_URL}/health")
if health_data:
    print(f"  Detailed Health: {health_data}")
    if health_data.get("database", "").startswith("error"):
        print("  🚨 CRITICAL: Database connection is failing in production!")
    else:
        print("  ✅ Database connection confirmed healthy.")

# 3. Check Stats (DB Data)
check_endpoint("Backend Stats", f"{BACKEND_URL}/stats")

print("\n--- VERIFICATION COMPLETE ---")
