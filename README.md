# Training an AI to play Flappy Bird using NEAT

A project to recreate the classic game Flappy Bird in Python using Pygame. Further, creation of an AI to play this game using NEAT.

## Installation and running

This has been tested with Python `3.10.6`, but should work for Python `3.7+`. Alternative pip installation commands are given below.

1. Download this repo.
2. Create a new virtual environment: `python -m venv venv`
3. Activate this virtual environment: `venv\Scripts\activate` (if Windows OS)
4. Install required packages: `pip install -r requirements.txt`
5. Run the program using: `python NEAT_FlappyBird.py`

Please note that to successfully run this project, the *assets* folder (with all contents) and *config-feedforward.txt* file must be downloaded **and must be placed in the same location as the .py file**.

Alternative pip installation commands (use if the installation using the `requirements.txt` file fails):
```
pip install neat-python pygame-ce
```

## References

> The Pygame Development Team. *Pygame Community Edition.* Nov. 2023. url: https://pyga.me/docs/

> Alan McIntyre et al. *neat-python.* Mar. 2022. url: https://neat-python.readthedocs.io/en/latest/
