# Neuroguard Bridge Developer Guide

Welcome, contributor! This guide provides all the information you need to get started with developing Neuroguard Bridge.

## Getting Started: Development Setup

### Prerequisites

-   Python 3.11
-   Git

### Setup Instructions

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/kn-neuron/neuroguard-bridge.git
    cd neuroguard-bridge
    ```

2.  **Create and activate a virtual environment:**
    This isolates project dependencies from your system's Python installation.
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3.  **Install the project in editable mode with all development dependencies:**
    The `[dev]` extra includes everything needed for development, such as `pytest`, `ruff`, `black`, and `mypy`. The `-e` flag installs the package in "editable" mode, so changes to the source code are immediately reflected.
    ```bash
    pip install -e .[dev]
    ```

4.  **Install a device SDK (optional):**
    If you are developing a feature related to a specific device (e.g., BrainAccess), you must install its SDK manually. Refer to the main `README.md` for instructions.

## Architecture Overview

The project is structured to be modular and extensible.

-   `src/eeg/core/`: Defines the abstract `EEGDevice` base class and common data structures (`DeviceData`). This is the core interface that all device plugins must implement.
-   `src/eeg/brainaccess/`: An example of a device plugin package. It contains the `BrainaccessDevice` class, which inherits from `EEGDevice` and implements the connection and data acquisition logic using the BrainAccess SDK.
-   `src/eeg/__init__.py`: This file implements a simple plugin discovery system. It attempts to import device classes (like `BrainaccessDevice`) and registers them in a central list. This allows the `EEGConnector` to be decoupled from specific implementations.
-   `src/eeg/connector.py`: The `EEGConnector` is the main entry point for the SDK. It iterates through all registered device classes and attempts to connect to the first one that is available.
-   `src/server/`: Contains the WebSocket server logic, which uses the `EEGConnector` to interact with the hardware.

## How to Add Support for a New EEG Device

Adding a new device is the most common way to contribute. Follow these steps:

1.  **Create a New Package:**
    Inside `src/eeg/`, create a new directory for your device (e.g., `src/eeg/mydevice/`). Add an `__init__.py` file to it.

2.  **Implement the `EEGDevice` Interface:**
    In your new package, create a `device.py` file. Inside it, define a class that inherits from `eeg.core.EEGDevice`. You must implement all abstract methods:
    -   `connect(self) -> None`
    -   `disconnect(self) -> None`
    -   `get_output(self, duration: float, output_file: str | None = None) -> EEGArray`
    -   `get_device_data(self) -> DeviceData | None`
    -   Optionally, you can also implement `get_impedance`.

    ```python
    # src/eeg/mydevice/device.py
    from eeg.core import DeviceData, EEGArray, EEGDevice
    from mydevice_sdk import SomeDeviceAPI

    class MyDevice(EEGDevice):
        def __init__(self):
            super().__init__()
            self._api = SomeDeviceAPI()
            self._is_connected = False

        def connect(self) -> None:
            self._logger.info("Connecting to MyDevice...")
            self._api.connect()
            self._is_connected = True
            self._logger.info("MyDevice connected.")

        def disconnect(self) -> None:
            # ... implementation ...

        def get_output(self, duration: float, output_file: str | None = None) -> EEGArray:
            # ... implementation ...

        def get_device_data(self) -> DeviceData | None:
            # ... implementation ...
    ```

3.  **Register Your Device:**
    In `src/eeg/__init__.py`, add a `try...except ImportError` block to register your new device class. This ensures the bridge runs even if the new device's SDK isn't installed.

    ```python
    # src/eeg/__init__.py

    # ... existing imports ...

    try:
        from .mydevice import MyDevice # Add this
        device_classes.append(MyDevice) # Add this
        logger.debug("Successfully registered MyDevice support.") # Add this
    except ImportError:
        logger.warning("Could not load MyDevice support.") # Add this

    # ... rest of the file ...
    ```

4.  **Add Tests:**
    Create a new test file in the `tests/` directory (e.g., `tests/test_mydevice.py`). Write unit tests for your new device class. You will likely need to mock the device's SDK to test your implementation in isolation.

## Code Style & Quality Assurance

We enforce strict code quality standards to maintain a clean and reliable codebase. Before submitting a pull request, please run the following checks locally.

### Running Tests

Execute the full test suite using `pytest`:
```bash
pytest
```

### Running Linter & Formatter

We use `ruff` for linting and `black` for formatting. The CI pipeline will fail if your code does not adhere to the configured style.

To check for issues:
```bash
# Check formatting
black --check .
ruff format --check .

# Check for linting errors
ruff check .
```

To automatically fix issues:
```bash
black .
ruff format .
ruff check --fix .
```

### Running Type Checker

We use `mypy` for static type checking.
```bash
mypy src
```