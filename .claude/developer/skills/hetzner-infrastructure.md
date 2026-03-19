# Hetzner Infrastructure Reference for StreamTeX Deployment

This skill provides reference data for all `stx-deploy:*` commands. Read this before
making infrastructure decisions or advising users on server sizing.

## 1. Hetzner Cloud Server Types (prices as of April 2026, EUR/month excl. VAT)

### CAX Series — ARM (Ampere Altra) — Best value

| Type   | vCPU | RAM    | SSD     | Traffic | Price/mo | Projects (Doc) | Projects (Data) |
|--------|------|--------|---------|---------|----------|----------------|-----------------|
| CAX11  | 2    | 4 GB   | 40 GB   | 20 TB   | ~4.49 €  | 3–5            | 1–2             |
| CAX21  | 4    | 8 GB   | 80 GB   | 20 TB   | ~8.49 €  | 8–15           | 3–5             |
| CAX31  | 8    | 16 GB  | 160 GB  | 20 TB   | ~16.49 € | 15–30          | 6–12            |
| CAX41  | 16   | 32 GB  | 320 GB  | 20 TB   | ~31.99 € | 30–60          | 12–25           |

### CX Series — x86 Shared (Intel/AMD)

| Type  | vCPU | RAM    | SSD     | Price/mo  |
|-------|------|--------|---------|-----------|
| CX22  | 2    | 4 GB   | 40 GB   | ~5.09 €   |
| CX32  | 4    | 8 GB   | 80 GB   | ~9.09 €   |
| CX42  | 8    | 16 GB  | 160 GB  | ~21.49 €  |
| CX52  | 16   | 32 GB  | 320 GB  | ~42.49 €  |

### CCX Series — Dedicated vCPU (guaranteed performance)

| Type   | vCPU (ded) | RAM     | SSD     | Price/mo   |
|--------|-----------|---------|---------|------------|
| CCX13  | 2         | 8 GB    | 80 GB   | ~12.49 €   |
| CCX23  | 4         | 16 GB   | 160 GB  | ~24.49 €   |
| CCX33  | 8         | 32 GB   | 240 GB  | ~48.49 €   |
| CCX43  | 16        | 64 GB   | 360 GB  | ~96.49 €   |
| CCX53  | 32        | 128 GB  | 600 GB  | ~191.99 €  |

### Recommendation by use case

| Use case                 | Server  | Why                                  |
|--------------------------|---------|--------------------------------------|
| Personal, testing        | CAX11   | Cheapest, enough for 3-5 light apps  |
| Small group, training    | CAX31   | Best value for 15-30 projects        |
| Class with 30+ students  | CAX41   | Many concurrent sessions             |
| Production with SLA      | CCX33   | Dedicated CPU, no noisy neighbor     |
| High load                | CCX43+  | 60+ projects, hundreds of users      |

## 2. Hetzner Load Balancers

| LB   | Services | Targets | SSL Certs | Connections | Traffic | Price/mo |
|------|----------|---------|-----------|-------------|---------|----------|
| LB11 | 5        | 25      | 10        | 10,000      | 1 TB    | ~6 €     |
| LB21 | 15       | 75      | 25        | 20,000      | 2 TB    | ~40 €    |
| LB31 | 30       | 150     | 50        | 40,000      | 3 TB    | ~91 €    |

**CRITICAL for Streamlit**: Sticky sessions MUST be enabled (cookie-based).
Streamlit uses persistent WebSocket connections — if a user's request is routed
to a different server mid-session, the connection breaks.

## 3. Other Hetzner Pricing

| Resource              | Price                |
|-----------------------|----------------------|
| IPv4 (primary)        | Included (0.50 €/mo) |
| Floating IPv4         | 3 €/mo               |
| Floating IPv6         | 1 €/mo               |
| Block Storage         | 0.057 €/GB/mo        |
| Snapshots             | 0.012 €/GB/mo        |
| Backups               | +20% of server price  |
| Extra traffic (>20TB) | 1 €/TB               |
| Cloud Firewall        | Free                 |
| Private Networks      | Free                 |

