# Verify Docker Image Leaness
# This script builds the image and checks if build tools like git or gcc are present.

Write-Host "Building Docker image 'omnius-test'..." -ForegroundColor Cyan
docker build -t omnius-test .

if ($LASTEXITCODE -ne 0) {
    Write-Host "Docker build failed!" -ForegroundColor Red
    exit 1
}

Write-Host "`nChecking for build tools in the final image..." -ForegroundColor Cyan
$gitCheck = docker run --rm omnius-test which git 2>$null
$gccCheck = docker run --rm omnius-test which gcc 2>$null

if ($gitCheck) {
    Write-Host "[FAIL] 'git' found in image: $gitCheck" -ForegroundColor Red
} else {
    Write-Host "[OK] 'git' not found." -ForegroundColor Green
}

if ($gccCheck) {
    Write-Host "[FAIL] 'gcc' found in image: $gccCheck" -ForegroundColor Red
} else {
    Write-Host "[OK] 'gcc' not found." -ForegroundColor Green
}

$imageSize = docker images omnius-test --format "{{.Size}}"
Write-Host "`nFinal Image Size: $imageSize" -ForegroundColor Yellow
