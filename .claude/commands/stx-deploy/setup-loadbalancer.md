# /stx-deploy:setup-loadbalancer — Configure multi-server load balancing

Arguments: $ARGUMENTS

## Argument parsing

Parse `$ARGUMENTS` as: `[OPTIONS]`

**Options**:
- `--type TYPE` — Load balancer type (default: `lb11`)
- `--servers NAME1,NAME2` — Existing servers to add as targets
- `--add-worker` — Provision a new worker server before creating the LB
- `--help` — Show load balancer comparison table

### Examples

```
/stx-deploy:setup-loadbalancer
/stx-deploy:setup-loadbalancer --type lb11 --servers streamtex-prod,streamtex-worker-1
/stx-deploy:setup-loadbalancer --add-worker --type lb11
/stx-deploy:setup-loadbalancer --help
```

## Required readings BEFORE execution

1. `.claude/developer/skills/hetzner-infrastructure.md` — LB pricing and specs
2. `.claude/developer/agents/deploy-operator.md` — deployment protocol

## Workflow

### Step 1: Adopt the Deploy Operator role

Read and adopt `.claude/developer/agents/deploy-operator.md`.

### Step 2: Handle `--help`

Display the load balancer comparison table:

| LB   | Services | Targets | Connections | Traffic | Price/mo |
|------|----------|---------|-------------|---------|----------|
| LB11 | 5        | 25      | 10,000      | 1 TB    | ~6 EUR   |
| LB21 | 15       | 75      | 20,000      | 2 TB    | ~40 EUR  |
| LB31 | 30       | 150     | 40,000      | 3 TB    | ~91 EUR  |

Explain sticky sessions requirement for Streamlit (WebSocket).

### Step 3: Provision worker (if --add-worker)

If `--add-worker`:
1. Determine worker name: `streamtex-worker-N` (increment from existing workers)
2. Use same server type and location as primary (from `.stx-deploy.json`)
3. Run the equivalent of `/stx-deploy:provision --name $WORKER_NAME`
4. Run the equivalent of `/stx-deploy:secure` on the new worker
5. Install Docker on the worker (Coolify will manage it):
   ```bash
   ssh $USER@$WORKER_IP "curl -fsSL https://get.docker.com | sudo sh"
   ```

### Step 4: Add worker to Coolify

Guide the user:
```
In Coolify dashboard (https://coolify.$DOMAIN):
1. Servers → Add Server
2. Name: $WORKER_NAME
3. IP: $WORKER_IP
4. User: $SSH_USER
5. SSH Key: use Coolify's generated key (copy it to the worker)
6. Validate connection
```

Alternatively, set up SSH key for Coolify:
```bash
# On the primary server, get Coolify's SSH public key
ssh $USER@$PRIMARY_IP "sudo cat /data/coolify/ssh/keys/id.root@host.docker.internal.pub"

# Add it to the worker's authorized_keys
ssh $USER@$WORKER_IP "echo '$COOLIFY_PUB_KEY' >> ~/.ssh/authorized_keys"
```

### Step 5: Create the load balancer

```bash
hcloud load-balancer create \
  --name streamtex-lb \
  --type $LB_TYPE \
  --location $LOCATION

# Add all servers as targets
for SERVER in $SERVERS; do
  hcloud load-balancer add-target streamtex-lb --server $SERVER
done
```

### Step 6: Configure services with sticky sessions

```bash
# HTTPS service with sticky sessions (CRITICAL for Streamlit WebSocket)
hcloud load-balancer add-service streamtex-lb \
  --protocol https \
  --listen-port 443 \
  --destination-port 443 \
  --http-sticky-sessions \
  --http-cookie-name STXLB \
  --http-cookie-lifetime 3600 \
  --health-check-protocol http \
  --health-check-port 80 \
  --health-check-path / \
  --health-check-interval 15 \
  --health-check-timeout 10

# HTTP service (will be redirected to HTTPS by Traefik)
hcloud load-balancer add-service streamtex-lb \
  --protocol http \
  --listen-port 80 \
  --destination-port 80
```

### Step 7: Update DNS

Get the LB IP and display DNS update instructions:
```bash
LB_IP=$(hcloud load-balancer describe streamtex-lb -o format='{{.PublicNet.IPv4.IP}}')
```

```
Update your DNS records to point to the Load Balancer IP:

| Type | Name | Old Value      | New Value    |
|------|------|----------------|--------------|
| A    | @    | $SERVER_IP     | $LB_IP       |
| A    | *    | $SERVER_IP     | $LB_IP       |

Update these records at your registrar, then confirm.
```

### Step 8: Verify

```bash
# Check LB status
hcloud load-balancer describe streamtex-lb

# Check targets are healthy
hcloud load-balancer describe streamtex-lb -o format='{{range .Targets}}{{.Server.Server.Name}}: {{.HealthStatus}}{{"\n"}}{{end}}'

# Test access through LB
curl -I "https://coolify.$DOMAIN"
```

### Step 9: Update state file

Update `.stx-deploy.json`:
- Add load_balancer section (name, ID, type, IP)
- Add new worker to servers list
- Update DNS records

### Step 10: Display result

```
Load Balancer configured!
  LB:      streamtex-lb (lb11)
  IP:      $LB_IP
  Targets: streamtex-prod (healthy), streamtex-worker-1 (healthy)
  Sticky:  enabled (cookie: STXLB, 1h)

DNS updated: *.$DOMAIN → $LB_IP

To redistribute projects across servers, use Coolify dashboard.
```
