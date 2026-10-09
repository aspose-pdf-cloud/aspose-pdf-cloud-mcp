# Publishing to PyPI from GitHub

The package is named `aspose-pdf-cloud-mcp`. Both console commands (`apdf`
and `aspose-pdf-cloud-cli`), `py.typed`, and the bundled agent skill are
included in the wheel. Setuptools builds the package from `src/`, and
setuptools-scm generates its version and `_version.py` from Git tags.
Do not edit `_version.py` or set a static project version.

## One-time account setup

1. Push this repository to GitHub. The project metadata currently points to
   `aspose-pdf-cloud/aspose-pdf-cloud-mcp`. If your actual owner or repository
   differs, update `[project.urls]` in `pyproject.toml` and use the actual
   owner and repository in the environment settings below.
2. Create a GitHub Actions environment named `pypi` in repository Settings
   → Environments. Restrict deployments to release tags (`v*`), and configure
   required reviewers if your GitHub plan supports them.
3. Sign in to PyPI with two-factor authentication and create a project-scoped
   API token for `aspose-pdf-cloud-mcp`.
4. Add that token as `PYPI_API_TOKEN` in the GitHub `pypi` environment
   secrets.

The project name must be available, or your account must have publishing
rights to the existing project. Aspose credentials are not needed for the
release workflow.

## Release a version

Version 1.0.0 is the existing release; the examples below target the next
release, 1.1.0. Preserve the `v1.0.0` tag and its changelog entry. During
development, keep changes under `Unreleased` and let setuptools-scm derive
the development version. When preparing 1.1.0, rename `Unreleased` to
`1.1.0` with the actual release date. Do not create the release tag until
the release commit is ready and validated.

1. Merge the release changes and update `CHANGELOG.md`. Wait for CI to pass.
2. Choose an unused stable version, then tag that tested commit:

   ```powershell
   git checkout main
   git pull --ff-only
   git tag -a v1.1.0 -m "Release 1.1.0"
   git push origin v1.1.0
   ```

   Use your actual default branch if it is not `main`. The example version
   must be replaced if it has already been published.
3. Watch **Publish to PyPI** in GitHub Actions and approve the `pypi`
   deployment if required by your environment settings.
4. Verify installation in a fresh virtual environment:

   ```powershell
   python -m venv .venv-release-check
   ./.venv-release-check/Scripts/python.exe -m pip install aspose-pdf-cloud-mcp==1.1.0
   ./.venv-release-check/Scripts/apdf.exe --help
   ```

Pushing `v*` triggers the release workflow. It runs the reusable CI workflow,
including unit tests on Python 3.11–3.13 with a 75% coverage floor, then builds
an sdist and a wheel from that sdist, validates metadata and packaged files,
and installs the wheel into an isolated environment for smoke testing. The
publishing job uploads the same verified artifacts using the
`PYPI_API_TOKEN` secret from the selected GitHub environment.
Tags must be exactly `vX.Y.Z`; the workflow rejects development, local,
prerelease, and mismatched distribution versions before upload.

PyPI versions cannot be overwritten. If publication succeeds, make a new
version for subsequent changes. If a job fails before uploading, resolve
the cause and rerun only if the artifacts and tag still identify the
intended release. Check PyPI for a partial upload before rerunning.

## Optional TestPyPI rehearsal

Create a separate `testpypi` GitHub environment and add a TestPyPI
project-scoped API token as `PYPI_API_TOKEN`.

Run **Publish to PyPI** manually with an existing `vX.Y.Z` tag selected as
the ref. Manual runs publish only to TestPyPI; selecting a branch skips
publishing. You can use an existing release tag to check the TestPyPI token
setup. A normal tag push publishes to production PyPI.

Download the specific package from TestPyPI without resolving dependencies
there, then install the downloaded wheel with dependencies from PyPI:

```powershell
python -m pip download --no-deps --index-url https://test.pypi.org/simple/ --dest test-dist aspose-pdf-cloud-mcp==1.1.0
python -m pip install ./test-dist/aspose_pdf_cloud_mcp-1.1.0-py3-none-any.whl
```

## Local distribution checks

Use the project's Python 3.11+ virtual environment:

```powershell
python -m pip install -e ".[dev]"
python -m pytest -q -m "not live" --cov=aspose_pdf_cloud_mcp --cov-report=term-missing
python -m build
python -m twine check --strict dist/*
python scripts/check_distribution.py dist
```

Build in a fresh checkout or remove only previous build artifacts first:
the checker requires exactly one wheel and one sdist. Full Git history and
tags are needed for SCM versioning. Source archives downloaded from GitHub
without `.git` are not release sdists; use the generated sdist, a clone, or
the published wheel instead.
