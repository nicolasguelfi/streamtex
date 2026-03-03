# Plan de Maintenance : Systeme de Donations et Financement de StreamTeX

> **Date** : 2026-03-03
> **Auteur** : Nicolas Guelfi + Claude
> **Version** : 1.0
> **Statut** : A FAIRE

---

## Table des matieres

1. [Contexte et objectif](#1-contexte-et-objectif)
2. [Analyse des plateformes](#2-analyse-des-plateformes)
3. [Tableau comparatif](#3-tableau-comparatif)
4. [Strategie recommandee pour StreamTeX](#4-strategie-recommandee-pour-streamtex)
5. [Specificites du public academique](#5-specificites-du-public-academique)
6. [Aspects fiscaux (France/UE)](#6-aspects-fiscaux-franceue)
7. [Monetisation par dual licensing ?](#7-monetisation-par-dual-licensing-)
8. [Plan d'action](#8-plan-daction)
9. [Integration technique](#9-integration-technique)
10. [Checklist de validation](#10-checklist-de-validation)

---

## 1. Contexte et objectif

StreamTeX est une librairie Python open-source construite sur Streamlit, destinee aux
enseignants, chercheurs et developpeurs dans l'enseignement superieur. L'objectif est
de mettre en place un systeme de donations/financement pour soutenir la maintenance
et le developpement continu de la librairie.

### Profil du projet

| Critere | StreamTeX |
|---------|-----------|
| **Type** | Librairie Python open-source (PyPI) |
| **Licence actuelle** | MIT |
| **Public cible** | Enseignants, chercheurs, developpeurs academiques |
| **Taille** | Projet individuel (1 mainteneur principal) |
| **Maturite** | En developpement actif, pre-1.0 |
| **Distribution** | PyPI + GitHub |
| **Hebergement** | GitHub (`nicolasguelfi/streamtex`) |

---

## 2. Analyse des plateformes

### 2.1 GitHub Sponsors (RECOMMANDE en priorite)

**Principe** : Les utilisateurs sponsorisent directement le mainteneur via GitHub.
Le bouton "Sponsor" apparait sur la page du repo.

| Critere | Detail |
|---------|--------|
| **Frais plateforme** | 0% (comptes personnels) ; jusqu'a 6% (comptes organisations) |
| **Frais paiement** | ~2.9% + 0.30$ (Stripe) ; +1.5% cross-border |
| **Total effectif** | **~3%** |
| **Dons ponctuels** | Oui |
| **Dons recurrents** | Oui (tiers mensuels definis par le mainteneur) |
| **Integration** | Native GitHub + `.github/FUNDING.yml` + PyPI via `[project.urls]` |
| **Payout** | Le 22 de chaque mois via Stripe Connect |
| **Pays supportes** | France : OUI |

**Pourquoi c'est le meilleur choix pour StreamTeX** :
- 0% de frais plateforme (seuls les frais Stripe s'appliquent)
- Integration native avec le repo GitHub (bouton "Sponsor" visible)
- Les utilisateurs de StreamTeX sont deja sur GitHub
- Support PyPI via les URLs `Funding` dans `pyproject.toml`
- Stripe Connect gere les paiements en EUR vers un compte francais

### 2.2 Liberapay (bon complement)

**Principe** : Plateforme de dons recurrents, elle-meme financee par des dons.
Geree par une association basee en **France** (Querrien).

| Critere | Detail |
|---------|--------|
| **Frais plateforme** | 0% (aucune commission) |
| **Frais paiement** | ~3.2% (Stripe) ou ~5% (PayPal) |
| **Total effectif** | **~3.2%** |
| **Dons ponctuels** | Non (recurrents uniquement) |
| **Dons recurrents** | Oui (hebdomadaire, mensuel, annuel) |
| **Integration** | `.github/FUNDING.yml` (`liberapay: USERNAME`) |

**Avantages** : 0% de frais, basee en France, forte philosophie open-source.
**Inconvenient** : Pas de dons ponctuels, base d'utilisateurs plus restreinte.

### 2.3 Ko-fi (tips ponctuels)

**Principe** : Plateforme de "tips" ("buy me a coffee") avec page personnalisable.

| Critere | Detail |
|---------|--------|
| **Frais plateforme** | 0% sur les tips |
| **Frais paiement** | ~3% (Stripe/PayPal) |
| **Total effectif** | **~3%** |
| **Dons ponctuels** | Oui |
| **Dons recurrents** | Oui (abonnements, 5% frais ou 0% avec Gold a 6$/mois) |
| **Integration** | `.github/FUNDING.yml` (`ko_fi: USERNAME`) |

**Avantage** : 0% sur les tips ponctuels, simple.
**Inconvenient** : Branding "createurs/artistes", moins courant dans l'OSS.

### 2.4 Polar.sh (si vente de produits)

**Principe** : Plateforme de monetisation pour developpeurs. Vente de produits
numeriques, abonnements, cles de licence. Agit comme **Merchant of Record**
(gere la TVA et la conformite fiscale globale).

| Critere | Detail |
|---------|--------|
| **Frais plateforme** | 4% + 0.40$ par transaction (inclut les frais Stripe) |
| **Total effectif** | **~4.4%** |
| **Dons ponctuels** | Oui |
| **Dons recurrents** | Oui (abonnements) |
| **Integration** | `.github/FUNDING.yml` (`polar: USERNAME`) |

**Avantage** : Gere toute la TVA/conformite UE automatiquement.
**Inconvenient** : Plus pertinent si vous vendez quelque chose (templates premium,
formations, cles de licence) plutot que pour de simples dons.

### 2.5 Thanks.dev (revenu passif)

**Principe** : Les entreprises connectent leur compte GitHub, Thanks.dev scanne
l'arbre de dependances et distribue automatiquement des micro-dons aux mainteneurs.

| Critere | Detail |
|---------|--------|
| **Frais plateforme** | ~5% (volontaire) + frais Stripe |
| **Total effectif** | **~5-8%** |
| **Dons ponctuels** | Non |
| **Dons recurrents** | Oui (distribution mensuelle automatique) |
| **Integration** | `.github/FUNDING.yml` (`thanks_dev: u/gh/USERNAME`) |

**Avantage** : Totalement passif, il suffit de s'inscrire.
**Inconvenient** : Revenus probablement faibles pour un package de niche.

### 2.6 Open Collective Europe (si le projet grandit)

**Principe** : Hebergement fiscal par une entite legale europeenne. Gere la
comptabilite, les taxes, les factures et la conformite.

| Critere | Detail |
|---------|--------|
| **Frais plateforme** | 8-10% (hebergeur fiscal) + ~3% (Stripe) |
| **Total effectif** | **~11-13%** |
| **Dons ponctuels** | Oui |
| **Dons recurrents** | Oui |
| **Integration** | `.github/FUNDING.yml` (`open_collective: USERNAME`) |

**Avantage** : Gestion fiscale complete, eligible aux subventions UE,
deductibilite fiscale pour les donateurs dans certains pays.
**Inconvenient** : Frais eleves, plus adapte a un projet avec plusieurs contributeurs.

### 2.7 Plateformes NON recommandees pour StreamTeX

| Plateforme | Raison |
|------------|--------|
| **Patreon** | Frais les plus eleves (10-13%), branding createurs, recurrent uniquement |
| **Buy Me a Coffee** | 5% frais plateforme + 3% paiement = ~8%, branding grand public |
| **Tidelift** | Modele entreprise, StreamTeX trop niche pour etre dans les arbres de dependances |

---

## 3. Tableau comparatif

| Plateforme | Frais total | Ponctuel | Recurrent | Integration GitHub | Recommandation |
|------------|------------|----------|-----------|-------------------|----------------|
| **GitHub Sponsors** | ~3% | Oui | Oui | Native | **Priorite 1** |
| **Liberapay** | ~3.2% | Non | Oui | FUNDING.yml | **Priorite 2** |
| **Ko-fi** | ~3% | Oui | Oui | FUNDING.yml | Optionnel |
| **Thanks.dev** | ~5-8% | Non | Auto | FUNDING.yml | Optionnel (passif) |
| **Polar.sh** | ~4.4% | Oui | Oui | FUNDING.yml | Si vente de produits |
| **Open Collective** | ~11-13% | Oui | Oui | FUNDING.yml | Si le projet grandit |

---

## 4. Strategie recommandee pour StreamTeX

### Tier 1 : A mettre en place immediatement (effort faible)

1. **GitHub Sponsors** — Canal principal de donations
2. **`.github/FUNDING.yml`** — Bouton "Sponsor" sur le repo
3. **`pyproject.toml` URL Funding** — Lien visible sur PyPI
4. **Thanks.dev** — S'inscrire (passif, couts zero)
5. **Section "Support" dans le README** — Visibilite pour les utilisateurs

### Tier 2 : A considerer (effort moyen)

6. **Liberapay** — Canal secondaire pour les dons recurrents (0% frais, base en France)
7. **Ko-fi** — Pour les tips ponctuels informels
8. **Polar.sh** — Si vous souhaitez vendre du contenu premium (templates de presentations
   pretes a l'emploi, formations video, support prioritaire)

### Tier 3 : A long terme (si le projet grandit)

9. **Open Collective Europe** — Hebergement fiscal pour gerer des subventions
10. **NumFOCUS** — Candidature si StreamTeX devient un outil scientifique reconnu
11. **Subventions** — NSF POSE, CZI EOSS, EU Horizon (effort eleve, montants importants)

---

## 5. Specificites du public academique

### Realite du financement en milieu academique

| Constat | Implication pour StreamTeX |
|---------|---------------------------|
| Les chercheurs ne paient **pas de leur poche** pour les outils logiciels | Les dons individuels seront faibles |
| Les universites achetent des **licences institutionnelles** | Possible canal si StreamTeX grandit |
| Les **grants de recherche** peuvent inclure des couts logiciels | Se positionner comme outil de recherche |
| Les **OSPO universitaires** emergent (12+ aux US, finances par Sloan Foundation) | Canal potentiel futur |
| Les entreprises ont des **credits d'impot** pour les dons OSS (60% en France) | Cibler les entreprises partenaires |

### Etude de cas : scikit-learn

scikit-learn, l'une des librairies Python les plus utilisees en academie :
- Financement principal : **institutionnel** (Inria, gouvernement francais)
- Sponsors corporate : :probabl., Chanel, BNP Paribas, NVIDIA
- Micro-dons communautaires via NumFOCUS : utiles pour "marketing, evenements, stages"
  mais pas pour la maintenance core

### Canaux de revenus realistes pour StreamTeX

| Canal | Probabilite | Montant potentiel | Effort |
|-------|------------|-------------------|--------|
| GitHub Sponsors (individus) | Faible-Moyen | 10-100 EUR/mois | Faible |
| Sponsors institutionnels | Moyen | 500-5000 EUR/an | Moyen |
| Consulting/formations | Moyen-Eleve | Variable | Moyen |
| Contenu educatif premium (Polar.sh) | Moyen | Variable | Moyen |
| Subventions de recherche | Faible (niche) | 50K-500K EUR | Eleve |
| Subventions UE Horizon | Faible-Moyen | Variable | Tres eleve |

### Bonnes pratiques

1. **Positionner StreamTeX comme outil de recherche** — encourager les citations dans les publications
2. **Lister les universites/departements utilisateurs** — cree de la credibilite pour les sponsors
3. **Proposer des ateliers/formations** lors de conferences (payes ou sponsorises)
4. **Cibler les departements d'informatique pedagogique** des universites
5. **Creer un fichier `CITATION.cff`** pour faciliter les citations academiques

---

## 6. Aspects fiscaux (France/UE)

### Principes cles

1. **Les dons/sponsorships sont imposables en France**, quelle que soit la plateforme

2. **Classification selon le statut** :

| Statut | Declaration | Avantages | Inconvenients |
|--------|------------|-----------|---------------|
| **Particulier** | BNC (revenus non commerciaux) sur declaration personnelle | Simple, pas de structure a creer | Pas de deductibilite pour le donateur |
| **Auto-entrepreneur** | URSSAF mensuel/trimestriel + 2042-C-PRO | Regime simplifie, plafonds genereux | Cotisations sociales sur le CA |
| **Association loi 1901** | Comptabilite associative | Credit d'impot 60% pour les donateurs entreprises | Structure formelle, AG, bureau |

3. **GitHub Sponsors** :
   - Ne retient pas d'impots a la source
   - Demande un formulaire W-8BEN (non-resident US)
   - Paiements en EUR via Stripe Connect vers compte francais

4. **TVA** :
   - Les simples dons ne sont **pas soumis a la TVA**
   - Si vous vendez des produits/services (via Polar.sh), la TVA UE s'applique
   - Polar.sh en tant que Merchant of Record gere la TVA automatiquement

### Recommandation pratique

Pour demarrer : recevoir les revenus GitHub Sponsors en tant que **particulier**, declarer en BNC.
Si les montants depassent quelques centaines d'euros/an, consulter un **expert-comptable**
pour evaluer la creation d'une micro-entreprise ou d'une association.

> **Note** : Si vous creez une association loi 1901 reconnue d'interet general,
> les entreprises francaises peuvent beneficier d'un **credit d'impot de 60%**
> sur leurs dons — un argument puissant pour le sponsoring corporate.

---

## 7. Monetisation par dual licensing ?

### Analyse

| Critere | Evaluation |
|---------|-----------|
| **Faisabilite technique** | Oui (StreamTeX est sous MIT, le mainteneur detient le copyright) |
| **Public cible** | Academiques (utilisent quasi-exclusivement la version gratuite) |
| **Effort de mise en place** | Eleve (CLA pour les contributeurs, double licence, gestion) |
| **Revenus potentiels** | Faibles (pas d'usage commercial significatif a ce stade) |
| **Impact sur l'adoption** | Negatif (les licences restrictives freinent l'adoption academique) |

### Verdict

**Non recommande pour StreamTeX actuellement.** Le public academique utiliserait
quasi-exclusivement la version gratuite, rendant les revenus de licence negligeables.
La licence MIT actuelle maximise l'adoption — c'est l'approche correcte.

**Alternatives preferables** :
- Monetiser via des donations/sponsorships (effort faible, pas de friction)
- Proposer du contenu premium via Polar.sh (templates, formations)
- Consulting/formations payes autour de StreamTeX

---

## 8. Plan d'action

### Etape 1 : Creer un profil GitHub Sponsors (30 min)

1. Aller sur `https://github.com/sponsors/` et cliquer "Get started"
2. Configurer Stripe Connect avec un compte bancaire francais
3. Remplir les informations fiscales (formulaire W-8BEN)
4. Definir 3-5 tiers de sponsoring :

| Tier | Montant/mois | Avantage |
|------|-------------|----------|
| Cafe | 3 EUR | Remerciement dans le README |
| Supporter | 10 EUR | Remerciement + badge "Sponsor" |
| Backer | 25 EUR | Remerciement + priorite sur les issues |
| Gold | 50 EUR | Logo dans le README + priorite |
| Platinum | 100 EUR | Logo + mention dans la doc + appel mensuel |

5. Activer les dons ponctuels (one-time sponsorships)

### Etape 2 : Configurer FUNDING.yml (5 min)

Creer `.github/FUNDING.yml` dans le repo `streamtex` :

```yaml
github: [nicolasguelfi]
liberapay: nicolasguelfi
ko_fi: nicolasguelfi
thanks_dev: u/gh/nicolasguelfi
```

### Etape 3 : Ajouter l'URL Funding dans pyproject.toml (2 min)

```toml
[project.urls]
Homepage = "https://github.com/nicolasguelfi/streamtex"
Repository = "https://github.com/nicolasguelfi/streamtex"
Issues = "https://github.com/nicolasguelfi/streamtex/issues"
Funding = "https://github.com/sponsors/nicolasguelfi"
```

### Etape 4 : Ajouter une section Support au README (10 min)

```markdown
## Support StreamTeX

StreamTeX is free and open-source. If you find it useful, consider supporting
its development:

- [GitHub Sponsors](https://github.com/sponsors/nicolasguelfi)
- [Liberapay](https://liberapay.com/nicolasguelfi)
- [Ko-fi](https://ko-fi.com/nicolasguelfi)

Your support helps maintain and improve StreamTeX for the academic community.
```

### Etape 5 : S'inscrire sur Thanks.dev (5 min)

1. Aller sur `https://thanks.dev`
2. Connecter le compte GitHub
3. S'enregistrer comme mainteneur

### Etape 6 (optionnel) : Creer un compte Liberapay (10 min)

1. Aller sur `https://liberapay.com`
2. Creer un compte avec le meme username GitHub
3. Connecter Stripe pour les paiements
4. Definir un objectif de financement hebdomadaire

### Etape 7 (a moyen terme) : Considerer Polar.sh

Si vous souhaitez vendre du contenu premium :
- Templates de presentations pretes a l'emploi
- Formations video sur StreamTeX
- Support prioritaire / consulting
- Polar.sh gere toute la TVA UE automatiquement

---

## 9. Integration technique

### 9.1 Fichier `.github/FUNDING.yml`

Ce fichier active le bouton "Sponsor" sur la page du repo GitHub.
Toutes les plateformes supportees nativement :

```yaml
# .github/FUNDING.yml — StreamTeX

# GitHub Sponsors (priorite 1)
github: [nicolasguelfi]

# Plateformes secondaires
liberapay: nicolasguelfi
ko_fi: nicolasguelfi
thanks_dev: u/gh/nicolasguelfi

# Si Polar.sh est configure plus tard
# polar: nicolasguelfi

# URLs personnalisees (max 4)
# custom: ["https://streamtex.dev/sponsor"]
```

### 9.2 Metadata PyPI (PEP 753)

L'URL `Funding` dans `[project.urls]` est reconnue par PyPI et affichee
avec une icone coeur/sponsor sur la page du package.

Labels reconnus (insensible a la casse) : `funding`, `sponsor`, `donate`, `donation`.

### 9.3 Fichier CITATION.cff

Pour encourager les citations academiques et renforcer la credibilite :

```yaml
cff-version: 1.2.0
message: "If you use StreamTeX, please cite it as below."
type: software
title: "StreamTeX"
authors:
  - family-names: "Guelfi"
    given-names: "Nicolas"
    orcid: "https://orcid.org/XXXX-XXXX-XXXX-XXXX"
version: "0.3.0"
date-released: "2026-03-01"
url: "https://github.com/nicolasguelfi/streamtex"
license: MIT
repository-code: "https://github.com/nicolasguelfi/streamtex"
keywords:
  - streamlit
  - presentations
  - education
  - python
```

---

## 10. Checklist de validation

### Etape 1 : GitHub Sponsors
- [ ] Profil GitHub Sponsors cree
- [ ] Stripe Connect configure (compte bancais FR)
- [ ] Informations fiscales soumises (W-8BEN)
- [ ] Tiers de sponsoring definis (3-5 niveaux)
- [ ] Dons ponctuels actives

### Etape 2 : FUNDING.yml
- [ ] `.github/FUNDING.yml` cree dans le repo `streamtex`
- [ ] Bouton "Sponsor" visible sur la page du repo

### Etape 3 : PyPI
- [ ] URL `Funding` ajoutee dans `pyproject.toml`
- [ ] Lien visible sur la page PyPI de streamtex

### Etape 4 : README
- [ ] Section "Support StreamTeX" ajoutee au README
- [ ] Liens vers les plateformes de dons

### Etape 5 : Thanks.dev
- [ ] Inscription comme mainteneur sur Thanks.dev

### Etape 6 : Liberapay (optionnel)
- [ ] Compte cree
- [ ] Stripe connecte
- [ ] Objectif de financement defini

### Etape 7 : CITATION.cff (optionnel)
- [ ] Fichier CITATION.cff cree dans le repo
- [ ] ORCID du mainteneur ajoute

### Etape 8 : Aspects fiscaux
- [ ] Expert-comptable consulte (si revenus > quelques centaines EUR/an)
- [ ] Regime fiscal choisi (particulier / auto-entrepreneur / association)

---

## Annexe : Sources et references

### Plateformes
- [GitHub Sponsors — Documentation](https://docs.github.com/en/sponsors)
- [Liberapay — FAQ](https://en.liberapay.com/about/faq)
- [Ko-fi — Pricing](https://ko-fi.com/pricing)
- [Polar.sh — Documentation](https://polar.sh/docs/introduction)
- [Thanks.dev](https://thanks.dev/)
- [Open Collective Europe](https://opencollective.com/europe)

### Standards Python
- [PEP 753 — Well-known Project URLs](https://peps.python.org/pep-0753/)
- [pyproject.toml URLs](https://packaging.python.org/en/latest/guides/writing-pyproject-toml/)

### Financement academique
- [scikit-learn Funding Model (2024)](https://arxiv.org/html/2404.06484v1)
- [Ten Simple Rules for Funding Scientific OSS](https://pmc.ncbi.nlm.nih.gov/articles/PMC9671312/)
- [University OSPOs (Sloan Foundation)](https://sloan.org/programs/digital-technology/ospo-loi)

### Fiscalite France
- [Declaration micro-entrepreneur (impots.gouv.fr)](https://www.impots.gouv.fr/particulier/questions/comment-declarer-les-revenus-provenant-de-mon-activite-dauto-entrepreneur)
- [GitHub Sponsors Tax Information](https://docs.github.com/en/sponsors/receiving-sponsorships-through-github-sponsors/tax-information-for-github-sponsors)

### Nouveautes 2026
- [Open Source Endowment](https://endowment.dev/funding/)
