# /stx-deploy:secure — Secure the Hetzner server

Arguments: $ARGUMENTS

## Argument parsing

Parse `$ARGUMENTS` as: `[OPTIONS]`

**Options**:
- `--user NAME` — Non-root user to create (default: `deploy`)
- `--ssh-port PORT` — SSH port (default: `22`)

### Examples

```
/stx-deploy:secure
/stx-deploy:secure --user admin
```

## Required readings BEFORE execution

1. `.claude/developer/agents/deploy-operator.md` — deployment protocol

## Workflow

### Step 1: Adopt the Deploy Operator role

Read and adopt `.claude/developer/agents/deploy-operator.md`.

### Step 2: Load state

Read `.stx-deploy.json`:
- Get the primary server IP
- Verify phase "provision" is completed
- If "secure" is already completed → inform user and skip (unless they insist)

### Step 3: Connect and update system

SSH into the server as root:
```bash
ssh root@$IP "apt update && apt upgrade -y"
```

### Step 4: Create non-root user

```bash
ssh root@$IP << 'REMOTE'
adduser --disabled-password --gecos "" $USER
usermod -aG sudo $USER
echo "$USER ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/$USER
mkdir -p /home/$USER/.ssh
cp ~/.ssh/authorized_keys /home/$USER/.ssh/
chown -R $USER:$USER /home/$USER/.ssh
chmod 700 /home/$USER/.ssh
chmod 600 /home/$USER/.ssh/authorized_keys
REMOTE
```

### Step 5: Test new user login

**CRITICAL**: Before disabling root login, verify the new user works:
```bash
ssh $USER@$IP "sudo echo 'sudo OK'"
```

If this fails, DO NOT proceed with SSH hardening. Report the error and stop.

### Step 6: Harden SSH

Only after Step 5 succeeds:
```bash
ssh $USER@$IP << 'REMOTE'
sudo sed -i 's/^#*PermitRootLogin.*/PermitRootLogin no/' /etc/ssh/sshd_config
sudo sed -i 's/^#*PasswordAuthentication.*/PasswordAuthentication no/' /etc/ssh/sshd_config
sudo sed -i 's/^#*PubkeyAuthentication.*/PubkeyAuthentication yes/' /etc/ssh/sshd_config
sudo sed -i 's/^#*MaxAuthTries.*/MaxAuthTries 3/' /etc/ssh/sshd_config
sudo systemctl restart sshd
REMOTE
```

### Step 7: Install and configure UFW

```bash
ssh $USER@$IP << 'REMOTE'
sudo apt install ufw -y
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow 22/tcp comment 'SSH'
sudo ufw allow 80/tcp comment 'HTTP'
sudo ufw allow 443/tcp comment 'HTTPS'
sudo ufw allow 8000/tcp comment 'Coolify dashboard (temporary)'
sudo ufw --force enable
REMOTE
```

### Step 8: Install ufw-docker

```bash
ssh $USER@$IP << 'REMOTE'
sudo wget -O /usr/local/bin/ufw-docker https://github.com/chaifeng/ufw-docker/raw/master/ufw-docker
sudo chmod +x /usr/local/bin/ufw-docker
sudo ufw-docker install
sudo systemctl restart ufw
REMOTE
```

### Step 9: Install fail2ban

```bash
ssh $USER@$IP << 'REMOTE'
sudo apt install fail2ban -y
sudo tee /etc/fail2ban/jail.local > /dev/null << 'JAIL'
[sshd]
enabled = true
port = 22
filter = sshd
logpath = /var/log/auth.log
maxretry = 3
bantime = 3600
findtime = 600
JAIL
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
REMOTE
```

### Step 10: Configure automatic updates

```bash
ssh $USER@$IP << 'REMOTE'
sudo apt install unattended-upgrades -y
sudo dpkg-reconfigure -plow unattended-upgrades
REMOTE
```

### Step 11: Verify all security measures

Run verification checks:
```bash
# Verify root login is disabled
ssh root@$IP "echo test" 2>&1  # Should fail

# Verify UFW is active
ssh $USER@$IP "sudo ufw status verbose"

# Verify fail2ban is running
ssh $USER@$IP "sudo systemctl status fail2ban"
```

Report results.

### Step 12: Update state file

Update `.stx-deploy.json`:
- Set `secured: true`
- Add `"secure"` to `phases_completed`
- Record the non-root username

### Step 13: Display next step

```
Server secured successfully!
  User: deploy (sudo, SSH key)
  SSH:  root login disabled, password auth disabled
  UFW:  active (22, 80, 443, 8000)
  fail2ban: active (3 attempts → 1h ban)
  Updates: automatic

Note: This secures the server at OS level. For application-level
protection (DDoS, bot blocking, rate limiting, WAF), Cloudflare CDN
will be proposed during /stx-deploy:configure-domain.

Next step: /stx-deploy:install-coolify
```
