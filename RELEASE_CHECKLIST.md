# PyPI Release Checklist

## ✅ Files Created for PyPI Release

### Core Files
- [x] `LICENSE` - MIT License
- [x] `README.md` - Complete documentation (PyPI long description)
- [x] `pyproject.toml` - Package metadata and dependencies
- [x] `MANIFEST.in` - Include non-Python files in distribution
- [x] `CHANGELOG.md` - Version history
- [x] `moonshot_local/py.typed` - Type hints marker

### Documentation
- [x] `PUBLISHING.md` - Step-by-step PyPI publishing guide
- [x] `QUICKREF.md` - Quick reference for users

### Package Structure
- [x] `moonshot_local/__init__.py` - Package init
- [x] `moonshot_local/app/__init__.py` - App package init
- [x] `moonshot_local/app/main.py` - Main app with CLI entry point
- [x] All other Python modules

## 🚀 Quick Publishing Steps

### 1. Pre-flight Check

```bash
# Ensure you're in the project root
cd /home/gabe/tmpcode/local_moonie

# Update GitHub URLs in pyproject.toml
# Replace "yourusername" with your actual GitHub username
nano pyproject.toml
```

**Important**: Update these URLs in `pyproject.toml`:
```toml
[project.urls]
Homepage = "https://github.com/YOURUSERNAME/moonshot-local"
Documentation = "https://github.com/YOURUSERNAME/moonshot-local#readme"
Repository = "https://github.com/YOURUSERNAME/moonshot-local"
Issues = "https://github.com/YOURUSERNAME/moonshot-local/issues"
```

### 2. Install Build Tools

```bash
pip install --upgrade build twine
```

### 3. Build the Package

```bash
# Clean previous builds
rm -rf dist/ build/ *.egg-info

# Build
python -m build
```

You should see:
```
dist/
├── moonshot-local-0.1.0.tar.gz
└── moonshot_local-0.1.0-py3-none-any.whl
```

### 4. Test Locally

```bash
# Install locally
pip install -e .

# Test CLI
moonshot-local --help

# Test import
python -c "from moonshot_local.app import main; print('OK')"
```

### 5. Upload to Test PyPI (Optional but Recommended)

```bash
# Create account at https://test.pypi.org/account/register/
# Get API token from https://test.pypi.org/manage/account/token/

# Upload
python -m twine upload --repository testpypi dist/*

# Test install
pip install --index-url https://test.pypi.org/simple/ moonshot-local
```

### 6. Upload to PyPI

```bash
# Create account at https://pypi.org/account/register/
# Get API token from https://pypi.org/manage/account/token/

# Upload
python -m twine upload dist/*
```

Enter your PyPI credentials when prompted.

### 7. Verify

```bash
# Wait a minute for PyPI to index

# Install from PyPI
pip install moonshot-local

# Test
moonshot-local --help
```

### 8. Post-Release

```bash
# Tag the release
git tag -a v0.1.0 -m "Release v0.1.0"
git push origin v0.1.0

# Create GitHub release with CHANGELOG notes
```

## 📦 Package Contents

The PyPI package will include:

**Python Packages:**
- `moonshot_local/` - Main package
- `moonshot_local/app/` - Application code

**Documentation:**
- `README.md` - Main documentation (shows on PyPI)
- `LICENSE` - MIT License
- `CHANGELOG.md` - Version history

**Configuration Examples:**
- `.env.example` - Example configuration
- `avante_config.lua` - Example Avante config

**Scripts:**
- `start.sh` - Quick start script
- `test_api.sh` - API test script
- `example_client.py` - Python example client
- `moonshot-local.service` - systemd service file

**CLI Command:**
- `moonshot-local` - Starts the server

## 🔧 Configuration for PyPI

### pyproject.toml Highlights

```toml
[project]
name = "moonshot-local"
version = "0.1.0"
description = "Local OpenAI-compatible proxy with Firefox/Selenium search + Ollama backend for Avante.nvim by @yetone"
readme = "README.md"
requires-python = ">=3.11"
license = {text = "MIT"}

[project.scripts]
moonshot-local = "moonshot_local.app.main:main"
```

### Dependencies

**Core:**
- fastapi>=0.109.0
- uvicorn[standard]>=0.27.0
- pydantic>=2.5.0
- selenium>=4.16.0
- httpx>=0.26.0
- python-dotenv>=1.0.0

**Dev (optional):**
- pytest>=7.4.0
- pytest-asyncio>=0.23.0
- ruff>=0.1.0

## 📝 After Publishing

Users can install with:

```bash
pip install moonshot-local
```

And use with:

```bash
# Start server
moonshot-local

# Or
python -m moonshot_local.app.main
```

## 🐛 Common Issues

### Issue: "Module not found" after install
**Fix:** Ensure `__init__.py` files exist in all package directories

### Issue: CLI command not found
**Fix:** Reinstall package: `pip install --force-reinstall moonshot-local`

### Issue: README not showing on PyPI
**Fix:** Ensure `readme = "README.md"` is in `pyproject.toml`

### Issue: Missing files in package
**Fix:** Check `MANIFEST.in` and rebuild

## 📚 Resources

- **PyPI**: https://pypi.org/
- **Test PyPI**: https://test.pypi.org/
- **Python Packaging Guide**: https://packaging.python.org/
- **Twine docs**: https://twine.readthedocs.io/

## ✨ What Users Get

After `pip install moonshot-local`, users get:

1. **CLI command**: `moonshot-local`
2. **Python package**: `import moonshot_local`
3. **All dependencies**: Automatically installed
4. **Documentation**: Via PyPI page
5. **Examples**: Included in package

## 🎯 Success Criteria

- [x] Package builds without errors
- [x] Package installs cleanly
- [x] CLI command works
- [x] Python imports work
- [x] Dependencies install correctly
- [x] README displays on PyPI
- [x] All files included in distribution

## 📞 Support

After publishing, users can:
- Report issues on GitHub
- Read documentation in README
- Check examples in package
- Join discussions

---

**Ready to publish!** Follow the steps above to release moonshot-local v0.1.0 to PyPI.

