# Changelog

## [Unreleased]

### Added
- **Reverse Shell Tool**: New network connection tool that establishes a reverse shell connection to a remote host
  - Command-line interface: `httpkit-reverse-shell <host> <port>`
  - Module interface: `python -m httpkit.reverse_shell <host> <port>`
  - Programmatic API: `from httpkit import establish_reverse_shell`
  - Configurable connection timeout
  - Cross-platform shell support (bash, sh, cmd.exe)
  - Proper resource cleanup and error handling
- Support for explicit HTTP/HTTPS scheme in proxy URL
- Environment variable configuration for production settings
- HTTP/2 support for improved performance
- Concurrency limiting via semaphore to prevent resource exhaustion

### Changed
- Reuse httpx.AsyncClient globally instead of creating a new one per request
- Use StreamingResponse instead of buffering the entire response
- Filter out unsafe or conflicting response headers
- Improved error handling and response streaming
- Disabled auto-reload in production for better performance

### Fixed
- Memory usage issues with large responses
- Connection pooling and reuse
- Header handling to prevent conflicts