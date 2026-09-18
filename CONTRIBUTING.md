# Contributing to TorchSigGUI

Thanks for helping improve TorchSigGUI. Before you start on a change, please discuss it with the maintainers in a [GitHub issue](https://github.com/TorchDSP/torchsig-gui/issues), so we can agree on the approach before you put in the work.

To report a security vulnerability, follow [SECURITY.md](SECURITY.md) instead of opening a public issue.

## How TorchSigGUI Is Built

TorchSigGUI has two parts:

- **The API** (`torchsiggui/`): a FastAPI server that wraps TorchSig, writes datasets, and streams progress to the interface over a websocket.
- **The interface** (`src/`): a Next.js app that is exported as static files into `torchsiggui/webbuild/`, which the API serves.

The built interface in `torchsiggui/webbuild/` is committed, so `pip install` works without Node.js. Any change to `src/` needs a rebuild, and the rebuilt files must be committed with it.

## Setup

Development requires the [prerequisites](README.md#prerequisites) and Node.js &ge; 20.9. From a clone of the repository, install the Python package with its development dependencies, then the interface dependencies:

```
pip install -e ".[dev]"
npm install
```

Or run `make install`, which uses `npm ci` to install exactly what `package-lock.json` specifies.

## Running in Development

Development runs two servers.

1. Start the API. It reloads when you change the Python code:

   ```
   torchsiggui --dev
   ```

   If the interface is open, refresh the page after the API reloads to reconnect.

2. From a second terminal, start the interface:

   ```
   npm run dev
   ```

   Open the URL it prints. Interface changes re-render automatically. You don't need to restart the API for interface changes, but you do need to restart the interface after changes to the API.

In development, the interface expects the API at `http://localhost:8000`.

## Checks

Run the same checks as CI before opening a pull request:

```
make check
```

This lints the Python code (`ruff check .`), lints and type checks the interface (`npm run lint`, `npx tsc --noEmit`), runs the API tests (`pytest`), rebuilds the interface, and fails if `torchsiggui/webbuild/` differs from the committed build.

Run `make help` to list the other tasks.

The `Makefile` uses Unix shell commands. On Windows, run `make` from Git Bash or WSL, or run the commands listed above directly.

### Tests

The API tests use pytest and live in `tests/`. Add or update tests for any API change. Bug fixes should include a test that fails without the fix.

The tests write to a temporary data folder, so they don't touch the datasets of a server you have running.

The server only answers requests addressed to `localhost` or `127.0.0.1`. The `affixed_client` fixture already uses `http://localhost`, but websocket tests must pass the full URL, as in `affixed_client.websocket_connect('ws://localhost/ws')`.

## Code Style

- **Python:** two-space indentation, single quotes, and a 120-character line limit, checked by `ruff`. Match the surrounding code, including its short comments above each block.
- **TypeScript:** follow the existing component and Redux slice layout in `src/`, checked by `eslint` and `tsc`.
- Keep TorchSig-specific code in `torchsiggui/utils/torchsig_interface.py`, so that updating the pinned TorchSig version stays contained.

## Pull Requests

1. Branch from `main` and keep each pull request focused on one change.
2. If you changed `src/`, run `make build-web` and commit `torchsiggui/webbuild/` in the same pull request.
3. Make sure `make check` passes.
4. Fill in the pull request template, and link the issue the change addresses.
5. A maintainer reviews the pull request and merges it once CI passes and review comments are resolved.

Maintainers update the version number in `torchsiggui/__init__.py` and `package.json` when preparing a release, so don't change it in your pull request.

## Code of Conduct

TorchSigGUI follows the [TorchSig Code of Conduct](https://github.com/TorchDSP/torchsig/blob/main/CONTRIBUTING.md#code-of-conduct). Please follow it in all your interactions with the project.

## License

By contributing, you agree that your contributions are licensed under the project's [MIT License](LICENSE).
