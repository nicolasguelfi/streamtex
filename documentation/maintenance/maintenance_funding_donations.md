# Plan de Maintenance : Systeme de Donations et Financement de StreamTeX

> **Date** : 2026-03-03
> **Auteur** : Nicolas Guelfi + Claude
> **Version** : 2.1
> **Statut** : A FAIRE

---

## Table des matieres

1. [Contexte et objectif](#1-contexte-et-objectif)
2. [Analyse des plateformes](#2-analyse-des-plateformes)
3. [Tableau comparatif des plateformes](#3-tableau-comparatif-des-plateformes)
4. [Scenarios de reception des revenus](#4-scenarios-de-reception-des-revenus)
5. [Comparatif detaille des scenarios](#5-comparatif-detaille-des-scenarios)
6. [**Scenario SARL integral — guide operationnel**](#6-scenario-sarl-integral--guide-operationnel)
7. [Aspects fiscaux Luxembourg](#7-aspects-fiscaux-luxembourg)
8. [Regime IP Box Luxembourg — avantage cle](#8-regime-ip-box-luxembourg--avantage-cle)
9. [Structures juridiques luxembourgeoises](#9-structures-juridiques-luxembourgeoises)
10. [Considerations transfrontalieres France-Luxembourg](#10-considerations-transfrontalieres-france-luxembourg)
11. [Specificites du public academique](#11-specificites-du-public-academique)
12. [Monetisation par dual licensing ?](#12-monetisation-par-dual-licensing-)
13. [Programmes et aides Luxembourg](#13-programmes-et-aides-luxembourg)
14. [Strategie recommandee](#14-strategie-recommandee)
15. [Plan d'action](#15-plan-daction)
16. [**Preparation reunion expert-comptable**](#16-preparation-reunion-expert-comptable)
17. [Integration technique](#17-integration-technique)
18. [Checklist de validation](#18-checklist-de-validation)
19. [Annexe : Sources et references](#19-annexe--sources-et-references)

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

### Profil du mainteneur

| Critere | Detail |
|---------|--------|
| **Nationalite** | Francaise |
| **Residence fiscale** | Luxembourg |
| **Societe existante** | SARL luxembourgeoise (domaine IT / Intelligence Artificielle) |
| **Statut** | Gerant/associe de la SARL + mainteneur OSS |

Ce profil ouvre des options fiscales et juridiques specifiques, notamment le
**regime IP Box luxembourgeois** (taux effectif ~4.77%) et la possibilite de
recevoir les revenus via la societe existante.

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
| **Luxembourg** | **Oui** — Stripe Connect entierement supporte au Luxembourg, paiements SEPA en EUR |

**Pourquoi c'est le meilleur choix pour StreamTeX** :
- 0% de frais plateforme (seuls les frais Stripe s'appliquent)
- Integration native avec le repo GitHub (bouton "Sponsor" visible)
- Les utilisateurs de StreamTeX sont deja sur GitHub
- Support PyPI via les URLs `Funding` dans `pyproject.toml`
- Stripe Connect gere les paiements en EUR vers un compte luxembourgeois
- W-8BEN-E (pour la SARL) ou W-8BEN (personnel) : **0% retenue a la source US**
  grace a la convention fiscale US-Luxembourg

### 2.2 Liberapay (bon complement)

**Principe** : Plateforme de dons recurrents, elle-meme financee par des dons.
Geree par une association basee en France (Querrien).

| Critere | Detail |
|---------|--------|
| **Frais plateforme** | 0% (aucune commission) |
| **Frais paiement** | ~3.2% (Stripe) ou ~5% (PayPal) |
| **Total effectif** | **~3.2%** |
| **Dons ponctuels** | Non (recurrents uniquement) |
| **Dons recurrents** | Oui (hebdomadaire, mensuel, annuel) |
| **Integration** | `.github/FUNDING.yml` (`liberapay: USERNAME`) |
| **Luxembourg** | **Oui** — SEPA Direct Debit accepte, Stripe disponible |

**Avantages** : 0% de frais, philosophie open-source.
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
| **Luxembourg** | **Oui** — Stripe/PayPal supportes |

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
| **Luxembourg** | **Oui** |

**Avantage** : Gere toute la TVA/conformite UE automatiquement (Merchant of Record).
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

**Principe** : Hebergement fiscal par une entite legale europeenne (Belgique).
Gere la comptabilite, les taxes, les factures et la conformite.

| Critere | Detail |
|---------|--------|
| **Frais plateforme** | 8-10% (hebergeur fiscal) + ~3% (Stripe) |
| **Total effectif** | **~11-13%** |
| **Dons ponctuels** | Oui |
| **Dons recurrents** | Oui |
| **Integration** | `.github/FUNDING.yml` (`open_collective: USERNAME`) |
| **Luxembourg** | Pas d'hote fiscal luxembourgeois, mais Open Collective Europe (Belgique) couvre l'UE |

**Avantage** : Gestion fiscale complete, eligible aux subventions UE.
**Inconvenient** : Frais eleves, plus adapte a un projet multi-contributeurs.

### 2.7 Plateformes NON recommandees pour StreamTeX

| Plateforme | Raison |
|------------|--------|
| **Patreon** | Frais les plus eleves (10-13%), branding createurs, recurrent uniquement |
| **Buy Me a Coffee** | 5% frais plateforme + 3% paiement = ~8%, branding grand public |
| **Tidelift** | Modele entreprise, StreamTeX trop niche pour etre dans les arbres de dependances |

---

## 3. Tableau comparatif des plateformes

| Plateforme | Frais total | Ponctuel | Recurrent | Integration GitHub | Luxembourg | Recommandation |
|------------|------------|----------|-----------|-------------------|------------|----------------|
| **GitHub Sponsors** | ~3% | Oui | Oui | Native | Oui | **Priorite 1** |
| **Liberapay** | ~3.2% | Non | Oui | FUNDING.yml | Oui | **Priorite 2** |
| **Ko-fi** | ~3% | Oui | Oui | FUNDING.yml | Oui | Optionnel |
| **Thanks.dev** | ~5-8% | Non | Auto | FUNDING.yml | Oui | Optionnel (passif) |
| **Polar.sh** | ~4.4% | Oui | Oui | FUNDING.yml | Oui | Si vente de produits |
| **Open Collective** | ~11-13% | Oui | Oui | FUNDING.yml | Via Belgique | Si le projet grandit |

---

## 4. Scenarios de reception des revenus

Trois scenarios principaux sont possibles, chacun avec des implications fiscales
et administratives differentes.

### Scenario A : Reception personnelle (resident fiscal luxembourgeois)

Les donations arrivent sur un compte personnel luxembourgeois via Stripe Connect.

| Aspect | Detail |
|--------|--------|
| **Classification fiscale** | Revenus divers ou benefice commercial/profession liberale selon la regularite |
| **Impot sur le revenu** | Bareme progressif luxembourgeois (0% a 42% + 7-9% de surcharge solidarite) |
| **Securite sociale** | ~24.2% si activite independante (CNS, pension, dependance) |
| **Seuil minimum CCSS** | EUR 2,637.79/mois (base minimale de cotisation) |
| **TVA** | Non applicable sur les dons purs |
| **Complexite** | Faible si secondaire, moyenne si activite principale |

**Attention** : Si c'est une activite secondaire (en plus d'un emploi salarie),
les cotisations sociales peuvent etre reduites ou plafonnees. Si c'est une activite
principale, les cotisations minimales CCSS (sur EUR 2,637.79/mois) s'appliquent
meme si les revenus sont inferieurs.

### Scenario B : Reception via la SARL luxembourgeoise existante

Les donations arrivent sur le compte de la societe IT/AI existante.

| Aspect | Detail |
|--------|--------|
| **Classification** | Revenus commerciaux de la societe |
| **Impot sur les societes (IRC)** | 16% (>EUR 200k) ou 14% (<=EUR 175k) + 7% surcharge solidarite |
| **Impot commercial communal (ICC)** | 6.75% (ville de Luxembourg) a 12% selon commune |
| **Taux combine effectif** | **~23.87%** (ville de Luxembourg) |
| **Avec IP Box** | **~4.77%** sur les revenus nets qualifies de propriete intellectuelle |
| **TVA** | Non applicable sur les dons purs ; seuil d'exemption EUR 50,000 si services |
| **Distribution dividendes** | 15% retenue a la source supplementaire |
| **Alternative** | Salaire verse par la SARL (deductible pour la societe) |
| **Depenses deductibles** | Developpement, hebergement, outils, comptabilite, conferences |
| **Complexite** | Faible (societe existante, comptabilite deja en place) |

### Scenario C : Approche hybride (RECOMMANDE)

Combiner reception personnelle pour les petits dons et la SARL pour les sponsorings
corporatifs significatifs.

| Type de revenu | Canal | Raison |
|----------------|-------|--------|
| GitHub Sponsors (individus, < EUR 500/mois) | Personnel | Simplicite, pas de charge admin supplementaire |
| Sponsoring corporate (entreprises, logos, support) | SARL | Depenses deductibles, IP Box, factures possibles |
| Vente de contenu premium (Polar.sh) | SARL | Activite commerciale, Polar gere la TVA |
| Subventions / grants | SARL | Structure formelle requise par les organismes |

---

## 5. Comparatif detaille des scenarios

### 5.1 Taux effectifs par niveau de revenu

#### Scenario A — Personnel (activite secondaire)

Hypothese : le mainteneur a deja un emploi salarie via la SARL, les donations sont
un revenu complementaire. L'impot marginal depend du revenu total.

| Dons/mois | Dons/an | Impot marginal (est.) | Secu complementaire | Charge totale | Taux effectif |
|-----------|---------|----------------------|---------------------|--------------|---------------|
| EUR 100 | EUR 1,200 | ~20-24% | Plafonnee/nulle | ~EUR 240-290 | **~20-24%** |
| EUR 500 | EUR 6,000 | ~24-30% | Plafonnee/nulle | ~EUR 1,440-1,800 | **~24-30%** |
| EUR 2,000 | EUR 24,000 | ~30-39% | Plafonnee/nulle | ~EUR 7,200-9,360 | **~30-39%** |

> Note : Si l'activite salariee atteint deja le plafond de cotisations CCSS
> (5x le salaire social minimum = EUR 13,188.96/mois), aucune cotisation sociale
> supplementaire n'est due sur les revenus de donations.

#### Scenario B — SARL sans IP Box

| Dons/mois | Dons/an | IRC+ICC (~23.87%) | Apres impots | Dividende (15% WHT) | Net proprietaire | Taux effectif |
|-----------|---------|-------------------|-------------|---------------------|-----------------|---------------|
| EUR 100 | EUR 1,200 | EUR 286 | EUR 914 | EUR 137 | EUR 777 | **~35%** |
| EUR 500 | EUR 6,000 | EUR 1,432 | EUR 4,568 | EUR 685 | EUR 3,883 | **~35%** |
| EUR 2,000 | EUR 24,000 | EUR 5,729 | EUR 18,271 | EUR 2,741 | EUR 15,530 | **~35%** |

> Les frais fixes de la SARL (comptabilite, depot de comptes) sont deja couverts
> par l'activite existante — pas de surcout.

#### Scenario B — SARL avec IP Box

| Dons/mois | Dons/an | IRC+ICC (~4.77%) | Apres impots | Dividende (15% WHT) | Net proprietaire | Taux effectif |
|-----------|---------|------------------|-------------|---------------------|-----------------|---------------|
| EUR 100 | EUR 1,200 | EUR 57 | EUR 1,143 | EUR 171 | EUR 972 | **~19%** |
| EUR 500 | EUR 6,000 | EUR 286 | EUR 5,714 | EUR 857 | EUR 4,857 | **~19%** |
| EUR 2,000 | EUR 24,000 | EUR 1,145 | EUR 22,855 | EUR 3,428 | EUR 19,427 | **~19%** |

#### Scenario B — SARL avec IP Box + salaire (pas de dividende)

Alternative : au lieu de distribuer des dividendes, se verser un salaire
supplementaire (charge deductible pour la SARL).

| Dons/mois | Dons/an | IRC IP Box (~4.77%) | Restant pour salaire | IR marginal (~30%) | Secu | Net approx. | Taux effectif |
|-----------|---------|---------------------|---------------------|-------------------|------|-------------|---------------|
| EUR 500 | EUR 6,000 | EUR 286 | EUR 5,714 | ~EUR 1,714 | Plafonnee | ~EUR 4,000 | **~33%** |
| EUR 2,000 | EUR 24,000 | EUR 1,145 | EUR 22,855 | ~EUR 6,857 | Plafonnee | ~EUR 16,000 | **~33%** |

> Note : Le salaire etant deductible pour la SARL, le taux IRC effectif se
> rapproche de 0% si tout est redistribue en salaire. Le cout final est
> essentiellement l'impot personnel sur le salaire.

### 5.2 Synthese comparative

| Scenario | Taux effectif | Avantages | Inconvenients |
|----------|--------------|-----------|---------------|
| **A — Personnel** | 20-39% | Simple, pas de demarche | Pas de deduction de frais, taux marginal eleve |
| **B — SARL sans IP Box** | ~35% | Depenses deductibles, structure existante | Double taxation (IRC + dividendes) |
| **B — SARL avec IP Box** | **~19%** | Taux tres bas, depenses deductibles | Documentation R&D requise |
| **B — SARL IP Box + salaire** | ~33% | Pas de double taxation | IR marginal sur le salaire |
| **C — Hybride** | 19-30% | Optimise chaque type de revenu | Deux canaux a gerer |

### 5.3 Recommandation par niveau de revenu

| Niveau | Structure recommandee | Raison |
|--------|----------------------|--------|
| < EUR 100/mois | Personnel | Trop faible pour justifier l'admin SARL |
| EUR 100-500/mois | **SARL existante** | Pas de surcout (societe deja en place), depenses deductibles |
| EUR 500-2,000/mois | **SARL + IP Box** | Taux effectif ~19%, nettement plus avantageux |
| > EUR 2,000/mois | **SARL + IP Box** | Avantage majeur ; envisager aussi Luxinnovation/SNCI |

> **Point cle** : Contrairement au scenario classique ou creer une SARL represente
> un cout fixe important, votre SARL existante absorbe les revenus de donations
> **sans surcout administratif significatif**. Meme a EUR 100/mois, il peut etre
> interessant de router via la SARL pour deduire les frais de developpement
> (hebergement, outils, etc.) de l'ensemble des revenus de la societe.

---

## 6. Scenario SARL integral — guide operationnel

Ce scenario detaille presume que **tous les fonds** (donations, sponsorships,
ventes de contenu, subventions) sont recus par votre SARL IT/AI luxembourgeoise
existante. C'est le scenario recommande pour optimiser la fiscalite et simplifier
la gestion.

### 6.1 Architecture globale du flux financier

```
Donateurs / Sponsors
        |
        v
+-------------------+     +-------------------+     +-------------------+
| GitHub Sponsors   |     | Polar.sh          |     | Virement direct   |
| Liberapay         |     | (Merchant of      |     | (sponsors corp.)  |
| Ko-fi             |     |  Record)           |     |                   |
| Thanks.dev        |     |                   |     |                   |
+--------+----------+     +--------+----------+     +--------+----------+
         |                          |                          |
         v                          v                          v
   Stripe Connect            Stripe / Virement            IBAN SARL
   (compte SARL)             (compte SARL)             (virement SEPA)
         |                          |                          |
         +----------+---------------+--------------------------+
                    |
                    v
         +---------------------+
         | Compte bancaire     |
         | SARL Luxembourg     |
         +---------------------+
                    |
          +---------+---------+
          |                   |
          v                   v
   Depenses deductibles   Extraction revenus
   (R&D, hebergement,     (salaire gerant ou
    outils, conferences)   dividendes ou mixte)
```

### 6.2 Configuration des plateformes pour la SARL

#### GitHub Sponsors (canal principal)

| Etape | Action | Detail |
|-------|--------|--------|
| 1 | Creer un compte GitHub Organisation | Pour la SARL, si pas deja existant |
| 2 | Activer GitHub Sponsors | Sur le compte organisation OU le compte personnel lie a la SARL |
| 3 | Stripe Connect | Connecter le **compte bancaire de la SARL** (IBAN LU) |
| 4 | Formulaire fiscal | **W-8BEN-E** (entite, pas individu) |
| 5 | TIN | Matricule fiscal de la SARL (13 chiffres) |
| 6 | Convention fiscale | US-Luxembourg → 0% retenue a la source |
| 7 | Tiers | Definir les paliers (voir section 17) |

**Point important** : GitHub Sponsors supporte aussi bien les comptes personnels
que les comptes organisations. Si vous souhaitez que la SARL soit le beneficiaire
legal, utilisez un compte organisation configure avec les coordonnees bancaires
et fiscales de la SARL.

#### Liberapay / Ko-fi / Thanks.dev

Ces plateformes n'ont generalement pas de concept "entreprise" — le paiement
arrive sur un compte Stripe/PayPal. **Solution** :

- Configurer Stripe Connect avec le **compte bancaire de la SARL**
- Ou recevoir sur un compte PayPal professionnel lie a la SARL
- Documenter comptablement chaque entree comme revenu de la societe

#### Polar.sh (si vente de contenu)

Polar agit comme **Merchant of Record** — il facture le client final, collecte
la TVA, et vous verse le net. Configuration pour la SARL :

- Enregistrer la SARL comme beneficiaire
- Fournir le numero TVA LU (si enregistre) ou indiquer l'exemption PME
- Polar gere la TVA de chaque pays automatiquement

#### Sponsoring corporate direct (virements)

Pour les sponsors entreprises (universites, societes) qui paient par virement :

- Fournir l'IBAN/BIC de la SARL
- Emettre une **facture** depuis la SARL (obligation legale pour le sponsor)
- Indiquer le numero TVA LU si applicable, ou mention "TVA non applicable,
  article 56bis paragraphe 1 de la loi modifiee du 12 fevrier 1979" (exemption PME)

### 6.3 Traitement comptable des differents types de revenus

| Type de revenu | Compte comptable | TVA | Facturation | IP Box eligible |
|----------------|-----------------|-----|-------------|-----------------|
| **Don pur** (sans contrepartie) | 7482 — Produits exceptionnels / Subventions | Hors champ | Non requise | A documenter (lien PI) |
| **Sponsoring avec logo/visibilite** | 706 — Prestations de services | 17% LU (si > seuil PME) | Oui | Oui (revenu PI) |
| **Sponsoring avec support prioritaire** | 706 — Prestations de services | 17% LU (si > seuil PME) | Oui | Partiel |
| **Vente templates/contenu** | 701 — Ventes de produits | Via Polar (MoR) | Polar facture | Possible |
| **Consulting/formation** | 706 — Prestations de services | 17% LU | Oui | Non |
| **Subvention publique** | 74 — Subventions | Hors champ | Conventions | Non |
| **Thanks.dev (micro-dons)** | 7482 — Produits exceptionnels | Hors champ | Non | A documenter |

> **Note** : Les numeros de comptes sont indicatifs (PCN luxembourgeois).
> Votre expert-comptable adaptera au plan comptable de votre SARL.

### 6.4 Depenses deductibles imputables a StreamTeX

Toutes les charges directement liees au developpement et a la maintenance
de StreamTeX sont deductibles du resultat de la SARL :

#### Charges directes

| Depense | Exemples | Deductible |
|---------|----------|------------|
| **Hebergement et infrastructure** | PyPI, GitHub (si plan payant), serveurs de test, CI/CD | Oui |
| **Outils de developpement** | Licences IDE, Claude API, outils SaaS | Oui |
| **Nom de domaine** | streamtex.dev (si applicable) | Oui |
| **Conferences et salons** | Frais de participation, deplacement, hebergement | Oui |
| **Formation continue** | Cours, livres, certifications liees au projet | Oui |
| **Materiel informatique** | Ordinateur, ecrans (amortissement) | Oui |
| **Sous-traitance** | Design, traduction, relecture (impact sur ratio nexus) | Oui |

#### Charges de personnel

| Depense | Detail | Deductible |
|---------|--------|------------|
| **Salaire du gerant** | Quote-part du temps consacre a StreamTeX | Oui |
| **Charges sociales patronales** | Part patronale sur le salaire | Oui |
| **Salaire d'employes** | Si embauche pour le developpement | Oui |

> **Astuce** : Tenir un **timesheet** (meme simplifie) du temps consacre a
> StreamTeX permet de justifier la quote-part de votre salaire imputable
> au projet. C'est aussi necessaire pour le calcul du ratio nexus IP Box.

#### Estimation des charges deductibles annuelles

| Poste | Estimation basse | Estimation haute |
|-------|-----------------|-----------------|
| Hebergement/outils | EUR 500 | EUR 2,000 |
| Conferences (1-2/an) | EUR 500 | EUR 3,000 |
| Materiel (amortissement) | EUR 500 | EUR 1,500 |
| Part salaire gerant (10-20% du temps) | EUR 5,000 | EUR 20,000 |
| **Total** | **EUR 6,500** | **EUR 26,500** |

Ces charges viennent en deduction des revenus de la SARL **dans leur ensemble**
(pas seulement des revenus de donations). Si les donations sont faibles au debut,
les charges liees a StreamTeX reduisent quand meme le resultat imposable global.

### 6.5 Strategies d'extraction des revenus

Trois strategies pour sortir l'argent de la SARL vers le gerant/associe :

#### Strategie 1 : Salaire (RECOMMANDE pour debuter)

```
Revenus donations          10,000 EUR/an
- Depenses deductibles     -6,500 EUR
- Salaire supplementaire   -3,500 EUR  (charge deductible)
= Resultat imposable SARL       0 EUR  → IRC = 0 EUR
Salaire supplementaire      3,500 EUR
- IR marginal (~30%)       -1,050 EUR
- Secu (plafonnee)              0 EUR  (deja au plafond)
= Net pour le gerant        2,450 EUR
Taux effectif global           ~25%
```

**Avantages** :
- Pas de double taxation (IRC + dividendes)
- Augmente les cotisations retraite/CNS (si pas au plafond)
- Deductible a 100% pour la SARL
- Simple comptablement

**Inconvenients** :
- IR au taux marginal (potentiellement eleve si revenus salaries importants)
- Cotisations sociales supplementaires si pas au plafond CCSS

#### Strategie 2 : Dividendes + IP Box

```
Revenus donations          10,000 EUR/an
- Depenses deductibles     -6,500 EUR
= Resultat avant impots     3,500 EUR
- IRC+ICC avec IP Box       -167 EUR  (~4.77%)
= Resultat net               3,333 EUR
- Dividende WHT (15%)        -500 EUR
= Net pour le gerant         2,833 EUR
Taux effectif global           ~17%
```

**Avantages** :
- Taux effectif tres bas grace a l'IP Box
- Pas de cotisations sociales sur les dividendes

**Inconvenients** :
- Necessite la qualification IP Box (documentation R&D)
- Double taxation (IRC + WHT) meme si les taux sont bas
- Les dividendes ne comptent pas pour la retraite/CNS

#### Strategie 3 : Mixte salaire + dividendes (RECOMMANDE si revenus significatifs)

```
Revenus donations          24,000 EUR/an
- Depenses deductibles     -8,000 EUR
- Salaire supplementaire   -6,000 EUR  (deductible)
= Resultat avant impots    10,000 EUR
- IRC+ICC avec IP Box        -477 EUR  (~4.77%)
= Resultat net               9,523 EUR
- Dividende WHT (15%)       -1,428 EUR
= Net dividende              8,095 EUR

Salaire supplementaire       6,000 EUR
- IR marginal (~30%)        -1,800 EUR
= Net salaire                4,200 EUR

Total net gerant            12,295 EUR
Taux effectif global         ~49%... mais en realite:
  - 8,000 EUR de depenses reelles absorbees
  - Retraite/CNS augmentees sur le salaire
  - Charges professionnelles couvertes
```

> **L'expert-comptable determinera le ratio optimal salaire/dividendes**
> en fonction de votre situation personnelle (classe d'impot, plafond CCSS,
> revenus salaries existants).

### 6.6 Calendrier comptable annuel

| Mois | Action |
|------|--------|
| **Mensuel** | Encaisser les payouts Stripe Connect (22 du mois) |
| **Mensuel** | Enregistrer les ecritures comptables (revenus + charges) |
| **Trimestriel** | Verifier le seuil TVA (EUR 50,000) |
| **Trimestriel** | Declaration TVA si assujetti |
| **Annuel (Q1)** | Compilation timesheet StreamTeX |
| **Annuel (Q1)** | Calcul ratio nexus IP Box |
| **Annuel (Q1)** | Preparation du bilan et de la declaration fiscale SARL |
| **Annuel (mars)** | Declaration IRC + ICC |
| **Annuel** | Assemblee generale → decision de distribution de dividendes |
| **Annuel** | Depot des comptes au RCS |

### 6.7 Documents a maintenir

| Document | Frequence | Usage |
|----------|-----------|-------|
| **Timesheet StreamTeX** | Mensuel | Quote-part salaire, ratio nexus IP Box |
| **Registre des depenses StreamTeX** | Continu | Charges deductibles, ratio nexus |
| **Releves Stripe Connect** | Mensuel | Justificatifs de revenus |
| **Factures emises** | Par sponsor corporate | Comptabilite, TVA |
| **Documentation R&D** | Annuel | Eligibilite IP Box |
| **W-8BEN-E** | Tous les 3 ans | Convention fiscale US (renouvellement) |
| **Registre des sponsors** | Continu | Suivi des contreparties (logo, support) |

### 6.8 Seuils et alertes a surveiller

| Seuil | Montant | Consequence si depasse |
|-------|---------|----------------------|
| **TVA exemption PME** | EUR 50,000 CA/an | Obligation d'enregistrement TVA |
| **TVA tolerance** | EUR 55,000 CA/an | Perte de l'exemption au 31/12 |
| **IRC taux reduit** | EUR 175,000 resultat | Passage de 14% a 16% |
| **CCSS plafond** | EUR 13,188.96/mois | Au-dela, plus de cotisations supplementaires |
| **OSS intra-UE** | EUR 10,000 ventes B2C UE | Obligation de facturer la TVA du pays client |

### 6.9 Risques et points de vigilance

| Risque | Mitigation |
|--------|-----------|
| **Objet social trop restrictif** | Verifier/amender les statuts pour couvrir "developpement et distribution de logiciels" |
| **Substance insuffisante pour IP Box** | Documenter le temps R&D, avoir un bureau physique au Luxembourg |
| **Confusion dons/prestations pour la TVA** | Bien distinguer les dons purs (pas de contrepartie) des sponsorings (avec logo/service) |
| **Ratio nexus insuffisant** | Si sous-traitance a des parties liees, le ratio diminue — privilegier le developpement interne |
| **W-8BEN-E expire** | Renouveler tous les 3 ans, sinon retenue US de 30% |
| **Non-declaration des revenus etrangers** | Tous les revenus Stripe/PayPal doivent etre declares meme si faibles |

---

## 7. Aspects fiscaux Luxembourg

### 7.1 Impot personnel (resident luxembourgeois)

Le Luxembourg utilise un bareme progressif. Extraits des tranches principales (2025) :

| Revenu imposable (EUR) | Taux marginal |
|------------------------|---------------|
| 0 - 13,230 | 0% |
| 13,230 - 15,435 | 8% |
| 22,050 - 24,255 | 12% |
| 31,140 - 33,435 | 20% |
| 42,615 - 44,910 | 30% |
| 54,090 - 117,450 | 39% |
| 117,450 - 176,160 | 40% |
| 176,160 - 234,870 | 41% |
| > 234,870 | 42% |

En plus : **surcharge de solidarite** de 7% du montant de l'impot (9% si revenus
> EUR 150,000 en classe 1/1a).

Taux marginal effectif maximum : **~45.78%**.

### 7.2 Categories de revenus applicables

Les donations/sponsorships recus personnellement au Luxembourg relèvent de :

| Situation | Categorie LIR | Articles |
|-----------|--------------|----------|
| Revenus occasionnels, non habituels | Revenus divers | Art. 99-102bis |
| Activite reguliere de maintenance OSS | Benefice commercial ou profession liberale | Art. 14-60 ou Art. 91-94 |

**Important** : Le Luxembourg n'a **pas** de regime micro-entrepreneur ou auto-entrepreneur
comme la France. Une activite reguliere implique une inscription comme independant.

### 7.3 Securite sociale (CCSS)

Si classifie comme activite independante :

| Branche | Taux |
|---------|------|
| Assurance maladie (CNS) | 5.60% |
| Pension | 16.00% |
| Assurance dependance | 1.40% |
| Accidents du travail | ~1.20% |
| **Total** | **~24.20%** |

- **Base minimale** : EUR 2,637.79/mois (salaire social minimum)
- **Base maximale** : EUR 13,188.96/mois (5x SSM)
- Si deja salarie avec cotisations au plafond : pas de cotisation supplementaire

### 7.4 Impot sur les societes (SARL)

| Composante | Taux |
|-----------|------|
| IRC (revenu <= EUR 175,000) | 14.00% |
| IRC (revenu > EUR 200,000) | 16.00% |
| Surcharge solidarite | 7% de l'IRC |
| ICC (ville de Luxembourg) | 6.75% |
| **Taux combine effectif** | **~23.87%** |

Le taux ICC varie de 6.75% a 12% selon la commune.

### 7.5 TVA luxembourgeoise

| Situation | TVA applicable |
|-----------|---------------|
| Dons purs (sans contrepartie) | **Hors champ TVA** |
| Sponsoring avec contrepartie (logo, pub, support) | TVA 17% (taux normal LU) |
| Vente de services numeriques B2C intra-UE | TVA du pays du client (via OSS) |

**Seuil d'exemption PME** : EUR 50,000 de chiffre d'affaires annuel (depuis 2025).
En dessous, pas d'obligation de facturer la TVA.

**Tolerance** : Jusqu'a EUR 55,000, l'exemption persiste jusqu'au 31 decembre.

### 7.6 Retenue a la source sur dividendes

Si la SARL distribue des dividendes au gerant/associe : **15% de retenue a la source**.

Alternative : se verser un salaire (deductible pour la societe, impose au bareme
personnel). Pas de double taxation dans ce cas.

---

## 8. Regime IP Box Luxembourg — avantage cle

### 8.1 Principe

Le regime de propriete intellectuelle (PI) luxembourgeois offre une **exemption
de 80%** sur les revenus nets qualifies de PI. C'est l'avantage fiscal le plus
significatif pour un developpeur de logiciel au Luxembourg.

### 8.2 Application a StreamTeX

| Critere | Eligibilite StreamTeX |
|---------|----------------------|
| **Type d'actif** | Logiciel protege par le droit d'auteur — **eligible** |
| **Developpement interne** | Developpe par le mainteneur/gerant — **eligible** |
| **Licence open-source** | Le copyright subsiste meme sous licence MIT — **eligible** |
| **Date** | Developpe apres le 31/12/2007 — **eligible** |

**Point important** : Un logiciel distribue sous licence MIT reste protege par le
droit d'auteur. La licence accorde des *permissions d'utilisation* mais ne transfere
pas le copyright. Le regime IP Box s'applique donc aux revenus generes par ce logiciel.

### 8.3 Calcul du taux effectif

```
Revenu net IP qualifie                        100,000 EUR
Exemption 80%                                 -80,000 EUR
Base imposable                                 20,000 EUR
IRC + surcharge (14% + 7% = 14.98%)            2,996 EUR
ICC ville de Luxembourg (6.75%)                 1,350 EUR
                                              ---------
Impot total                                     4,346 EUR
Taux effectif                                   ~4.35%
```

> Le taux effectif varie entre **4.35% et 4.77%** selon le calcul exact
> et la commune d'imposition.

### 8.4 Ratio nexus (approche OCDE modifiee)

L'exemption est proportionnelle au ratio de depenses R&D qualifiantes :

```
Ratio nexus = (Depenses R&D qualifiantes x 130%) / Depenses totales
```

- **Depenses qualifiantes** : salaires internes, sous-traitance non liee
- **Depenses non qualifiantes** : acquisitions de PI, sous-traitance a des parties liees
- Le facteur de 130% est plafonne a 100%

Pour un projet personnel ou le mainteneur est le seul developpeur, le ratio
nexus est generalement de **100%** (toutes les depenses sont qualifiantes).

### 8.5 Exigences pratiques

Pour beneficier du regime IP Box, la SARL doit :

1. **Documenter les depenses R&D** — tenir un suivi des heures et couts de developpement
2. **Identifier clairement l'actif PI** — le logiciel StreamTeX et son copyright
3. **Calculer le ratio nexus** annuellement
4. **Avoir une substance au Luxembourg** — employes ou gerant actif, locaux
5. **Documentation de transfer pricing** si transactions intra-groupe

### 8.6 Revenus qualifies pour l'IP Box

| Type de revenu | Qualifie IP Box ? |
|----------------|-------------------|
| Sponsorships lies au logiciel StreamTeX | **Oui** — revenus attribuables a la PI |
| Licences de logiciel (si applicable) | **Oui** |
| Consulting/formation sur StreamTeX | **Non** — services, pas revenus de PI |
| Vente de templates/contenu premium | **Possible** — si le contenu est protege par droit d'auteur |
| Dons purs sans contrepartie | **A analyser** — lien avec la PI a documenter |

> **Recommandation** : Consulter un expert fiscal luxembourgeois pour structurer
> correctement l'attribution des revenus au regime IP Box, en particulier pour
> les sponsorships et donations.

---

## 9. Structures juridiques luxembourgeoises

### 9.1 SARL existante (RECOMMANDE)

Votre SARL IT/AI existante est le vehicule ideal :

| Aspect | Detail |
|--------|--------|
| **Capital minimum** | EUR 12,000 (deja constitue) |
| **Avantage cle** | Pas de creation de structure, comptabilite deja en place |
| **IP Box** | Eligible si l'objet social couvre le developpement logiciel |
| **TVA** | Exemption PME si CA < EUR 50,000 |
| **Reception dons** | Produits exceptionnels ou revenus commerciaux |
| **Depenses deductibles** | Toutes les charges liees au developpement |

**Point d'attention** : Verifier que l'objet social de la SARL couvre le developpement
et la distribution de logiciels open-source. Si necessaire, un amendement des statuts
est simple et peu couteux.

### 9.2 SARL-S (si creation d'une structure dediee)

| Aspect | Detail |
|--------|--------|
| **Capital minimum** | EUR 1 (max EUR 12,000) |
| **Actionnaires** | Personnes physiques uniquement (max 100) |
| **Reserve legale** | 5% du benefice net annuel jusqu'a atteindre EUR 12,000 |
| **Fiscalite** | Identique a une SARL classique |
| **Creation** | ~EUR 3,000-5,000 (frais notaire + enregistrement) |

> Non recommande dans votre cas — la SARL existante suffit.

### 9.3 ASBL (Association Sans But Lucratif)

Equivalent luxembourgeois de l'association loi 1901 francaise. Reforme en 2023.

| Aspect | Detail |
|--------|--------|
| **Membres minimum** | 2 (reduit de 3 en 2023) |
| **Capital** | Aucun minimum |
| **Activite commerciale** | Possible si accessoire au but non lucratif |
| **Distribution de benefices** | Interdite |
| **Comptabilite** | Simplifiee si < 3 employes, < EUR 50,000 recettes, < EUR 100,000 actifs |
| **Reconnaissance d'utilite publique** | Par arrete grand-ducal (but scientifique, educatif, social) |

**Pour StreamTeX** : Pertinent uniquement si le projet devient communautaire avec
plusieurs contributeurs. Pas recommande pour un mainteneur individuel.

### 9.4 Fondation

- **Dotation minimale** : EUR 100,000 (reduit de EUR 250,000 en 2023)
- Uniquement pour des projets avec un financement initial important
- **Non recommande** pour StreamTeX a ce stade

### 9.5 GIE (Groupement d'Interet Economique)

- Structure pour la collaboration entre entreprises existantes
- Transparence fiscale (profits remontes aux membres)
- **Non pertinent** pour un projet mono-mainteneur

### 9.6 Synthese des structures

| Structure | Recommandation pour StreamTeX |
|-----------|-------------------------------|
| **SARL existante** | **OUI — priorite 1** |
| SARL-S dediee | Non necessaire |
| ASBL | Possible a long terme (projet communautaire) |
| Fondation | Non (dotation trop elevee) |
| GIE | Non pertinent |

---

## 10. Considerations transfrontalieres France-Luxembourg

### 10.1 Nationalite vs residence fiscale

| Aspect | Implication |
|--------|-------------|
| **Nationalite francaise** | Sans impact sur la fiscalite — seule la residence compte |
| **Residence fiscale Luxembourg** | Imposition au Luxembourg sur les revenus mondiaux |
| **Certificat de residence** | Delivre par l'ACD (Administration des Contributions Directes) |
| **France** | Ne peut imposer que les revenus de source francaise (aucun dans ce cas) |

### 10.2 Convention fiscale France-Luxembourg

La nouvelle convention (signee 20 mars 2018, amendement 10 octobre 2019) :

- **Methode** : La France est passee de l'exemption avec progressivite a un
  **systeme de credit d'impot fictif** pour eliminer la double imposition
- **Seuil frontalier** : Jusqu'a 34 jours de travail hors Luxembourg sans
  declencher une imposition francaise
- **Pour votre situation** : La convention confirme que la France ne peut pas
  imposer vos revenus de donations/sponsorships recus au Luxembourg

### 10.3 Convention US-Luxembourg (W-8BEN / W-8BEN-E)

GitHub etant une societe americaine (Microsoft), les regles de retenue US s'appliquent :

| Aspect | Detail |
|--------|--------|
| **Retenue par defaut** | 30% sur les revenus de source US |
| **Convention US-Luxembourg** | **0% de retenue** sur les royalties |
| **Formulaire personnel** | W-8BEN (individu) |
| **Formulaire societe** | W-8BEN-E (pour la SARL) |
| **TIN requis** | Numero fiscal luxembourgeois suffisant |
| **LOB (Limitation on Benefits)** | Residents individuels qualifient automatiquement |

**Action** : Lors de l'inscription a GitHub Sponsors, selectionner "Luxembourg"
comme pays de residence fiscale et revendiquer les avantages de la convention
US-Luxembourg pour obtenir 0% de retenue.

### 10.4 Compatibilite des plateformes avec le Luxembourg

| Plateforme | Support Luxembourg | Notes |
|------------|-------------------|-------|
| **GitHub Sponsors** | Oui | Stripe Connect entierement supporte |
| **Stripe Connect** | Oui | Comptes Custom et Express disponibles |
| **Liberapay** | Oui | SEPA, Stripe disponible |
| **PayPal** | Oui | Disponible au Luxembourg |
| **Ko-fi** | Oui | Via Stripe/PayPal |
| **Open Collective** | Partiel | Via Open Collective Europe (Belgique) |

---

## 11. Specificites du public academique

### Realite du financement en milieu academique

| Constat | Implication pour StreamTeX |
|---------|---------------------------|
| Les chercheurs ne paient **pas de leur poche** pour les outils logiciels | Les dons individuels seront faibles |
| Les universites achetent des **licences institutionnelles** | Possible canal si StreamTeX grandit |
| Les **grants de recherche** peuvent inclure des couts logiciels | Se positionner comme outil de recherche |
| Les **OSPO universitaires** emergent (12+ aux US, finances par Sloan Foundation) | Canal potentiel futur |
| Les entreprises ont des **credits d'impot** pour les dons OSS | Cibler les entreprises partenaires |

### Etude de cas : scikit-learn

scikit-learn, l'une des librairies Python les plus utilisees en academie :
- Financement principal : **institutionnel** (Inria, gouvernement francais)
- Sponsors corporate : :probabl., Chanel, BNP Paribas, NVIDIA
- Micro-dons communautaires via NumFOCUS : utiles pour "marketing, evenements, stages"
  mais pas pour la maintenance core

### Canaux de revenus realistes pour StreamTeX

| Canal | Probabilite | Montant potentiel | Effort | Structure ideale |
|-------|------------|-------------------|--------|------------------|
| GitHub Sponsors (individus) | Faible-Moyen | 10-100 EUR/mois | Faible | Personnel |
| Sponsors institutionnels | Moyen | 500-5000 EUR/an | Moyen | SARL |
| Consulting/formations | Moyen-Eleve | Variable | Moyen | SARL |
| Contenu educatif premium (Polar.sh) | Moyen | Variable | Moyen | SARL |
| Subventions de recherche | Faible (niche) | 50K-500K EUR | Eleve | SARL |
| Programmes Luxinnovation | Moyen | Jusqu'a 150K EUR | Moyen | SARL |
| Prets SNCI | Moyen | Jusqu'a 200K EUR | Moyen | SARL |

### Bonnes pratiques

1. **Positionner StreamTeX comme outil de recherche** — encourager les citations dans les publications
2. **Lister les universites/departements utilisateurs** — credibilite pour les sponsors
3. **Proposer des ateliers/formations** lors de conferences (payes ou sponsorises)
4. **Cibler les departements d'informatique pedagogique** des universites
5. **Creer un fichier `CITATION.cff`** pour faciliter les citations academiques
6. **Explorer les programmes Luxinnovation** (Fit 4 Start, Fit 4 AI) pour la SARL

---

## 12. Monetisation par dual licensing ?

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
- Exploiter le regime IP Box pour optimiser la fiscalite sur les revenus recus

---

## 13. Programmes et aides Luxembourg

### 13.1 Luxinnovation

[Luxinnovation](https://luxinnovation.lu/) est l'agence nationale d'innovation.
Programmes pertinents pour une SARL IT/AI :

| Programme | Detail | Montant |
|-----------|--------|---------|
| **Fit 4 Start** | Accelerateur 6 mois pour startups tech (AI, IoT, etc.) | Jusqu'a EUR 150,000 (equity-free) |
| **Fit 4 AI** | Evaluation et implementation IA | Variable |
| **Fit 4 Digital** | Transformation numerique | Variable |
| **SME Packages** | Packages Digital, AI, Cybersecurity | Jusqu'a EUR 17,500 chacun |
| **Luxembourg AI Factory** | Plateforme nationale pour l'IA responsable | Acces aux aides R&D nationales et europeennes |

### 13.2 SNCI (Societe Nationale de Credit et d'Investissement)

[SNCI](https://www.snci.lu/) — EUR 300 millions sur 5 ans pour les startups (2025) :

| Programme | Detail | Montant |
|-----------|--------|---------|
| **Prets de creation** | Conditions preferentielles | Jusqu'a EUR 200,000 |
| **proStart** | Phase de demarrage | Variable |
| **proDevelop** | Phase de developpement | Variable |
| **proInnovate** | Innovation | Variable |
| **Capital-risque** | Pour startups | Variable |

Secteurs cibles : cybersecurite, deeptech, technologies durables, healthtech, espace, fintech.

### 13.3 Ecosysteme tech Luxembourg

| Ressource | Detail |
|-----------|--------|
| **House of Startups** | Hub d'incubation centralise (host.lu) |
| **Technoport** | Incubateur tech national avec labs de prototypage |
| **LHoFT** | Luxembourg House of Financial Technology |
| **200+ startups IA** | 27% de l'ecosysteme startup national (2025) |
| **Startup Luxembourg** | Portail officiel (startupluxembourg.com) |

> **Opportunite** : Votre SARL IT/AI pourrait candidater aux programmes Luxinnovation
> pour financer le developpement de StreamTeX comme outil educatif base sur l'IA.
> Le positionnement "IA pour l'education" est en phase avec les priorites nationales.

---

## 14. Strategie recommandee

### Tier 1 : Immediat (effort faible)

1. **GitHub Sponsors via la SARL** — Canal principal, W-8BEN-E, 0% retenue US
2. **`.github/FUNDING.yml`** — Bouton "Sponsor" sur le repo
3. **`pyproject.toml` URL Funding** — Lien visible sur PyPI
4. **Thanks.dev** — S'inscrire (passif, cout zero)
5. **Section "Support" dans le README** — Visibilite pour les utilisateurs

### Tier 2 : Court terme (effort moyen)

6. **Evaluer l'eligibilite IP Box** avec l'expert-comptable de la SARL
7. **Liberapay** — Canal secondaire pour les dons recurrents
8. **Ko-fi** — Pour les tips ponctuels informels
9. **Polar.sh** — Si vente de contenu premium (templates, formations)

### Tier 3 : Moyen terme (effort significatif)

10. **Candidature Luxinnovation** (Fit 4 Start ou SME Packages)
11. **Explorer les prets SNCI** pour le developpement de StreamTeX
12. **Sponsoring institutionnel** — approcher les universites utilisatrices
13. **Open Collective Europe** — Si le projet devient communautaire

### Tier 4 : Long terme (si le projet grandit)

14. **ASBL** — Pour gerer une communaute de contributeurs
15. **Subventions UE** — Horizon Europe, Digital Europe Programme
16. **NumFOCUS** — Candidature si StreamTeX devient un outil scientifique reconnu

---

## 15. Plan d'action

### Etape 1 : Configurer GitHub Sponsors (30 min)

1. Aller sur `https://github.com/sponsors/` et cliquer "Get started"
2. **Choix du beneficiaire** :
   - Option A (recommande) : Configurer pour la SARL (compte organisation GitHub)
     → W-8BEN-E + Stripe Connect vers compte bancaire de la SARL
   - Option B : Configurer en personnel → W-8BEN + Stripe Connect perso
3. Remplir les informations fiscales :
   - Pays : **Luxembourg**
   - TIN : Numero fiscal luxembourgeois (personnel ou SARL)
   - Convention US-Luxembourg : revendiquer 0% de retenue
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

### Etape 6 : Consultation expert-comptable (1-2h)

**Points a aborder** :

1. Verification de l'objet social de la SARL — couvre-t-il le developpement logiciel ?
2. **Eligibilite IP Box** — documentation R&D, ratio nexus, structuration
3. Traitement comptable des donations/sponsorships
4. Optimisation : salaire vs dividendes pour l'extraction des revenus
5. Seuil TVA et obligations si sponsoring avec contrepartie

### Etape 7 (optionnel) : Creer un compte Liberapay (10 min)

1. Aller sur `https://liberapay.com`
2. Creer un compte avec le meme username GitHub
3. Connecter Stripe pour les paiements (compte LU)
4. Definir un objectif de financement hebdomadaire

### Etape 8 (moyen terme) : Explorer Luxinnovation

1. Consulter `https://luxinnovation.lu/find-funding`
2. Evaluer l'eligibilite aux programmes Fit 4 Start / Fit 4 AI
3. Candidater au SME Package AI (jusqu'a EUR 17,500)
4. Contacter un conseiller Luxinnovation pour un accompagnement personnalise

---

## 16. Preparation reunion expert-comptable

Cette section rassemble toutes les questions, informations et documents a preparer
pour votre reunion avec l'expert-comptable de la SARL. L'objectif est de valider
le montage juridique et fiscal avant de lancer la collecte de fonds.

### 16.1 Contexte a presenter

Presentez a votre expert-comptable le contexte suivant :

> *"Je suis gerant d'une SARL IT/AI au Luxembourg. J'ai developpe une librairie
> logicielle open-source appelee StreamTeX, distribuee gratuitement sous licence MIT
> sur PyPI et GitHub. Je souhaite mettre en place un systeme pour recevoir des
> donations et sponsorships de la part d'utilisateurs et d'entreprises, via des
> plateformes comme GitHub Sponsors (Microsoft/Stripe). Je veux que ces revenus
> soient recus par la SARL et j'aimerais savoir comment optimiser le traitement
> fiscal, notamment via le regime IP Box luxembourgeois."*

### 16.2 Informations a apporter a la reunion

#### Sur la SARL

- [ ] **Statuts de la SARL** — objet social exact (texte complet)
- [ ] **Dernier bilan** — pour situer le CA actuel et la capacite d'absorption
- [ ] **Regime TVA actuel** — assujetti, exempte (< EUR 50,000), ou non encore enregistre
- [ ] **Commune du siege social** — pour determiner le taux ICC applicable
- [ ] **Structure de remuneration actuelle** — salaire gerant, dividendes passes
- [ ] **Classe d'impot** — classe 1, 1a, ou 2 (impact IR personnel)

#### Sur le projet StreamTeX

- [ ] **Date de debut du developpement** — pour la qualification IP Box (post-2007)
- [ ] **Temps consacre** — estimation du % du temps de travail dedie a StreamTeX
- [ ] **Depenses engagees** — hebergement, outils, conferences (historique + previsions)
- [ ] **Revenus attendus** — estimation realiste (probablement EUR 0-500/mois au debut)
- [ ] **Types de revenus attendus** :
  - Dons purs (GitHub Sponsors, individus)
  - Sponsorings avec contrepartie (logo, mention, support)
  - Vente de contenu premium (templates, formations)
  - Consulting/formations lies a StreamTeX
- [ ] **Licence MIT** — expliquer que le copyright est conserve malgre la distribution gratuite
- [ ] **Pays des donateurs** — principalement UE, USA, international

#### Sur les plateformes de paiement

- [ ] **GitHub Sponsors** — societe US (Microsoft), paiement via Stripe Connect
- [ ] **Stripe Connect** — payout mensuel le 22 du mois, en EUR, vers IBAN LU
- [ ] **Retenue US** — formulaire W-8BEN-E, convention US-LU prevoit 0%
- [ ] **Autres plateformes** — Liberapay (FR), Ko-fi (UK), Thanks.dev, Polar.sh (NO)

### 16.3 Questions a poser — Objet social et structure

| # | Question | Contexte / Pourquoi c'est important |
|---|----------|-------------------------------------|
| 1 | **L'objet social actuel de la SARL couvre-t-il la reception de donations/sponsorships pour un logiciel open-source ?** | Si l'objet social est trop restrictif (ex: "consulting IT" uniquement), il faudra un amendement des statuts. |
| 2 | **Faut-il modifier les statuts pour mentionner explicitement "developpement et distribution de logiciels" ?** | Necessaire pour l'IP Box et pour securiser la qualification des revenus. |
| 3 | **Quel est le cout et le delai d'un amendement des statuts si necessaire ?** | Acte notarie + publication au Memorial + depot RCS. |
| 4 | **La SARL peut-elle recevoir des "dons" au sens juridique luxembourgeois, ou faut-il les qualifier autrement (subventions, produits exceptionnels) ?** | Une SARL n'est pas une ASBL — la qualification comptable du revenu a des implications fiscales. |

### 16.4 Questions a poser — IP Box (regime PI)

| # | Question | Contexte / Pourquoi c'est important |
|---|----------|-------------------------------------|
| 5 | **Le logiciel StreamTeX, distribue sous licence MIT, est-il eligible au regime IP Box luxembourgeois ?** | Le copyright subsiste meme sous licence open-source, mais l'expert-comptable doit confirmer. |
| 6 | **Comment documenter les depenses R&D pour le ratio nexus ? Quel niveau de detail est attendu par l'ACD ?** | Timesheet, releves de commits GitHub, factures d'outils ? |
| 7 | **Le ratio nexus serait-il de 100% si je suis le seul developpeur (pas de sous-traitance) ?** | Ratio nexus = (depenses R&D qualifiantes x 130%) / depenses totales. |
| 8 | **Les revenus de sponsorship (avec contrepartie : logo, mention) qualifient-ils comme revenus de PI pour l'IP Box ?** | Distinction entre revenus de PI (eligible) et revenus de services (non eligible). |
| 9 | **Les dons purs (sans contrepartie) qualifient-ils pour l'IP Box, ou faut-il les traiter separement ?** | Zone grise — le lien avec la PI doit etre documente. |
| 10 | **Quels sont les couts de mise en place et de suivi annuel du regime IP Box ?** | Documentation, calculs, declaration — combien cela coutera en honoraires comptables ? |
| 11 | **A partir de quel montant de revenus le regime IP Box devient-il rentable compte tenu des couts de mise en conformite ?** | Si les revenus sont faibles (< EUR 5,000/an), le cout du suivi IP Box peut depasser le gain fiscal. |
| 12 | **Faut-il deposer le logiciel aupres d'un organisme (ex: Copyright Office) ou le copyright automatique suffit-il ?** | En UE, le droit d'auteur est automatique. Mais l'ACD peut-elle demander une preuve ? |

### 16.5 Questions a poser — TVA

| # | Question | Contexte / Pourquoi c'est important |
|---|----------|-------------------------------------|
| 13 | **Les dons purs recus via GitHub Sponsors sont-ils hors champ TVA ?** | A confirmer : pas de contrepartie = pas de fait generateur TVA. |
| 14 | **Les sponsorings avec contrepartie (logo, mention dans la doc) constituent-ils une prestation de services soumise a TVA ?** | Si oui, TVA a 17% (LU) ou TVA du pays du client (B2B reverse charge) ? |
| 15 | **Le seuil d'exemption PME de EUR 50,000 s'applique-t-il au CA total de la SARL ou uniquement aux revenus de StreamTeX ?** | Critique — si la SARL a deja un CA > EUR 50,000 avec son activite principale, l'exemption peut deja etre depassee. |
| 16 | **Faut-il enregistrer la SARL au regime OSS (One Stop Shop) si des clients B2C sont dans d'autres pays UE ?** | Seuil de EUR 10,000 en ventes B2C transfrontalieres. |
| 17 | **Polar.sh agissant comme Merchant of Record, ai-je des obligations TVA sur les revenus recus de Polar ?** | Polar facture au client et vous verse le net — quelles sont vos obligations ? |

### 16.6 Questions a poser — Traitement comptable

| # | Question | Contexte / Pourquoi c'est important |
|---|----------|-------------------------------------|
| 18 | **Dans quel compte comptable enregistrer les differents types de revenus ?** | Produits exceptionnels (7482) vs prestations de services (706) vs ventes (701). |
| 19 | **Comment comptabiliser les frais de plateforme (commission Stripe ~3%) ?** | Charge financiere ou charge d'exploitation ? |
| 20 | **Comment traiter les paiements en USD si certains dons arrivent en dollars ?** | Ecarts de change — quel taux utiliser (taux BCE du jour, taux mensuel) ? |
| 21 | **Comment documenter la quote-part du salaire du gerant imputable a StreamTeX ?** | Timesheet, deliberation de l'AG, contrat de travail amende ? |
| 22 | **Quelle est la meilleure strategie d'extraction des revenus : salaire supplementaire, dividendes, ou mixte ?** | Presenter les 3 scenarios calcules dans ce document (section 6.5) pour avoir l'avis de l'expert. |
| 23 | **La SARL doit-elle emettre des factures pour les dons recus via GitHub Sponsors ?** | GitHub n'est pas le donateur — il est intermediaire. Qui est le "client" ? |

### 16.7 Questions a poser — International et retenue a la source

| # | Question | Contexte / Pourquoi c'est important |
|---|----------|-------------------------------------|
| 24 | **Le formulaire W-8BEN-E est-il correctement rempli pour la SARL ? Pouvez-vous le verifier avant soumission ?** | Erreur = 30% de retenue US au lieu de 0%. |
| 25 | **La SARL a-t-elle besoin d'un numero ITIN/EIN americain, ou le matricule fiscal LU suffit-il ?** | Pour revendiquer les avantages de la convention US-LU. |
| 26 | **Y a-t-il des obligations declaratives supplementaires pour les revenus provenant de plateformes US ?** | Formulaire 200 (declaration IRC) — rubrique revenus etrangers ? |
| 27 | **Ma nationalite francaise cree-t-elle un risque de requalification par le fisc francais ?** | Convention FR-LU confirme la residence fiscale LU. A documenter ? |

### 16.8 Questions a poser — Aspects pratiques et conformite

| # | Question | Contexte / Pourquoi c'est important |
|---|----------|-------------------------------------|
| 28 | **Faut-il ouvrir un compte bancaire dedie pour les revenus StreamTeX, ou le compte courant de la SARL suffit-il ?** | Pour la tracabilite comptable. |
| 29 | **Quelles sont les obligations de conservation des documents pour les revenus de plateformes numeriques ?** | Releves Stripe, emails de confirmation de dons, etc. |
| 30 | **Y a-t-il des obligations specifiques si un sponsor est une entite publique (universite, organisme de recherche) ?** | Conventions de subvention, rapports d'activite, etc. |
| 31 | **Quel surcout annuel en honoraires comptables represente l'ajout de cette activite a la comptabilite existante ?** | Pour evaluer le seuil de rentabilite. |
| 32 | **Connaissez-vous des precedents de SARL luxembourgeoises recevant des sponsorships open-source ? Des bonnes pratiques ?** | L'expert-comptable a peut-etre deja traite un cas similaire. |

### 16.9 Documents a demander a l'expert-comptable apres la reunion

- [ ] Confirmation ecrite de l'eligibilite IP Box (ou non) avec justification
- [ ] Modele de timesheet R&D acceptable pour l'ACD
- [ ] Projet d'amendement des statuts si necessaire
- [ ] Schema comptable pour les differents types de revenus
- [ ] Estimation des couts annuels supplementaires (honoraires comptables, IP Box)
- [ ] Recommandation salaire vs dividendes formalisee
- [ ] Checklist des obligations declaratives supplementaires
- [ ] Formulaire W-8BEN-E pre-rempli ou verifie

### 16.10 Resume — points decisionnels cles de la reunion

La reunion doit aboutir a des decisions claires sur ces 5 points :

| # | Decision | Options | Impact |
|---|----------|---------|--------|
| **D1** | L'objet social est-il suffisant ? | Oui / Amendement necessaire | Bloquant — a resoudre avant de commencer |
| **D2** | IP Box : on l'active ou non ? | Oui (si rentable) / Non (si trop cher au debut) | Taux effectif 4.77% vs 23.87% |
| **D3** | Extraction : salaire, dividendes, ou mixte ? | Salaire seul / Dividendes IP Box / Mixte | Impact IR personnel + secu |
| **D4** | TVA : regime applicable ? | Exemption PME / Assujetti / OSS | Obligations declaratives |
| **D5** | Cout du montage : ca vaut le coup ? | Oui des maintenant / Attendre un seuil de revenus | Seuil de rentabilite a chiffrer |

---

## 17. Integration technique

### 17.1 Fichier `.github/FUNDING.yml`

Ce fichier active le bouton "Sponsor" sur la page du repo GitHub.

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

### 17.2 Metadata PyPI (PEP 753)

L'URL `Funding` dans `[project.urls]` est reconnue par PyPI et affichee
avec une icone coeur/sponsor sur la page du package.

Labels reconnus (insensible a la casse) : `funding`, `sponsor`, `donate`, `donation`.

### 17.3 Fichier CITATION.cff

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

## 18. Checklist de validation

### Etape 1 : GitHub Sponsors
- [ ] Profil GitHub Sponsors cree
- [ ] Choix du beneficiaire : personnel ou SARL (recommande)
- [ ] Stripe Connect configure (compte bancaire LU)
- [ ] Formulaire W-8BEN ou W-8BEN-E rempli (pays : Luxembourg, 0% retenue)
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

### Etape 6 : Expert-comptable
- [ ] Objet social SARL verifie (developpement logiciel couvert)
- [ ] Eligibilite IP Box evaluee
- [ ] Strategie fiscale definie (salaire vs dividendes vs mixte)
- [ ] Documentation R&D mise en place pour le ratio nexus
- [ ] Traitement comptable des dons/sponsorships valide

### Etape 7 : Liberapay (optionnel)
- [ ] Compte cree
- [ ] Stripe connecte (compte LU)
- [ ] Objectif de financement defini

### Etape 8 : CITATION.cff (optionnel)
- [ ] Fichier CITATION.cff cree dans le repo
- [ ] ORCID du mainteneur ajoute

### Etape 9 : Luxinnovation (moyen terme)
- [ ] Eligibilite programmes evaluee
- [ ] Candidature SME Package AI soumise
- [ ] Contact avec conseiller Luxinnovation

---

## 19. Annexe : Sources et references

### Plateformes de dons
- [GitHub Sponsors — Documentation](https://docs.github.com/en/sponsors)
- [Liberapay — FAQ](https://en.liberapay.com/about/faq)
- [Ko-fi — Pricing](https://ko-fi.com/pricing)
- [Polar.sh — Documentation](https://polar.sh/docs/introduction)
- [Thanks.dev](https://thanks.dev/)
- [Open Collective Europe](https://opencollective.com/europe)

### Standards Python
- [PEP 753 — Well-known Project URLs](https://peps.python.org/pep-0753/)
- [pyproject.toml URLs](https://packaging.python.org/en/latest/guides/writing-pyproject-toml/)

### Fiscalite Luxembourg
- [PWC — Luxembourg Individual Taxes](https://taxsummaries.pwc.com/luxembourg/individual/taxes-on-personal-income)
- [PWC — Luxembourg Corporate Taxes](https://taxsummaries.pwc.com/luxembourg/corporate/taxes-on-corporate-income)
- [Taxx.lu — Bareme fiscal Luxembourg](https://taxx.lu/en/tax-return-guide/the-tax-scale-in-luxembourg)
- [EasyBiz — Corporate Tax Luxembourg 2025](https://easybiz.lu/en/blog/luxembourg-corporation-tax)
- [EasyBiz — Independant Luxembourg 2025](https://easybiz.lu/en/blog/how-to-become-self-employed-in-luxembourg)
- [CCSS — Parametres sociaux](https://ccss.public.lu/en/parametres-sociaux.html)

### IP Box Luxembourg
- [The Global Wealth — Luxembourg IP Box Regime](https://theglobalwealth.com/taxes/luxembourg-ip-box)
- [Lexgo — IP Box End of Transition Period](https://www.lexgo.lu/en/news-and-articles/11031-luxembourg-ip-box-tax-regime-end-of-the-transition-period)
- [AVOGAMA — IP Box Regimes Europe](https://avogama-international.com/ip-box-regimes-europe-netherlands-luxembourg-ireland-uk/)
- [Chambers — Corporate Tax 2025 Luxembourg](https://practiceguides.chambers.com/practice-guides/corporate-tax-2025/luxembourg)

### Structures juridiques Luxembourg
- [Guichet.lu — Creation ASBL](https://guichet.public.lu/en/citoyens/loisirs/milieu-associatif/engagement-benevole/creation-asbl.html)
- [Guichet.lu — GIE](https://guichet.public.lu/en/entreprises/creation-developpement/forme-juridique/groupements-association-entreprises/gie.html)
- [Guichet.lu — Fondation](https://guichet.public.lu/en/entreprises/creation-developpement/forme-juridique/fondations/creation-fondation.html)
- [EasyBiz — Creation SARL Luxembourg 2025](https://easybiz.lu/en/blog/creation-sarl-luxembourg)
- [Fiduciaire LPG — Reforme ASBL 2023](https://www.fiduciaire-lpg.lu/en/publications/administrative-law/non-profit-organization-2023-reform)

### Convention fiscale France-Luxembourg
- [Taxx.lu — Nouvelle convention franco-luxembourgeoise](https://taxx.lu/fr/articles/nouvelle-convention-fiscale-franco-luxembourgeoise-ce-qui-change-a-partir-de-2025)
- [KPMG — France-Luxembourg Treaty](https://kpmg.com/xx/en/our-insights/gms-flash-alert/flash-alert-2024-094.html)
- [EasyBiz — Double Tax Treaty Luxembourg](https://easybiz.lu/en/blog/double-tax-treaty-luxembourg)

### Convention US-Luxembourg
- [IRS — Luxembourg Tax Treaty Documents](https://www.irs.gov/businesses/international-businesses/luxembourg-tax-treaty-documents)
- [IRS — W-8BEN Instructions](https://www.irs.gov/instructions/iw8ben)
- [GitHub Sponsors Tax Information](https://docs.github.com/en/sponsors/receiving-sponsorships-through-github-sponsors/tax-information-for-github-sponsors)

### Programmes et aides Luxembourg
- [Luxinnovation](https://luxinnovation.lu/)
- [Luxinnovation — Find Funding](https://luxinnovation.lu/find-funding)
- [SNCI — Rapport annuel 2024](https://www.snci.lu/en/snci-annual-report-2024-stronger-support-for-luxembourg-companies-in-a-challenging-economic-environment/)
- [Luxembourg Trade & Invest — EUR 300M Startup Plan](https://luxembourgtradeandinvest.com/news/%E2%82%AC300-million-and-10-point-plan-to-grow-and-scale-luxembourg%E2%80%99s-startups)
- [Startup Luxembourg](https://startupluxembourg.com/)
- [Startup Luxembourg — AI Factory](https://startupluxembourg.com/news/luxembourg-ai-factory-luxinnovation-as-a-single-point-of-entry)

### Financement academique
- [scikit-learn Funding Model (2024)](https://arxiv.org/html/2404.06484v1)
- [Ten Simple Rules for Funding Scientific OSS](https://pmc.ncbi.nlm.nih.gov/articles/PMC9671312/)
- [University OSPOs (Sloan Foundation)](https://sloan.org/programs/digital-technology/ospo-loi)

### TVA Luxembourg
- [Taxually — Luxembourg VAT Guide 2025](https://www.taxually.com/manuals/luxembourg)
- [RTC Suite — Luxembourg VAT Threshold 2025](https://rtcsuite.com/luxembourgs-vat-registration-threshold-changes-for-2025-what-you-need-to-know/)
