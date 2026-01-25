cd "c:\Users\dz FB\Documents\dz_kitab\dz-kitab-backend"

# Set DATABASE_URL
"postgresql://neondb_owner:npg_W4JkICUq7Fbr@ep-young-pine-ah3abvjg-pooler.c-3.us-east-1.aws.neon.tech/neondb?sslmode=require" | vercel env add DATABASE_URL production

# Set JWT_SECRET_KEY  
"2b87beba9e6551eee16f3ffd8b93f683" | vercel env add JWT_SECRET_KEY production

Write-Output "Environment variables set. Redeploying..."

# Redeploy
vercel --prod --yes --force

Write-Output "Deployment complete!"
