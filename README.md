# TorchSigGUI

TorchSigGUI is an open-source graphical interface for [TorchSig](https://torchsig.com). It lets you build simple signal datasets with many of TorchSig's features, and preview generated signals as spectrogram images before you start writing new datasets.

## Prerequisites

- Linux (tested on Ubuntu &ge; 22.04), macOS, or Windows 10 or later
- &ge; 1 TB of hard drive storage
- CPU with &ge; 4 cores
- GPU with &ge; 16 GB of memory (recommended; PyTorch does not support NVIDIA GPUs on macOS)
- Python &ge; 3.10
- [TorchSig](https://github.com/TorchDSP/torchsig) 2.2.0 (installed automatically)

## Installation

Install a release directly from GitHub:

```
pip install git+https://github.com/TorchDSP/torchsig-gui.git@v0.0.1
```

Or clone this repository and install it:

```
git clone https://github.com/TorchDSP/torchsig-gui.git
cd torchsig-gui
pip install .
```

## Starting the Interface

Start the interface with:

```
torchsiggui
```

This starts a server that hosts the interface. The URL to access it is printed in the console.

To see the available server options:

```
torchsiggui --help
```

You can also configure the server with a `.env` file in the folder where you start the server, matching the format of [`.env.example`](.env.example).

Datasets are written to the save location you choose in the interface, `~/torchsig_datasets` by default. Set the `TORCHSIGGUI_DATASET_LOCATION` environment variable to change the default.

While the server runs, it keeps spectrogram previews and its working files in your user cache folder, and removes them when it stops:

- Linux: `~/.cache/torchsiggui` (or `$XDG_CACHE_HOME/torchsiggui`)
- macOS: `~/Library/Caches/torchsiggui`
- Windows: `%LOCALAPPDATA%\torchsiggui`

Set the `TORCHSIGGUI_DATA_DIR` environment variable to use a different folder.

### Running on the Same Computer

If TorchSigGUI is installed on the computer you're using, start the server:

```
torchsiggui
```

Then open [http://localhost:8000](http://localhost:8000) in your browser. If you started the server with a different port, for example `torchsiggui --port 8080`, use that port instead.

### Running on a Remote Server

TorchSigGUI can run on a remote machine, such as a GPU server, while you use the interface from the browser on your own computer. The server only accepts connections from the machine it runs on, so you reach it through an SSH tunnel instead of opening it to the network.

1. On the remote server, install TorchSigGUI and start the server:

   ```
   torchsiggui
   ```

   To keep the server running after you disconnect, start it inside `tmux` or `screen`.

2. On your computer, open a new terminal and forward a local port to the server's port:

   ```
   ssh -N -L 8000:localhost:8000 <user>@<server>
   ```

   The format is `-L <local port>:localhost:<server port>`. `-N` keeps the connection open without starting a remote shell. Leave this terminal open while you use the interface.

3. On your computer, open [http://localhost:8000](http://localhost:8000) in your browser.

If port 8000 is already in use on your computer, pick another local port. For example, `ssh -N -L 9000:localhost:8000 <user>@<server>` makes the interface available at `http://localhost:9000`. If you started the server with `--port`, use that port as the server port.

Datasets are generated and stored on the remote server, in the save location you choose. The interface shows the server's name next to the **Save Location** field, so enter a folder path on the server, not on your computer. Datasets stay on the server after it stops. Use them there, or copy them to your computer, for example with `rsync -a <user>@<server>:~/torchsig_datasets/<name> .`

## Using the Interface

Open the printed URL in your browser to load the interface. Adjust the settings as needed, then test your input with the **Generate Sample** button near the bottom right of the window.

When you're ready, set the dataset's **Save Location** and **Dataset Name**, then press the **Generate Dataset** button next to **Generate Sample**. The dataset is written to a new folder, `<save location>/<dataset name>`, on the machine running the server. The save location must already exist, except for the default `~/torchsig_datasets`, which is created for you.

If a folder with that name already exists, the dataset is not started. Turn on **Overwrite** to replace an earlier TorchSig dataset with the same name. Folders that are not TorchSig datasets are never replaced.

After you press **Generate Dataset**, a new section appears in the bottom right of the window showing the dataset's progress and the folder it is written to:

- **Cancel** stops a dataset that is still being written and deletes its partial folder.
- **Delete** removes a dataset that failed, along with its partial folder.
- **Remove from List** hides a finished dataset from the list. Its files are kept.

Finished datasets are kept after you stop the server. Spectrogram previews are removed.

### Loading a Dataset

Each dataset folder holds a `data.h5` file with the signals, and `dataset_info.yaml` and `writer_info.yaml` files describing how it was made. Load it with TorchSig:

```python
from pathlib import Path
from torchsig.datasets.datasets import StaticTorchSigDataset

root = Path('~/torchsig_datasets/<dataset name>').expanduser()
dataset = StaticTorchSigDataset(root=str(root), target_labels=['class_name'])
data, targets = dataset[0]
```

The interface also shows each finished dataset's full path, with a line you can copy to load it.

## Development

To set up a development environment, run the checks, and open a pull request, see [CONTRIBUTING.md](CONTRIBUTING.md).

## License

TorchSigGUI is released under the MIT License. See [LICENSE](LICENSE) for details.
