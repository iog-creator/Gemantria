# Network DSN Setup for CI

## Problem

CI environments (GitHub Actions) cannot use local socket DSNs (e.g., `postgresql://user@/dbname?host=/var/run/postgresql`) because there's no local PostgreSQL server. CI requires network DSNs with explicit host and port.

## Solution

Convert your local socket DSN to a network DSN format:

### Format Comparison

**Socket DSN (local only):**
```
postgresql://user@/dbname?host=/var/run/postgresql
postgresql:///dbname
```

**Network DSN (works in CI):**
```
postgresql://user:password@host:5432/dbname
postgresql://user:password@db.example.com:5432/gematria
```

### Conversion Helper

Use the conversion script:

```bash
python3 scripts/ops/convert_socket_to_network_dsn.py \
    "postgresql://user@/dbname?host=/var/run/postgresql" \
    "db.example.com" \
    5432
```

### Setting the GitHub Secret

1. **Get your network DSN** (either convert from socket or use existing network DSN)

2. **Set the secret** using one of these methods:

   **Method A: Via environment variable (recommended)**
   ```bash
   export ATLAS_DSN_RO_NET='postgresql://user:pass@host:5432/dbname'
   # Then run the OPS block - it will automatically update the secret
   ```

   **Method B: Direct via GitHub CLI**
   ```bash
   echo 'postgresql://user:pass@host:5432/dbname' | \
       gh secret set ATLAS_DSN_RO -b-
   ```

   **Method C: Via GitHub Web UI**
   - Go to: Settings → Secrets and variables → Actions
   - Edit `ATLAS_DSN_RO`
   - Paste the network DSN

### Required Format

The network DSN must include:
- ✅ Protocol: `postgresql://` or `postgres://`
- ✅ Username: `user`
- ✅ Password: `password` (if required)
- ✅ Host: `hostname` or IP address
- ✅ Port: `5432` (or your PostgreSQL port)
- ✅ Database: `dbname`

**Example:**
```
postgresql://gem_ro:secret123@db.example.com:5432/gematria
```

### Verification

After setting the secret, cut a new proof tag:

```bash
git tag -a ops/rc-proof-test-$(date -u +%Y%m%dT%H%M%SZ) \
    -m "Test: network DSN"
git push origin --tags
```

Check the workflow run - the tagproof export should now succeed.

### Troubleshooting

**Error: "connection is bad: connection to server on socket"**
- The secret still contains a socket DSN
- Update it to a network DSN format

**Error: "connection refused" or "timeout"**
- The host/port is incorrect or unreachable from CI
- Verify the database is accessible from the internet (or use a VPN/tunnel)

**Error: "authentication failed"**
- The username/password is incorrect
- Verify credentials in the DSN

