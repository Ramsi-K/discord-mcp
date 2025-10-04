# Publishing to PyPI Guide

This guide explains how to publish the Discord MCP server to PyPI for testing and production releases.

## Version Progression

```
Local Development → Alpha → Beta → Production
  (not on PyPI)    (0.0.x)  (0.1.x)   (1.0.0+)
```

### Version Number Meaning

- **0.0.1a1** = First alpha pre-release
- **0.0.1a2** = Second alpha (with fixes)
- **0.0.1** = Alpha release (stable alpha)
- **0.1.0b1** = First beta pre-release
- **0.1.0** = Beta release
- **1.0.0** = First production release

### When to Publish

| Stage | When | Version | Purpose |
|-------|------|---------|---------|
| **Local** | Now | - | Test with MCP Inspector |
| **Alpha** | After local testing | 0.0.1a1 | Test with Claude Desktop |
| **Beta** | Core features work | 0.1.0b1 | Final testing before v1.0 |
| **Production** | Ready for users | 1.0.0 | Stable public release |

## Prerequisites

### 1. PyPI Accounts

Create accounts on both Test PyPI and real PyPI:

- **Test PyPI**: https://test.pypi.org/account/register/
- **Real PyPI**: https://pypi.org/account/register/

### 2. API Tokens

Generate API tokens for automated uploads:

1. Go to Account Settings → API tokens
2. Create token with scope: "Entire account"
3. Save the token (you won't see it again!)

### 3. Configure Credentials

Create/edit `~/.pypirc` (or `%USERPROFILE%\.pypirc` on Windows):

```ini
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = pypi-YOUR-REAL-PYPI-TOKEN-HERE

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-YOUR-TEST-PYPI-TOKEN-HERE
```

**Security**: Keep this file private! Add to `.gitignore`.

## Pre-Release Checklist

Before publishing, ensure:

- [ ] All tests pass: `uv run pytest`
- [ ] Code is formatted: `uv run black src/ tests/`
- [ ] Imports are sorted: `uv run isort src/ tests/`
- [ ] Version number updated in `pyproject.toml`
- [ ] CHANGELOG.md updated with changes
- [ ] README.md reflects current version
- [ ] All changes committed to git
- [ ] Tests pass with MCP Inspector locally

## Building the Package

### 1. Clean Previous Builds

```bash
# Remove old build artifacts
rm -rf dist/ build/ *.egg-info src/*.egg-info
```

### 2. Build with UV

```bash
# Build source distribution and wheel
uv build
```

### 3. Verify Build

```bash
# Check dist/ directory
ls -lh dist/

# You should see:
# discord_mcp-0.0.1a1.tar.gz          (source distribution)
# discord_mcp-0.0.1a1-py3-none-any.whl (wheel)
```

## Publishing to Test PyPI (ALWAYS DO THIS FIRST!)

### 1. Upload to Test PyPI

```bash
# Using twine (recommended)
uv pip install twine
twine upload --repository testpypi dist/*

# OR using uv publish (if supported)
uv publish --index-url https://test.pypi.org/legacy/
```

### 2. Test Installation from Test PyPI

```bash
# Create a fresh test environment
python -m venv test_env
source test_env/bin/activate  # Windows: test_env\Scripts\activate

# Install from Test PyPI
pip install --index-url https://test.pypi.org/simple/ \
    --extra-index-url https://pypi.org/simple/ \
    discord-mcp

# Note: --extra-index-url allows installing dependencies from real PyPI
```

### 3. Test the Package

```bash
# Test the entry point
python -m discord_mcp --help

# Test with MCP Inspector
npx @modelcontextprotocol/inspector python -m discord_mcp

# Test in Claude Desktop (configure and restart)
```

### 4. Fix Issues (If Any)

If you find issues:

1. Fix the code
2. Increment version (e.g., 0.0.1a1 → 0.0.1a2)
3. Rebuild and re-upload to Test PyPI
4. Test again

## Publishing to Production PyPI

**⚠️ ONLY AFTER Test PyPI testing succeeds!**

### 1. Final Verification

- [ ] Tested on Test PyPI successfully
- [ ] Tested with Claude Desktop
- [ ] No known critical bugs
- [ ] Version number is correct
- [ ] CHANGELOG.md is complete

### 2. Upload to PyPI

```bash
# Using twine
twine upload dist/*

# OR using uv publish
uv publish
```

### 3. Verify on PyPI

- Visit https://pypi.org/project/discord-mcp/
- Check version number
- Verify description displays correctly
- Test README rendering

### 4. Test Installation

```bash
# In a fresh environment
pip install discord-mcp

# Should install version you just published
python -m discord_mcp --version
```

## Git Tagging and Releases

After successful PyPI publish:

### 1. Tag the Release

```bash
# Create annotated tag
git tag -a v0.0.1a1 -m "Alpha release v0.0.1a1"

# Push tag to GitHub
git push origin v0.0.1a1
```

### 2. Create GitHub Release

1. Go to GitHub repository
2. Releases → "Create a new release"
3. Choose the tag you just created
4. Title: "v0.0.1-alpha1"
5. Description: Copy from CHANGELOG.md
6. Check "This is a pre-release" for alpha/beta
7. Attach dist/ files (optional)
8. Publish release

## Version Bumping

### For Next Alpha (0.0.1a1 → 0.0.1a2)

```toml
# pyproject.toml
version = "0.0.1a2"
```

### For Next Beta (0.0.1 → 0.1.0b1)

```toml
# pyproject.toml
version = "0.1.0b1"
```

### For Production (0.1.0 → 1.0.0)

```toml
# pyproject.toml
version = "1.0.0"
```

## Yanking a Release

If you publish a broken version:

```bash
# Mark version as broken (doesn't delete, just hides)
# Users can still install if they specifically request it
# Go to PyPI project page → Manage → Yank release
```

Or via command line:

```bash
# Not recommended - contact PyPI support for deletions
```

## Troubleshooting

### Error: File already exists

You can't re-upload the same version. Solutions:

1. Increment version number (e.g., 0.0.1a1 → 0.0.1a2)
2. Use Test PyPI for testing
3. Delete from Test PyPI (allowed) and re-upload

### Error: Invalid credentials

- Check `~/.pypirc` has correct token
- Ensure username is `__token__` (not your username!)
- Verify token hasn't expired

### Error: Package name already taken

- Choose a different name in pyproject.toml
- Or request name transfer if you own it

### README not rendering

- Ensure README.md is valid markdown
- Check `readme = "README.md"` in pyproject.toml
- Test locally: `python -m readme_renderer README.md`

## Automation (Future)

For automated releases, consider:

- **GitHub Actions**: Auto-publish on tag push
- **Version bumping**: Use `bump2version` or `commitizen`
- **Changelog**: Auto-generate from commits

Example GitHub Action:

```yaml
# .github/workflows/publish.yml
name: Publish to PyPI

on:
  push:
    tags:
      - 'v*'

jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
      - run: pip install uv
      - run: uv build
      - run: uv publish
        env:
          PYPI_TOKEN: ${{ secrets.PYPI_TOKEN }}
```

## Security Best Practices

1. **Never commit tokens** - Use `.gitignore` for `.pypirc`
2. **Use API tokens** - Not username/password
3. **Limit token scope** - Per-project when possible
4. **Rotate tokens** - Periodically update
5. **Test PyPI first** - Always test before production

## Support

- PyPI Help: https://pypi.org/help/
- Packaging Guide: https://packaging.python.org/
- UV Docs: https://docs.astral.sh/uv/

---

**Remember**: Test PyPI → Real PyPI. Always test first!
