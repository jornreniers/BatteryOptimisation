# Optimal battery dispatch

## Overview
This project groups code to instruct a battery to charge and discharge in order to trade power on two power markets. The objective is to maximise profit.

The inputs are in the `Data`-folder, outputs in the `Results`-folder and code in `src`.

The project has been designed to be flexible and modular, for instance by easily being able to add variables or constraints to the model. However, this means it is not the most computationally-efficient way of solving it.

## Tooling & Getting started
The project is setup using UV, and the .toml file contains the packages and their version numbers. It needs to be installed from [their website](https://docs.astral.sh/uv/getting-started/) if you have not done so. 

The code must be downloaded into a folder, and the data supplied by email put into the `Data`-folder (relative to the main-file) because the code will automatically try to read the file `Data/Attachment 2.xlsx` (if you have this file somewhere else, you can change the file name in `src/Settings.py`). Ie the struct is project/main.py, project/Data/Attachment 2.xlsx, project/src and project/Results.

To run the code, open a terminal and navigate to the project folder.

- `uv sync`: this will install all the required packages into your venv. It is needed only once.
- `uv run python main.py`: this will run the code.

The project was written in VS code on Windows, with two main VS code extensions from Astral: `Ruff` is used for formatting, and the dev version of `ty` for type checking. It was assumed no use of AI or coding agents was allowed, so all code has been manually written

## Limitations

Due to the 4-hour limitation, I only managed to implement one optimisation over one window. In reality, one would need to add a rolling-window approach where eg the first optimisation is days 1-7, then the window slides by a day to optimise days 2-8, etc. 

It would require little modification, the two main things are the initial SoC and the capacity, both of which are hard-coded in the settings-class. These values should only be used for the first window, while later windows need to start where the previous one finished. 

A further large improvement in performance would be to not rebuild the entire model for every period. At the moment all values are stored in matrices and each matrix is rebuild each time you build the model. However, each window would only have minor changes with respect to the previous one (objective function due to different price, and SoC constraint due to different initial SoC and capacity) so by allowing the user to overwrite these rows of the model, you wouldn't have to rebuild all the matrices again.