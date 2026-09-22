# Publish autotouch-patch to GitHub
# Requires: Git for Windows + GitHub CLI (gh), authenticated via `gh auth login`

$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path $PSScriptRoot -Parent

Set-Location $RepoRoot
Write-Host "[*] Repo root: $RepoRoot" -ForegroundColor Cyan

if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    Write-Host "[!] Git not found. Install: https://git-scm.com/download/win" -ForegroundColor Red
    exit 1
}
if (-not (Get-Command gh -ErrorAction SilentlyContinue)) {
    Write-Host "[!] GitHub CLI not found. Install: https://cli.github.com/" -ForegroundColor Red
    exit 1
}

$RemoteName = "smartmaster35rus-dev/autotouch-patch"
$Tag = "v8.5.5-v2"
$Deb = "releases/me.autotouch.autotouch.ios8_8.5.5_iphoneos-arm64_patched.deb"

if (-not (Test-Path $Deb)) {
    Write-Host "[!] Missing $Deb — run: python scripts/build_deb.py" -ForegroundColor Red
    exit 1
}

if (-not (Test-Path ".git")) {
    git init -b main
}

git add README.md LICENSE CHANGELOG.md .gitignore patch/ releases/ scripts/
git status --short

$Status = git status --porcelain
if ($Status) {
    git commit -m "Release AutoTouch 8.5.5 v2 arm64 patch (fix 2-min license timeout)"
}

if (-not (git remote | Select-String -Pattern "^origin$")) {
    gh repo create $RemoteName --public --source=. --remote=origin --description 'Patched AutoTouch .deb for jailbroken iOS arm64 rootless'
} else {
    git push -u origin main
}

git push -u origin main 2>$null
git push origin main

gh release upload $Tag $Deb --clobber 2>$null
if ($LASTEXITCODE -ne 0) {
    gh release create $Tag $Deb `
        --title "AutoTouch 8.5.5 Patched v2 (arm64)" `
        --notes "crackATT v2 — fixes 2-minute license timeout in AutoTouch 8.5.5. Hooks CommandServer_907239, Global_983499, JSEngine, PlayingManager_932730. Install: curl -fsSL https://raw.githubusercontent.com/smartmaster35rus-dev/autotouch-patch/main/scripts/install.sh | bash"
}

Write-Host "[+] Published: https://github.com/$RemoteName" -ForegroundColor Green
