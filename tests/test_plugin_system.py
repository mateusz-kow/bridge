import importlib
import unittest
from unittest.mock import MagicMock, patch


class TestPluginSystem(unittest.TestCase):
    @patch("bridge.eeg.init_functions", [MagicMock()])
    @patch("bridge.eeg.close_functions", [MagicMock()])
    def test_init_and_close_call_registered_functions(self) -> None:
        """
        Verify that eeg.init() and eeg.close() call the functions
        registered by the plugin system.
        """
        from bridge.eeg import close, close_functions, init, init_functions

        init_func_mock = init_functions[0]
        close_func_mock = close_functions[0]

        init()
        init_func_mock.assert_called_once()
        close_func_mock.assert_not_called()

        init()
        self.assertEqual(init_func_mock.call_count, 2, "Expected init function to be called a second time.")

        close()
        close_func_mock.assert_called_once()
        self.assertEqual(init_func_mock.call_count, 2)

    def test_logs_warning_when_no_plugins_are_loaded(self) -> None:
        """
        Verify that a WARNING is logged if the devices module is loaded and no
        device classes were successfully registered.
        """
        import bridge.eeg

        # By removing brainaccess from sys.modules, we ensure that the import
        # within bridge.eeg.__init__ will fail, simulating an environment where
        # the plugin is not installed.
        with patch.dict("sys.modules", {"brainaccess": None}):
            with self.assertLogs("bridge.eeg", level="WARNING") as cm:
                # Reload the module to trigger the module-level logic
                importlib.reload(bridge.eeg)

        # The reload will cause two warnings: one for failing to load BrainAccess,
        # and one because no device classes are registered as a result.
        # We check for the latter, which is the purpose of this test.
        self.assertTrue(
            any("No EEG device classes have been registered" in message for message in cm.output),
            "Expected warning log message not found.",
        )
