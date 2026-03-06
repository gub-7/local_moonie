# AUR Packaging Summary

## What Was Done

This project has been prepared for packaging as `python-local_moonie` in the Arch User Repository (AUR).

### 1. Created AUR Package Files (`aur/` directory)

- **PKGBUILD** - Main build script for the AUR package
  - Package name: `python-local_moonie`
  - Pulls source from GitHub releases or PyPI
  - Installs via `python-build` and `python-installer`
  - Includes systemd service and config file
  - Installs to standard system locations

- **.SRCINFO** - AUR metadata file
  - Generated from PKGBUILD
  - Must be regenerated after any PKGBUILD changes

- **local_moonie.service** - Generic systemd service file
  - Uses `/etc/local-moonie/config.env` for configuration
  - Runs the installed `local_moonie` binary
  - System-wide service (not user-specific)

- **python-local_moonie.install** - Post-install messages
  - Guides users through setup after installation
  - Shows how to configure Ollama
  - Explains how to start the service

- **README.md** - AUR packaging guide
  - Instructions for testing the package locally
  - Steps to publish to AUR
  - Update procedures for new versions

### 2. Updated Application Code

#### `moonshot_local/app/config.py`
- **Added multi-location env file search**:
  1. `./.env` (current directory - for development)
  2. `/etc/local-moonie/config.env` (system-wide - for AUR install)
  3. Falls back to environment variables

- **Added `get_env_file_path()` method**:
  - Returns the absolute path of the loaded env file
  - Returns `None` if no file was found (env vars only)

#### `moonshot_local/app/main.py`
- **Added config file path logging on startup**:
  - Logs the actual file path being used for configuration
  - Shows "environment variables only" if no file was found
  - Users always know where their config is coming from

#### `.env.example`
- **Updated with better defaults and comments**:
  - `API_KEY=` (empty by default = no auth required)
  - Added explanatory comments for each section
  - Made it truly "ready to use" without edits

#### `README.md`
- **Added AUR installation instructions**:
  - `yay -S python-local_moonie` as Option A
  - Documented config file location for AUR install
  - Added note about config path logging

### 3. Key Features

#### Configuration File Discovery
When the service starts, it:
1. Searches for config files in order
2. Loads the first one found
3. **Logs the absolute path** of the loaded file
4. Falls back to environment variables if no file found

Example output:
```
INFO: Starting local_moonie proxy
INFO: Configuration loaded from: /etc/local-moonie/config.env
INFO: Ollama host: http://127.0.0.1:11434
INFO: Ollama model: llama3.2:3b
INFO: Listening on: 127.0.0.1:8080
```

#### Default Configuration
The installed config at `/etc/local-moonie/config.env` has valid defaults:
- Ollama on localhost:11434
- llama3.2:3b model
- No API key required (empty = no auth)
- Server on localhost:8080
- Visible browser (not headless)

Works out-of-the-box after installing Ollama and pulling models.

## Installation Methods

### For End Users (via AUR)
```bash
# Install the package
yay -S python-local_moonie

# Configure (optional - defaults work)
sudo nano /etc/local-moonie/config.env

# Start the service
systemctl --user enable --now local_moonie.service

# Or run directly
local_moonie
```

### For Development
```bash
# Clone and install
git clone https://github.com/gub-7/local_moonie.git
cd local_moonie
pip install -e .

# Configure
cp .env.example .env
nano .env

# Run
local_moonie
```

## Publishing to AUR

### Prerequisites
1. AUR account: https://aur.archlinux.org
2. SSH key added to AUR account
3. Package tested locally with `makepkg -si`

