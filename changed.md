---
title: TorchSigGUI 0.0.1 Release Preparation
subtitle: Change report for the developer
date: 2026-09-16
---

**Repository:** `torchsig-gui` (target `https://github.com/TorchDSP/torchsig-gui`)\
**Baseline:** commit `8bb328b` "initial commit"

> **Purpose.** Prepare TorchSigGUI for a first public **0.0.1 release on GitHub**. PyPI publishing is explicitly out of scope, so users install from GitHub (`pip install git+https://…@v0.0.1`, or clone + `pip install .`). The TorchDSP/torchsig repository was used as the reference for project conventions: issue/PR templates, CI workflows, Makefile, security policy, and `vX.Y.Z` tags.
>
> **State of the work.** All changes are in the working tree only. **Nothing has been staged, committed, tagged, or pushed.** Reviewing, committing, and tagging are left to you.

## Contents

1. Summary of changes
2. Decisions and constraints from the project owner
3. P0: Release blockers (bugs and incorrect metadata)
4. P1: Repository hygiene, CI and linting
5. README: local vs. remote (SSH tunnel) usage
6. P2: Makefile, security policy, tests folder rename
7. Verification performed
8. Complete file inventory
9. Items needing your attention
10. Suggested commit and release procedure

## 1. Summary of changes

| Area | What changed | Why it matters |
|---|---|---|
| Versioning | Version set to `0.0.1` in `torchsiggui/__init__.py`, `package.json`, `package-lock.json`. | Previously `0.0.0a1` (Python) vs `0.0.1-alpha` (npm). |
| Packaging | Fixed `pyproject.toml`: description, license, license-files, package data, dev extras, pinned TorchSig, URLs, classifiers, coverage target, ruff config. | A non-editable install (`pip install git+…`) previously shipped *without the frontend and SQL file*. |
| Server bugs | Awaited the stale-worker DB deletes; handled dead PIDs in `main.py`. | Stale worker records were never removed; a crashed worker could crash startup. |
| Data location | Datasets moved from "next to the package" to `~/.cache/torchsiggui` (overridable). | For normal installs, data was written into, and `rmtree`'d from, `site-packages`. |
| Frontend build | Build now outputs directly to `torchsiggui/webbuild` with a fixed build ID. | `npm run build` previously wrote to `./webbuild`, and output was not reproducible. |
| Frontend code | WebSocket URL derived from the page host; 31 ESLint errors fixed (types, `const`, store creation). | Needed for SSH tunnels on a different local port; lint must pass in CI. |
| Linting | ESLint (Next.js config) and Ruff configured; unused imports and variables removed. | `npm run lint` previously failed (ESLint not installed, no config). |
| GitHub | CI workflow, release workflow, bug/feature issue templates, PR template, `.gitattributes`. | Automated checks, and GitHub Releases replace PyPI as the distribution path. |
| Docs | README (install URLs, TorchSig pin, data folder, dev setup, local vs remote usage), `.env.example`, `LICENSE` copyright, `SECURITY.md`. | README pointed to a redacted URL and a missing `.env.example`. |
| Tooling | `Makefile`; `testing/` renamed to `tests/`. | Matches TorchSig conventions. |

## 2. Decisions and constraints from the project owner

- **No PyPI.** Distribution is via GitHub tags and Releases only.
- **Repository URL:** `https://github.com/TorchDSP/torchsig-gui`.
- **Copyright holder:** TorchSig.
- **TorchSig dependency:** locked to exactly `torchsig==2.2.0`.
- **No git commands** were to be run on the owner's behalf. *Disclosure:* two read-only commands were run by mistake: `git status --short` during baseline testing, and `git diff --stat` with its output discarded. Neither modified the repository, the index, or history. The folder rename was done with plain `mv`, not `git mv`.
- **Declined:** `CHANGELOG.md`; README "polish" (badges, screenshot, citation, relaxing prerequisites).
- **Not requested, so skipped:** `CONTRIBUTING.md`, Dockerfile, CI coverage upload.
- **Accepted:** all P0 fixes; `.github/`; ESLint and Ruff; `.gitattributes`; Makefile; `SECURITY.md`; rename to `tests/`; README section on local vs remote use.

## 3. P0: Release blockers

### 3.1 Consistent version number

*Files:* `torchsiggui/__init__.py`, `package.json`, `package-lock.json`

**Before:** Python reported `__version__ = "0.0.0a1"`, while npm reported `"0.0.1-alpha"`. `torchsiggui --version` and the wheel filename come from the Python value, so the release would have shipped as `0.0.0a1`.

**After:** both are `0.0.1`, including the lockfile's two root `version` fields. The release tag should be `v0.0.1`, following TorchSig's `vX.Y.Z` convention. The new release workflow enforces that the tag matches `__version__`.

### 3.2 `pyproject.toml` metadata and packaging

*File:* `pyproject.toml`

