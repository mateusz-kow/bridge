# Neuroguard Bridge!

[![CI](https://github.com/kn-neuron/neuroguard-bridge/actions/workflows/ci.yml/badge.svg)](https://github.com/kn-neuron/neuroguard-bridge/actions/workflows/ci.yml)
[![PyPI version](https://badge.fury.io/py/neuroguard-bridge.svg)](https://badge.fury.io/py/neuroguard-bridge)
[![Python Version](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/)

Neuroguard Bridge is a versatile application and Python SDK designed to standardize and simplify real-time data acquisition from various EEG devices. It acts as a "bridge" between EEG hardware and other applications, exposing data through a clean Python API or a ready-to-use WebSocket server.

## Key Features

-   **Plugin-Based Architecture**: Easily extensible to support new EEG devices without changing core logic. New hardware integrations are treated as self-contained plugins.
-   **Dual-Purpose**: Use it as a standalone WebSocket server for language-agnostic integration or as a Python library (SDK) in your own applications.
-   **Standardized API**: Interact with different EEG devices using a single, consistent programming interface. Write your code once, and it works with any supported device.
-   **Ready-to-Use Server**: Launch a WebSocket server with a single command to stream EEG data to web applications, game engines, or other clients in real-time.
-   **Robust Resource Management**: Cleanly initializes and deinitializes device SDKs to ensure stable, long-running operation and prevent resource leaks.

## Supported Devices
-   BrainAccess (MAXI, HALO)

## Installation

This project requires Python 3.11.

### 1. Install Neuroguard Bridge

Install the package directly from PyPI:

```bash
# For SDK-only usage
pip install neuroguard-bridge

# To include the WebSocket server dependencies
pip install "neuroguard-bridge[server]"
```

### 2. Install EEG Device SDKs

Neuroguard Bridge acts as an abstraction layer and does **not** bundle third-party device SDKs. You must install the SDK for your specific device(s) manually.

-   **For BrainAccess:** Follow the manufacturer's installation instructions available at the [BrainAccess Download Page](https://www.brainaccess.ai/download/).

## Quick Start

### As a Standalone Server

Launch the WebSocket server from your terminal. The server will automatically find and connect to the first available EEG device.

```bash
bridge-server --host localhost --port 50050
```

You can now connect to `ws://localhost:50050` with any WebSocket client.

### As a Python Library (SDK)

Use the `EEGConnector` to interact with a connected device in your Python code.

```python
import numpy as np
from bridge.eeg import EEGConnector, init, close

# Initialize all installed device SDKs
init()

try:
    # EEGConnector finds and connects to the first available device
    with EEGConnector() as device:
        print("Successfully connected to a device.")

        # Get device metadata
        device_info = device.get_device_data()
        if device_info:
            print(f"Device Name: {device_info.name}")
            print(f"Sample Rate: {device_info.sample_rate} Hz")

        # Acquire 5 seconds of EEG data
        print("Acquiring 5 seconds of EEG data...")
        eeg_data: np.ndarray = device.get_output(duration=5.0)

        print(f"Acquired data with shape: {eeg_data.shape}")
        # e.g., (32, 1250) for a 32-channel device at 250 Hz

except RuntimeError as e:
    print(f"An error occurred: {e}")

finally:
    # Cleanly close all device SDKs
    close()
```

## WebSocket API Reference

Connect your client to the address specified when running `bridge-server`. All communication is done via JSON-formatted text messages.

### Requests

Send a JSON object with a `request` key.

-   **Connect to Device**
    ```json
    {"request": "connect_device"}
    ```
-   **Get Device Info**
    ```json
    {"request": "get_device_info"}
    ```
-   **Acquire and Send Data**
    Acquires 10 seconds of data and sends it back.
    ```json
    {"request": "send_data"}
    ```
-   **Disconnect from Device**
    ```json
    {"request": "disconnect_device"}
    ```

### Responses

The server replies with a JSON object containing either a `result` or an `error` key.

-   **Success Response**
    ```json
    {
      "result": {
        "name": "BRAINACCESS-MAXI-1234",
        "mac_address": "00:11:22:33:44:55",
        "manufacturer": "BrainAccess",
        "electrodes_num": 32,
        "sample_rate": 250
      }
    }
    ```
-   **Error Response**
    ```json
    {"error": "Device not connected. Please send 'connect_device' request first."}
    ```