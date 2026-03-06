# Version Management Guide

## Current Version: 0.1.0

## Where Version is Stored

The version number appears in **3 places** that must be kept in sync:

1. **`pyproject.toml`** (line 3)
   ```toml
   version = "0.1.0"
   ```

2. **`local_moonie/__init__.py`** (line 2)
   ```python
   __version__ = "0.1.0"
   ```

3. **`aur/PKGBUILD`** (line 6)
   ```bash
   pkgver=0.1.0
   ```

4. **`aur/.SRCINFO`** (line 3) - Auto-generated, don't edit manually
   ```
   pkgver = 0.1.0
   ```

## Semantic Versioning

This project uses [Semantic Versioning](https://semver.org/): `MAJOR.MINOR.PATCH`

- **MAJOR** (0.x.x): Breaking changes, incompatible API changes
- **MINOR** (x.1.x): New features, backwards-compatible
- **PATCH** (x.x.1): Bug fixes, backwards-compatible

### Examples:
- `0.1.0` → `0.1.1` - Bug fix
- `0.1.0` → `0.2.0` - New feature
- `0.1.0` → `1.0.0` - First stable release, or breaking change

## How to Increment Version

### Method 1: Manual (Simple)

**Step 1: Update pyproject.toml**
```bash
nano pyproject.toml
# Change line 3: version = "0.1.0" → version = "0.2.0"
```

**Step 2: Update local_moonie/__init__.py**
```bash
nano local_moonie/__init__.py
# Change line 2: __version__ = "0.1.0" → __version__ = "0.2.0"
```

**Step 3: Update aur/PKGBUILD**
```bash
nano aur/PKGBUILD
# Change line 6: pkgver=0.1.0 → pkgver=0.2.0
# Change line 7: pkgrel=1 (reset to 1 for new version)
```

**Step 4: Regenerate aur/.SRCINFO**
```bash
cd aur/
makepkg --printsrcinfo > .SRCINFO
```

### Method 2: Using sed (Automated)

```bash
# Set new version
NEW_VERSION="0.2.0"

# Update pyproject.toml
sed -i "s/^version = .*/version = \"$NEW_VERSION\"/" pyproject.toml

# Update __init__.py
sed -i "s/^__version__ = .*/__version__ = \"$NEW_VERSION\"/" local_moonie/__init__.py

# Update PKGBUILD
sed -i "s/^pkgver=.*/pkgver=$NEW_VERSION/" aur/PKGBUILD
sed -i "s/^pkgrel=.*/pkgrel=1/" aur/PKGBUILD

# Regenerate .SRCINFO
cd aur/
makepkg --printsrcinfo > .SRCINFO
cd ..

echo "✅ Version updated to $NEW_VERSION"
```

### Method 3: Create a version bump script

Create `bump_version.sh`:
```bash
#!/usr/bin/env bash
# Version bump script

if [ -z "$1" ]; then
    echo "Usage: ./bump_version.sh <new_version>"
    echo "Example: ./bump_version.sh 0.2.0"
    exit 1
fi

NEW_VERSION="$1"

echo "🔄 Updating version to $NEW_VERSION..."

# Update pyproject.toml
sed -i "s/^version = .*/version = \"$NEW_VERSION\"/" pyproject.toml
echo "✅ Updated pyproject.toml"

# Update __init__.py
sed -i "s/^__version__ = .*/__version__ = \"$NEW_VERSION\"/" local_moonie/__init__.py
echo "✅ Updated local_moonie/__init__.py"

# Update PKGBUILD
sed -i "s/^pkgver=.*/pkgver=$NEW_VERSION/" aur/PKGBUILD
sed -i "s/^pkgrel=.*/pkgrel=1/" aur/PKGBUILD
echo "✅ Updated aur/PKGBUILD"

# Regenerate .SRCINFO
cd aur/
makepkg --printsrcinfo > .SRCINFO
cd ..
echo "✅ Regenerated aur/.SRCINFO"

echo ""
echo "🎉 Version bumped to $NEW_VERSION!"
echo ""
echo "Next steps:"
echo "1. Review changes: git diff"
echo "2. Update CHANGELOG.md with changes"
echo "3. Commit: git commit -am 'Bump version to $NEW_VERSION'"
echo "4. Tag: git tag v$NEW_VERSION"
echo "5. Build: python -m build"
echo "6. Publish to PyPI: python -m twine upload dist/local_moonie-$NEW_VERSION*"
echo "7. Push: git push && git push --tags"
echo "8. Create GitHub release"
echo "9. Update AUR package"
```

Make it executable:
```bash
chmod +x bump_version.sh
```

Use it:
```bash
./bump_version.sh 0.2.0
```

## After Updating Version

### 1. Update CHANGELOG.md
Document what changed in this version:
```markdown
## [0.2.0] - 2024-03-06

### Added
- New feature X
- New feature Y

### Fixed
- Bug Z

### Changed
- Improved performance of W
```

### 2. Commit the changes
```bash
git add pyproject.toml local_moonie/__init__.py aur/PKGBUILD aur/.SRCINFO CHANGELOG.md
git commit -m "Bump version to 0.2.0"
```

### 3. Create a git tag
```bash
git tag v0.2.0
git push origin main
git push origin v0.2.0
```

### 4. Build the package
```bash
# Clean old builds
rm -rf dist/ build/ *.egg-info/

# Build new version
python -m build
```

### 5. Publish to PyPI
```bash
python -m twine upload dist/local_moonie-0.2.0*
```

### 6. Create GitHub Release
Go to: https://github.com/gub-7/local_moonie/releases/new
- Tag: `v0.2.0`
- Title: `v0.2.0`
- Description: Copy from CHANGELOG.md
- Attach: `dist/local_moonie-0.2.0.tar.gz`

### 7. Update AUR Package
```bash
cd aur/

# Update checksums after PyPI publish
makepkg -g
# Copy the sha256sums and update PKGBUILD

# Regenerate .SRCINFO
makepkg --printsrcinfo > .SRCINFO

# Commit to AUR
cd /path/to/aur-repo/
cp ../aur/PKGBUILD .
cp ../aur/.SRCINFO .
git commit -am "Update to 0.2.0"
git push
```

## PKGBUILD pkgrel

The `pkgrel` in PKGBUILD is separate from the version:

- **pkgver**: The upstream version (0.1.0, 0.2.0, etc.)
- **pkgrel**: The package release number (starts at 1)

**When to increment pkgrel:**
- You fix the PKGBUILD without changing the upstream version
- Example: Fix dependencies, change build options

**When to reset pkgrel to 1:**
- Every time you bump pkgver to a new version

Example:
```bash
pkgver=0.1.0
pkgrel=1  # First package of 0.1.0

# Later, fix PKGBUILD
pkgver=0.1.0
pkgrel=2  # Second package of 0.1.0

# New version released
pkgver=0.2.0
pkgrel=1  # Reset to 1 for new version
```

## Quick Reference

```bash
# Current version
grep "^version" pyproject.toml
grep "__version__" local_moonie/__init__.py
grep "^pkgver" aur/PKGBUILD

# Bump version (manual)
# 1. Edit pyproject.toml
# 2. Edit local_moonie/__init__.py
# 3. Edit aur/PKGBUILD (pkgver and reset pkgrel=1)
# 4. cd aur/ && makepkg --printsrcinfo > .SRCINFO

# Bump version (automated)
./bump_version.sh 0.2.0

# After version bump
# 1. Update CHANGELOG.md
# 2. git commit -am "Bump version to 0.2.0"
# 3. git tag v0.2.0
# 4. python -m build
# 5. python -m twine upload dist/*
# 6. git push && git push --tags
# 7. Create GitHub release
# 8. Update AUR package
```

## Version History

- **0.1.0** (2024-03-06) - Initial release
  - OpenAI-compatible API
  - Firefox/Selenium search
  - Ollama backend
  - Avante.nvim integration

## Tips

1. **Always keep versions in sync** across all files
2. **Use semantic versioning** for clarity
3. **Update CHANGELOG.md** with each version
4. **Tag releases in git** for easy tracking
5. **Test before publishing** - build and install locally first
6. **Regenerate .SRCINFO** after every PKGBUILD change

## Checking Current Version

```bash
# From Python
python -c "import local_moonie; print(local_moonie.__version__)"

# From installed binary
local-moonie --version  # (if you add --version support)

# From files
grep "^version" pyproject.toml
```

