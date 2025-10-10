# PowerShell script to open GitHub Desktop with this repository
# Run this if GitHub Desktop doesn't show your repository

$repoPath = "C:\A1_School_ai_25\001_My_proj_AI\my_proj_05_prompt\my_project_05"
$gitHubDesktopPath = "$env:LOCALAPPDATA\GitHubDesktop\GitHubDesktop.exe"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Opening GitHub Desktop" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Repository: $repoPath" -ForegroundColor Green
Write-Host "Branch: my_proj_05_prompt" -ForegroundColor Green
Write-Host "Remote: https://github.com/raj-harit-v2/Raj_Projects_25" -ForegroundColor Green
Write-Host ""

if (Test-Path $gitHubDesktopPath) {
    Write-Host "Launching GitHub Desktop..." -ForegroundColor Yellow
    Start-Process -FilePath $gitHubDesktopPath -ArgumentList $repoPath
    Write-Host ""
    Write-Host "GitHub Desktop opened!" -ForegroundColor Green
    Write-Host ""
    Write-Host "If you don't see the repository:" -ForegroundColor Yellow
    Write-Host "1. Click 'File' > 'Add Local Repository'" -ForegroundColor White
    Write-Host "2. Navigate to: $repoPath" -ForegroundColor White
    Write-Host "3. Click 'Add Repository'" -ForegroundColor White
} else {
    Write-Host "ERROR: GitHub Desktop not found at: $gitHubDesktopPath" -ForegroundColor Red
    Write-Host "Please check if GitHub Desktop is installed." -ForegroundColor Red
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Press any key to continue..." -ForegroundColor Cyan
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")