| Setting | Before | After, and reason |
|---|---|---|
| `build-system.requires` | `["setuptools>=61", "build"]` | `["setuptools>=77"]`. The SPDX string form of `license` requires setuptools 77+. `build` is a build frontend, not a backend requirement. |
| `description` | "Signal Processing Machine Learning Toolkit" (copied from TorchSig) | "Graphical interface for building TorchSig datasets". |
| `license` | `"MIT AND Apache-2.0 AND BSD-2-Clause AND BSD-3-Clause"` | `"MIT"`. No third-party Python code is vendored; dependencies are only imported, so their licenses are not part of this package's license expression. |
| `license-files` | `["LICENSE.md", "licenses/LICENSE*"]` | `["LICENSE"]`. `LICENSE.md` does not exist; the file is `LICENSE`. |
| `keywords` | signal processing, machine learning | Added `torchsig`, `gui`. |
| `classifiers` | Python, Python 3 | Added Development Status 3 (Alpha), Framework FastAPI, Intended Audience Science/Research, OS POSIX Linux, Python 3 Only, Topic Scientific/Engineering. |
| Runtime `dependencies` | `fastapi` and `torchsig` unpinned; `pytest`, `pytest_asyncio`, `pytest-timeout`, `pytest-cov`, `httpx2` listed as runtime deps | `fastapi>=0.141`: the code uses `app.frontend()`, confirmed present in 0.141.1. `torchsig==2.2.0`: the code imports TorchSig internals that can change between versions. Test tools moved out of runtime deps. |
| `[project.optional-dependencies]` | none | New `dev` extra: the pytest packages, `httpx2`, and `ruff`. Install with `pip install -e ".[dev]"`. |
| `[project.urls]` | commented-out TODO | Homepage, Repository, Issues (GitHub), TorchSig (torchsig.com). |
| `packages.find` | `where = ["."]` | Added `include = ["torchsiggui*"]` so only the package is discovered, not `tests`, `node_modules`, etc. |
| `package-data` | `files = ["*.sql"]` and `webbuild = ["*"]` | `torchsiggui = ["files/*.sql", "webbuild/**/*"]`. **Bug fix:** the keys must be package names. `files` and `webbuild` are not packages, so a wheel shipped without `database_sql.sql` and without the frontend. This went unnoticed only because editable installs read straight from the source tree. |
| pytest `addopts` | `--cov=torchsig` | `--cov=torchsiggui`. Coverage was measuring the TorchSig dependency instead of this project. |
| `testpaths` | `["testing"]` | `["tests"]` (see §6.3). |
| `[tool.ruff]` | none | New; see §4.3. |

