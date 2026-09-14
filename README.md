# TorchSigGUI

TorchSigGUI is an open-source graphical interface for [TorchSig](https://torchsig.com). It lets you build simple signal datasets with many of TorchSig's features, and preview generated signals as spectrogram images before you start writing new datasets.

## Prerequisites

- Ubuntu &ge; 22.04
- &ge; 1 TB of hard drive storage
- CPU with &ge; 4 cores
- GPU with &ge; 16 GB of memory (recommended)
- Python &ge; 3.10

## Installation

Clone this repository and install it:

```
git clone https://<redacted-host>/torchsig/torchsig-gui.git
cd torchsig-gui
pip install -e .
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

You can also configure the server with a `.env` file in the folder where you cloned the repository, matching the format of `.env.example`.

## Using the Interface

Open the printed URL in your browser to load the interface. Adjust the settings as needed, then test your input with the **Generate Sample** button near the bottom right of the window. When you're ready, create your dataset with the **Generate Dataset** button next to it. Give each dataset a unique name.

After you press **Generate Dataset**, a new section appears in the bottom right of the window showing progress for that dataset. When the dataset is finished, click its **Download** button to save it to your machine. You can remove a dataset at any time with its **Cancel** button.

***All datasets and spectrogram images are removed from your device when you stop the server.***

## Development

Development runs two servers: the Python API that wraps TorchSig, and the web interface that connects to it.

### Starting the TorchSig API

Start the API first, since TorchSigGUI relies on it. From the cloned repository, run:

```
torchsiggui --dev
```

This starts a development server for the API that reloads on changes. If you have the interface open, refresh the page to re-establish the connection.

### Starting the TorchSigGUI Interface

From a new terminal in the cloned repository, run:

```
npm run dev
```

This opens a development page showing the current state of the interface. Interface changes re-render automatically. You don't need to restart the API for interface changes, but you do need to restart the interface for changes made to the API.

### Testing

The repository uses pytest to test the API. From the `testing/` folder, run:

```
pytest
```

## License

TorchSigGUI is released under the MIT License. See [LICENSE](LICENSE) for details.
