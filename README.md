# <img src="chromaplot/resources/cp_logo.png" alt="ChromaPlot logo" width="400" />

# ChromaPlot v2

**ChromaPlot** is a Python-based desktop application for creating high-quality chromatography figures from exported instrument data.

[Originally developed](https://github.com/beh22/ChromaPlot) for Cytiva ÄKTA chromatography systems, ChromaPlot v2 introduces a completely redesigned project-based workflow focused on flexibility, reproducibility, and publication-quality figure generation.

## Key Improvements Over ChromaPlot v1

ChromaPlot v2 is a complete rewrite of the original application with a much more flexible architecture and significantly expanded functionality.

### New Features in v2

- Project-based workflow with saveable `.chromaplot` project files
- Overlay multiple datasets within a single workspace
- Improved curve and dataset management
- Dataset-specific settings and metadata
- Improved plot customisation options
- Better export handling for publication-quality figures
- Improved GUI
- Improved importer framework for future dataset compatibility
- Cleaner and more maintainable internal code structure

## Supported File Formats

ChromaPlot v2 currently supports chromatography data exported from Cytiva ÄKTA systems using  software.

### Currently Supported

- Exported text-based chromatography files from UNICORN
  - `.txt`
  - `.csv`
  - `.asc`

As far as we are aware, exports from all versions of UNICORN are currently supported.

If you encounter a file that does not import correctly, please open an issue on GitHub and include:
- the UNICORN version (if known)
- the export format used
- a screenshot or example file if possible

### Planned Future Support

Additional chromatography and biophysical data formats are planned for future releases.

## Planned Features

The following features are planned for future releases:

- Fraction number display and annotation
- Shaded regions based on fractions or volume ranges
- Vertical marker / measurement tools
- Secondary axis support
- Additional dataset types
  - SEC-MALS
  - FIDA
  - LC-MS
  - Generic CSV support
- Packaged desktop installers for macOS and Windows
- Update checker
- Additional analysis tools

## Installation

At the moment, ChromaPlot v2 is intended to be run from source code. 

Packaged standalone applications for Windows and macOS will be introduced soon.

### Requirements

- Python 3.11 or newer
- Git (recommended for cloning the repository)


### 1. Clone the Repository

```bash
git clone https://github.com/beh22/ChromaPlot_v2.git
cd ChromaPlot_v2
```

### 2. Create a Virtual Environment (Recommended)

It is recommended to install ChromaPlot inside a dedicated Python virtual environment to avoid dependency conflicts.

### Option A — Standard Python `venv`

Create the environment:

```bash
python -m venv chromaplot_env
```

Activate it:

#### macOS / Linux

```bash
source chromaplot_env/bin/activate
```

#### Windows

```bash
chromaplot_env\Scripts\activate
```


### Option B — Conda Environment

If you already use Anaconda or Miniconda:

```bash
conda create -n chromaplot python=3.12
conda activate chromaplot
```


### 3. Install ChromaPlot

Install ChromaPlot and its dependencies:

```bash
pip install .
```

### 4. Launch ChromaPlot

Once installed, start the application with:

```bash
chromaplot
```

## Updating ChromaPlot

To update to the latest version, run the following commands from the `ChromaPlot_v2` directory:

```bash
git pull
pip install .
```

If you are using a virtual environment, make sure it is activated before running the commands above.


## Troubleshooting

### `chromaplot: command not found`

Make sure:

- your virtual environment is activated
- the installation completed successfully
- you installed using:

```bash
pip install .
```


### PyQt / GUI Issues

If the GUI does not launch correctly:

- ensure you are using a supported Python version
- try creating a fresh virtual environment
- ensure PyQt5 installed successfully

You can verify installation with:

```bash
pip show PyQt5
```


## Project Status

ChromaPlot v2 is under active development.

While already functional and usable for figure generation, the application is still evolving and the project structure, GUI, and feature set may continue to change between releases.

Bug reports, suggestions, and feedback are very welcome.


## Support / Contact

### Reporting Issues

Please report bugs or feature requests through the GitHub Issues page:

- https://github.com/beh22/ChromaPlot_v2/issues

When reporting issues, please include:

- Operating system
- ChromaPlot version
- Steps to reproduce the issue
- Example files/screenshots if relevant

### Contact

For questions or other enquiries:

- Billy Hobbs — <billyehobbs@gmail.com>


## Acknowledgements

If ChromaPlot is used to generate figures for publications, presentations, or reports, an acknowledgement is appreciated.


## License

This project is licensed under the MIT License. See the `LICENSE` file for details.