## 4. Datacenters

| Location       | ID   | Region     | Latency EU | Latency US | ARM available |
|----------------|------|------------|------------|------------|---------------|
| Falkenstein    | fsn1 | Germany    | ~10-20 ms  | ~100 ms    | Yes           |
| Nuremberg      | nbg1 | Germany    | ~10-20 ms  | ~100 ms    | Yes           |
| Helsinki       | hel1 | Finland    | ~30-40 ms  | ~120 ms    | Yes           |
| Ashburn        | ash  | USA (VA)   | ~80 ms     | ~10 ms     | No            |
| Hillsboro      | hil  | USA (OR)   | ~120 ms    | ~20 ms     | No            |

Default recommendation: **fsn1** for EU users, **ash** for US users.

## 5. StreamTeX Resource Consumption Profiles

### System overhead (incompressible)

| Component          | RAM     |
|--------------------|---------|
| OS + Docker        | ~500 MB |
| Coolify + Postgres | ~600 MB |
| Traefik            | ~100 MB |
| **Total**          | **~1.2 GB** |

### Per-project profiles

| Profile         | RAM idle | RAM/user   | Users/1GB | Typical projects              |
|-----------------|----------|------------|-----------|-------------------------------|
| **Documentation** | ~100 MB  | +30 MB     | 15–25     | manuals, courses, slides      |
| **Data/Visu**     | ~250 MB  | +80 MB     | 5–8       | dashboards, plotly, pandas    |
| **AI/Multimedia** | ~500 MB  | +150 MB    | 2–3       | image gen, ML models          |

### Capacity formula

```
Available RAM = Server RAM - 1.2 GB (overhead)
Max projects (idle) = Available RAM / Profile RAM idle
Max concurrent users = (Available RAM - N × Profile RAM idle) / Profile RAM per user
```

### Example: CAX31 (16 GB)

```
Available: 16 - 1.2 = 14.8 GB
Doc projects (idle): 14.8 GB / 100 MB = ~148 (theoretical max)
Practical limit: ~30 projects with moderate usage
```

## 6. Streamlit Configuration for Reverse Proxy

Every StreamTeX project deployed behind Traefik MUST have this `.streamlit/config.toml`:

```toml
[server]
headless = true
port = 8501
address = "0.0.0.0"
enableCORS = false
enableXsrfProtection = false

[browser]
gatherUsageStats = false
```

**Why CORS=false and XSRF=false?**
- Traefik terminates SSL and forwards traffic to the container
- The origin changes (external HTTPS → internal HTTP)
- CORS and XSRF protection would reject these "cross-origin" requests
- This is safe because Traefik handles the external security

## 7. Standard Dockerfile Template

```dockerfile
FROM python:3.13-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 \
    STREAMLIT_SERVER_HEADLESS=true UV_LINK_MODE=copy
WORKDIR /app
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev
COPY . .
EXPOSE 8501
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health
ENTRYPOINT ["uv", "run", "streamlit", "run", "book.py", \
    "--server.port=8501", "--server.address=0.0.0.0", \
    "--server.enableCORS=false", "--server.enableXsrfProtection=false"]
```

## 8. State File (.stx-deploy.json)

The state file tracks infrastructure state for idempotent operations. It is stored
at the workspace root and should NOT be committed to git (add to `.gitignore`).

**Key principle**: Credentials (API tokens, passwords) are NEVER stored in this file.
They are referenced via environment variable names pointing to `~/.stx-deploy.env`.

**Phases tracked**: provision, secure, install-coolify, configure-domain.
Each command checks which phases are completed before executing.

## 9. Security Checklist

- [ ] Non-root user with SSH key
- [ ] Root login disabled
- [ ] Password auth disabled
- [ ] UFW active (ports 22, 80, 443 only)
- [ ] ufw-docker installed (prevents Docker firewall bypass)
- [ ] fail2ban active (3 attempts → 1h ban)
- [ ] Unattended upgrades enabled
- [ ] Coolify dashboard behind HTTPS (not port 8000)
- [ ] No credentials in `.stx-deploy.json` or git
