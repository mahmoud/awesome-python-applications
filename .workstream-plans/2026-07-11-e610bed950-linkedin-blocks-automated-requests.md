---
id: 2026-07-11-e610bed950
title: "LinkedIn blocks automated requests"
status: implemented
plan_type: tactical
workstream: "2026-04-06-04fc3fc27d"
repo: awesome-python-applications
created: 2026-07-11
updated: 2026-07-11
tabled_note: ""
---
## Context

The daily link checker CI workflow (`.github/workflows/workflow.yml`) has been failing on every run because the GitHub Action it depends on — `cam-barts/linkchecker-action@master` — no longer exists (the repository was deleted or made private). GitHub returns `Unable to resolve action cam-barts/linkchecker-action, repository not found`. The last successful run was 2026-02-07; failures have been continuous since at least mid-2025 with intermittent successes. The workflow also pins `actions/checkout@master`, which is a deprecated ref.

The fix: replace the dead action with `lycheeverse/lychee-action@v2` (the most widely-used, actively-maintained link checker action, written in Rust), modernize the checkout step, and configure appropriately for this repo's ~500+ URLs across `README.md`.

## Approach

### Step 1: Rewrite `.github/workflows/workflow.yml`

Replace the entire file content with:

```yaml
on:
  schedule:
    - cron: "00 9 * * *"
  workflow_dispatch:
name: Link Checker
jobs:
  linkchecker:
    name: linkchecker
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Restore lychee cache
        uses: actions/cache@v4
        with:
          path: .lycheecache
          key: cache-lychee-${{ github.sha }}
          restore-keys: cache-lychee-

      - name: Link Checker
        uses: lycheeverse/lychee-action@v2
        with:
          args: --cache --max-cache-age 3d --no-progress --max-retries 3 --max-concurrency 5 'README.md'
          fail: true
```

Changes from the old workflow:
- **`cam-barts/linkchecker-action@master` → `lycheeverse/lychee-action@v2`**: The dead action is replaced. lychee is fast (Rust), well-maintained (11k+ stars), and the de facto standard for this job.
- **`actions/checkout@master` → `actions/checkout@v4`**: `@master` is deprecated and risks breaking on any upstream force-push. Pin to the current stable major.
- **`on: push` removed, `workflow_dispatch` added**: A link checker on every push is wasteful (links don't break from local code changes) and noisy. Replace with manual trigger (`workflow_dispatch`) plus the existing daily schedule. This matches the pattern used by lychee-action's own repo and similar awesome-list repos.
- **Caching added**: `actions/cache@v4` persists lychee's response cache (`.lycheecache`) across runs. With `--max-cache-age 3d`, URLs verified in the last 3 days are skipped, reducing external load and rate-limit risk across the ~500 URLs.
- **`--max-concurrency 5`**: Limits parallel requests to avoid triggering rate limiters on GitHub, PyPI, etc.
- **`--max-retries 3`**: Retries transient failures (502s, timeouts).
- **`exclude_links.json` artifact upload step removed**: This was specific to `cam-barts/linkchecker-action`'s output format. lychee produces `lychee/out.md` by default; if we need artifact upload later, we can add it for that file.

### Step 2: Create `.lycheeignore` for known-flaky URLs

Create `.lycheeignore` in the repo root with regular expressions for URLs that are expected to fail (rate-limited, geo-blocked, or legitimately ephemeral):

```
# LinkedIn blocks automated requests
https://www\.linkedin\.com

# Archive.org Wayback Machine URLs can be slow/flaky
https://web\.archive\.org

# PayPal donation links return 4xx to bots
https://www\.paypal\.com/cgi-bin
https://www\.paypal\.me

# Patreon returns 403 to bots
https://www\.patreon\.com

# SourceForge can be flaky
http://.*\.sourceforge\.net

# Buy Me a Coffee blocks bots
https://buymeacoffee\.com

# Ko-fi blocks bots
https://ko-fi\.com

# Some demo instances may be down
https://demo\.baby-buddy\.net
https://sandbox\.getindico\.io
```

This file is checked in and can be extended as new flaky URLs surface. Each line is a regex matched against the full URL.

Do **not** add `.lycheecache` to `.gitignore` — it is only generated in CI (the `actions/cache` step handles persistence) and never appears locally.

## Critical files & anchors

| File | Region | Why |
|---|---|---|
| `.github/workflows/workflow.yml` | Entire file (22 lines) | The only file being replaced — contains the dead action reference |
| `README.md` | Lines 5–631 | The file being link-checked; not modified, but its URL density (~500 links) drives the concurrency/cache config choices |

## Verification

1. **Syntax check**: After editing, run `python3 -c "import yaml; yaml.safe_load(open('.github/workflows/workflow.yml'))"` to confirm valid YAML.
2. **Manual trigger**: After pushing, trigger the workflow via `gh workflow run workflow.yml` and watch with `gh run watch`. The run should complete (pass or fail with actual link errors, NOT the "repository not found" error).
3. **Confirm lychee output**: The run log should show lychee scanning `README.md` with individual URL results. Any failures should be real broken links, not infrastructure errors.
4. **Cache behavior**: A second manual trigger should show "Restored lychee cache" in the cache step and skip recently-verified URLs (faster run).

## Assumptions & contingencies

- **Only `README.md` is checked**, matching the old `include_files: "README.md"` behavior. `BY_PLATFORM.md` (847 lines, largely overlapping URLs) is excluded to keep run times short. To add it later: append `'BY_PLATFORM.md'` to the `args` line.
- **`fail: true`** means the workflow will report failure on broken links. If this causes too much noise from transient failures, change to `fail: false` and optionally add the `peter-evans/create-issue-from-file` step (as shown in the lychee-action README) to create issues instead.
- **If lychee itself gets rate-limited by GitHub's API** (for github.com repo links), add `token: ${{ secrets.GITHUB_TOKEN }}` to the lychee-action `with:` block — this raises the rate limit from 60/hr (anonymous) to 5000/hr.
