$ErrorActionPreference = "Stop"

Write-Host "🚀 Starting database/backend cleanup and deployment..." -ForegroundColor Green

# 1. Deploy Backend
Write-Host "📦 Deploying Backend..." -ForegroundColor Cyan
Set-Location ".\dz-kitab-backend"
vercel --prod --yes
if ($LASTEXITCODE -ne 0) { Write-Error "Backend deployment failed"; exit 1 }

# 2. Deploy Frontend
Write-Host "🎨 Deploying Frontend..." -ForegroundColor Cyan
Set-Location "..\dz-kitab-frontend"
vercel --prod --yes
if ($LASTEXITCODE -ne 0) { Write-Error "Frontend deployment failed"; exit 1 }

Write-Host "✅ All deployments completed successfully!" -ForegroundColor Green
Set-Location ..
pause
