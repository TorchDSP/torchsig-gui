# Security Policy

## Supported Versions

TorchSigGUI is in early development. Security fixes are made only for the latest release.

| Version | Supported |
|---------|-----------|
| 0.0.x   | Yes       |

## Security Model

TorchSigGUI is a single-user tool meant to run on your own machine, or on a server you reach through an SSH tunnel. Keep the following in mind:

- **No authentication.** Anyone who can reach the server can use the interface, generate datasets, download them, and cancel them.
- **Local connections only.** The server listens on `127.0.0.1`, so other machines on the network cannot connect to it. To use it from another computer, forward the port over SSH as described in the [README](README.md#running-on-a-remote-server).
- **Local host names only.** The server rejects requests addressed to any host name other than `localhost` or `127.0.0.1`. This blocks DNS rebinding, where a web page points its own domain at your machine to reach the server. Open the interface at `http://localhost:<port>` or `http://127.0.0.1:<port>`.
- **Do not expose the server.** Do not bind it to a public address, or put it behind a reverse proxy or port forward that is reachable by others, without adding your own authentication in front of it.
- **Shared servers.** On a machine with other users, anyone logged in to that machine can connect to `127.0.0.1` and use your running server. Avoid leaving it running on shared machines when you are not using it.
- **Resource use.** Dataset generation can use large amounts of disk space, memory, CPU, and GPU time. Anyone with access to the interface can start this work.
- **Temporary data.** Generated datasets and spectrogram images are stored in the data folder (by default `~/.cache/torchsiggui`) and deleted when the server stops.

## Reporting a Vulnerability

Please do not report security vulnerabilities in public issues.

Report them privately through GitHub's [private vulnerability reporting](https://github.com/TorchDSP/torchsig-gui/security/advisories/new). Include:

- A description of the vulnerability and its impact
- Steps to reproduce it
- The TorchSigGUI and TorchSig versions affected

We will acknowledge your report and keep you updated as we investigate and work on a fix.