### Steps
```bash
# 1. Update PKGBUILD placeholders
cd aur/
nano PKGBUILD  # Update GitHub URL, maintainer info

# 2. Test build
makepkg -si

# 3. Verify with namcap (optional but recommended)
namcap PKGBUILD
namcap python-local_moonie-*.pkg.tar.zst

# 4. Update checksums (after GitHub release)
makepkg -g >> PKGBUILD
# Move the generated sums to sha256sums array

# 5. Regenerate .SRCINFO
makepkg --printsrcinfo > .SRCINFO

# 6. Clone AUR repo
git clone ssh://aur@aur.archlinux.org/python-local_moonie.git aur-repo
cd aur-repo

# 7. Copy files
cp ../PKGBUILD ../. SRCINFO ../local_moonie.service ../python-local_moonie.install .

# 8. Commit and push
git add .
git commit -m "Initial release: local_moonie 0.1.0"
git push
```

### After Publishing
Users can install with:
```bash
yay -S python-local_moonie
```

## File Locations After Installation

| File | Location | Purpose |
|------|----------|---------|
| Binary | `/usr/bin/local_moonie` | CLI entry point |
| Python package | `/usr/lib/python3.*/site-packages/moonshot_local/` | Application code |
| Config | `/etc/local-moonie/config.env` | System-wide configuration |
| Service | `/usr/lib/systemd/system/local_moonie.service` | Systemd service |
| License | `/usr/share/licenses/python-local_moonie/LICENSE` | MIT license |
| Docs | `/usr/share/doc/python-local_moonie/README.md` | Documentation |

## Updating the Package

When releasing a new version (e.g., 0.2.0):

1. **Update version in project**:
   - `pyproject.toml`: `version = "0.2.0"`
   - Create GitHub release: `v0.2.0`

2. **Update PKGBUILD**:
   ```bash
   pkgver=0.2.0
   pkgrel=1  # Reset to 1 for new version
   ```

3. **Update checksums**:
   ```bash
   makepkg -g
   ```

4. **Regenerate .SRCINFO**:
   ```bash
   makepkg --printsrcinfo > .SRCINFO
   ```

5. **Test**:
   ```bash
   makepkg -si
   ```

6. **Push to AUR**:
   ```bash
   git commit -am "Update to 0.2.0"
   git push
   ```

## Dependencies

### Runtime Dependencies (automatically installed by AUR)
- `python>=3.11`
- `python-fastapi`
- `python-uvicorn`
- `python-pydantic`
- `python-selenium`
- `python-httpx`
- `python-dotenv`

### Optional Dependencies (user must install manually)
- `ollama` - Required for LLM generation
- `firefox` - Required for web search
- `geckodriver` - Required for web search

## Testing Checklist

Before publishing to AUR, verify:

- [ ] PKGBUILD builds successfully: `makepkg -si`
- [ ] No namcap warnings: `namcap PKGBUILD`
- [ ] Binary works: `local_moonie --help` or just `local_moonie`
- [ ] Config file installed: `ls /etc/local-moonie/config.env`
- [ ] Service file installed: `ls /usr/lib/systemd/system/local_moonie.service`
- [ ] Service can start: `systemctl --user start local_moonie`
- [ ] Config path logged: `journalctl --user -u local_moonie | grep "Configuration loaded"`
- [ ] License installed: `ls /usr/share/licenses/python-local_moonie/`
- [ ] Docs installed: `ls /usr/share/doc/python-local_moonie/`
- [ ] Uninstall clean: `yay -Rns python-local_moonie`

## Support

- **AUR Guidelines**: https://wiki.archlinux.org/title/AUR_submission_guidelines
- **PKGBUILD Reference**: https://wiki.archlinux.org/title/PKGBUILD
- **Python Packaging**: https://wiki.archlinux.org/title/Python_package_guidelines

## Notes

- The package name `python-local_moonie` follows AUR conventions for Python packages
- The PyPI package name is `local_moonie` (different from AUR name)
- The binary is called `local_moonie` (from pyproject.toml entry point)
- Config file has `0640` permissions (readable by owner and group only)
- The `.install` file provides helpful post-install messages
- The service logs config file path on every startup for transparency

