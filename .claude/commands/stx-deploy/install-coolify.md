# /stx-deploy:install-coolify — Install Coolify v4 on the server

Arguments: $ARGUMENTS

## Argument parsing

No arguments required. Reads server info from `.stx-deploy.json`.

### Examples

```
/stx-deploy:install-coolify
```

## Required readings BEFORE execution

1. `.claude/developer/agents/deploy-operator.md` — deployment protocol

## Workflow

### Step 1: Adopt the Deploy Operator role

Read and adopt `.claude/developer/agents/deploy-operator.md`.

### Step 2: Load state

Read `.stx-deploy.json`:
- Get primary server IP and SSH user
- Verify "secure" phase is completed
- If "install-coolify" already completed → inform and skip

### Step 3: Install Coolify

Connect to the server and run the official installer:
```bash
ssh $USER@$IP "curl -fsSL https://cdn.coollabs.io/coolify/install.sh | sudo bash"
```

This installs:
- Docker and Docker Compose (if not present)
- Coolify containers
- Traefik reverse proxy
- PostgreSQL database for Coolify

The installation takes approximately 3 minutes.

### Step 4: Wait for Coolify to be ready

Poll until Coolify responds:
```bash
# Check every 15 seconds, timeout after 5 minutes
for i in $(seq 1 20); do
  if ssh $USER@$IP "curl -s -o /dev/null -w '%{http_code}' http://localhost:8000" | grep -q "200\|301\|302"; then
    echo "Coolify is ready"
    break
  fi
  sleep 15
done
```

### Step 5: Guide initial setup

Tell the user:
```
Coolify is installed and running!

Please complete the initial setup in your browser:
1. Open http://<IP>:8000
2. Create an admin account (email + password)
3. Complete the onboarding wizard
4. Come back here and confirm when done.
```

Wait for user confirmation.

### Step 6: Verify Docker and Traefik

```bash
ssh $USER@$IP << 'REMOTE'
# Check Docker
sudo docker ps --format "table {{.Names}}\t{{.Status}}" | head -20

# Check Traefik is running
sudo docker ps --filter "name=coolify-proxy" --format "{{.Status}}"
REMOTE
```

Report status of all Coolify containers:
- `coolify` — main application
- `coolify-db` — PostgreSQL
- `coolify-proxy` — Traefik
- `coolify-realtime` — WebSocket server
- `coolify-redis` — Redis cache

### Step 7: Update state file

Update `.stx-deploy.json`:
- Set `coolify_installed: true`
- Set `coolify_url: "http://<IP>:8000"` (temporary, will be updated in domain phase)
- Add `"install-coolify"` to `phases_completed`

### Step 8: Display next step

```
Coolify installed and running!
  Dashboard: http://<IP>:8000
  Docker:    active
  Traefik:   active
  Containers: 5 running

Next step: /stx-deploy:configure-domain <your-domain.com>
```
