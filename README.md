# Optimal battery dispatch

## Overview
This project groups code to instruct a battery to charge and discharge in order to trade power on two power markets. The objective is to maximise profit.

The inputs are in the `Data`-folder, outputs in the `Results`-folder and code in `src`. Due to the low complexity of the project and limited time, settings are put into a simple class.

## Tooling & Getting started
The project is setup using UV, and the .toml file contains the packages and their version numbers. It needs to be installed from [their website](https://docs.astral.sh/uv/getting-started/) if you have not done so. 

The code must be downloaded into a project, and the data supplied by email put into the `Data`-folder because the code will automatically try to read the file `Data/Attachment 2.xlsx` (if you have this file somewhere else, you can change the file name in `src/Settings.py`).

To run the code, open a terminal and navigate to the project folder.

- `uv sync`: this will install all the required packages into your venv. It is needed only once.
- `uv run python main.py`: this will run the code.

The project was written in VS code on Windows, with two main VS code extensions from Astral: `Ruff` is used for formatting, and the dev version of `ty` for type checking. It was assumed no use of AI or coding agents was allowed, so all code has been manually written

## Approach