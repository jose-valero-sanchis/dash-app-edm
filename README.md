# Dash App EDM

## Description

This Dash application is designed to visualize and analyze traffic in the city of Valencia during the Fallas week and the following week. It uses various interactive charts and maps to provide a clear view of how the festivities affect traffic.

## Features

- **General Situation:** Provides an overview of traffic conditions during the Fallas.
- **Street Impact:** Shows how Fallas affect specific streets.
- **Best Route:** Calculates the best route between two points avoiding closed streets.
- **Real-Time Traffic:** Displays real-time traffic conditions in Valencia.

## Installation

### Using Python Virtual Environment

1. Clone the repository:

    ```bash
    git clone https://github.com/jose-valero-sanchis/dash-app-edm.git
    cd dash-app-edm
    ```

2. Create a virtual environment and install dependencies:

    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    pip install -r requirements.txt
    ```

3. Run the application:

    ```bash
    python src/app.py
    ```

### Using Docker

1. Clone the repository:

    ```bash
    git clone https://github.com/jose-valero-sanchis/dash-app-edm.git
    cd dash-app-edm
    ```

2. Build the Docker image:

    ```bash
    docker build -t dash-app-edm .
    ```

3. Run the Docker container:

    ```bash
    docker run -p 8050:8050 dash-app-edm
    ```

## Usage

1. Navigate to `http://127.0.0.1:8050` in your browser.
2. Explore different sections using the navigation bar:
    - **Home:** General information about the project.
    - **General Situation:** Detailed analysis of traffic conditions during Fallas.
    - **How do the Fallas affect your street?:** Specific information on how Fallas affect selected streets.
    - **Find the best route:** Calculate the best route between two points.
    - **Real-Time Traffic:** View real-time traffic conditions.

## Data

- **Traffic Data:** Includes information on traffic conditions during and after the Fallas.
- **Geospatial Data:** Used for map and route visualizations.
  
## Contributors

- [Sebastián Gómez](https://github.com/2gomez)
- [Martín Juanes](https://github.com/mjuahop)
- [Jose Valero](https://github.com/jose-valero-sanchis) 
