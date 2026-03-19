# /stx-deploy:provision — Provision a Hetzner server

Arguments: $ARGUMENTS

## Argument parsing

Parse `$ARGUMENTS` as: `[OPTIONS]`

**Options**:
- `--type TYPE` — Server type (default: `cax31`). See help for all types.
- `--location LOC` — Datacenter location (default: `fsn1`)
- `--name NAME` — Server name (default: `streamtex-prod`)
- `--help` — Show server comparison tables and help choose

### Examples

```
/stx-deploy:provision
/stx-deploy:provision --type cax41 --name my-server
/stx-deploy:provision --help
```

## Required readings BEFORE execution

1. `.claude/developer/skills/hetzner-infrastructure.md` — pricing tables, datacenter info
2. `.claude/developer/agents/deploy-operator.md` — deployment protocol

## Workflow

### Step 1: Adopt the Deploy Operator role

Read and adopt `.claude/developer/agents/deploy-operator.md`.

### Step 2: Handle `--help`

If `--help` is passed, display:
1. The server comparison tables from `hetzner-infrastructure.md` (CAX, CX, CCX)
2. The scenario recommendation table
3. The datacenter table with latency estimates
4. Ask the user which configuration they want, then proceed.

### Step 3: Load credentials

Read `~/.stx-deploy.env` and extract `HETZNER_API_TOKEN`.

If the file doesn't exist or the token is missing:
1. Explain how to create a Hetzner account (https://console.hetzner.cloud/)
2. Explain how to generate an API token (Security → API Tokens → Read & Write)
3. Guide the user to save it:
   ```bash
   echo "HETZNER_API_TOKEN=your-token" >> ~/.stx-deploy.env
   chmod 600 ~/.stx-deploy.env
   ```
4. Wait for the user to confirm, then re-read the file.

### Step 4: Check existing state

Read `.stx-deploy.json` if it exists:
- If a server with the same name already exists → warn and ask to confirm
- If the provision phase is already completed → skip and suggest next phase

### Step 5: Confirm with user

Display a summary before creating:
```
Server Configuration:
  Name:     streamtex-prod
  Type:     cax31 (8 vCPU ARM, 16 GB RAM, 160 GB SSD)
  Location: fsn1 (Falkenstein, Germany)
  Image:    Ubuntu 24.04
  Cost:     ~16.49 EUR/month

Proceed? (yes/no)
```

Wait for user confirmation.

### Step 6: Check SSH key

Verify that an SSH key exists in the Hetzner project:
```bash
hcloud ssh-key list
```

If none:
1. Read the user's public key: `cat ~/.ssh/id_ed25519.pub` (or `id_rsa.pub`)
2. Upload it: `hcloud ssh-key create --name "local-key" --public-key-from-file ~/.ssh/id_ed25519.pub`

### Step 7: Create the server

```bash
hcloud server create \
  --name $NAME \
  --type $TYPE \
  --image ubuntu-24.04 \
  --location $LOCATION \
  --ssh-key "local-key"
```

Capture the server ID and IP address.

### Step 8: Create and apply firewall

```bash
hcloud firewall create --name "${NAME}-fw"
hcloud firewall add-rule "${NAME}-fw" --direction in --protocol tcp --port 22 --source-ips 0.0.0.0/0 --source-ips ::/0 --description "SSH"
hcloud firewall add-rule "${NAME}-fw" --direction in --protocol tcp --port 80 --source-ips 0.0.0.0/0 --source-ips ::/0 --description "HTTP"
hcloud firewall add-rule "${NAME}-fw" --direction in --protocol tcp --port 443 --source-ips 0.0.0.0/0 --source-ips ::/0 --description "HTTPS"
hcloud firewall add-rule "${NAME}-fw" --direction in --protocol tcp --port 8000 --source-ips 0.0.0.0/0 --source-ips ::/0 --description "Coolify (temporary)"
hcloud firewall apply-to-resource "${NAME}-fw" --type server --server $NAME
```

### Step 9: Verify SSH access

Wait 30 seconds for the server to boot, then:
```bash
ssh -o StrictHostKeyChecking=accept-new root@$IP "echo 'SSH OK'"
```

If it fails, wait and retry (up to 3 attempts with 15s intervals).

### Step 10: Update state file

Write or update `.stx-deploy.json` with:
- Server name, ID, type, location, IP
- Role: "primary"
- Status: "running"
- Firewall name and ID
- `phases_completed: ["provision"]`

### Step 11: Display next step

```
Server provisioned successfully!
  Name: streamtex-prod
  IP:   65.108.xxx.xxx
  Type: cax31 (16 GB RAM)

Next step: /stx-deploy:secure
```
