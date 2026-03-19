# /stx-deploy:status — Show infrastructure and project status

Arguments: $ARGUMENTS

## Argument parsing

Parse `$ARGUMENTS` as: `[OPTIONS]`

**Options**:
- `--project NAME` — Status of a specific project
- `--all` — Full infrastructure status (default)
- `--verbose` — Include metrics, recent logs, and detailed info

### Examples

```
/stx-deploy:status
/stx-deploy:status --project cours-python --verbose
/stx-deploy:status --all --verbose
```

## Required readings BEFORE execution

1. `.claude/developer/agents/deploy-operator.md` — deployment protocol

## Workflow

### Step 1: Load state

Read `.stx-deploy.json`. If it doesn't exist:
```
No deployment state found. Start with: /stx-deploy:preflight
```

### Step 2: Infrastructure status

Display server information:
```
Infrastructure Status:
  Provider:  Hetzner Cloud
  Server:    streamtex-prod (cax31, 16 GB RAM)
  IP:        65.108.xxx.xxx
  Location:  fsn1 (Falkenstein, DE)
  Domain:    mondomaine.com (wildcard, SSL active)
  Dashboard: https://coolify.mondomaine.com
  LB:        none
  Phases:    provision ✓ secure ✓ coolify ✓ domain ✓
```

### Step 3: Probe each project

For each deployed project:
```bash
# Health check
HTTP_CODE=$(curl -s -o /dev/null -w '%{http_code}' "https://$SUBDOMAIN/_stcore/health" --max-time 10)

# Response time
RESPONSE_TIME=$(curl -s -o /dev/null -w '%{time_total}' "https://$SUBDOMAIN" --max-time 10)
```

Determine status:
- `running` — health check returns 200
- `slow` — health check returns 200 but response time > 3s
- `down` — health check fails or returns non-200
- `unknown` — cannot reach the server

### Step 4: Display project status

```
Projects (N deployed):
  #  Project          Status   URL                              Response  Memory
  1  cours-python     running  https://cours-python.domain.com  0.4s      512/1024 MB
  2  cours-docker     running  https://cours-docker.domain.com  0.3s      480/1024 MB
  3  dashboard-ml     slow     https://dashboard-ml.domain.com  4.2s      1800/2048 MB
```

### Step 5: Verbose mode

If `--verbose`, additionally:

1. **Server metrics** (via SSH):
   ```bash
   ssh $USER@$IP "free -h && echo '---' && df -h / && echo '---' && uptime"
   ```

2. **Docker stats** (per container):
   ```bash
   ssh $USER@$IP "sudo docker stats --no-stream --format 'table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}'"
   ```

3. **Recent logs** (last 20 lines per project):
   ```bash
   ssh $USER@$IP "sudo docker logs --tail 20 $CONTAINER_NAME 2>&1"
   ```

4. **SSL certificate expiry**:
   ```bash
   echo | openssl s_client -servername $SUBDOMAIN -connect $IP:443 2>/dev/null | openssl x509 -noout -dates
   ```

### Step 6: Recommendations

Based on the data collected, provide recommendations:
- If any project is `down` → suggest checking logs
- If RAM > 80% → suggest scaling (`/stx-deploy:scale --analyze`)
- If SSL expires < 14 days → warn about certificate renewal
- If disk > 80% → suggest `docker system prune`
- If response time > 3s → suggest investigating CPU or memory
