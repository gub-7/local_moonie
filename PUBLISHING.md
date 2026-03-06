# Publishing to PyPI

This guide explains how to publish moonshot-local to PyPI.

## Prerequisites

1. **PyPI Account**: Create accounts on both:
   - Test PyPI: https://test.pypi.org/account/register/
   - PyPI: https://pypi.org/account/register/

2. **Install build tools**:
```bash
pip install --upgrade build twine
```

3. **Configure PyPI credentials**:

Create `~/.pypirc`:
```ini
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = pypi-YOUR-API-TOKEN-HERE

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-YOUR-TEST-API-TOKEN-HERE
```

Get API tokens from:
- PyPI: https://pypi.org/manage/account/token/
- Test PyPI: https://test.pypi.org/manage/account/token/

## Pre-release Checklist

- [ ] Update version in `pyproject.toml`
- [ ] Update `CHANGELOG.md` with release notes
- [ ] Update GitHub URLs in `pyproject.toml` to your actual repository
- [ ] Ensure all tests pass
- [ ] Ensure README.md is complete and accurate
- [ ] Commit all changes

## Build the Package

```bash
# Clean previous builds
rm -rf dist/ build/ *.egg-info

# Build source distribution and wheel
python -m build
```

This creates:
- `dist/moonshot-local-0.1.0.tar.gz` (source distribution)
- `dist/moonshot_local-0.1.0-py3-none-any.whl` (wheel)

## Test on Test PyPI First

```bash
# Upload to Test PyPI
python -m twine upload --repository testpypi dist/*

# Test installation from Test PyPI
pip install --index-url https://test.pypi.org/simple/ moonshot-local

# Test the installed package
moonshot-local --help
```

## Publish to PyPI

Once testing is successful:

```bash
# Upload to PyPI
python -m twine upload dist/*
```

## Verify Installation

```bash
# Install from PyPI
pip install moonshot-local

# Test
moonshot-local --help
```

## Post-release

1. Create a git tag:
```bash
git tag -a v0.1.0 -m "Release v0.1.0"
git push origin v0.1.0
```

2. Create a GitHub release with the CHANGELOG notes

3. Update version in `pyproject.toml` to next development version (e.g., `0.2.0-dev`)

## Updating the Package

For subsequent releases:

1. Update version in `pyproject.toml`
2. Update `CHANGELOG.md`
3. Commit changes
4. Rebuild: `python -m build`
5. Upload: `python -m twine upload dist/*`
6. Tag and push

## Common Issues

### Issue: README not displaying on PyPI
- Ensure `readme = "README.md"` is in `pyproject.toml`
- Ensure README.md uses standard Markdown

### Issue: Missing files in distribution
- Check `MANIFEST.in` includes all necessary files
- Rebuild package

### Issue: Import errors after installation
- Ensure `[tool.setuptools]` packages list is correct
- Check `__init__.py` files exist in all packages

### Issue: CLI command not found
- Ensure `[project.scripts]` is correct in `pyproject.toml`
- Reinstall package

## Package Structure for PyPI

```
moonshot-local/
├── moonshot_local/          # Main package
│   ├── __init__.py
│   └── app/
│       ├── __init__.py
│       └── *.py
├── README.md                # Package description
├── LICENSE                  # MIT License
├── pyproject.toml           # Package metadata
├── MANIFEST.in              # Include non-Python files
├── CHANGELOG.md             # Version history
└── .env.example             # Example config
```

## Version Numbering

Follow [Semantic Versioning](https://semver.org/):
- **Major** (X.0.0): Breaking changes
- **Minor** (0.X.0): New features, backwards compatible
- **Patch** (0.0.X): Bug fixes

Examples:
- `0.1.0` - Initial release
- `0.1.1` - Bug fixes
- `0.2.0` - New features
- `1.0.0` - Stable release

## Distribution Checklist

Before each release:

- [ ] All tests pass
- [ ] Documentation is up to date
- [ ] CHANGELOG.md is updated
- [ ] Version is bumped
- [ ] README.md is accurate
- [ ] Dependencies are pinned appropriately
- [ ] License is included
- [ ] GitHub URLs are correct
- [ ] Package builds without errors
- [ ] Package installs correctly
- [ ] CLI command works
- [ ] Test on Test PyPI first

## Resources

- PyPI: https://pypi.org/
- Test PyPI: https://test.pypi.org/
- Python Packaging Guide: https://packaging.python.org/
- Twine docs: https://twine.readthedocs.io/
- Setuptools docs: https://setuptools.pypa.io/

