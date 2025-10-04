# Step-by-Step Commit Guide

## Current Status

You have unstaged changes. Let's commit them in logical groups.

## Step 1: Clean up docs first (optional but recommended)

```powershell
# Run the cleanup script
.\cleanup_docs.ps1

# This will move old docs to specs/archive/
```

## Step 2: Check what changed

```powershell
git status
```

## Step 3: Commit changes one by one

### Commit 1: Remove legacy main.py

```powershell
git add -A
git reset HEAD pyproject.toml README.md specs/ CLAUDE.md PUBLISHING.md CHANGELOG.md .gitignore uv.lock
git status
# Should show only: deleted main.py, deleted server_registry/__main__.py

git commit -m "refactor: remove legacy main.py entry points" -m "- Remove root-level main.py (deprecated)" -m "- Entry point is now: python -m discord_mcp" -m "- CLI remains at cli/main.py for standalone usage"
```

### Commit 2: Update version to alpha

```powershell
git add pyproject.toml
git commit -m "chore: change version to 0.0.1a1 (alpha)" -m "- Version: 0.1.0 to 0.0.1a1" -m "- Mark as alpha in description"
```

### Commit 3: Reorganize specs

```powershell
# If you ran cleanup_docs.ps1, specs/archive/ is ready
git add specs/
git reset HEAD specs/ROADMAP.md specs/README.md specs/implemented/core_tools.md specs/implemented/database.md specs/future/schema/README.md
git status
# Should show moves to specs/future/ and specs/archive/

git commit -m "docs: reorganize specs into implemented/, future/, and archive/" -m "Move unimplemented to specs/future/" -m "Move old planning docs to specs/archive/"
```

### Commit 4: Add new spec documentation

```powershell
git add specs/ROADMAP.md specs/README.md
git add specs/implemented/core_tools.md specs/implemented/database.md
git add specs/future/schema/README.md
git add specs/archive/README.md
git commit -m "docs: add roadmap and implementation documentation" -m "- specs/ROADMAP.md - version planning" -m "- specs/implemented/ - current features" -m "- specs/future/schema/README.md - PostgreSQL warning" -m "- specs/archive/README.md - explain archived docs"
```

### Commit 5: Update README

```powershell
git add README.md
git commit -m "docs: update README for alpha and MCP Inspector" -m "- Mark as ALPHA SOFTWARE" -m "- Add MCP Inspector usage instructions" -m "- Add project status and roadmap"
```

### Commit 6: Add development docs

```powershell
git add CLAUDE.md PUBLISHING.md CHANGELOG.md
git commit -m "docs: add development and publishing guides" -m "- CLAUDE.md - AI assistant guidance" -m "- PUBLISHING.md - PyPI publishing guide" -m "- CHANGELOG.md - version history"
```

### Commit 7: Update .gitignore

```powershell
git add .gitignore
git commit -m "chore: update .gitignore for temp files"
```

### Commit 8: Update uv.lock (optional)

```powershell
git add uv.lock
git commit -m "chore: update uv.lock"
```

## Step 4: Clean up temp files

```powershell
# Delete temp scripts and backups
Remove-Item make_commits.ps1, make_commits.sh, make_commits_fixed.ps1, cleanup_docs.ps1
Remove-Item *.bak -ErrorAction SilentlyContinue
Remove-Item COMMIT_PLAN.md, DOCS_CLEANUP_PLAN.md, RELEASE_CHECKLIST.md, COMMIT_STEPS.md

# Ignore .claude/ directory
git status
# .claude/ should still be untracked - that's fine, .gitignore will handle it
```

## Step 5: Review your commits

```powershell
git log --oneline -8
```

## Done!

Now you can continue testing with MCP Inspector.