> **Note on `httpx2`:** it was kept as-is because it is what is installed in the working venv and the tests pass with it. Please confirm it is the intended package name (FastAPI's `TestClient` traditionally depends on `httpx`).

### 3.3 Server lifespan bugs

*File:* `torchsiggui/main.py`

**Bug 1: un-awaited coroutine.** In both the startup and shutdown sections of `startup_shutdown()`, stale worker records were removed with `run_query(queries.delete_worker_entry, …)` *without* `await`. `run_query` is `async`, so this only created a coroutine object that never ran. Stale records were never deleted, and Python emitted "coroutine was never awaited" warnings. Stale records affect `get_worker_count`, which decides whether the dataset folder is deleted at shutdown.

**Bug 2: crash on a dead PID.** `psutil.Process(worker['pid'])` raises `psutil.NoSuchProcess` when that PID no longer exists, which is exactly the "crashed worker" case the loop is meant to clean up. The server would fail during startup or shutdown instead of removing the record.

**Fix.** The duplicated loop was extracted into one helper that is awaited in both places:

```python
# Removes the database records of workers that are no longer running
async def remove_crashed_workers():
  worker_map = await get_worker_info()
  for worker in worker_map:
    try:
      process = psutil.Process(worker['pid'])
      crashed = not process.is_running() or process.create_time() != worker['created']
    except psutil.NoSuchProcess:
      crashed = True
    if crashed:
      await run_query(queries.delete_worker_entry, process_id=worker['pid'])
```

Startup and shutdown now call `await remove_crashed_workers()`. The PID-reuse check (comparing `create_time`) is preserved.

Separately, the Ruff cleanup (§4.3) removed the now-unused `MODULE_LOCK_FILE` and `FileLock` imports. The commented-out locking code is still there for future multi-worker support and would need those imports restored if enabled.

### 3.4 Dataset storage location

*File:* `torchsiggui/files/file_io.py`

**Before:**

```python
MODULE_PARENT_FOLDER = MODULE_FOLDER.parent
MODULE_LOCK_FILE = MODULE_PARENT_FOLDER / 'workers.lock'
DATASET_FOLDER = MODULE_PARENT_FOLDER / 'datasets'
```

`MODULE_FOLDER` is the installed `torchsiggui` package directory. With an editable install, its parent is the repository root, which works. With a normal install (the `pip install git+…` path the README now documents), its parent is **`site-packages/`**. The server would create `site-packages/datasets` (often not writable) and, at shutdown, `rmtree` it.

**After:**

```python
# - Uses TORCHSIGGUI_DATA_DIR if set, otherwise the user cache folder, so data is never written into the install location
DATA_FOLDER = Path(environ.get('TORCHSIGGUI_DATA_DIR') or Path(environ.get('XDG_CACHE_HOME') or Path.home() / '.cache') / 'torchsiggui')
MODULE_LOCK_FILE = DATA_FOLDER / 'workers.lock'
DATASET_FOLDER = DATA_FOLDER / 'datasets'
```

- **Default:** `~/.cache/torchsiggui/datasets`, or `$XDG_CACHE_HOME/torchsiggui/datasets` if that variable is set.
- **Override:** the `TORCHSIGGUI_DATA_DIR` environment variable. It is read from the real process environment, *not* from `.env`; only `AppConfig` reads `.env`.
- No new dependency (such as `platformdirs`) was added.
- Only `datasets/` is removed at shutdown, never the whole cache folder.
- `MODULE_PARENT_FOLDER` was removed; nothing else referenced it. All other modules and tests still import `DATASET_FOLDER` and `DATABASE` unchanged.

### 3.5 README, `.env.example`, LICENSE, Node version

*Files:* `README.md`, `.env.example` (new), `LICENSE`, `package.json`

- **Clone URL:** replaced the placeholder `https://<redacted-host>/torchsig/torchsig-gui.git` with `https://github.com/TorchDSP/torchsig-gui.git`. Added the direct install option `pip install git+https://github.com/TorchDSP/torchsig-gui.git@v0.0.1`. Changed `pip install -e .` to `pip install .` for users; the editable install is now in the Development section.
- **Prerequisites:** added "TorchSig 2.2.0 (installed automatically)". The other prerequisites were intentionally left unchanged.
- **`.env` wording:** now says the `.env` file is read from the folder where the server is *started* (pydantic reads it relative to the working directory), with a link to `.env.example`.
- **Data folder:** documented the default location and `TORCHSIGGUI_DATA_DIR`.
- **Development setup:** new "Setup" subsection: Node.js ≥ 20.9, `pip install -e ".[dev]"`, `npm install`.
- **`.env.example` (new):** the README referenced it but it was missing. It contains `TORCHSIGGUI_PORT=8000` with comments, and `.gitignore` already whitelists it. `TORCHSIGGUI_DEV_MODE` was left out on purpose because dev mode is an internal flag.
- **LICENSE:** `Copyright (c) 2026-2026 TorchSigGUI` → `Copyright (c) 2026 TorchSig`.
- **`package.json`:** added `"engines": { "node": ">=20.9.0" }`, the minimum required by Next.js 16.3.4.

> **Not changed:** `NOTICE`, `THIRD_PARTY_LICENSES`, and `licenses/` are untouched, and they are no longer listed in the package metadata. Such files are only needed for redistributed code. The Python dependencies they list are not redistributed, but the built `webbuild/` JavaScript bundle *does* redistribute npm packages (React, Bootstrap, Redux, etc.). A decision is still needed; see §9.

## 4. P1: Repository hygiene, CI and linting

### 4.1 Frontend build output and reproducibility

*Files:* `package.json`, `next.config.ts`, `torchsiggui/webbuild/**` (regenerated)

**Problem found while setting up CI.**

- **Wrong output folder.** The build script was `NEXT_STATIC_BUILD=webbuild next build`, and `next.config.ts` uses that value as `distDir`, relative to the project root. The build therefore went to `./webbuild`, *not* `torchsiggui/webbuild`, which is the folder the server serves and the wheel packages. The committed bundle must have been copied there by hand.
- **Random build ID.** Next.js assigns a random build ID on every build (e.g. `_next/static/tMHizx5hQb_ydNult2RoH/`), so two builds of identical source always differed. A CI "is the committed build up to date?" check would always fail.

**Fix:**

```js
// package.json
"build": "NEXT_STATIC_BUILD=torchsiggui/webbuild next build"

// next.config.ts
// Uses a fixed build ID so rebuilding unchanged source reproduces the committed static build
generateBuildId: async () => "torchsiggui",
```

**Effect:**

- `npm run build` writes straight into the served folder.
- Repeated builds are byte-identical (verified by building twice and diffing recursively).
- The bundle was rebuilt after all the frontend source changes below.
- The first rebuild, made before any source edits, differed from the original committed bundle only in files that carry the build ID: the HTML, the `.txt` payload files, and the manifest folder name. All JS and CSS chunks were identical, which confirms the committed bundle matched the source at that point.
- The build also leaves an empty `torchsiggui/webbuild/_next/torchsiggui/` directory, which git ignores.

### 4.2 ESLint setup and frontend lint fixes

*Files:* `eslint.config.mjs` (new), `package.json`, `package-lock.json`, files under `src/`

**Before:** `"lint": "eslint"` existed, but ESLint was not installed and there was no configuration, so the script could not run.

**New dev dependencies, and why these exact versions:**

| Package | Reason |
|---|---|
| `eslint ^9.39.5` | ESLint 10 was tried first, but `eslint-plugin-react` (bundled by `eslint-config-next`) crashes on it (`contextOrFilename.getFilename is not a function`). ESLint 9 is what Next 16 supports. |
| `eslint-config-next ^16.3.4` | Matches the installed `next` version and provides the `core-web-vitals` and `typescript` presets. |
| `"typescript": "npm:@typescript/typescript6@^6.0.2"` and `"@typescript/native": "npm:typescript@^7.0.2"` | `typescript-eslint` refuses to run with TypeScript 7.0, because TS 7 ships without a JS API. This is Microsoft's documented side-by-side setup: tools that `import "typescript"` get the TS 6 API, while `npx tsc` still runs TypeScript **7.0.2** (verified). Revert to plain `typescript@^7` once typescript-eslint supports TS 7. |

**`eslint.config.mjs`:** a flat config that spreads `eslint-config-next/core-web-vitals` and `eslint-config-next/typescript`. It ignores `.next/`, `node_modules/`, `.venv/`, `torchsiggui/` (the built bundle), and `next-env.d.ts`. `.venv` had to be ignored because otherwise ESLint lints the JavaScript that matplotlib bundles inside the virtualenv.

**Lint results on the existing code:** 42 problems (31 errors, 11 warnings). All errors were fixed; 5 warnings remain.

| Rule (count) | Location | Fix |
|---|---|---|
| `no-explicit-any` (5) | `src/api/api-slice.ts` | `builder.mutation<any, any>` → `<unknown, unknown>` for write-sample and write-dataset; `<any, string>` → `<unknown, string>` for cancel-dataset. No caller reads the mutation results, so behaviour is unchanged. |
| `no-explicit-any` (1) | `src/components/form-parts/FormControls.tsx` | Tooltip render prop typed as `OverlayInjectedProps` from `react-bootstrap/Overlay`. |
| `no-explicit-any` (16), plus 6 unused `_state` warnings | `src/components/form-parts/select-style.ts` | The style object became a typed generic function, `customSelectStyle<IsMulti extends boolean>(): StylesConfig<FormOption, IsMulti>`. The `FormOption` interface moved here from `FormControls.tsx` and is exported. Call sites use `customSelectStyle<false>()` for single selects and `customSelectStyle<true>()` for multi-selects. A single non-generic type does not type-check, because react-select's style callbacks are invariant in the option and multi types. Style values are unchanged. |
| `prefer-const` (7) | `FormControls.tsx`, `DownloadList.tsx` (×2), `TransformParameters.tsx` (×2), `transform-slice.ts`, `transform-utils.ts` | `let` → `const` via ESLint autofix, for variables that are never reassigned. No behaviour change. |
| `react-hooks/refs` (2) | `src/providers/StoreProvider.tsx` | The store was created lazily in a `useRef` that was read during render, which React 19's rules flag. Replaced with `const [store] = useState(makeStore);`. Passing the function rather than calling it makes React create the store exactly once per provider instance, the same behaviour as before. The unused `AppStore` import was removed. |

**Remaining warnings (they do not fail CI):**

- **`FormControls.tsx` (×2):** unused `_action` parameters, required by the react-select callback signature.
- **`TransformAddModal.tsx`:** unused `parent` prop.
- **`SpectrogramImage.tsx` (×2):** an `<img>` without `alt` text, and Next.js's `no-img-element` suggestion. `next/image` offers little with a static export.

### 4.3 Ruff (Python lint) setup and fixes

*Files:* `pyproject.toml`, `torchsiggui/app.py`, `torchsiggui/main.py`, `torchsiggui/files/database_io.py`, `torchsiggui/utils/torchsig_interface.py`, `tests/test_downloads.py`, `tests/test_lifespan.py`

**Configuration**, chosen to match the existing code style so that no mass reformat is needed:

```toml
[tool.ruff]
line-length = 120
indent-width = 2
target-version = "py310"
extend-exclude = ["torchsiggui/webbuild", "node_modules"]

[tool.ruff.lint]
# Allows single-line if statements, which the codebase uses for short guards
ignore = ["E701"]

[tool.ruff.format]
quote-style = "single"
```

`ruff format` was **not** run on the codebase; only `ruff check` is enforced. `ruff` was added to the `dev` extra.

**Findings fixed (19):**

- **`torchsiggui/app.py`:**
  - Removed unused imports `MODULE_LOCK_FILE`, `WEBBUILD_FOLDER`, `get_worker_info`, `psutil`, `asynccontextmanager`, `FileLock`, `makedirs`, `getpid` and `StaticFiles`, left over from when the lifespan code lived in this file.
  - In the WebSocket loop, `msg = await websocket.receive_text()` → `await websocket.receive_text()`, since the value was never used.
- **`torchsiggui/main.py`:** removed the unused `MODULE_LOCK_FILE` and `FileLock` imports (see §3.3).
- **`torchsiggui/files/database_io.py`:**
  - Removed the unused `pathlib.Path` import.
  - `except Exception as e:` → `except Exception:` in three places. The handlers roll back and re-raise with a bare `raise`, so `e` was unused.
- **`torchsiggui/utils/torchsig_interface.py`:** `base_transform_map` is unused because the return statement that uses it is commented out. It was kept with `# noqa: F841` to preserve that intended future use.
- **`tests/test_downloads.py`:** `signal = reader.read(0)` → `reader.read(0)`; the test only checks that reading succeeds.
- **`tests/test_lifespan.py`:** `with TestClient(app) as client:` → `with TestClient(app):`.

### 4.4 WebSocket URL no longer hardcoded to localhost

*File:* `src/api/api-slice.ts`

**Before:**

```ts
const prodPort = (typeof window === "undefined") ? "8000" : window.location.port;
const wsPort = process.env.NODE_ENV === "development" ? "8000" : prodPort;
// …
const ws = new WebSocket("ws://localhost:" + wsPort + "/ws");
```

**After:**

```ts
function buildWebSocketLink() {
  if (process.env.NODE_ENV === "development") {
    return "ws://localhost:8000/ws";
  }
  const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
  return protocol + "//" + window.location.host + "/ws";
}
// …
const ws = new WebSocket(buildWebSocketLink());
```

**Why:**

- **Correct host:** in production the same server hosts the page and the WebSocket, so the page's own host is always the right address. The old code broke when the page was opened by a hostname other than `localhost`, or over `https`.
- **`window` is safe:** the function is only called inside `onCacheEntryAdded`, which runs in the browser, so `window` is always defined there. The old `typeof window` guard existed because that code ran when the module loaded during static prerendering.
- **Scope:** development mode behaviour is unchanged, and the production bundle no longer contains the string `localhost:8000` (verified).

### 4.5 Logging instead of `print`

*File:* `torchsiggui/app_write_spectrogram.py`

```python
# Before
print('An error occured while trying to create a new spectrogram image: ' + str(error))

# After
import logging
logger = logging.getLogger(__name__)
logger.exception('An error occurred while trying to create a new spectrogram image: %s', error)
```

Errors now go through the logging system that uvicorn configures and include the full traceback. The typo "occured" is also fixed.

### 4.6 GitHub configuration (`.github/`)

*Files (all new):* `.github/workflows/ci.yml`, `.github/workflows/release.yml`, `.github/ISSUE_TEMPLATE/bug_report.md`, `.github/ISSUE_TEMPLATE/feature_request.md`, `.github/PULL_REQUEST_TEMPLATE.md`

**`ci.yml`** runs on pushes to `main` and on all pull requests. Its permissions are read-only, and a new push cancels any run still in progress for the same branch.

| Job | Steps |
|---|---|
| **api** (matrix: Python 3.10, 3.12) | Checkout → setup-python with pip cache → install **CPU-only** `torch` and `torchaudio` from the PyTorch CPU index (the tests need no GPU, and this avoids several GB of CUDA wheels) → `pip install -e ".[dev]"` → `ruff check .` → `pytest` with `working-directory: tests` (the tests load data files by relative path). |
| **interface** (Node 22) | Checkout → setup-node with npm cache → `npm ci` → `npm run lint` → `npx tsc --noEmit` → `npm run build` → fail if `git status --porcelain torchsiggui/webbuild` is non-empty, with an error telling the contributor to rebuild and commit. |

**`release.yml`** runs when a tag matching `v*` is pushed, with `contents: write` permission:

1. Build the interface (`npm ci`, `npm run build`) and fail if the committed bundle is stale.
2. Fail if the tag is not `v` followed by the `__version__` in `torchsiggui/__init__.py`.
3. Run `python -m build` to produce the wheel and sdist in `dist/`.
4. Create the GitHub Release with `softprops/action-gh-release@v2`, attaching `dist/*`, with auto-generated release notes. Tags containing a hyphen (e.g. `v0.0.1-rc1`) are marked as pre-releases.

> Because of the version check, a test tag like `v0.0.1-rc1` fails unless `__version__` is temporarily set to `0.0.1-rc1`. Keep that in mind if you dry-run the workflow on a fork.

**Issue templates:**

- **Bug report** (label `bug`): description, reproduction steps, expected behaviour, screenshots/logs, and environment (TorchSigGUI, TorchSig, Python, OS, browser, GPU).
- **Feature request** (label `enhancement`): problem, proposed solution, alternatives.

**PR template:** a description, the linked issue, and a checklist that mirrors CI:

- pytest passes, run from `tests/`.
- `ruff check .` passes.
- `npm run lint` and `npx tsc --noEmit` pass.
- If `src/` changed, `torchsiggui/webbuild/` was rebuilt and committed.

### 4.7 `.gitattributes`

*File:* `.gitattributes` (new)

```gitattributes
torchsiggui/webbuild/** linguist-generated=true -diff
package-lock.json linguist-generated=true
```

- **On GitHub:** generated files are collapsed in pull request diffs and excluded from the repository's language statistics, which the minified JS would otherwise dominate.
- **Locally:** `-diff` makes `git diff` print "binary files differ" for the bundle instead of megabytes of minified text.
- **CI:** git still tracks the changes, so the check that the committed bundle is up to date keeps working.

## 5. README: local vs. remote usage

*File:* `README.md`, with new subsections under "Starting the Interface".

**Running on the Same Computer:** run `torchsiggui` and open `http://localhost:8000`. If `--port` was used, substitute that port.

**Running on a Remote Server**, e.g. a GPU machine used from a laptop's browser:

1. On the server: install and run `torchsiggui`. The README suggests `tmux` or `screen` to keep it running after you disconnect.
2. On the local computer: run `ssh -N -L 8000:localhost:8000 <user>@<server>` and keep that terminal open. The README explains the `-L <local port>:localhost:<server port>` format and that `-N` means no remote shell.
3. Open `http://localhost:8000` locally.

The section also covers:

- **Busy local port:** use a different one, e.g. `-L 9000:localhost:8000` and then `http://localhost:9000`.
- **Custom server port:** if the server was started with `--port`, use that value as the server-side port.
- **Where data lives:** datasets are stored on the remote server, and **Download** transfers them through the tunnel, so download before stopping the server.

**Why a tunnel is required:** uvicorn binds to `127.0.0.1` in `main.py`, so by design the server can't be reached from the network, and there is no authentication.

**Why a different local port works:** this relies on the WebSocket change in §4.4, which makes the page connect back to whatever address it was loaded from. The old `localhost:<page port>` URL happened to work through a plain tunnel; the new one is also correct behind proxies and over `https`.

## 6. P2: Makefile, security policy, tests folder rename

### 6.1 Makefile

*File:* `Makefile` (new)

Modeled on TorchSig's Makefile. Running `make` with no target prints help generated from the `##` comments. `PYTHON` and `NPM` can be overridden, e.g. `make test PYTHON=.venv/bin/python`.

| Target | Action |
|---|---|
| `help` | List targets (default). |
| `install` | `install-api` + `install-web`. |
| `install-api` | `$(PYTHON) -m pip install -e ".[dev]"` |
| `install-web` | `npm ci` |
| `dev-api` | `torchsiggui --dev` |
| `dev-web` | `npm run dev` |
| `build-web` | `npm run build` (into `torchsiggui/webbuild`) |
| `test` | `cd tests && $(PYTHON) -m pytest` |
| `lint` | `lint-api` (`ruff check .`) + `lint-web` (`npm run lint`, `npx tsc --noEmit`). |
| `check` | Same checks as CI: lint, test, build, then fail if `torchsiggui/webbuild` has uncommitted changes (uses `git status --porcelain`). |
| `package` | Builds the web bundle, then `python -m build` into `dist/`. |
| `clean` | Removes `build/`, `dist/`, `*.egg-info`, `.next`, the pytest and ruff caches, coverage and JUnit reports (in the root and `tests/`), `tsconfig.tsbuildinfo`, and `__pycache__` folders outside `node_modules` and `.venv`. |

`make test` uses the first `python` on `PATH`, so activate the virtualenv first (the local `.envrc` does this through direnv).

### 6.2 SECURITY.md

*File:* `SECURITY.md` (new)

- **Supported versions:** only the latest release (0.0.x) receives security fixes.
- **Security model:**
  - There is no authentication.
  - The server binds to loopback only.
  - Don't expose it publicly, or behind a reverse proxy or port forward, without adding authentication.
  - On shared multi-user machines, any local user can connect to `127.0.0.1`.
  - Dataset generation can use large amounts of disk, memory, CPU and GPU.
  - Data is temporary and deleted when the server stops.
  - It links to the README's remote-server section.
- **Reporting:** don't use public issues. Report through GitHub private vulnerability reporting at `https://github.com/TorchDSP/torchsig-gui/security/advisories/new`, including impact, reproduction steps, and affected versions.

> **Action required:** private vulnerability reporting must be enabled in the GitHub repository (Settings → Code security → Private vulnerability reporting), or the link in `SECURITY.md` won't work.

### 6.3 Rename `testing/` → `tests/`

*Changes:* folder move, plus references in `pyproject.toml`, `README.md`, `.github/workflows/ci.yml`, and `.github/PULL_REQUEST_TEMPLATE.md`

- **Why:** matches TorchSig and common Python convention.
- **How:** the move used `mv`, not `git mv`. Git normally detects the rename automatically once both sides are staged (`git add -A`).
- **References updated:** `testpaths`, the README testing section, the CI `working-directory` and its comment, and the PR checklist. No other file referenced the old name.
- **Test files:** contents are unchanged apart from the two Ruff fixes in §4.3.

The tests still open data with relative paths like `./test_data/data_default.json`, so pytest must be run **from inside `tests/`**. Running from the repository root gives 9 `FileNotFoundError` failures. This was already the case in the original code (verified).

## 7. Verification performed

| Check | Result | Details |
|---|---|---|
| Baseline pytest before any change (from `testing/`) | 16 passed | Plus 29 subtests. Establishes that any later failures would be regressions. |
| pytest after P0 changes | 16 passed | Coverage now reported for `torchsiggui` (85% total at that point). |
| pytest after P1 changes | 16 passed | 29 subtests passed. |
| pytest after the P2 rename (`make test`) | 16 passed | Run from `tests/` via the Makefile. |
| Wheel build (`pip wheel . --no-deps`) | Pass | `torchsiggui-0.0.1-py3-none-any.whl`, 48 files, including `torchsiggui/files/database_sql.sql`, `torchsiggui/webbuild/index.html` and all `_next/static` chunks. Metadata shows `Version: 0.0.1`, `License-Expression: MIT`, the project URLs, `torchsig==2.2.0` and `fastapi>=0.141`. |
| Non-editable smoke test: server run from the unpacked wheel, outside the repo, with `TORCHSIGGUI_DATA_DIR` set to a scratch folder | Pass | `GET /` → 200. `GET /api/metadata-defaults` → 200 with JSON. `datasets/state.db` was created in the chosen data folder, and the folder was removed on shutdown (SIGINT). |
| Live server after the frontend rebuild, using the installed `torchsiggui` command | Pass | `GET /` → 200. WebSocket `/ws` accepted with the connection open. No message arrived within 5 s, which is expected because the feeds only push when sample or file state changes. |
| `ruff check .` | Pass | "All checks passed!" |
| `npm run lint` | Pass | 0 errors, 5 warnings (listed in §4.2). |
| `npx tsc --noEmit` (TypeScript 7.0.2) | Pass | No type errors. |
| `npm run build` reproducibility | Pass | Two consecutive builds diffed recursively: identical. |
| Hardcoded URLs in the production bundle | Pass | `localhost:8000` no longer appears in `torchsiggui/webbuild`. |
| Workflow YAML syntax | Pass | Both workflow files parse with PyYAML. |
| `make help`, `make -n check`, `make lint-api` | Pass | Targets list correctly; `check` expands to the expected commands. |

> **Not verified:**
>
> - The GitHub Actions workflows have not run on GitHub, because nothing was pushed.
> - The WebSocket URL change was tested with a Python WebSocket client against a live server, not in a real browser and not through an actual SSH tunnel.
> - That a Linux build produces the same chunk hashes as the macOS build (see §9).
> - Full end-to-end dataset generation and download through the UI. The API tests cover it, but nobody clicked through it manually.
> - Python 3.10 and 3.12 specifically; local testing used Python 3.14.

## 8. Complete file inventory

### Modified

| File | Change (section) |
|---|---|
| `torchsiggui/__init__.py` | Version `0.0.1` (3.1) |
| `package.json` | Version, `engines`, build output path, ESLint and TypeScript dev dependencies (3.1, 3.5, 4.1, 4.2) |
| `package-lock.json` | Version; lock entries for the new dev dependencies (3.1, 4.2) |
| `pyproject.toml` | Metadata, dependencies, dev extra, package data, URLs, coverage, ruff, testpaths (3.2, 4.3, 6.3) |
| `LICENSE` | Copyright line (3.5) |
| `README.md` | Install, prerequisites, config, data folder, local/remote usage, dev setup, tests path (3.5, 5, 6.3) |
| `next.config.ts` | Fixed `generateBuildId` (4.1) |
| `torchsiggui/main.py` | `remove_crashed_workers()`; unused imports removed (3.3, 4.3) |
| `torchsiggui/files/file_io.py` | Data folder in the user cache (3.4) |
| `torchsiggui/app.py` | Unused imports and variable removed (4.3) |
| `torchsiggui/app_write_spectrogram.py` | Logging (4.5) |
| `torchsiggui/files/database_io.py` | Unused import and exception variables removed (4.3) |
| `torchsiggui/utils/torchsig_interface.py` | `# noqa: F841` (4.3) |
| `src/api/api-slice.ts` | WebSocket URL; `unknown` mutation types (4.2, 4.4) |
| `src/components/form-parts/select-style.ts` | Typed generic style function; exports `FormOption` (4.2) |
| `src/components/form-parts/FormControls.tsx` | Tooltip prop type; imports `FormOption`; explicit style generics; `const` (4.2) |
| `src/providers/StoreProvider.tsx` | `useState(makeStore)` (4.2) |
| `src/features/spectrogram/DownloadList.tsx` | `const` (4.2) |
| `src/features/transform-form/TransformParameters.tsx` | `const` (4.2) |
| `src/features/transform-form/transform-slice.ts` | `const` (4.2) |
| `src/features/transform-form/transform-utils.ts` | `const` (4.2) |
| `tests/test_downloads.py`, `tests/test_lifespan.py` | Unused variables (4.3) |
| `torchsiggui/webbuild/**` | Regenerated from the current source with the fixed build ID. The old `_next/static/tMHizx5hQb_ydNult2RoH/` folder is replaced by `_next/static/torchsiggui/` (4.1) |

### Added

| File | Purpose (section) |
|---|---|
| `.env.example` | Example server configuration (3.5) |
| `eslint.config.mjs` | ESLint flat config (4.2) |
| `.gitattributes` | Marks generated files (4.7) |
| `.github/workflows/ci.yml` | Continuous integration (4.6) |
| `.github/workflows/release.yml` | Tag-triggered GitHub Release (4.6) |
| `.github/ISSUE_TEMPLATE/bug_report.md` | Issue template (4.6) |
| `.github/ISSUE_TEMPLATE/feature_request.md` | Issue template (4.6) |
| `.github/PULL_REQUEST_TEMPLATE.md` | PR checklist (4.6) |
| `Makefile` | Developer tasks (6.1) |
| `SECURITY.md` | Security policy (6.2) |
| `changed.md`, `changed.pdf` | This report and its source. Delete them or leave them uncommitted, as you prefer. |

### Renamed

| From | To |
|---|---|
| `testing/` | `tests/` (all 7 Python files and `test_data/`; see 6.3) |

### Local-only artifacts (git-ignored, not part of the change)

- **Still present:** `node_modules/` (from `npm ci` / `npm install`), `tsconfig.tsbuildinfo`, `.ruff_cache/`, `.pytest_cache/`, `.coverage`, `torchsiggui.egg-info/`.
- **Removed after use:** generated `coverage.xml` and `report.xml` files, the temporary `./webbuild` and `.next` build folders, and `__pycache__` in the tests folder.
- **Outside the repository:** test wheels and smoke-test data were written to a temporary scratch directory.

## 9. Items needing your attention

| # | Item | Details and recommendation |
|---|---|---|
| 1 | **Enable private vulnerability reporting** | Needed for the reporting link in `SECURITY.md` to work. GitHub → Settings → Code security. |
| 2 | **Third-party license files** | `NOTICE`, `THIRD_PARTY_LICENSES` and `licenses/` still list Python and test dependencies that are not redistributed, while the bundled JS *does* redistribute npm packages. Recommendation: regenerate `THIRD_PARTY_LICENSES` from the production npm dependencies (e.g. with `license-checker --production`) and drop the Python entries, or remove the files if legal review agrees. |
| 3 | **Cross-platform build hashes** | The CI check that the committed bundle is up to date assumes Linux and macOS produce identical bundles. If the first CI run reports `torchsiggui/webbuild` as out of date with no source changes, commit the bundle built on Linux (e.g. from a CI artifact or a Linux container). |
| 4 | **First CI run** | The workflows are untested on GitHub. Watch the first run, especially the CPU-only PyTorch install and TorchSig 2.2.0 dependency resolution on Python 3.10 and 3.12. |
| 5 | **npm audit** | `npm ci` reported known vulnerabilities in the dependency tree. `npm audit fix` was deliberately not run. Review `npm audit` before release. |
| 6 | **TypeScript alias workaround** | The `typescript` → TS 6 alias exists only for typescript-eslint. Remove it once typescript-eslint supports TS 7. |
| 7 | **`httpx2`** | Confirm this is the intended test dependency, rather than `httpx`. |
| 8 | **Browser and tunnel test** | Before tagging, click through the UI once locally (Generate Sample, Generate Dataset, Download, Cancel), and once through `ssh -L` with a different local port. |
| 9 | **Data folder change is user-visible** | Developers used to finding `datasets/` in the repository root will now find it under `~/.cache/torchsiggui/`. This is documented in the README, and `TORCHSIGGUI_DATA_DIR` can point it somewhere else. |
| 10 | **Tests require `cd tests`** | Optional follow-up: build the test data paths from `Path(__file__).parent` so `pytest` works from the repo root, then simplify CI and the Makefile. |
| 11 | **Remaining lint warnings** | 5 ESLint warnings (§4.2). Adding `alt` text to the `<img>` is a small accessibility fix worth doing. |
| 12 | **Skipped by choice** | `CHANGELOG.md`, `CONTRIBUTING.md`, Dockerfile, coverage upload, README badges, screenshot and citation. With no changelog, the release workflow's auto-generated notes serve as the release notes. |
| 13 | **Unused locking code** | The commented-out `FileLock` blocks in `main.py` would need their imports restored if multi-worker mode is enabled. |

## 10. Suggested commit and release procedure

1. Review the working-tree changes (`git status`, `git diff`). `.gitattributes` hides the webbuild diffs, so use `git diff --text` if you want to see them.
2. Run `make install` if needed, then run `make check` locally.
3. Stage everything, including the rename, with `git add -A`, and commit. Optionally split the work into logical commits: packaging/P0, lint and CI, docs, rename.
4. Push to a branch and open a PR to trigger `ci.yml`. Resolve any Linux build-hash mismatch (§9, item 3).
5. Merge to `main`, and enable private vulnerability reporting.
6. Tag and push: `git tag -a v0.0.1 -m "TorchSigGUI 0.0.1"`, then `git push origin v0.0.1`.
7. `release.yml` checks the bundle and version, builds the wheel and sdist, and publishes the GitHub Release. Edit the auto-generated notes if you want.
8. Smoke-test the published install: `pip install git+https://github.com/TorchDSP/torchsig-gui.git@v0.0.1`, then `torchsiggui --version` (expect `TorchSigGUI 0.0.1`).
