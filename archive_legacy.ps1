# Archive legacy documentation files (Windows PowerShell)

Write-Host "🗂️  Archiving legacy documentation files..." -ForegroundColor Cyan
Write-Host ""

# Create archive directory if it doesn't exist
if (-not (Test-Path "archive")) {
    New-Item -ItemType Directory -Path "archive" | Out-Null
    Write-Host "✅ Created archive/ directory" -ForegroundColor Green
}

# Move legacy files to archive
Write-Host "📦 Moving legacy files..." -ForegroundColor Yellow

$files = @(
    "CHALLENGE_CHECKLIST.md",
    "CHALLENGE_MODIFICATIONS.md",
    "CHALLENGE_README.md",
    "CHALLENGE_STRUCTURE.md",
    "CHALLENGE_SUBMISSION.md",
    "CHALLENGE_TEST_GUIDE.md",
    "DELIVERABLE_FINAL.md",
    "FILE_INVENTORY.md",
    "IMPLEMENTATION_SUMMARY.md",
    "INDEX.md",
    "POSTGRES_SETUP.md",
    "QUICK_START.md",
    "RAG_GUIDE.md",
    "RAG_IMPLEMENTATION.md",
    "RAG_QUICK_REFERENCE.md",
    "README_EXECUTIF.md",
    "SOLUTION_COMPLETE.md",
    "STARTUP_GUIDE.md"
)

foreach ($file in $files) {
    if (Test-Path $file) {
        Move-Item $file archive/ -Force
        Write-Host "   ✓ $file" -ForegroundColor Green
    }
}

Write-Host ""
Write-Host "✅ Legacy files archived!" -ForegroundColor Green
Write-Host ""
Write-Host "📁 Current structure:" -ForegroundColor Cyan
Write-Host "   Root: Essential files only"
Write-Host "   archive/: Legacy documentation"
Write-Host ""
Write-Host "✨ Repository is now clean and organized!" -ForegroundColor Magenta
