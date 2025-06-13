"""Tests for the reverse shell functionality."""

import pytest
import socket
import threading
import time
from unittest.mock import patch, MagicMock
from httpkit.tools.reverse_shell import ReverseShell, establish_reverse_shell


class TestReverseShell:
    """Test cases for the ReverseShell class."""
    
    def test_reverse_shell_init(self):
        """Test ReverseShell initialization."""
        shell = ReverseShell("localhost", 8080)
        assert shell.host == "localhost"
        assert shell.port == 8080
        assert shell.socket is None
        assert shell.process is None
    
    def test_connect_success(self):
        """Test successful connection."""
        # Create a mock server
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind(('localhost', 0))
        server_port = server_socket.getsockname()[1]
        server_socket.listen(1)
        
        def mock_server():
            conn, addr = server_socket.accept()
            time.sleep(0.1)  # Brief delay
            conn.close()
        
        server_thread = threading.Thread(target=mock_server, daemon=True)
        server_thread.start()
        
        # Test connection
        shell = ReverseShell("localhost", server_port)
        result = shell.connect()
        
        assert result is True
        assert shell.socket is not None
        
        # Cleanup
        shell.cleanup()
        server_socket.close()
    
    def test_connect_failure(self):
        """Test connection failure."""
        shell = ReverseShell("localhost", 65534)  # Valid port but likely closed
        result = shell.connect()
        
        assert result is False
        assert shell.socket is None
    
    def test_cleanup(self):
        """Test cleanup functionality."""
        shell = ReverseShell("localhost", 8080)
        
        # Mock socket and process
        mock_socket = MagicMock()
        mock_process = MagicMock()
        shell.socket = mock_socket
        shell.process = mock_process
        
        shell.cleanup()
        
        mock_socket.close.assert_called_once()
        mock_process.terminate.assert_called_once()
        assert shell.socket is None
        assert shell.process is None


class TestEstablishReverseShell:
    """Test cases for the establish_reverse_shell function."""
    
    @patch('httpkit.tools.reverse_shell.ReverseShell')
    def test_establish_reverse_shell_success(self, mock_reverse_shell_class):
        """Test successful reverse shell establishment."""
        # Mock the ReverseShell instance
        mock_shell = MagicMock()
        mock_shell.connect.return_value = True
        mock_reverse_shell_class.return_value = mock_shell
        
        result = establish_reverse_shell("localhost", 8080)
        
        assert result is True
        mock_reverse_shell_class.assert_called_once_with("localhost", 8080)
        mock_shell.connect.assert_called_once()
        mock_shell.spawn_shell.assert_called_once()
    
    @patch('httpkit.tools.reverse_shell.ReverseShell')
    def test_establish_reverse_shell_failure(self, mock_reverse_shell_class):
        """Test failed reverse shell establishment."""
        # Mock the ReverseShell instance
        mock_shell = MagicMock()
        mock_shell.connect.return_value = False
        mock_reverse_shell_class.return_value = mock_shell
        
        result = establish_reverse_shell("localhost", 8080)
        
        assert result is False
        mock_reverse_shell_class.assert_called_once_with("localhost", 8080)
        mock_shell.connect.assert_called_once()
        mock_shell.spawn_shell.assert_not_called()


class TestIntegration:
    """Integration tests for reverse shell functionality."""
    
    def test_import_from_main_module(self):
        """Test that the function can be imported from the main module."""
        from httpkit import establish_reverse_shell
        assert callable(establish_reverse_shell)
    
    def test_module_entry_point(self):
        """Test that the module can be imported correctly."""
        import httpkit.tools.reverse_shell
        assert hasattr(httpkit.tools.reverse_shell, 'main')
        assert hasattr(httpkit.tools.reverse_shell, 'establish_reverse_shell')
        assert hasattr(httpkit.tools.reverse_shell, 'ReverseShell')