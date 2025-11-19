# GitHub Releases Creation Script
# This script creates GitHub releases using the GitHub API

# Configuration
$owner = "vcse59"
$repo = "ConvoAI"
$apiUrl = "https://api.github.com/repos/$owner/$repo/releases"

# GitHub Personal Access Token (You need to set this)
# Create token at: https://github.com/settings/tokens
# Required scopes: repo (Full control of private repositories)
$token = $env:GITHUB_TOKEN

if (-not $token) {
    Write-Host "ERROR: GITHUB_TOKEN environment variable not set!" -ForegroundColor Red
    Write-Host ""
    Write-Host "To create releases via API, you need a GitHub Personal Access Token:" -ForegroundColor Yellow
    Write-Host "1. Go to: https://github.com/settings/tokens" -ForegroundColor Cyan
    Write-Host "2. Click 'Generate new token (classic)'" -ForegroundColor Cyan
    Write-Host "3. Give it a name: 'ConvoAI Release Token'" -ForegroundColor Cyan
    Write-Host "4. Select scope: 'repo' (Full control of private repositories)" -ForegroundColor Cyan
    Write-Host "5. Click 'Generate token'" -ForegroundColor Cyan
    Write-Host "6. Copy the token" -ForegroundColor Cyan
    Write-Host "7. Run: `$env:GITHUB_TOKEN = 'your_token_here'" -ForegroundColor Cyan
    Write-Host "8. Run this script again" -ForegroundColor Cyan
    Write-Host ""
    exit 1
}

# Function to create a GitHub release
function Create-GitHubRelease {
    param(
        [string]$TagName,
        [string]$Name,
        [string]$Body,
        [bool]$IsLatest = $false
    )

    Write-Host "Creating release: $Name..." -ForegroundColor Yellow

    $headers = @{
        "Authorization" = "Bearer $token"
        "Accept" = "application/vnd.github+json"
        "X-GitHub-Api-Version" = "2022-11-28"
    }

    $releaseData = @{
        tag_name = $TagName
        name = $Name
        body = $Body
        draft = $false
        prerelease = $false
        make_latest = if ($IsLatest) { "true" } else { "false" }
    } | ConvertTo-Json -Depth 10

    try {
        $response = Invoke-RestMethod -Uri $apiUrl -Method Post -Headers $headers -Body $releaseData -ContentType "application/json"
        Write-Host "✓ Successfully created release: $Name" -ForegroundColor Green
        Write-Host "  URL: $($response.html_url)" -ForegroundColor Cyan
        return $response
    }
    catch {
        Write-Host "✗ Failed to create release: $Name" -ForegroundColor Red
        Write-Host "  Error: $($_.Exception.Message)" -ForegroundColor Red
        
        # Parse error response
        if ($_.ErrorDetails.Message) {
            $errorJson = $_.ErrorDetails.Message | ConvertFrom-Json
            Write-Host "  Details: $($errorJson.message)" -ForegroundColor Red
        }
        return $null
    }
}

# Read release notes
Write-Host "`n=== ConvoAI GitHub Releases Creation ===" -ForegroundColor Cyan
Write-Host "Repository: $owner/$repo`n" -ForegroundColor Cyan

Write-Host "Reading release notes files..." -ForegroundColor Yellow

$releaseNotes_v1_0_0 = Get-Content "RELEASE_NOTES_v1.0.0.md" -Raw -ErrorAction Stop
$releaseNotes_v1_1_0 = Get-Content "RELEASE_NOTES_v1.1.0.md" -Raw -ErrorAction Stop
$releaseNotes_v2_0_0 = Get-Content "RELEASE_NOTES_v2.0.0.md" -Raw -ErrorAction Stop

Write-Host "✓ Release notes loaded successfully`n" -ForegroundColor Green

# Create releases
Write-Host "Creating releases...`n" -ForegroundColor Cyan

# Create v1.0.0
$release_v1_0_0 = Create-GitHubRelease -TagName "v1.0.0" -Name "v1.0.0 - Initial Production Release" -Body $releaseNotes_v1_0_0 -IsLatest $false
Start-Sleep -Seconds 2

# Create v1.1.0
$release_v1_1_0 = Create-GitHubRelease -TagName "v1.1.0" -Name "v1.1.0 - Analytics Service Integration" -Body $releaseNotes_v1_1_0 -IsLatest $false
Start-Sleep -Seconds 2

# Create v2.0.0 (Latest)
$release_v2_0_0 = Create-GitHubRelease -TagName "v2.0.0" -Name "v2.0.0 - MCP Integration (Major Feature Release)" -Body $releaseNotes_v2_0_0 -IsLatest $true

# Summary
Write-Host "`n=== Summary ===" -ForegroundColor Cyan
Write-Host "Releases created:" -ForegroundColor Yellow

$successCount = 0
if ($release_v1_0_0) { 
    Write-Host "  ✓ v1.0.0 - Initial Production Release" -ForegroundColor Green
    $successCount++
}
else {
    Write-Host "  ✗ v1.0.0 - Failed" -ForegroundColor Red
}

if ($release_v1_1_0) { 
    Write-Host "  ✓ v1.1.0 - Analytics Service Integration" -ForegroundColor Green
    $successCount++
}
else {
    Write-Host "  ✗ v1.1.0 - Failed" -ForegroundColor Red
}

if ($release_v2_0_0) { 
    Write-Host "  ✓ v2.0.0 - MCP Integration (Major Feature Release) [LATEST]" -ForegroundColor Green
    $successCount++
}
else {
    Write-Host "  ✗ v2.0.0 - Failed" -ForegroundColor Red
}

Write-Host "`nTotal: $successCount/3 releases created successfully" -ForegroundColor Cyan

if ($successCount -eq 3) {
    Write-Host "`n✓ All releases created successfully!" -ForegroundColor Green
    Write-Host "View releases at: https://github.com/$owner/$repo/releases" -ForegroundColor Cyan
}
else {
    Write-Host "`n⚠ Some releases failed. Check errors above." -ForegroundColor Yellow
}

Write-Host ""
