#!/usr/bin/env bash
# Version bump script for local_moonie

set -e

if [ -z "$1" ]; then
    echo "Usage: ./bump_version.sh <new_version>"
    echo "Example: ./bump_version.sh 0.2.0"
    echo ""
    echo "Current version:"
    grep "^version" pyproject.toml
    exit 1
fi

NEW_VERSION="$1"

# Validate version format (basic check)
if ! [[ "$NEW_VERSION" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
    echo "❌ Invalid version format: $NEW_VERSION"
    echo "   Expected format: MAJOR.MINOR.PATCH (e.g., 0.2.0)"
    exit 1
fi

echo "🔄 Updating version to $NEW_VERSION..."
echo ""

# Update pyproject.toml
sed -i "s/^version = .*/version = \"$NEW_VERSION\"/" pyproject.toml
echo "✅ Updated pyproject.toml"

# Update __init__.py
sed -i "s/^__version__ = .*/__version__ = \"$NEW_VERSION\"/" local_moonie/__init__.py
echo "✅ Updated local_moonie/__init__.py"

# Update PKGBUILD
sed -i "s/^pkgver=.*/pkgver=$NEW_VERSION/" aur/PKGBUILD
sed -i "s/^pkgrel=.*/pkgrel=1/" aur/PKGBUILD
echo "✅ Updated aur/PKGBUILD (pkgver=$NEW_VERSION, pkgrel=1)"

# Regenerate .SRCINFO
cd aur/
makepkg --printsrcinfo > .SRCINFO
cd ..
echo "✅ Regenerated aur/.SRCINFO"

echo ""
echo "🎉 Version bumped to $NEW_VERSION!"
echo ""
echo "Files changed:"
echo "  - pyproject.toml"
echo "  - local_moonie/__init__.py"
echo "  - aur/PKGBUILD"
echo "  - aur/.SRCINFO"
echo ""
echo "Next steps:"
echo "  1. Review changes: git diff"
echo "  2. Update CHANGELOG.md with changes for v$NEW_VERSION"
echo "  3. Commit: git commit -am 'Bump version to $NEW_VERSION'"
echo "  4. Tag: git tag v$NEW_VERSION"
echo "  5. Build: python -m build"
echo "  6. Test: pip install dist/local_moonie-$NEW_VERSION-py3-none-any.whl"
echo "  7. Publish to PyPI: python -m twine upload dist/local_moonie-$NEW_VERSION*"
echo "  8. Push: git push && git push --tags"
echo "  9. Create GitHub release at: https://github.com/gub-7/local_moonie/releases/new"
echo " 10. Update AUR package with new checksums"
echo ""

