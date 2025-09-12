from logging import getLogger
from typing import Callable

from .core import DeviceData, EEGArray, EEGDevice

logger = getLogger(__name__)

device_classes_list: list[type[EEGDevice]] = []
init_functions: list[Callable[[], None]] = []
close_functions: list[Callable[[], None]] = []

try:
    from brainaccess import core

    from .brainaccess import BrainaccessDevice

    device_classes_list.append(BrainaccessDevice)
    init_functions.append(core.init)
    close_functions.append(core.close)
    logger.debug("Successfully registered BrainAccess device support.")

except ImportError:
    logger.warning(
        "Could not load BrainAccess support. This is expected if the 'brainaccess' plugin is not installed. "
        "If you intended to use it, please ensure the external BrainAccess SDK is installed correctly. "
        "Support for BrainAccess eeg will be disabled."
    )

device_classes = tuple(device_classes_list)
if not device_classes:
    logger.warning("No EEG device classes have been registered. Please ensure at least one device plugin is installed.")


def init() -> None:
    """Initializes all registered device SDKs."""
    for func in init_functions:
        func()


def close() -> None:
    """Closes all registered device SDKs."""
    for func in close_functions:
        func()


__all__ = [
    "device_classes",
    "init_functions",
    "close_functions",
    "DeviceData",
    "EEGDevice",
    "EEGArray",
    "init",
    "close",
]
