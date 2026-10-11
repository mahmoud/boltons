---
name: release
description: |
	Release boltons to PyPI. Handles version bumping (CalVer YY.MINOR.MICRO),
	tagging, pushing, and post-publish verification. Use when asked to
	"release boltons", "cut a release", "publish to PyPI", or "bump version".
---

# Release boltons

boltons uses CalVer: `YY.MINOR.MICRO` (e.g. `25.1.0`). The version lives in
`boltons/__init__.py` as a `__version__` literal string. During development it
carries a `dev` suffix (e.g. `25.0.1dev`). Flit reads this at build time.

Tags are bare version numbers (e.g. `25.1.0`, NOT `v25.1.0`). The publish
workflow triggers on tags matching `[0-9]*.[0-9]*.[0-9]*`.

## Pre-flight checks

Before starting, verify ALL of these:

1. Working tree is clean (`git status` shows nothing dirty/staged)
2. You are on `master` branch
3. `boltons/__init__.py` has a `dev` suffix on `__version__`
4. All tests pass: `tox -p auto` (or at minimum `pytest tests/ -v`)
5. Check what is actually published on PyPI: https://pypi.org/project/boltons/
   **PyPI is canonical.** If the intended version already exists on PyPI, it
   cannot be re-released -- bump to the next version instead. If a local/GitHub
   tag exists for a version that is NOT on PyPI, the prior release failed and
   should be retried (see "Failed release" under Error recovery).

If any check fails, stop and report. Do not proceed with a dirty tree or
failing tests.

## Release steps

### 1. Determine the release version

Read `__version__` from `boltons/__init__.py`. Strip the `dev` suffix.
Example: `25.0.1dev` becomes `25.0.1`.

Ask the user to confirm the version. If they want a different version
(e.g. bumping minor instead of micro), use that instead.

### 2. Update version for release

Edit `boltons/__init__.py`: remove the `dev` suffix from `__version__`.

```python
# Before
__version__ = '25.0.1dev'
# After
__version__ = '25.0.1'
```

### 3. Update CHANGELOG.md

Add a new section at the top of `CHANGELOG.md` (below the `# boltons Changelog`
heading and the intro paragraph) for the release version. Use this format:

```markdown
## 25.0.1

_(Month Day, Year)_

- First change description
- Second change description
```

To determine what changed, review the commits since the last tag:

```bash
git log $(git describe --tags --abbrev=0)..HEAD --pretty=format:'%s' --no-merges
```

Summarize the user-facing changes as concise bullet points. Omit version bump
commits and other release-mechanical commits. Ask the user to confirm or adjust
the changelog entry.

### 4. Commit the release

```bash
git commit -am "boltons version 25.0.1"
```

Use the exact format `boltons version X.Y.Z` for the commit message.

### 5. Tag the release

```bash
git tag -a 25.0.1 -m "short summary of key changes in this release"
```

Tags are bare version numbers (no `v` prefix). The tag message should be a
short, lowercase, descriptive summary of the release (not just the version
number). Examples:

- `"fix omd equality, bytes2human boundary, tbutils crash"`
- `"python 3.14 support, frozen structures"`
- `"modernize build system, drop python 3.7"`

### 6. Bump to next dev version

Increment the micro version and add `dev` suffix:

```python
__version__ = '25.0.2dev'
```

### 7. Commit the dev bump

```bash
git commit -am "bump version to 25.0.2dev"
```

### 8. Push

```bash
git push origin master --tags
```

This triggers two GitHub Actions workflows:
- `Tests` (on the push to master)
- `Publish to PyPI` (on the tag)

The publish workflow validates that `__version__` on the tagged commit does
not contain `dev` and matches the tag. It parses `__version__` from the file
with `sed` rather than importing the module (the build job does not install
dependencies). If either check fails, publishing is blocked.

The `pypi` deployment environment has a wait timer. The publish job will show
`status: waiting` during this period — it auto-approves after the timer
expires.

### 9. Create GitHub release

```bash
gh release create 25.0.1 --title "25.0.1" --notes "<changelog entries>"
```

Use the changelog bullet points as the release notes body. Include a
`**Full Changelog**` link comparing the previous tag to the new one:
`https://github.com/mahmoud/boltons/compare/PREV...NEW` (bare tags).

## Post-publish verification

After pushing, wait ~2 minutes for PyPI propagation, then verify in a
temporary virtualenv **outside the repo** (to avoid the local source tree
shadowing the installed package):

```bash
python3 -m venv /tmp/boltons-verify && source /tmp/boltons-verify/bin/activate
pip install boltons==25.0.1 --index-url https://pypi.org/simple/
cd /tmp  # MUST leave repo root so local boltons/ does not shadow the install
python -c "import boltons; print(boltons.__version__)"
# Should print: 25.0.1
deactivate && rm -rf /tmp/boltons-verify
```

If `--index-url` fails with 404, wait another minute and retry. PyPI CDN
propagation can take 1-5 minutes.

Report the results to the user.

## Error recovery

- **Failed release** (tag exists locally/on GitHub but not on PyPI): PyPI is
	the source of truth. Delete the stale tag locally and on the remote:
	```bash
	git tag -d 25.0.1
	git push origin :refs/tags/25.0.1  # if it was pushed
	```
	Then check `__version__` in `boltons/__init__.py`. If it was already bumped
	past the failed release (e.g. `25.0.2dev`), reset it to `25.0.1dev` so
	the release flow strips the suffix to the correct version. Amend or revert
	the bump commit as needed, then restart the release from step 1.
- **Wrong version tagged**: `git tag -d X.Y.Z && git push origin :refs/tags/X.Y.Z`
	then fix and re-tag.
- **Publish workflow failed**: Check the GitHub Actions log. Common causes:
	version mismatch, dev suffix present, PyPI trusted publisher not configured.
- **Tests fail after publish**: The package is already on PyPI. File an issue,
	fix forward with a patch release.

## Prerequisites (one-time setup)

These must be done once by the repo owner before the first automated release:

1. **PyPI trusted publisher**: In PyPI project settings
   (https://pypi.org/manage/project/boltons/settings/publishing/), add a new
   publisher: GitHub, repository `mahmoud/boltons`, workflow `publish.yml`,
   environment `pypi`.
2. **GitHub environment**: In repo settings (Settings → Environments), create
   an environment named `pypi`. Optionally add a deployment protection timer.
