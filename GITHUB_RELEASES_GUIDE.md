# GitHub Releases Creation Guide

This guide will help you create GitHub releases for ConvoAI versions v1.0.0, v1.1.0, v2.0.0, and v3.0.0.

## Prerequisites

✅ Git tags have been created and pushed to GitHub
✅ Release notes have been generated for each version

## Method 1: Using GitHub Web Interface (Recommended)

### Step 1: Navigate to Releases Page

1. Go to: https://github.com/vcse59/ConvoAI
2. Click on "Releases" (right sidebar or under "Code" tab)
3. Click "Draft a new release" button

### Step 2: Create Release v1.0.0

1. **Choose a tag**: Select `v1.0.0` from dropdown
2. **Release title**: `v1.0.0 - Initial Production Release`
3. **Description**: Copy content from `RELEASE_NOTES_v1.0.0.md`
4. **This is a pre-release**: Leave unchecked
5. Click "Publish release"

### Step 3: Create Release v1.1.0

1. Click "Draft a new release" again
2. **Choose a tag**: Select `v1.1.0` from dropdown
3. **Release title**: `v1.1.0 - Analytics Service Integration`
4. **Description**: Copy content from `RELEASE_NOTES_v1.1.0.md`
5. **This is a pre-release**: Leave unchecked
6. Click "Publish release"

### Step 4: Create Release v2.0.0

1. Click "Draft a new release" again
2. **Choose a tag**: Select `v2.0.0` from dropdown
3. **Release title**: `v2.0.0 - MCP Integration (Major Feature Release)`
4. **Description**: Copy content from `RELEASE_NOTES_v2.0.0.md`
5. **This is a pre-release**: Leave unchecked
6. Click "Publish release"

### Step 5: Create Release v3.0.0

1. Click "Draft a new release" again
2. **Choose a tag**: Select `v3.0.0` from dropdown
3. **Release title**: `v3.0.0 - Theme Toggle, Cross-Platform Support & Documentation Enhancement`
4. **Description**: Copy content from `RELEASE_NOTES_v3.0.0.md`
5. **Set as latest release**: Check this box
6. **This is a pre-release**: Leave unchecked
7. Click "Publish release"

## Method 2: Using GitHub CLI (If Available)

If you want to install GitHub CLI, download from: https://cli.github.com/

Then run these commands:

```bash
# Login to GitHub
gh auth login

# Create release v1.0.0
gh release create v1.0.0 --title "v1.0.0 - Initial Production Release" --notes-file RELEASE_NOTES_v1.0.0.md

# Create release v1.1.0
gh release create v1.1.0 --title "v1.1.0 - Analytics Service Integration" --notes-file RELEASE_NOTES_v1.1.0.md

# Create release v2.0.0
gh release create v2.0.0 --title "v2.0.0 - MCP Integration (Major Feature Release)" --notes-file RELEASE_NOTES_v2.0.0.md

# Create release v3.0.0
gh release create v3.0.0 --title "v3.0.0 - Theme Toggle, Cross-Platform Support & Documentation Enhancement" --notes-file RELEASE_NOTES_v3.0.0.md --latest
```

## Method 3: Using PowerShell Script (Advanced)

If you prefer automation, you can use the GitHub API. See `create_releases_api.ps1` for details.

## Verification

After creating releases, verify at:
https://github.com/vcse59/ConvoAI/releases

You should see:
- ✅ v3.0.0 - Theme Toggle, Cross-Platform Support & Documentation Enhancement (Latest)
- ✅ v2.0.0 - MCP Integration
- ✅ v1.1.0 - Analytics Service Integration
- ✅ v1.0.0 - Initial Production Release

## Release Assets (Optional)

You can add these assets to each release:
- Source code (automatically added by GitHub)
- Docker images (if published to registry)
- Build artifacts
- Installation packages

## Post-Release Checklist

- [ ] All three releases created
- [ ] v2.0.0 marked as "Latest Release"
- [ ] Release notes properly formatted
- [ ] Links in release notes work correctly
- [ ] Announcement posted (Twitter, Discord, etc.)
- [ ] Documentation updated with release links
- [ ] Users notified of new releases

## Troubleshooting

### Tag Not Found
If tags don't appear in dropdown:
```bash
git push origin --tags
```
Wait a few minutes and refresh GitHub page.

### Release Notes Formatting
- Use Markdown preview in GitHub editor
- Check that links are not broken
- Verify code blocks render correctly
- Ensure images (if any) are accessible

### Permission Issues
Ensure you have write access to the repository.

## Support

For issues, contact repository maintainers or open an issue at:
https://github.com/vcse59/ConvoAI/issues
