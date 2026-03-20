# /stx-deploy:scale — Scale infrastructure up or out

Arguments: $ARGUMENTS

## Argument parsing

Parse `$ARGUMENTS` as: `[OPTIONS]`

**Options**:
- `--analyze` — Analyze current metrics and recommend a scaling strategy (no action)
- `--vertical TYPE` — Upgrade the primary server to TYPE (e.g. `cax41`)
- `--horizontal` — Add a worker server + load balancer
- `--help` — Show scaling decision guide

### Examples

```
/stx-deploy:scale --analyze
/stx-deploy:scale --vertical cax41
/stx-deploy:scale --horizontal
/stx-deploy:scale --help
```

## Required readings BEFORE execution

1. `.claude/developer/skills/hetzner-infrastructure.md` — server types, pricing, capacity
2. `.claude/developer/agents/deploy-operator.md` — deployment protocol

## Workflow

### Step 1: Adopt the Deploy Operator role

Read and adopt `.claude/developer/agents/deploy-operator.md`.

### Step 2: Handle `--help`

Display the scaling decision table:

| Signal                           | Action                          |
|----------------------------------|---------------------------------|
| RAM > 80% sustained             | Vertical scaling (upgrade)      |
| RAM > 80% AND already on CCX43  | Horizontal scaling (add worker) |
| Need zero downtime              | Horizontal (multi-server + LB)  |
| Response time > 3s              | Check CPU; if saturated, scale  |
| LB connections > 80% capacity   | Upgrade load balancer           |
| 60+ projects on one server      | Add a server                    |

### Step 3: Check CDN status first

Read `.stx-deploy.json` and check `cdn.enabled`. If CDN is NOT configured:
```
Before scaling, consider adding Cloudflare CDN (free):
  - CDN caching reduces server load significantly
  - Bot/crawler blocking prevents wasted resources
  - Rate limiting stops abusive traffic
  - This may resolve your performance issue without scaling

Set up CDN: /stx-deploy:configure-domain $DOMAIN
```

### Step 4: Analyze (--analyze or default)

Collect metrics via SSH:
```bash
# RAM usage
ssh $USER@$IP "free -m | awk '/Mem:/{printf \"%.0f\", \$3/\$2*100}'"

# CPU usage
ssh $USER@$IP "top -bn1 | grep 'Cpu(s)' | awk '{print \$2}'"

# Disk usage
ssh $USER@$IP "df -h / | awk 'NR==2{print \$5}'"

# Container count and memory
ssh $USER@$IP "sudo docker stats --no-stream --format '{{.Name}} {{.MemUsage}}'"

# Number of projects
# (from .stx-deploy.json)
```

Display analysis:
```
Current Infrastructure Analysis:
  Server:     cax31 (8 vCPU, 16 GB RAM)
  RAM usage:  12.4 GB / 16 GB (78%)
  CPU usage:  35%
  Disk usage: 45%
  Projects:   22 deployed
  Capacity:   ~8 more projects (Doc profile)

Recommendation: RAM is approaching 80%. Consider:
  - Vertical: /stx-deploy:scale --vertical cax41 (32 GB, ~32 EUR/mo)
  - Horizontal: /stx-deploy:scale --horizontal (add worker, ~17 EUR/mo + LB ~6 EUR/mo)

Vertical is simpler. Horizontal provides redundancy.
```

### Step 5: Vertical scaling (--vertical)

**IMPORTANT**: Vertical scaling requires a brief server shutdown (2-5 minutes of downtime).

1. Confirm with user:
```
Scaling streamtex-prod from cax31 → cax41:
  RAM:  16 GB → 32 GB
  vCPU: 8 → 16
  Cost: ~16.49 → ~31.99 EUR/month (+15.50 EUR)
  Downtime: 2-5 minutes

Proceed? (yes/no)
```

2. Shutdown, resize, restart:
```bash
hcloud server shutdown streamtex-prod
# Wait for status powered-off
hcloud server change-type streamtex-prod $NEW_TYPE
hcloud server poweron streamtex-prod
```

3. Wait for server to come back:
```bash
# Poll SSH until server responds
for i in $(seq 1 20); do
  ssh -o ConnectTimeout=5 $USER@$IP "echo ok" 2>/dev/null && break
  sleep 15
done
```

4. Verify all containers are running:
```bash
ssh $USER@$IP "sudo docker ps --format 'table {{.Names}}\t{{.Status}}'"
```

5. Run health checks on all projects.

6. Update `.stx-deploy.json` with new server type.

### Step 6: Horizontal scaling (--horizontal)

1. Provision and secure a new worker (reuse provision + secure logic)
2. If no load balancer exists, create one (reuse setup-loadbalancer logic)
3. Add the worker to Coolify
4. Suggest which projects to move to the new worker

```
Horizontal scaling complete!
  New worker: streamtex-worker-1 (cax31, 16 GB)
  Load balancer: streamtex-lb (lb11)
  Total capacity: 32 GB (2 servers)

To move projects to the new worker:
  In Coolify → Application → Settings → Server → select streamtex-worker-1
```

### Step 7: Update state and display result

Update `.stx-deploy.json` with all changes and display final status.
