# log_fetch

Simple log viewer utility for quickly viewing and fetching logs.

## Overview

This repository contains a small Python script to inspect and fetch logs locally.

## Files

- [log_viewer.py](log_viewer.py) — main script to view/fetch logs.

## Prerequisites

- Python 3.8 or newer
- (Optional) A virtual environment

## Setup

Windows (PowerShell):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt  # if present
```

macOS / Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt  # if present
```

## Run

Run the log viewer script:

```bash
python log_viewer.py
```

If `requirements.txt` exists, install dependencies first. If the script accepts CLI arguments, see the script header or run `python log_viewer.py --help`.

## Contributing

Feel free to open issues or pull requests for improvements, features, or fixes.

## License

Add a `LICENSE` file to declare a license. If you prefer MIT, add an MIT license file.
