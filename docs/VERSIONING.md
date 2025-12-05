# Git Versioning Guide

## Current Version

**Version**: 3.0.0  
**Tag**: v3.0.0  
**Date**: December 5, 2025

## Version History

| Version | Date | Description |
|---------|------|-------------|
| v3.0.0 | December 5, 2025 | Theme Toggle, Cross-Platform Support, UI Version Display & Documentation Enhancement |
| v2.0.0 | November 18, 2024 | MCP Integration (Major Feature Release) |
| v1.1.0 | November 10, 2024 | Analytics Service Integration |
| v1.0.0 | October 15, 2024 | Initial Production Release |

## Versioning Strategy

This project follows [Semantic Versioning 2.0.0](https://semver.org/):

**MAJOR.MINOR.PATCH** (e.g., 3.0.0)

- **MAJOR**: Incompatible API changes
- **MINOR**: New functionality (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

## Version File

The current version is stored in `VERSION` file at project root:
```
3.0.0
```

## Git Tags

All releases are tagged in Git with annotated tags:
```bash
git tag -l
# v1.0.0
# v1.1.0
# v2.0.0
# v3.0.0
```

## View Version History

```bash
# View all commits with tags
git log --oneline --graph --all --decorate

# View specific tag details
git show v3.0.0

# List all tags
git tag -l

# Show tag message
git tag -l -n9 v3.0.0
```

## Creating New Releases

### Patch Release (1.0.1)

For bug fixes:

```bash
# Update VERSION file
echo "1.0.1" > VERSION

# Stage and commit
git add VERSION
git commit -m "chore: Bump version to 1.0.1"

# Create tag
git tag -a v1.0.1 -m "Version 1.0.1 - Bug Fixes

Fixes:
- Fix issue #123
- Fix issue #124"

# Push with tags
git push origin main --tags
```

### Minor Release (1.1.0)

For new features (backward compatible):

```bash
# Update VERSION file
echo "1.1.0" > VERSION

# Stage and commit
git add VERSION
git commit -m "chore: Bump version to 1.1.0"

# Create tag
git tag -a v1.1.0 -m "Version 1.1.0 - New Features

Added:
- Feature A
- Feature B

Changed:
- Enhancement C"

# Push with tags
git push origin main --tags
```

### Major Release (2.0.0)

For breaking changes:

```bash
# Update VERSION file
echo "2.0.0" > VERSION

# Stage and commit
git add VERSION
git commit -m "chore: Bump version to 2.0.0

BREAKING CHANGE: Description of breaking changes"

# Create tag
git tag -a v2.0.0 -m "Version 2.0.0 - Major Release

Breaking Changes:
- Breaking change A
- Breaking change B

Added:
- New feature

Migration Guide:
- Steps to migrate from 1.x to 2.0"

# Push with tags
git push origin main --tags
```

## Release Checklist

Before creating a new release:

- [ ] Update `VERSION` file
- [ ] Update `CHANGELOG.md` with all changes
- [ ] Update documentation (README.md, guides)
- [ ] Run all tests: `pytest tests/ -v`
- [ ] Build Docker images: `docker-compose build`
- [ ] Test deployment locally
- [ ] Review all changes since last release
- [ ] Commit version bump
- [ ] Create annotated Git tag
- [ ] Push commits and tags
- [ ] Create GitHub Release with release notes
- [ ] Update Docker Hub tags (if applicable)

## Version Tag Format

```bash
git tag -a v<VERSION> -m "Version <VERSION> - <TITLE>

<Description>

<Changes>

<Breaking Changes (if any)>

<Migration Guide (if needed)>"
```

## Current Release

```bash
git show v1.0.0
```

**Tag**: v1.0.0  
**Commit**: b02e7c7  
**Date**: November 16, 2025

**Features**:
- Complete AI ChatBot Platform
- Analytics Service with real-time tracking
- OAuth 2.0 authentication
- WebSocket support
- OpenAI integration
- Admin dashboard
- Mobile responsive UI

## Pushing to Remote

```bash
# Push commits
git push origin main

# Push tags
git push origin --tags

# Or push both together
git push origin main --tags
```

## Deleting Tags

If you need to delete a tag:

```bash
# Delete local tag
git tag -d v1.0.0

# Delete remote tag
git push origin --delete v1.0.0
```

## Best Practices

1. **Always use annotated tags** (`-a` flag) for releases
2. **Write meaningful tag messages** with release notes
3. **Update VERSION file** before tagging
4. **Update CHANGELOG.md** for every release
5. **Test thoroughly** before tagging
6. **Use conventional commits** for better history
7. **Tag only on main branch** (or release branch)
8. **Push tags immediately** after creating them

## Conventional Commits

Use these commit prefixes:

- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `style:` - Code style changes (formatting)
- `refactor:` - Code refactoring
- `perf:` - Performance improvements
- `test:` - Test changes
- `chore:` - Build/tooling changes
- `ci:` - CI/CD changes
- `build:` - Build system changes
- `revert:` - Revert previous commit

Example:
```bash
git commit -m "feat: add analytics side panel to chat UI

- Toggleable analytics panel
- Real-time metrics display
- Auto-refresh every 30 seconds"
```

## Release Branches (Optional)

For larger projects, consider release branches:

```bash
# Create release branch
git checkout -b release/1.1.0

# Make release preparations
# Update VERSION, CHANGELOG, docs

# Merge to main
git checkout main
git merge release/1.1.0

# Tag
git tag -a v1.1.0 -m "..."

# Push
git push origin main --tags

# Delete release branch
git branch -d release/1.1.0
```

## Version History

| Version | Date | Description |
|---------|------|-------------|
| 1.0.0 | 2025-11-16 | Initial production release with complete analytics integration |

## Automation (Future)

Consider automating version management:

1. **GitHub Actions** for automated releases
2. **semantic-release** for automated versioning
3. **Changelog automation** with conventional commits
4. **Docker image tagging** with version numbers

## Support

For questions about versioning:
- Check CHANGELOG.md for release notes
- View Git tags: `git tag -l`
- See Git history: `git log --oneline`
- Contact maintainers via GitHub issues
