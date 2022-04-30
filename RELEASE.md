# Release

-----

Requirements:

- `pip install -U build tox twine`

A brief checklist for release:

- `tox`
- `git commit` (if applicable)
- bump `boltons/__init__.py` version off of -dev
- `git commit -a -m "bump version for x.y.z release"`
- `python -m build`
- `twine upload dist/*`
- bump `docs/conf.py` version
- `git commit`
- `git tag -a x.y.z -m "brief summary"`
- write `CHANGELOG.md`
- `git commit`
- bump `boltons/__init__.py` version onto n+1 dev
- `git commit`
- `git push`
