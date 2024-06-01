# CEUR WS Workshops

Welcome to the CEUR WS Workshops project. This guide will help you set up your environment and install the necessary dependencies using the provided wheel file.

## Prerequisites

- Python 3.7 or higher
- pip (Python package installer)

## Installation Instructions

### 1. Create a Virtual Environment

First, create a virtual environment to ensure that the dependencies are installed in an isolated environment, preventing any potential conflicts with other projects.

```sh
python -m venv myenv
```

### 2. Activate the Virtual Environment 

Activate the virtual environment. The command to activate the environment varies based on your operating system:

```sh
source myenv/bin/activate
```

### 3. Install the Project Dependencies 

Once the virtual environment is activated, use pip to install the project dependencies from the provided wheel file.

```sh
pip install dist/ceur_ws_workshops-0.1-py3-none-any.whl
```


