import unittest
from unittest.mock import patch, MagicMock
import orchestrator
import time

class TestOrchestrator(unittest.TestCase):
    @patch('orchestrator.subprocess.Popen')
    @patch('orchestrator.time.sleep', side_effect=lambda t: orchestrator.shutdown_event.set())
    def test_restarts_process_on_exit(self, mock_sleep, mock_popen):
        # Mock Popen to simulate process crashing
        mock_process = MagicMock()
        mock_process.poll.side_effect = [None, 1, None, None, None, None]
        mock_popen.return_value = mock_process

        # Run the orchestrator main loop in a separate thread to test its monitoring
        import threading
        # To prevent the test from running indefinitely, we'll stop the thread manually
        orchestrator.shutdown_event = threading.Event()
        orchestrator_thread = threading.Thread(target=orchestrator.main, daemon=True)
        orchestrator_thread.start()

        orchestrator_thread.join(timeout=5)

        # Assert that Popen was called at least twice for each process
        self.assertGreaterEqual(mock_popen.call_count, 2 * len(orchestrator.PROCESSES))
        
if __name__ == '__main__':
    unittest.main()
