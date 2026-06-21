# Contributing to bank2ynab

Thank you for taking the time to contribute!

For general contribution guidelines — bug reports, feature requests, code style,
and pull-request process — see [docs/CONTRIBUTING.md](docs/CONTRIBUTING.md).

This document covers the **release process** for maintainers.

---

## Table of Contents

- [Release Flow](#release-flow)
- [release: Label Semantics](#release-label-semantics)
- [One-Time Setup Checklist](#one-time-setup-checklist)
- [Dry-Run Instructions](#dry-run-instructions)
- [Manual Recovery Runbook](#manual-recovery-runbook)

---

## Release Flow

Releases follow a `develop → main` promotion model:

1. Open a pull request from `develop` to `main`.
2. Apply **exactly one** `release:` label to the PR (see [label semantics](#release-label-semantics)).
3. Merge the PR.
4. The `Bump and Tag` workflow (`bump-and-tag.yml`) triggers automatically on
   push to `main`. It reads the merged PR's labels, calculates the next
   semantic version, updates `pyproject.toml`, commits the bump, creates an
   annotated git tag (e.g. `v1.2.3`), pushes both to `main`, and opens a
   GitHub Release with auto-generated release notes.
5. The tag push triggers the `Publish to PyPI` workflow (`publish.yml`). It
   runs the test suite, builds the distribution, publishes to TestPyPI, verifies
   the install, then publishes to PyPI — all using Trusted Publisher (OIDC),
   so no PyPI API token is required.

---

## release: Label Semantics

| Label | Version bump | Example |
|-------|-------------|---------|
| `release: patch` | `x.y.Z → x.y.(Z+1)` | `1.2.3 → 1.2.4` |
| `release: minor` | `x.Y.z → x.(Y+1).0` | `1.2.3 → 1.3.0` |
| `release: major` | `X.y.z → (X+1).0.0` | `1.2.3 → 2.0.0` |

**Highest wins.** If multiple labels are applied, the workflow picks the most
significant one (`major > minor > patch`).

**Default on direct push.** If a commit is pushed directly to `main` without
an associated PR (or the PR has no `release:` label), the workflow defaults to
`patch` and emits a warning in the Actions log. Prefer labelled PRs to avoid
surprises.

---

## One-Time Setup Checklist

These steps are required before the release pipeline can publish to PyPI.
Complete them once when setting up the repository (or after a fork).

### PyPI Trusted Publisher

Register a Trusted Publisher on **pypi.org**:

1. Log in to [pypi.org](https://pypi.org) and go to
   **Account settings → Publishing → Add a new pending publisher**.
2. Fill in:
   - **PyPI project name:** `bank2ynab`
   - **Owner:** `bank2ynab`
   - **Repository:** `bank2ynab`
   - **Workflow filename:** `publish.yml`
   - **Environment name:** `pypi`
3. Save.

Register the same configuration on **test.pypi.org**:

1. Log in to [test.pypi.org](https://test.pypi.org) and go to
   **Account settings → Publishing → Add a new pending publisher**.
2. Use the same values as above.
3. Save.

### GitHub Labels

Create the following labels in the repository
(**Settings → Labels → New label**):

| Label name | Colour |
|------------|--------|
| `release: patch` | `#0075ca` |
| `release: minor` | `#e4e669` |
| `release: major` | `#d73a4a` |

### GitHub Environment

Create the `pypi` deployment environment
(**Settings → Environments → New environment**):

1. Name it exactly `pypi`.
2. Optionally add protection rules (e.g. require a reviewer before publishing).
3. Save — no secrets needed; Trusted Publisher uses OIDC.

---

## Dry-Run Instructions

To preview what version would be calculated without making any changes:

1. Go to **Actions → Bump and Tag → Run workflow**.
2. Select the `main` branch.
3. Check the **Dry run** checkbox.
4. Click **Run workflow**.

The workflow logs will show:
- The bump type resolved from the most recent merged PR's labels
- The current version read from `pyproject.toml`
- The next version that would be created
- The tag and commit message that would be written

No files are changed, no tags are created, and `publish.yml` is not triggered.

---

## Manual Recovery Runbook

Use this runbook when `publish.yml` fails **after** the tag has already been
created by `bump-and-tag.yml`.

**Symptom:** The `Publish to PyPI` workflow failed (e.g. a transient network
error during upload) but the git tag `vX.Y.Z` already exists.

**Do not re-run `bump-and-tag.yml`** — it will detect the existing tag and
abort with an error.

**Recovery steps:**

1. Investigate the failure in **Actions → Publish to PyPI** and fix the
   root cause (e.g. confirm PyPI Trusted Publisher is configured, check the
   environment name is `pypi`).
2. Go to **Actions → Publish to PyPI → Run workflow**.
3. In the **Use workflow from** dropdown, select **Tags** and choose the
   existing tag (e.g. `v1.2.3`).
4. Click **Run workflow**.

The workflow will re-run against the existing tag and publish the distribution.
If TestPyPI already has the version, the TestPyPI step may fail — that is
expected and harmless; the PyPI publish step will still proceed.
