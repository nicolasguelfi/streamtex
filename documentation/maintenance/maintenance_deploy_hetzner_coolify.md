# Plan de Maintenance : Deploiement StreamTeX sur Hetzner + Coolify

> **Date** : 2026-03-02
> **Auteur** : Nicolas Guelfi + Claude
> **Version** : 1.0
> **Statut** : A FAIRE
> **Prerequis** : Compte Hetzner existant (projets Quasible, GAIWA)

---

## Table des matieres

1. [Resume executif](#1-resume-executif)
2. [Architecture cible](#2-architecture-cible)
3. [Choix du serveur Hetzner](#3-choix-du-serveur-hetzner)
4. [Phase 1 : Provisionner le serveur Hetzner](#4-phase-1--provisionner-le-serveur-hetzner)
5. [Phase 2 : Securiser le serveur](#5-phase-2--securiser-le-serveur)
6. [Phase 3 : Installer Coolify](#6-phase-3--installer-coolify)
7. [Phase 4 : Configurer le domaine et le DNS](#7-phase-4--configurer-le-domaine-et-le-dns)
8. [Phase 5 : Deployer le premier projet StreamTeX](#8-phase-5--deployer-le-premier-projet-streamtex)
9. [Phase 6 : Deployer tous les projets](#9-phase-6--deployer-tous-les-projets)
10. [Phase 7 : Adapter le CLI `stx deploy`](#10-phase-7--adapter-le-cli-stx-deploy)
11. [Monitoring et maintenance courante](#11-monitoring-et-maintenance-courante)
12. [Estimation des couts](#12-estimation-des-couts)
13. [Capacite et limites de Streamlit](#13-capacite-et-limites-de-streamlit)
14. [Troubleshooting](#14-troubleshooting)
15. [Checklist de validation](#15-checklist-de-validation)

---

## 1. Resume executif

### 1.1 Objectif

Migrer le deploiement des projets StreamTeX depuis Render (plan free, limites de performance)
vers un VPS Hetzner auto-gere avec **Coolify** comme plateforme de deploiement, permettant :

1. **Multi-projets** sur un seul serveur (~40 EUR/mois pour 10-20 projets)
2. **Load balancing** via Traefik (integre dans Coolify)
3. **SSL automatique** (Let's Encrypt)
4. **Deploiement continu** via GitHub webhooks
5. **Scalabilite** supportant des centaines d'utilisateurs simultanes par projet

### 1.2 Decisions cles

| Aspect | Decision | Justification |
|--------|----------|---------------|
| Hebergeur | Hetzner | Excellent rapport qualite/prix, datacenters EU |
| Type serveur | Cloud VPS (CAX41 ARM) ou dedie (AX41) | 32-64 GB RAM, suffisant pour 10-20 projets |
| PaaS | Coolify v4 (self-hosted) | Alternative gratuite a Render, interface web, Traefik integre |
| Reverse proxy | Traefik (via Coolify) | WebSocket natif, SSL auto, routing par sous-domaine |
| Routing | Sous-domaines (`stx-ai4se.domaine.com`) | Streamlit ne supporte pas le path-based routing |
| CI/CD | GitHub webhooks (via Coolify) | Auto-deploy sur push, zero config cote GitHub |
| Firewall | Hetzner Cloud Firewall + ufw-docker | Defense en profondeur, Docker ne contourne pas |

### 1.3 Mapping Render → Coolify

| Avant (Render) | Apres (Coolify/Hetzner) |
|---|---|
| render.yaml | Configuration Coolify (UI ou API) |
| Service Render par projet | Container Docker par projet |
| Domaine `*.onrender.com` | Sous-domaine `*.ton-domaine.com` |
| SSL automatique | Let's Encrypt via Traefik |
| `stx deploy render .` | `stx deploy coolify .` (a creer) |
| Plan free (limites) | Ressources du serveur (partagees) |

---

## 2. Architecture cible

### 2.1 Vue globale

```
[Internet]
    |
[Hetzner Cloud Firewall]          ← Ports 80, 443, 22 seulement
    |
[Hetzner VPS - CAX41 ou AX41]
    |
[UFW + ufw-docker]                ← Firewall host-level
    |
[Coolify]                         ← Management platform
    |
    +-- Traefik (reverse proxy)
    |     |
    |     +-- stx-ai4se.domaine.com       → container:8501
    |     +-- stx-modelsward.domaine.com   → container:8501
    |     +-- stx-aiai18h.domaine.com      → container:8501
    |     +-- stx-html-example.domaine.com → container:8501
    |     +-- docs.domaine.com             → container:8501
    |     +-- ... (futurs projets)
    |
    +-- Container stx-ai4se        (Streamlit, 1-2 GB RAM)
    +-- Container stx-modelsward   (Streamlit, 1-2 GB RAM)
    +-- Container stx-aiai18h      (Streamlit, 1-2 GB RAM)
    +-- Container stx-html-example (Streamlit, 1-2 GB RAM)
    +-- Container streamtex-docs   (Streamlit, 1-2 GB RAM)
```

### 2.2 Budget memoire (CAX41 — 32 GB RAM)

| Composant | RAM estimee | Note |
|-----------|-------------|------|
| OS + Docker | ~500 MB | Overhead systeme |
| Coolify + PostgreSQL | ~600 MB | Plateforme de gestion |
| Traefik | ~100 MB | Reverse proxy |
| **Disponible pour les apps** | **~30 GB** | |
| 1 projet Streamlit | 500 MB — 2 GB | Selon la complexite et le nombre d'utilisateurs |
| **Capacite estimee** | **15-30 projets** | Avec 1 GB par projet en moyenne |

### 2.3 Budget memoire (AX41 — 64 GB RAM)

| Composant | RAM estimee | Note |
|-----------|-------------|------|
| OS + Docker | ~500 MB | Overhead systeme |
| Coolify + PostgreSQL | ~600 MB | Plateforme de gestion |
| Traefik | ~100 MB | Reverse proxy |
| **Disponible pour les apps** | **~62 GB** | |
| **Capacite estimee** | **30-60 projets** | Avec 1 GB par projet en moyenne |

---

## 3. Choix du serveur Hetzner

### 3.1 Options recommandees

| Serveur | CPU | RAM | Stockage | Prix/mois | Trafic | Ideal pour |
|---------|-----|-----|----------|-----------|--------|------------|
| **CAX41** (ARM Cloud) | 16 vCPU | 32 GB | 320 GB SSD | ~25 EUR | 20 TB | Debut, 5-15 projets |
| **AX41-NVMe** (Dedie) | 6C/12T Ryzen | 64 GB | 2x512 GB NVMe | ~40 EUR | Illimite | Production, 15-30+ projets |
| **AX42** (Dedie) | 8C/16T Ryzen Zen4 | 64 GB DDR5 | 2x512 GB NVMe Gen4 | ~50 EUR | Illimite | Performance maximale |

### 3.2 Recommandation

**Pour commencer : CAX41 (ARM, 32 GB, ~25 EUR/mois)**

- Suffisant pour 10-15 projets StreamTeX
- Laisse de la marge dans le budget pour un domaine (~10 EUR/an) et des backups (~3 EUR/mois)
- Facile a upgrader vers un AX41 si les besoins augmentent
- Architecture ARM64 supportee par Coolify et Docker

**Pour la production a terme : AX41-NVMe (64 GB, ~40 EUR/mois)**

- Double la capacite memoire
- Trafic illimite (important pour des milliers d'utilisateurs)
- Performances I/O superieures (NVMe dedie)
- Pas de "noisy neighbors" (serveur dedie vs cloud partage)

### 3.3 Note sur les prix (avril 2026)

Hetzner a annonce une augmentation des prix a partir du 1er avril 2026 (+3-30% selon les produits).
Commander avant cette date pour beneficier des prix actuels.

---

## 4. Phase 1 : Provisionner le serveur Hetzner

### 4.1 Creer un nouveau projet Hetzner

1. Se connecter a la console Hetzner : https://console.hetzner.cloud/
2. Cliquer sur **"+ New project"** (a cote de Quasible et GAIWA)
3. Nommer le projet : **`StreamTeX`**

### 4.2 Creer le serveur (Cloud VPS — CAX41)

1. Dans le projet StreamTeX, cliquer sur **"Add Server"**
2. Configurer :

| Parametre | Valeur |
|-----------|--------|
| **Location** | Falkenstein (FSN1) ou Nuremberg (NBG1) — les moins chers |
| **Image** | Ubuntu 24.04 LTS |
| **Type** | ARM64 — **CAX41** (16 vCPU, 32 GB, 320 GB) |
| **Networking** | IPv4 + IPv6 |
| **SSH Key** | Ajouter ta cle publique SSH |
| **Firewall** | Creer un nouveau (voir section 5) |
| **Backups** | Activer (~20% du prix, ~5 EUR/mois) |
| **Name** | `stx-prod-01` |

3. Cliquer sur **"Create & Buy now"**
4. Noter l'adresse IP du serveur : `XXX.XXX.XXX.XXX`

### 4.2b Alternative : Serveur dedie (AX41-NVMe)

1. Aller sur https://www.hetzner.com/dedicated-rootserver/ax41-nvme
2. Commander le serveur
3. Choisir Ubuntu 24.04 comme OS
4. Le serveur sera provisionne en 1-24h (vs instantane pour le cloud)

### 4.3 Configurer la cle SSH (si pas deja fait)

```bash
# Sur ta machine locale — generer une cle SSH si necessaire
ssh-keygen -t ed25519 -C "nicolas@streamtex" -f ~/.ssh/hetzner_stx

# Afficher la cle publique pour la coller dans Hetzner
cat ~/.ssh/hetzner_stx.pub

# Configurer le fichier SSH config pour un acces facile
cat >> ~/.ssh/config << 'EOF'

Host stx-prod
    HostName XXX.XXX.XXX.XXX
    User root
    IdentityFile ~/.ssh/hetzner_stx
    ServerAliveInterval 60
    ServerAliveCountMax 3
EOF
```

### 4.4 Premier acces au serveur

```bash
# Connexion SSH
ssh stx-prod

# Verifier les specs du serveur
uname -m                    # aarch64 (ARM) ou x86_64 (dedie)
free -h                     # RAM disponible
df -h                       # Espace disque
nproc                       # Nombre de CPU
```

---

## 5. Phase 2 : Securiser le serveur

### 5.1 Configurer le Hetzner Cloud Firewall

> **IMPORTANT** : Le firewall Hetzner est au niveau reseau, Docker ne peut PAS le contourner.
> C'est la premiere ligne de defense.

1. Dans le projet StreamTeX sur la console Hetzner
2. Aller dans **Firewalls > Create Firewall**
3. Nom : `stx-firewall`
4. Ajouter les regles **Inbound** :

| Protocole | Port | Source | Description |
|-----------|------|--------|-------------|
| TCP | 22 | `TON_IP/32` | SSH (restreint a ton IP) |
| TCP | 80 | `0.0.0.0/0, ::/0` | HTTP (redirection HTTPS) |
| TCP | 443 | `0.0.0.0/0, ::/0` | HTTPS (trafic web) |
| TCP | 8000 | `TON_IP/32` | Coolify UI (restreint a ton IP) |

> Remplacer `TON_IP` par ton adresse IP publique (verifier avec `curl ifconfig.me`)

5. **Outbound** : laisser tout ouvert (par defaut)
6. Attacher le firewall au serveur `stx-prod-01`

### 5.2 Securiser l'OS

```bash
ssh stx-prod

# 1. Mise a jour systeme
apt update && apt upgrade -y

# 2. Creer un utilisateur non-root
adduser stxadmin
usermod -aG sudo stxadmin

# 3. Copier la cle SSH pour le nouvel utilisateur
mkdir -p /home/stxadmin/.ssh
cp /root/.ssh/authorized_keys /home/stxadmin/.ssh/
chown -R stxadmin:stxadmin /home/stxadmin/.ssh
chmod 700 /home/stxadmin/.ssh
chmod 600 /home/stxadmin/.ssh/authorized_keys

# 4. Desactiver le login root par SSH et le login par mot de passe
sed -i 's/^PermitRootLogin yes/PermitRootLogin no/' /etc/ssh/sshd_config
sed -i 's/^#PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config
sed -i 's/^PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config
systemctl restart sshd

# 5. Mises a jour de securite automatiques
apt install unattended-upgrades -y
dpkg-reconfigure -plow unattended-upgrades

# 6. Installer fail2ban
apt install fail2ban -y
systemctl enable fail2ban
systemctl start fail2ban
```

> **IMPORTANT** : Apres l'etape 4, ouvrir un nouveau terminal et verifier que
> `ssh stxadmin@XXX.XXX.XXX.XXX` fonctionne AVANT de fermer la session root.

### 5.3 Configurer UFW + ufw-docker

```bash
# En tant que root (necessaire pour Coolify install plus tard)
ssh stx-prod

# 1. Configurer UFW de base
ufw default deny incoming
ufw default allow outgoing
ufw allow 22/tcp comment 'SSH'
ufw allow 80/tcp comment 'HTTP'
ufw allow 443/tcp comment 'HTTPS'
ufw allow 8000/tcp comment 'Coolify UI'
ufw enable

# 2. Installer ufw-docker (corrige le probleme Docker/UFW)
wget -O /usr/local/bin/ufw-docker \
  https://github.com/chaifeng/ufw-docker/raw/master/ufw-docker
chmod +x /usr/local/bin/ufw-docker

# 3. Appliquer les regles ufw-docker
ufw-docker install
systemctl restart ufw

# Verification
ufw status verbose
```

> **Pourquoi ufw-docker ?** Docker manipule `iptables` directement et contourne UFW.
> Sans `ufw-docker`, tous les ports exposes par Docker sont accessibles depuis Internet,
> meme si UFW les bloque. Le Hetzner Cloud Firewall est la premiere protection, mais
> ufw-docker ajoute une defense en profondeur.

### 5.4 Mettre a jour le fichier SSH config local

```bash
# Sur ta machine locale — mettre a jour pour utiliser stxadmin
cat >> ~/.ssh/config << 'EOF'

# Remplacer la config precedente (root) par :
Host stx-prod
    HostName XXX.XXX.XXX.XXX
    User stxadmin
    IdentityFile ~/.ssh/hetzner_stx
    ServerAliveInterval 60
    ServerAliveCountMax 3
EOF
```

---

## 6. Phase 3 : Installer Coolify

### 6.1 Installation (en root)

```bash
# IMPORTANT : Coolify necessite un acces root pour l'installation
ssh root@XXX.XXX.XXX.XXX  # ou via sudo depuis stxadmin

# Installation en une commande
curl -fsSL https://cdn.coollabs.io/coolify/install.sh | sudo bash
```

L'installateur effectue automatiquement :
- Installation de Docker Engine (si pas present)
- Creation des repertoires sous `/data/coolify`
- Configuration des cles SSH internes
- Demarrage de Coolify + Traefik + PostgreSQL
- Duree : ~3 minutes

### 6.2 Configuration initiale

1. Ouvrir dans le navigateur : `http://XXX.XXX.XXX.XXX:8000`
2. **IMMEDIATEMENT** creer le compte admin (la page d'inscription est publique jusqu'a la creation)
   - Email : ton email
   - Mot de passe : un mot de passe fort
3. Completer l'assistant de configuration :
   - Nom de l'instance : `StreamTeX Production`
   - Serveur par defaut : `localhost` (deja configure)

### 6.3 Verifier que tout fonctionne

Dans le dashboard Coolify :
1. Aller dans **Servers**
2. Le serveur `localhost` devrait etre `Online` avec un check vert
3. Verifier les ressources (CPU, RAM, Disque)

```bash
# Sur le serveur — verifier que les containers Coolify tournent
docker ps

# Attendu : coolify, coolify-proxy (Traefik), coolify-db (PostgreSQL),
#            coolify-redis, coolify-realtime
```

### 6.4 Configurer le source GitHub

Pour deployer automatiquement depuis les repos GitHub :

1. Dans Coolify, aller dans **Sources > Add**
2. Choisir **GitHub App** (recommande) ou **Public Repository**

#### Option A : GitHub App (repos prives + webhooks automatiques)

1. Cliquer sur **"Create GitHub App"**
2. Suivre les instructions (redirige vers GitHub)
3. Installer l'app sur le compte `nicolasguelfi`
4. Selectionner les repos : `stx-ai4se`, `stx-modelsward`, `stx-aiai18h`, `stx-html-example`

#### Option B : Repository public (plus simple, pas de webhooks auto)

- Entrer directement l'URL du repo lors du deploiement
- Le re-deploiement se fait manuellement ou via l'API Coolify

> **Recommandation** : GitHub App pour les deploiements automatiques sur `git push`.

---

## 7. Phase 4 : Configurer le domaine et le DNS

### 7.1 Acheter ou configurer un domaine

Si tu n'as pas encore de domaine pour StreamTeX, options :
- **Namecheap** : ~10-15 EUR/an pour un `.com`
- **Gandi** : ~15-20 EUR/an
- **Cloudflare Registrar** : prix coutant (~10 EUR/an)

Exemples de domaines possibles :
- `streamtex.app`
- `streamtex.dev`
- `stx-projects.com`

### 7.2 Configurer les enregistrements DNS

Chez ton registrar DNS, ajouter :

| Type | Nom | Valeur | TTL |
|------|-----|--------|-----|
| A | `@` | `XXX.XXX.XXX.XXX` | 300 |
| A | `*` | `XXX.XXX.XXX.XXX` | 300 |
| AAAA | `@` | `XXXX:XXXX::XXXX` (IPv6 du serveur) | 300 |
| AAAA | `*` | `XXXX:XXXX::XXXX` | 300 |

> L'enregistrement wildcard `*` permet de router automatiquement tous les sous-domaines
> (`stx-ai4se.domaine.com`, `stx-modelsward.domaine.com`, etc.) vers le serveur.
> Traefik (via Coolify) s'occupe ensuite du routing vers le bon container.

### 7.3 Configurer le domaine dans Coolify

1. Aller dans **Settings > Configuration**
2. Remplir le champ **"Instance's domain"** : `https://coolify.ton-domaine.com`
3. Sauvegarder

Le dashboard Coolify sera desormais accessible via `https://coolify.ton-domaine.com`
au lieu de `http://XXX.XXX.XXX.XXX:8000`.

### 7.4 Verifier la propagation DNS

```bash
# Depuis ta machine locale
dig +short ton-domaine.com
# → Devrait retourner l'IP de ton serveur

dig +short stx-ai4se.ton-domaine.com
# → Meme IP (grace au wildcard)

# Ou utiliser un service web
# https://dnschecker.org/
```

### 7.5 (Optionnel) Cloudflare comme proxy DNS

Si tu veux ajouter une couche de protection DDoS et un CDN :

1. Creer un compte Cloudflare (gratuit)
2. Ajouter ton domaine
3. Pointer les nameservers vers Cloudflare
4. Activer le proxy orange pour les enregistrements A/AAAA
5. Configurer le mode SSL sur **"Full (Strict)"**
6. Dans Coolify, les certificats Let's Encrypt seront toujours generes

> **Avantage** : protection DDoS gratuite, CDN pour les assets statiques, analytics
> **Inconvenient** : une couche de plus a gerer

---

## 8. Phase 5 : Deployer le premier projet StreamTeX

### 8.1 Preparer le Dockerfile du projet

Chaque projet StreamTeX a deja un Dockerfile. Verifier qu'il contient les bonnes options
pour fonctionner derriere un reverse proxy.

**Dockerfile type pour un projet StreamTeX** (ex: `stx-ai4se/Dockerfile`) :

```dockerfile
FROM python:3.13-slim

WORKDIR /app

# Installer les dependances systeme
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copier les fichiers de dependances
COPY pyproject.toml uv.lock* ./

# Installer uv et les dependances
RUN pip install --no-cache-dir uv \
    && uv sync --no-dev --frozen 2>/dev/null || uv pip install --system -r <(uv pip compile pyproject.toml)

# Copier le code du projet
COPY . .

# Exposer le port Streamlit
EXPOSE 8501

# Configuration Streamlit pour le reverse proxy
CMD ["python", "-m", "streamlit", "run", "book.py", \
     "--server.port=8501", \
     "--server.address=0.0.0.0", \
     "--server.headless=true", \
     "--server.enableCORS=false", \
     "--server.enableXsrfProtection=false", \
     "--browser.gatherUsageStats=false"]
```

### 8.2 Verifier la configuration Streamlit

Chaque projet doit avoir dans `.streamlit/config.toml` :

```toml
[server]
enableStaticServing = true
headless = true
address = "0.0.0.0"
port = 8501
enableCORS = false
enableXsrfProtection = false

[browser]
gatherUsageStats = false

[theme]
base = "dark"
```

> **Pourquoi `enableCORS=false` et `enableXsrfProtection=false` ?**
> Derriere un reverse proxy (Traefik), les requetes arrivent depuis un domaine different.
> Sans ces options, Streamlit bloque les connexions WebSocket et affiche "Please wait...".

### 8.3 Deployer sur Coolify

#### Etape 1 : Creer le projet dans Coolify

1. Dashboard Coolify > **Projects > Add**
2. Nom : `StreamTeX`
3. Description : `Projets StreamTeX de formation`

#### Etape 2 : Ajouter le premier service (stx-html-example)

> On commence par `stx-html-example` car c'est le plus simple, ideal pour tester.

1. Dans le projet StreamTeX, cliquer **"+ New"** > **"Public Repository"**
   (ou GitHub App si configure)
2. URL du repository : `https://github.com/nicolasguelfi/stx-html-example`
3. Branche : `main`
4. **Build Pack** : changer de "Nixpacks" a **"Dockerfile"**
5. Port : **8501**

#### Etape 3 : Configurer le service

Dans les settings du service :

| Parametre | Valeur |
|-----------|--------|
| **Name** | `stx-html-example` |
| **Domain** | `https://stx-html-example.ton-domaine.com` |
| **Port** | 8501 |
| **Build Pack** | Dockerfile |
| **Dockerfile Path** | `./Dockerfile` |
| **Auto Deploy** | Enabled |

Variables d'environnement (onglet "Environment Variables") :

```
STX_PASSWORD=ton_mot_de_passe_ici
```

#### Etape 4 : Configurer les limites de ressources

Dans **General > Custom Docker Options** :

```
--memory=1g --memory-reservation=512m --cpus=1.0
```

Cela limite le container a 1 GB de RAM et 1 vCPU maximum.

#### Etape 5 : Deployer

1. Cliquer sur **"Deploy"**
2. Suivre les logs de build en temps reel
3. Attendre le message "Deployment successful"

#### Etape 6 : Verifier

```bash
# Depuis ta machine locale
curl -I https://stx-html-example.ton-domaine.com
# → Devrait retourner HTTP/2 200

# Ouvrir dans le navigateur
open https://stx-html-example.ton-domaine.com
```

### 8.4 Verifier le WebSocket

Le point critique avec Streamlit derriere un reverse proxy est le WebSocket.
Si la page affiche "Please wait..." indefiniment, verifier :

1. **Dans les logs Coolify** : chercher des erreurs de connexion
2. **Dans la console du navigateur** (F12) : chercher des erreurs WebSocket
3. **Verifier les headers** :

```bash
# Tester la connexion WebSocket
curl -i -N \
  -H "Connection: Upgrade" \
  -H "Upgrade: websocket" \
  -H "Host: stx-html-example.ton-domaine.com" \
  -H "Sec-WebSocket-Version: 13" \
  -H "Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==" \
  https://stx-html-example.ton-domaine.com/_stcore/stream
```

> Traefik gere nativement les WebSockets. Normalement, aucune configuration
> supplementaire n'est necessaire au-dela de `enableCORS=false`.

---

## 9. Phase 6 : Deployer tous les projets

### 9.1 Repeter pour chaque projet

Une fois le premier projet valide, deployer les autres de la meme facon :

| Projet | Repo GitHub | Domaine |
|--------|-------------|---------|
| stx-ai4se | `nicolasguelfi/stx-ai4se` | `stx-ai4se.ton-domaine.com` |
| stx-modelsward | `nicolasguelfi/stx-modelsward` | `stx-modelsward.ton-domaine.com` |
| stx-aiai18h | `nicolasguelfi/stx-aiai18h` | `stx-aiai18h.ton-domaine.com` |
| stx-html-example | `nicolasguelfi/stx-html-example` | `stx-html-example.ton-domaine.com` |
| streamtex-docs | `nicolasguelfi/streamtex-docs` | `docs.ton-domaine.com` |

### 9.2 Configuration par projet

Chaque service dans Coolify :
- **Build Pack** : Dockerfile
- **Port** : 8501
- **Auto Deploy** : Enabled
- **Limites** : `--memory=1g --cpus=1.0` (ajuster si necessaire)
- **Variables d'env** : `STX_PASSWORD` specifique a chaque projet

### 9.3 Verifier l'etat de tous les services

```bash
# Via l'API Coolify (si activee)
curl -s -H "Authorization: Bearer COOLIFY_TOKEN" \
  https://coolify.ton-domaine.com/api/v1/applications | jq '.[] | {name, status}'
```

Ou dans le dashboard Coolify : **Projects > StreamTeX** — tous les services
doivent afficher un statut vert "Running".

---

## 10. Phase 7 : Adapter le CLI `stx deploy`

### 10.1 Objectif

Ajouter une commande `stx deploy coolify` qui genere la configuration et deploie
directement via l'API Coolify, similaire a `stx deploy render`.

### 10.2 Specification de la commande

```bash
stx deploy coolify [PATH]           # Deployer sur Coolify
  --name NAME                       # Nom du service (defaut: nom du repertoire)
  --domain DOMAIN                   # Domaine (defaut: <name>.domaine-par-defaut)
  --branch BRANCH                   # Branche git (defaut: main)
  --memory MEMORY                   # Limite RAM (defaut: 1g)
  --cpus CPUS                       # Limite CPU (defaut: 1.0)
  --env KEY=VALUE                   # Variables d'environnement (repetable)
  --server SERVER                   # URL du serveur Coolify (defaut: depuis stx.toml)
  --token TOKEN                     # Token API Coolify (defaut: depuis env COOLIFY_TOKEN)
  --dry-run                         # Afficher la configuration sans deployer
```

### 10.3 Configuration dans stx.toml

```toml
[deploy]
# Render (existant)
# render_owner = "nicolasguelfi"
# render_region = "oregon"

# Coolify (nouveau)
coolify_url = "https://coolify.ton-domaine.com"
coolify_project = "StreamTeX"
coolify_default_domain = "ton-domaine.com"
coolify_default_memory = "1g"
coolify_default_cpus = "1.0"
```

### 10.4 API Coolify a utiliser

```bash
# Lister les applications
GET /api/v1/applications

# Creer une application
POST /api/v1/applications
{
  "name": "stx-ai4se",
  "project_uuid": "...",
  "server_uuid": "...",
  "type": "dockerfile",
  "git_repository": "https://github.com/nicolasguelfi/stx-ai4se",
  "git_branch": "main",
  "ports_exposes": "8501",
  "fqdn": "https://stx-ai4se.ton-domaine.com"
}

# Deployer une application
POST /api/v1/applications/{uuid}/deploy

# Voir les logs
GET /api/v1/applications/{uuid}/logs
```

> **Note** : L'API Coolify doit etre activee dans Settings > Configuration > Advanced.
> Generer un token API dans Settings > API Tokens.

### 10.5 Fichier a creer : `streamtex/cli/coolify_cmd.py`

Structure prevue :

```python
"""Coolify deployment commands."""

import click
import requests

@click.command("coolify")
@click.argument("path", default=".")
@click.option("--name", default=None)
@click.option("--domain", default=None)
@click.option("--branch", default="main")
@click.option("--memory", default="1g")
@click.option("--cpus", default="1.0")
@click.option("--env", multiple=True)
@click.option("--dry-run", is_flag=True)
def coolify(path, name, domain, branch, memory, cpus, env, dry_run):
    """Deploy a StreamTeX project to Coolify."""
    ...
```

> **A implementer plus tard** — ce n'est pas bloquant pour le deploiement initial
> qui se fait via le dashboard Coolify.

---

## 11. Monitoring et maintenance courante

### 11.1 Dashboard Coolify

Coolify fournit un monitoring integre :
- CPU, RAM, disque par container
- Logs en temps reel
- Alertes sur les redemarrages

### 11.2 Commandes utiles sur le serveur

```bash
# Voir l'utilisation des ressources par container
docker stats --no-stream

# Voir les logs d'un container specifique
docker logs <container_id> --tail 100 -f

# Voir l'espace disque
df -h

# Nettoyer les images Docker inutilisees (a faire periodiquement)
docker system prune -a --volumes
# ATTENTION : ne pas executer pendant un deploiement

# Voir les containers en cours
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

# Verifier Traefik
docker logs coolify-proxy --tail 50
```

### 11.3 Taches de maintenance periodiques

| Frequence | Tache | Commande |
|-----------|-------|----------|
| Quotidien | Verifier les logs d'erreur | Dashboard Coolify |
| Hebdomadaire | Verifier l'espace disque | `df -h` |
| Hebdomadaire | Nettoyer les images Docker | `docker system prune -f` |
| Mensuel | Mise a jour OS | `apt update && apt upgrade -y` |
| Mensuel | Mise a jour Coolify | Dashboard > Settings > Update |
| Trimestriel | Verifier les certificats SSL | Dashboard > services > domaines |
| Trimestriel | Revoir les limites de ressources | `docker stats` |

### 11.4 Backups

```bash
# Les donnees critiques de Coolify sont dans /data/coolify/
# Hetzner Backups (automatique si active) sauvegarde tout le disque

# Backup manuel des configs Coolify
tar -czf /root/coolify-backup-$(date +%Y%m%d).tar.gz /data/coolify/

# Copier sur ta machine locale
scp stx-prod:/root/coolify-backup-*.tar.gz ~/backups/
```

### 11.5 Mise a jour de Coolify

```bash
# Depuis le dashboard : Settings > Update
# Ou en SSH :
cd /data/coolify
docker compose pull
docker compose up -d
```

---

## 12. Estimation des couts

### 12.1 Budget mensuel (option CAX41)

| Poste | Cout/mois |
|-------|-----------|
| Hetzner CAX41 (32 GB ARM) | ~25 EUR |
| Backups Hetzner | ~5 EUR |
| Domaine (annualise) | ~1 EUR |
| Coolify | 0 EUR (self-hosted, open source) |
| Let's Encrypt SSL | 0 EUR |
| **Total** | **~31 EUR/mois** |

### 12.2 Budget mensuel (option AX41-NVMe)

| Poste | Cout/mois |
|-------|-----------|
| Hetzner AX41-NVMe (64 GB dedie) | ~40 EUR |
| Backups (snapshots manuels) | ~3 EUR |
| Domaine (annualise) | ~1 EUR |
| **Total** | **~44 EUR/mois** |

### 12.3 Comparaison avec Render

| Scenario | Render | Hetzner + Coolify |
|----------|--------|-------------------|
| 1 projet (free) | 0 EUR | ~31 EUR |
| 5 projets (starter) | ~35 EUR | ~31 EUR |
| 10 projets (starter) | ~70 EUR | ~31 EUR |
| 20 projets (starter) | ~140 EUR | ~31-44 EUR |
| Projets illimites | Non viable | ~31-44 EUR |

> **Seuil de rentabilite** : a partir de **5 projets**, Hetzner + Coolify est
> plus economique que Render. Et le gap se creuse exponentiellement.

---

## 13. Capacite et limites de Streamlit

### 13.1 Consommation memoire par utilisateur

Streamlit utilise des connexions **WebSocket persistantes**. Chaque utilisateur actif
= 1 session Python en memoire.

| Complexite du projet | RAM par session | Note |
|----------------------|-----------------|------|
| Simple (quelques blocks) | ~30-80 MB | stx-html-example |
| Moyen (presentation) | ~80-150 MB | stx-ai4se, stx-modelsward |
| Complexe (donnees, graphiques) | ~150-300 MB | Projets avec pandas, matplotlib |

### 13.2 Estimation du nombre d'utilisateurs simultanes

Avec 1 GB de RAM alloue par container :

| Type de projet | Utilisateurs simultanes | Note |
|----------------|------------------------|------|
| Simple | ~15-30 | Suffisant pour un cours en amphi |
| Moyen | ~8-12 | Suffisant pour une presentation |
| Complexe | ~3-6 | Preferer le cache ou l'export statique |

Avec 2 GB de RAM alloue par container :

| Type de projet | Utilisateurs simultanes |
|----------------|------------------------|
| Simple | ~30-60 |
| Moyen | ~15-25 |
| Complexe | ~6-12 |

### 13.3 Strategies pour supporter "des milliers d'utilisateurs"

Pour depasser les limites inherentes de Streamlit :

#### Strategie 1 : Augmenter la RAM par container

Avec le AX41 (64 GB), on peut allouer 4-8 GB par projet critique :
- 4 GB → ~60-120 utilisateurs simultanes (projet moyen)
- 8 GB → ~120-240 utilisateurs simultanes

#### Strategie 2 : Multi-instance avec sticky sessions

```yaml
# Configuration Traefik pour sticky sessions
# (a ajouter dans la configuration Coolify avancee)
services:
  streamlit:
    deploy:
      replicas: 3      # 3 instances du meme container
    labels:
      - "traefik.http.services.streamlit.loadbalancer.sticky.cookie=true"
      - "traefik.http.services.streamlit.loadbalancer.sticky.cookie.name=stx_session"
```

> **Attention** : le multi-instance Streamlit necessite que les sessions soient
> independantes (pas de `st.session_state` partage entre instances).
> Les projets StreamTeX utilisent `st.session_state` pour la pagination,
> donc les sticky sessions sont **obligatoires**.

#### Strategie 3 : Export HTML statique (pour le contenu en lecture seule)

Pour les projets de type "presentation" qui n'ont pas d'interactivite complexe,
generer un export HTML statique qui ne necessite pas de serveur Streamlit :
- 0 RAM sur le serveur
- CDN possible (Cloudflare, Hetzner Object Storage)
- Milliers d'utilisateurs sans probleme

> Voir `stx deploy huggingface --skip-push` pour generer les fichiers statiques,
> ou la feature future `stx export html`.

#### Strategie 4 : Scaling horizontal (multi-serveur)

Si un seul serveur ne suffit pas :
1. Commander un 2eme serveur Hetzner
2. Configurer comme "Remote Server" dans Coolify
3. Repartir les projets entre les serveurs
4. Utiliser un load balancer Hetzner (~5 EUR/mois) devant les deux serveurs

---

## 14. Troubleshooting

### 14.1 "Please wait..." — Streamlit bloque au chargement

**Cause** : les WebSockets ne passent pas le reverse proxy.

**Solutions** :
1. Verifier `enableCORS=false` dans `.streamlit/config.toml`
2. Verifier `enableXsrfProtection=false`
3. Verifier que le port 8501 est bien configure dans Coolify
4. Verifier les logs Traefik : `docker logs coolify-proxy --tail 100`

### 14.2 Certificat SSL invalide

**Cause** : le DNS n'est pas encore propage ou Let's Encrypt a echoue.

**Solutions** :
1. Verifier la propagation DNS : `dig +short ton-domaine.com`
2. Verifier les logs Traefik pour les erreurs ACME
3. Attendre 5-10 minutes et redemarrer le service dans Coolify
4. Si Cloudflare : verifier que le mode SSL est "Full (Strict)"

### 14.3 Container qui redmarre en boucle (OOM Kill)

**Cause** : le container depasse sa limite memoire.

**Solutions** :
1. Verifier les logs : `docker logs <container> --tail 50`
2. Augmenter la limite : `--memory=2g` dans Custom Docker Options
3. Optimiser le code Streamlit (reduire les imports, le cache)
4. Verifier avec `docker stats` la consommation reelle

### 14.4 Build Docker echoue

**Cause** : dependances incompatibles ou Dockerfile incorrect.

**Solutions** :
1. Tester le build en local : `docker build -t test .`
2. Verifier les logs de build dans Coolify
3. S'assurer que `pyproject.toml` et `uv.lock` sont commites

### 14.5 Auto-deploy ne se declenche pas

**Cause** : webhook GitHub mal configure.

**Solutions** :
1. Verifier dans GitHub > Settings > Webhooks que le webhook Coolify existe
2. Verifier le "Recent Deliveries" du webhook pour les erreurs
3. Verifier que la branche est correcte (main vs master)
4. Deployer manuellement et verifier les logs

### 14.6 Performances degradees

**Cause** : trop de containers, pas assez de ressources.

**Solutions** :
1. `docker stats` pour identifier le container gourmand
2. Reduire le nombre de replicas ou de projets
3. Arreter les projets non utilises dans Coolify (bouton "Stop")
4. Upgrader le serveur (CAX41 → AX41 ou AX42)

---

## 15. Checklist de validation

### Phase 1 : Serveur provisionne

- [ ] Projet "StreamTeX" cree dans la console Hetzner
- [ ] Serveur commande et accessible en SSH
- [ ] IP notee dans le fichier `~/.ssh/config`

### Phase 2 : Securite

- [ ] Hetzner Cloud Firewall configure (ports 22, 80, 443, 8000)
- [ ] Utilisateur `stxadmin` cree
- [ ] Login root SSH desactive
- [ ] Login par mot de passe desactive
- [ ] UFW active
- [ ] ufw-docker installe
- [ ] fail2ban installe
- [ ] Mises a jour automatiques activees

### Phase 3 : Coolify installe

- [ ] Coolify accessible sur `http://IP:8000`
- [ ] Compte admin cree
- [ ] Serveur localhost "Online" dans le dashboard
- [ ] Source GitHub configuree (App ou public)

### Phase 4 : Domaine configure

- [ ] Domaine achete/configure
- [ ] Enregistrement A + wildcard `*` vers l'IP du serveur
- [ ] DNS propage (verifiable avec `dig`)
- [ ] Dashboard Coolify accessible via `https://coolify.domaine.com`
- [ ] Certificat SSL valide (Let's Encrypt)

### Phase 5 : Premier projet deploye

- [ ] `stx-html-example` deploye et accessible
- [ ] HTTPS fonctionne
- [ ] WebSocket fonctionne (pas de "Please wait...")
- [ ] Variable `STX_PASSWORD` configuree
- [ ] Limites de ressources definies

### Phase 6 : Tous les projets deployes

- [ ] `stx-ai4se` deploye et accessible
- [ ] `stx-modelsward` deploye et accessible
- [ ] `stx-aiai18h` deploye et accessible
- [ ] `stx-html-example` deploye et accessible
- [ ] `streamtex-docs` deploye et accessible (optionnel)
- [ ] Auto-deploy fonctionne sur `git push`

### Phase 7 : CLI adapte

- [ ] `stx deploy coolify` implemente (optionnel, peut etre fait plus tard)
- [ ] `stx.toml` mis a jour avec les parametres Coolify

### Maintenance

- [ ] Backups Hetzner actives
- [ ] Monitoring Coolify verifie
- [ ] Procedure de mise a jour documentee
- [ ] Contacts d'urgence notes (support Hetzner, communaute Coolify)

---

## Annexe A : Commandes de reference rapide

```bash
# === Serveur ===
ssh stx-prod                              # Connexion au serveur
docker stats --no-stream                  # Ressources des containers
docker system prune -f                    # Nettoyage Docker
df -h                                     # Espace disque

# === Coolify ===
# Dashboard : https://coolify.ton-domaine.com
# API : https://coolify.ton-domaine.com/api/v1/

# === Deploiement manuel ===
# Via le dashboard : Projects > StreamTeX > service > Deploy
# Via l'API :
curl -X POST \
  -H "Authorization: Bearer COOLIFY_TOKEN" \
  https://coolify.ton-domaine.com/api/v1/applications/{uuid}/deploy

# === Logs ===
# Via le dashboard : service > Logs
# Via SSH :
docker logs <container_id> --tail 100 -f

# === DNS ===
dig +short stx-ai4se.ton-domaine.com     # Verifier la resolution
curl -I https://stx-ai4se.ton-domaine.com # Verifier HTTPS

# === Backups ===
tar -czf /root/coolify-backup-$(date +%Y%m%d).tar.gz /data/coolify/
scp stx-prod:/root/coolify-backup-*.tar.gz ~/backups/
```

## Annexe B : Arborescence des fichiers modifies

```
streamtex-dev/
├── streamtex/
│   ├── streamtex/cli/
│   │   ├── deploy_cmd.py           # Ajouter sous-commande "coolify"
│   │   └── coolify_cmd.py          # NOUVEAU — commandes Coolify
│   └── stx.toml template           # Ajouter section [deploy.coolify]
│
├── stx-ai4se/
│   ├── Dockerfile                  # Verifier les options Streamlit
│   └── .streamlit/config.toml      # enableCORS=false, enableXsrfProtection=false
│
├── stx-modelsward/
│   ├── Dockerfile
│   └── .streamlit/config.toml
│
├── stx-aiai18h/
│   ├── Dockerfile
│   └── .streamlit/config.toml
│
└── stx-html-example/
    ├── Dockerfile
    └── .streamlit/config.toml
```
