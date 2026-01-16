# Release Management

Comprehensive guide for managing GitHub releases using the gh CLI.

## Table of Contents
- [Viewing Releases](#viewing-releases)
- [Creating Releases](#creating-releases)
- [Editing Releases](#editing-releases)
- [Deleting Releases](#deleting-releases)
- [Managing Assets](#managing-assets)
- [Release Notes](#release-notes)
- [Common Workflows](#common-workflows)

## Viewing Releases

### List releases
```bash
# List all releases
gh release list

# Limit results
gh release list --limit 20

# Exclude drafts and pre-releases
gh release list --exclude-drafts --exclude-pre-releases

# Get JSON output
gh release list --json tagName,name,publishedAt,isPrerelease,isDraft

# List only pre-releases
gh release list --json tagName,isPrerelease --jq '.[] | select(.isPrerelease == true)'

# List only draft releases
gh release list --json tagName,isDraft --jq '.[] | select(.isDraft == true)'
```

### View specific release
```bash
# View latest release
gh release view

# View specific release by tag
gh release view v1.0.0

# View release in browser
gh release view v1.0.0 --web

# Get JSON output
gh release view v1.0.0 --json tagName,name,body,publishedAt,assets

# View release notes only
gh release view v1.0.0 --json body --jq -r .body

# List release assets
gh release view v1.0.0 --json assets --jq '.assets[] | {name: .name, size: .size}'
```

### Download release
```bash
# Download all assets from latest release
gh release download

# Download all assets from specific release
gh release download v1.0.0

# Download specific asset
gh release download v1.0.0 --pattern "*.tar.gz"
gh release download v1.0.0 --pattern "app-*"

# Download to specific directory
gh release download v1.0.0 --dir ./downloads

# Download archive (not including assets)
gh release download v1.0.0 --archive tar.gz
gh release download v1.0.0 --archive zip

# Skip existing files
gh release download v1.0.0 --skip-existing
```

## Creating Releases

### Create release
```bash
# Create release (interactive)
gh release create v1.0.0

# Create release with title and notes
gh release create v1.0.0 --title "Version 1.0.0" --notes "First stable release"

# Create release with notes from file
gh release create v1.0.0 --title "v1.0.0" --notes-file CHANGELOG.md

# Create release with auto-generated notes
gh release create v1.0.0 --generate-notes

# Create draft release
gh release create v1.0.0 --draft --notes "WIP release"

# Create pre-release
gh release create v1.0.0-beta.1 --prerelease --notes "Beta release"

# Create release with target commitish
gh release create v1.0.0 --target main --notes "Release from main"
gh release create v1.0.0 --target abc123 --notes "Release from commit"

# Create release and set as latest
gh release create v1.0.0 --latest --notes "Latest release"

# Create release but don't mark as latest
gh release create v1.0.1-hotfix --latest=false --notes "Hotfix release"
```

### Create release with assets
```bash
# Create release and upload files
gh release create v1.0.0 \
  --title "Version 1.0.0" \
  --notes "Release with binaries" \
  dist/app-linux.tar.gz \
  dist/app-macos.tar.gz \
  dist/app-windows.zip

# Upload with glob pattern
gh release create v1.0.0 --notes "Release" dist/*.tar.gz

# Upload with labels
gh release create v1.0.0 \
  --notes "Release" \
  dist/app.tar.gz#"Application Binary (Linux)" \
  dist/checksums.txt#"SHA256 Checksums"
```

### Create release from tag
```bash
# Create tag first
git tag -a v1.0.0 -m "Version 1.0.0"
git push origin v1.0.0

# Create release from existing tag
gh release create v1.0.0 --notes "Release notes"

# Or create tag and release together
gh release create v1.0.0 --target main --notes "Combined tag and release"
```

## Editing Releases

### Edit release metadata
```bash
# Edit release interactively
gh release edit v1.0.0

# Update title
gh release edit v1.0.0 --title "Version 1.0.0 - Stable"

# Update notes
gh release edit v1.0.0 --notes "Updated release notes"

# Update notes from file
gh release edit v1.0.0 --notes-file updated-notes.md

# Convert draft to published
gh release edit v1.0.0 --draft=false

# Convert to draft
gh release edit v1.0.0 --draft

# Mark as pre-release
gh release edit v1.0.0 --prerelease

# Mark as stable release
gh release edit v1.0.0 --prerelease=false

# Set as latest release
gh release edit v1.0.0 --latest

# Remove latest tag
gh release edit v1.0.0 --latest=false

# Update discussion category
gh release edit v1.0.0 --discussion-category "Announcements"
```

## Deleting Releases

### Delete release
```bash
# Delete release (keeps tag)
gh release delete v1.0.0

# Delete release with confirmation
gh release delete v1.0.0 --yes

# Delete release and tag
gh release delete v1.0.0 --yes && git push origin :refs/tags/v1.0.0

# Delete release but cleanup later
gh release delete v1.0.0 --cleanup-tag
```

### Delete old releases
```bash
# List releases older than 1 year
gh release list --json tagName,publishedAt --jq '
  .[] |
  select(.publishedAt < (now - 31536000 | strftime("%Y-%m-%dT%H:%M:%SZ"))) |
  .tagName
'

# Delete old pre-releases
gh release list --json tagName,isPrerelease --jq '
  .[] | select(.isPrerelease == true) | .tagName
' | xargs -I {} gh release delete {} --yes
```

## Managing Assets

### Upload assets
```bash
# Upload asset to existing release
gh release upload v1.0.0 dist/app.tar.gz

# Upload multiple assets
gh release upload v1.0.0 dist/*.tar.gz

# Upload with clobber (overwrite existing)
gh release upload v1.0.0 dist/app.tar.gz --clobber

# Upload with label
gh release upload v1.0.0 dist/app.tar.gz#"Linux Binary"
```

### Delete assets
```bash
# Delete asset by name
gh release delete-asset v1.0.0 app.tar.gz

# Delete with confirmation
gh release delete-asset v1.0.0 app.tar.gz --yes

# Delete all assets
gh release view v1.0.0 --json assets --jq '.assets[].name' \
  | xargs -I {} gh release delete-asset v1.0.0 {} --yes
```

### Download specific assets
```bash
# Download by pattern
gh release download v1.0.0 --pattern "*.tar.gz"

# Download specific file
gh release download v1.0.0 --pattern "app-linux-amd64.tar.gz"

# Download source code
gh release download v1.0.0 --archive tar.gz
```

## Release Notes

### Auto-generated release notes
```bash
# Generate notes from commits
gh release create v1.0.0 --generate-notes

# Generate notes with custom configuration
gh release create v1.0.0 --generate-notes --notes-start-tag v0.9.0

# View generated notes without creating
gh api repos/:owner/:repo/releases/generate-notes \
  -f tag_name=v1.0.0 \
  -f target_commitish=main \
  --jq .body
```

### Release notes configuration
```yaml
# .github/release.yml
changelog:
  exclude:
    labels:
      - ignore-for-release
    authors:
      - dependabot
  categories:
    - title: Breaking Changes 🛠
      labels:
        - breaking-change
    - title: New Features 🎉
      labels:
        - enhancement
        - feature
    - title: Bug Fixes 🐛
      labels:
        - bug
        - fix
    - title: Documentation 📚
      labels:
        - documentation
        - docs
    - title: Other Changes
      labels:
        - "*"
```

### Custom release notes
```bash
# Generate custom release notes
cat > notes.md << 'EOF'
## What's Changed

### New Features
* Added dark mode support
* Improved performance by 50%

### Bug Fixes
* Fixed login issue (#123)
* Resolved memory leak (#124)

### Breaking Changes
* Removed deprecated API endpoints

**Full Changelog**: https://github.com/owner/repo/compare/v0.9.0...v1.0.0
EOF

gh release create v1.0.0 --notes-file notes.md
```

### Template-based release notes
```bash
# Create template
cat > release-template.md << 'EOF'
## Release {{VERSION}}

Released on {{DATE}}

### Highlights
{{HIGHLIGHTS}}

### Changes
{{CHANGELOG}}

### Installation
Download the appropriate binary for your platform from the assets below.

### Contributors
Thank you to all contributors! 🎉
EOF

# Use with substitution
VERSION="v1.0.0"
DATE=$(date +%Y-%m-%d)
HIGHLIGHTS="Major performance improvements"
CHANGELOG=$(git log v0.9.0..v1.0.0 --pretty=format:"* %s" --no-merges)

envsubst < release-template.md | gh release create "$VERSION" --notes-file -
```

## Common Workflows

### Workflow 1: Standard release process

```bash
# 1. Update version in code
sed -i 's/VERSION = ".*"/VERSION = "1.0.0"/' version.py

# 2. Update changelog
cat >> CHANGELOG.md << EOF

## [1.0.0] - $(date +%Y-%m-%d)

### Added
- New feature X
- New feature Y

### Fixed
- Bug fix Z

EOF

# 3. Commit changes
git add version.py CHANGELOG.md
git commit -m "chore: bump version to 1.0.0"
git push

# 4. Create and push tag
git tag -a v1.0.0 -m "Release v1.0.0"
git push origin v1.0.0

# 5. Build release artifacts
make build
# Creates files in dist/

# 6. Create GitHub release with artifacts
gh release create v1.0.0 \
  --title "Version 1.0.0" \
  --notes-file CHANGELOG.md \
  dist/*

# 7. Verify release
gh release view v1.0.0 --web
```

### Workflow 2: Pre-release workflow

```bash
# Create beta release
gh release create v2.0.0-beta.1 \
  --prerelease \
  --generate-notes \
  --title "v2.0.0 Beta 1" \
  dist/*

# After testing, create RC
gh release create v2.0.0-rc.1 \
  --prerelease \
  --notes "Release candidate for v2.0.0" \
  dist/*

# When ready, create final release
gh release create v2.0.0 \
  --generate-notes \
  --title "Version 2.0.0" \
  dist/*
```

### Workflow 3: Hotfix release

```bash
# Create hotfix branch
git checkout -b hotfix/1.0.1 v1.0.0

# Apply fix
# ... make changes ...
git commit -am "fix: critical bug"

# Create hotfix release
gh release create v1.0.1 \
  --target hotfix/1.0.1 \
  --title "v1.0.1 Hotfix" \
  --notes "Critical bug fix for v1.0.0" \
  --latest=false \
  dist/*

# Merge back to main
git checkout main
git merge hotfix/1.0.1
git push
```

### Workflow 4: Automated release with CI

```yaml
# .github/workflows/release.yml
name: Release
on:
  push:
    tags:
      - 'v*'

jobs:
  release:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Build artifacts
        run: |
          make build
          cd dist && sha256sum * > checksums.txt

      - name: Create Release
        env:
          GH_TOKEN: ${{ github.token }}
        run: |
          gh release create ${{ github.ref_name }} \
            --generate-notes \
            --title "Release ${{ github.ref_name }}" \
            dist/*
```

```bash
# Trigger release by pushing tag
git tag v1.0.0
git push origin v1.0.0
# CI automatically creates release with artifacts
```

### Workflow 5: Draft release for review

```bash
# Create draft release
gh release create v1.0.0 \
  --draft \
  --generate-notes \
  --title "Version 1.0.0 (Draft)" \
  dist/*

# Team reviews the release
gh release view v1.0.0 --web

# After approval, publish
gh release edit v1.0.0 --draft=false

# Announce
echo "Released v1.0.0: $(gh release view v1.0.0 --json url --jq .url)"
```

### Workflow 6: Multi-platform release

```bash
# Build for different platforms
make build-linux
make build-macos
make build-windows

# Create release with all platforms
gh release create v1.0.0 \
  --title "Version 1.0.0" \
  --notes "Multi-platform release" \
  dist/app-linux-amd64.tar.gz#"Linux (AMD64)" \
  dist/app-linux-arm64.tar.gz#"Linux (ARM64)" \
  dist/app-darwin-amd64.tar.gz#"macOS (Intel)" \
  dist/app-darwin-arm64.tar.gz#"macOS (Apple Silicon)" \
  dist/app-windows-amd64.zip#"Windows (AMD64)" \
  dist/checksums.txt#"SHA256 Checksums"

# Verify all assets uploaded
gh release view v1.0.0 --json assets --jq '.assets[] | .name'
```

## Advanced Techniques

### Release asset patterns
```bash
# Download source archives
gh release download v1.0.0 --archive tar.gz
gh release download v1.0.0 --archive zip

# Download with multiple patterns
gh release download v1.0.0 --pattern "*.tar.gz" --pattern "*.deb"

# Download and verify checksums
gh release download v1.0.0 --pattern "checksums.txt"
gh release download v1.0.0 --pattern "*.tar.gz"
sha256sum -c checksums.txt
```

### Release notifications
```bash
# Get latest release info for notifications
LATEST=$(gh release view --json tagName,url,publishedAt)
TAG=$(echo "$LATEST" | jq -r .tagName)
URL=$(echo "$LATEST" | jq -r .url)
DATE=$(echo "$LATEST" | jq -r .publishedAt)

# Send notification (example with curl)
curl -X POST https://hooks.slack.com/... \
  -d "{\"text\": \"New release $TAG published: $URL\"}"
```

### Compare releases
```bash
# Get changes between releases
gh api repos/:owner/:repo/compare/v1.0.0...v1.1.0 \
  --jq '{
    commits: .commits | length,
    files_changed: .files | length,
    additions: ([.files[].additions] | add),
    deletions: ([.files[].deletions] | add)
  }'

# Generate comparison URL
echo "https://github.com/owner/repo/compare/v1.0.0...v1.1.0"
```

### Release metrics
```bash
# Count downloads per release
gh release list --json tagName --limit 50 | jq -r '.[].tagName' | while read tag; do
  downloads=$(gh api repos/:owner/:repo/releases/tags/$tag \
    --jq '[.assets[].download_count] | add')
  echo "$tag: $downloads downloads"
done

# Get total download count
gh api repos/:owner/:repo/releases \
  --jq '[.[].assets[].download_count] | add | "Total downloads: \(.)"'

# Latest release stats
gh release view --json tagName,publishedAt,assets \
  --jq '{
    tag: .tagName,
    published: .publishedAt,
    asset_count: (.assets | length),
    total_downloads: ([.assets[].downloadCount] | add)
  }'
```

## Tips and Best Practices

1. **Semantic versioning**: Use semver (MAJOR.MINOR.PATCH)
2. **Tag naming**: Prefix tags with 'v' (v1.0.0, v2.1.3)
3. **Changelog**: Maintain comprehensive changelogs
4. **Pre-releases**: Use for betas and release candidates
5. **Draft releases**: Review before publishing
6. **Release notes**: Auto-generate with proper PR labels
7. **Assets**: Include checksums for verification
8. **Multi-platform**: Build for all target platforms
9. **Automation**: Use CI/CD for consistent releases
10. **Announcements**: Notify users of new releases
11. **Security**: Sign release artifacts when possible
12. **Documentation**: Update docs with each release

## Quick Reference

```bash
# List & View
gh release list                                # List all releases
gh release view                                # View latest release
gh release view v1.0.0                         # View specific release
gh release view v1.0.0 --web                   # View in browser

# Create
gh release create v1.0.0                       # Create release (interactive)
gh release create v1.0.0 --notes "text"        # With notes
gh release create v1.0.0 --generate-notes      # Auto-generate notes
gh release create v1.0.0 --draft               # Create as draft
gh release create v1.0.0 --prerelease          # Create as pre-release
gh release create v1.0.0 file1 file2           # With assets

# Edit
gh release edit v1.0.0                         # Edit interactively
gh release edit v1.0.0 --draft=false           # Publish draft
gh release edit v1.0.0 --latest                # Mark as latest

# Delete
gh release delete v1.0.0                       # Delete release
gh release delete v1.0.0 --yes                 # Skip confirmation

# Assets
gh release upload v1.0.0 file.tar.gz           # Upload asset
gh release upload v1.0.0 file.tar.gz --clobber # Overwrite existing
gh release download v1.0.0                     # Download all assets
gh release download v1.0.0 --pattern "*.tar.gz" # Download by pattern
gh release delete-asset v1.0.0 file.tar.gz     # Delete asset

# Common patterns
gh release create v1.0.0 --generate-notes dist/* # Release with auto-notes
gh release download --pattern "*.deb"            # Download latest .deb files
gh release view --json assets --jq '.assets[].name' # List asset names
```
