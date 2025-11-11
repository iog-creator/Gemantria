#!/usr/bin/env python3
"""
Helper script to convert a local socket DSN to a network DSN format.

Usage:
    python3 scripts/ops/convert_socket_to_network_dsn.py <socket_dsn> <host> [port]

Example:
    python3 scripts/ops/convert_socket_to_network_dsn.py \
        "postgresql://user@/dbname?host=/var/run/postgresql" \
        "db.example.com" \
        5432
"""

import sys
from urllib.parse import urlparse, urlunparse, parse_qs, urlencode


def convert_socket_to_network(socket_dsn: str, host: str, port: int = 5432) -> str:
    """Convert a socket DSN to a network DSN."""
    parsed = urlparse(socket_dsn)
    
    # Extract user and database
    username = parsed.username or "postgres"
    database = parsed.path.lstrip("/").split("?")[0] or "postgres"
    
    # Build network DSN
    netloc = f"{username}@{host}:{port}"
    path = f"/{database}"
    
    # Preserve query parameters (except host)
    query_params = parse_qs(parsed.query)
    query_params.pop("host", None)  # Remove socket host parameter
    
    query = urlencode(query_params, doseq=True) if query_params else ""
    
    network_dsn = urlunparse((
        parsed.scheme or "postgresql",
        netloc,
        path,
        parsed.params,
        query,
        parsed.fragment
    ))
    
    return network_dsn


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(__doc__, file=sys.stderr)
        sys.exit(1)
    
    socket_dsn = sys.argv[1]
    host = sys.argv[2]
    port = int(sys.argv[3]) if len(sys.argv) > 3 else 5432
    
    try:
        network_dsn = convert_socket_to_network(socket_dsn, host, port)
        print(network_dsn)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

