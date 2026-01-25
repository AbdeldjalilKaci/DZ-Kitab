import subprocess
import sys

# Clean DATABASE_URL without any trailing characters
db_url = "postgresql://neondb_owner:npg_W4JkICUq7Fbr@ep-young-pine-ah3abvjg-pooler.c-3.us-east-1.aws.neon.tech/neondb?sslmode=require"

print("Removing old DATABASE_URL...")
subprocess.run(["vercel", "env", "rm", "DATABASE_URL", "production", "--yes"], 
               cwd="c:/Users/dz FB/Documents/dz_kitab/dz-kitab-backend",
               capture_output=True)

print("Adding clean DATABASE_URL...")
result = subprocess.run(["vercel", "env", "add", "DATABASE_URL", "production"],
                       input=db_url,
                       encoding="utf-8",
                       cwd="c:/Users/dz FB/Documents/dz_kitab/dz-kitab-backend",
                       capture_output=True,
                       text=True)

print(f"Result: {result.stdout}")
if result.stderr:
    print(f"Error: {result.stderr}")

print("\nRedeploying backend...")
deploy_result = subprocess.run(["vercel", "--prod", "--yes", "--force"],
                              cwd="c:/Users/dz FB/Documents/dz_kitab/dz-kitab-backend",
                              capture_output=True,
                              text=True)

print("Deployment complete!")
print(deploy_result.stdout)
