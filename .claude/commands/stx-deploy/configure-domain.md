# /stx-deploy:configure-domain — Configure DNS and SSL

Arguments: $ARGUMENTS

## Argument parsing

Parse `$ARGUMENTS` as: `<domain> [OPTIONS]`

- **domain** (required): The domain name to configure (e.g. `mondomaine.com`)

**Options**:
- `--registrar namecheap|gandi|ovh|cloudflare` — Show registrar-specific DNS instructions

### Examples

```
/stx-deploy:configure-domain mondomaine.com
/stx-deploy:configure-domain mondomaine.com --registrar gandi
```

## Required readings BEFORE execution

1. `.claude/developer/agents/deploy-operator.md` — deployment protocol

## Workflow

### Step 1: Adopt the Deploy Operator role

Read and adopt `.claude/developer/agents/deploy-operator.md`.

### Step 2: Load state

Read `.stx-deploy.json`:
- Get server IP
- Verify "install-coolify" phase is completed
- If "configure-domain" already completed → inform and offer to reconfigure

### Step 3: Display DNS records to configure

```
Configure these DNS records at your registrar:

| Type | Name | Value           | TTL |
|------|------|-----------------|-----|
| A    | @    | <server-IP>     | 300 |
| A    | *    | <server-IP>     | 300 |

The wildcard (*) record enables all subdomains (project-a.domain.com,
project-b.domain.com, etc.) to point to your server automatically.
```

### Step 4: Registrar-specific instructions

If `--registrar` is specified, provide step-by-step instructions:

**Namecheap**:
1. Log in → Domain List → Manage → Advanced DNS
2. Add A Record: Host=`@`, Value=`<IP>`, TTL=Automatic
3. Add A Record: Host=`*`, Value=`<IP>`, TTL=Automatic

**Gandi**:
1. Log in → Domaines → domain → Enregistrements DNS
2. Ajouter un enregistrement A: Nom=`@`, Valeur=`<IP>`, TTL=300
3. Ajouter un enregistrement A: Nom=`*`, Valeur=`<IP>`, TTL=300

**OVH**:
1. Manager → Noms de domaine → domain → Zone DNS
2. Ajouter une entree A: Sous-domaine=(vide), Cible=`<IP>`, TTL=300
3. Ajouter une entree A: Sous-domaine=`*`, Cible=`<IP>`, TTL=300

**Cloudflare**:
1. Dashboard → domain → DNS → Records
2. Add A: Name=`@`, Content=`<IP>`, Proxy=OFF (DNS only), TTL=Auto
3. Add A: Name=`*`, Content=`<IP>`, Proxy=OFF (DNS only), TTL=Auto
4. **IMPORTANT**: Disable Cloudflare proxy (orange cloud → grey) for WebSocket compatibility

### Step 5: Wait for user confirmation

```
Configure the DNS records above, then confirm here.
DNS propagation typically takes 5-30 minutes.
```

### Step 6: Verify DNS propagation

Loop until DNS resolves correctly (timeout: 10 minutes):
```bash
# Check main domain
dig +short $DOMAIN

# Check wildcard
dig +short test.$DOMAIN
```

Both should return the server IP. If not after 10 minutes:
- Suggest checking the DNS configuration
- Suggest using `dig @8.8.8.8 $DOMAIN` (Google DNS) to bypass local cache
- Offer to continue anyway (Let's Encrypt will retry)

### Step 7: Configure Coolify wildcard domain

Via the Coolify API (or guide the user through the UI):
```
In Coolify dashboard:
1. Settings → Configuration
2. Instance's Domain: https://coolify.$DOMAIN
3. Save
```

### Step 8: Wait for SSL certificate

```bash
# Check if SSL is valid (retry for up to 2 minutes)
for i in $(seq 1 8); do
  if curl -s -o /dev/null -w '%{http_code}' "https://coolify.$DOMAIN" 2>/dev/null | grep -q "200\|301\|302"; then
    echo "SSL OK"
    break
  fi
  sleep 15
done
```

### Step 9: Close temporary port 8000

Once the Coolify dashboard is accessible via HTTPS:
```bash
ssh $USER@$IP "sudo ufw delete allow 8000/tcp"
```

### Step 10: Verify final access

```bash
curl -I "https://coolify.$DOMAIN"
```

Should return HTTP 200 with valid SSL.

### Step 11: Update state file

Update `.stx-deploy.json`:
- Set domain name, registrar, DNS configured, SSL active, wildcard
- Update `coolify_url` to `https://coolify.$DOMAIN`
- Add `"configure-domain"` to `phases_completed`

### Step 12: Display next step

```
Domain configured successfully!
  Domain:    $DOMAIN
  Wildcard:  *.$DOMAIN → <IP>
  SSL:       active (Let's Encrypt)
  Dashboard: https://coolify.$DOMAIN

Next step: /stx-deploy:deploy [project-path]
```
