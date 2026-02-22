import streamlit as st
from streamtex import *
import streamtex as stx
from streamtex.styles import Style as ns, StyleGrid as sg
from streamtex.enums import Tags as t, ListTypes as lt
from shared.custom.styles import Styles as s

class BlockStyles:
    """Local styles for this block.
    """
    pass

bs = BlockStyles

def build():
    st_space(size=1)
    st_write(s.project.doc.titles.h1, "1. TABLE OF CONTENT", tag=t.h1, toc_lvl="1")
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_write(s.project.doc.titles.h1, "2. ChatBot Ideas - Administration & Support Services", tag=t.h1, toc_lvl="1")
    st_space(size=1)
    st_write(s.project.doc.titles.h2, "2.1. ChatBot Ideas - Secretariat", tag=t.h2, toc_lvl="+1")
    st_space(size=1)
    st_write(s.project.doc.titles.h3, "2.1.1. Chatbot «Planification de l’Agenda»", tag=t.h3)
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_sm,
                (s.bold, "Expertise A"),
                " : Organisation et priorisation des tâches ",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_sm,
                (s.bold, "Expertise B"),
                " : Coordination d’équipes (gestion des disponibilités, synchronisation d’agendas) ",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_sm,
                (s.bold, "Expertise C"),
                " : Communication écrite (rédaction d’e-mails ou de notes de service pour confirmer un planning) ",
            )
    st_write(
        s.project.doc.paragraphs.p_sm,
        (s.italic, "Première étape"),
        " : S’appuie sur l’organisation des tâches et la coordination d’équipes pour proposer un créneau ou un plan préliminaire.",
        (s.italic, "Deuxième étape"),
        " : Vérifie et ajuste la proposition avec un savoir-faire en communication écrite (envoi d’invitations, confirmation par e-mail, etc.). ",
    )
    st_space(size=1)
    st_write(s.project.doc.titles.h3, "2.1.2. Chatbot «Accueil et Communication Professionnelle»", tag=t.h3)
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_sm,
                (s.bold, "Expertise A"),
                " : Techniques d’accueil (présentiel et téléphonique) ",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_sm,
                (s.bold, "Expertise B"),
                " : Gestion de conflits ou situations délicates (savoir désamorcer, réorienter) ",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_sm,
                (s.bold, "Expertise C"),
                " : Rédaction de scripts ou de guides de réponses (modèles de réponses, FAQ) ",
            )
    st_write(
        s.project.doc.paragraphs.p_sm,
        (s.italic, "Première étape"),
        " : Combine les techniques d’accueil et la gestion de conflits pour fournir une première approche de réponse ou de contact.",
        (s.italic, "Deuxième étape"),
        " : Utilise la rédaction de scripts pour structurer et finaliser la réponse (guide d’accueil, formulations spécifiques). ",
    )
    st_space(size=1)
    st_write(s.project.doc.titles.h3, "2.1.3. Chatbot «Organisateur d’Événements Internes»", tag=t.h3)
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_sm,
                (s.bold, "Expertise A"),
                " : Planification événementielle (réservations, liste de tâches) ",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_sm,
                (s.bold, "Expertise B"),
                " : Gestion logistique (budget, matériel, fournitures) ",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_sm,
                (s.bold, "Expertise C"),
                " : Communication interne (mailings, diffusion d’informations, affichage) ",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_sm,
                (s.bold, "Expertise D"),
                " : Suivi administratif (contrats avec prestataires, validations internes) ",
            )
    st_write(
        s.project.doc.paragraphs.p_sm,
        (s.italic, "Première étape"),
        " : Applique la planification événementielle et la gestion logistique pour établir un plan d’événement.",
        (s.italic, "Deuxième étape"),
        " : Exploite la communication interne et le suivi administratif pour diffuser, officialiser et finaliser la préparation. ",
    )
    st_space(size=1)
    st_write(s.project.doc.titles.h3, "2.1.4. Chatbot «Soutien à la Gestion Documentaire»", tag=t.h3)
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_sm,
                (s.bold, "Expertise A"),
                " : Organisation et classement de documents (procédures, outils de rangement numérique) ",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_sm,
                (s.bold, "Expertise B"),
                " : Conformité légale (respect des normes de confidentialité, durées de conservation) ",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_sm,
                (s.bold, "Expertise C"),
                " : Digitalisation et archivage (conseils d’outils, formatage) ",
            )
    st_write(
        s.project.doc.paragraphs.p_sm,
        (s.italic, "Première étape"),
        " : Combine l’organisation et la conformité légale pour définir un mode de classement initial.",
        (s.italic, "Deuxième étape"),
        " : Déploie la digitalisation et l’archivage, en fonction du plan validé à la première étape. ",
    )
    st_space(size=1)
    st_write(s.project.doc.titles.h3, "2.1.5. Chatbot «Assistant de Gestion Administrative Quotidienne»", tag=t.h3)
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_sm,
                (s.bold, "Expertise A"),
                " : Saisie et mise à jour de bases de données (contact, clients, fournisseurs) ",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_sm,
                (s.bold, "Expertise B"),
                " : Priorisation des demandes administratives (traitement, niveaux d’urgence) ",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_sm,
                (s.bold, "Expertise C"),
                " : Production de documents officiels (modèles, formats, relecture) ",
            )
    st_write(
        s.project.doc.paragraphs.p_sm,
        (s.italic, "Première étape"),
        " : Utilise la saisie de bases de données et la priorisation pour proposer un ordre de traitement des demandes.",
        (s.italic, "Deuxième étape"),
        " : Génère ou met à jour les documents adéquats grâce à l’expertise de production documentaire. ",
    )
    st_space(size=1)
    st_write(s.project.doc.titles.h3, "2.1.6. Chatbot «Assistant de Communication Écrite»", tag=t.h3)
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_sm,
                (s.bold, "Expertise A"),
                " : Rédaction de mails et courriers formels (structure, langage professionnel) ",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_sm,
                (s.bold, "Expertise B"),
                " : Orthographe et grammaire (vérifications linguistiques) ",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_sm,
                (s.bold, "Expertise C"),
                " : Adaptation du ton et du style (selon le destinataire, la culture d’entreprise) ",
            )
    st_write(
        s.project.doc.paragraphs.p_sm,
        (s.italic, "Première étape"),
        " : Combine la rédaction de mails formels et la correction linguistique pour proposer un premier brouillon de texte.",
        (s.italic, "Deuxième étape"),
        " : Ajuste ton et style selon le contexte ou le type de destinataire. ",
    )
    st_space(size=1)
    st_write(s.project.doc.titles.h3, "2.1.7. Chatbot «Coordinateur de Réunions et Comptes Rendus»", tag=t.h3)
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_sm,
                (s.bold, "Expertise A"),
                " : Identification d’objectifs et d’ordre du jour (quelle réunion, pour quel besoin) ",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_sm,
                (s.bold, "Expertise B"),
                " : Gestion du temps en réunion (techniques d’animation, respect du timing) ",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_sm,
                (s.bold, "Expertise C"),
                " : Rédaction de comptes rendus (synthèse, mise en forme, diffusion) ",
            )
    st_write(
        s.project.doc.paragraphs.p_sm,
        (s.italic, "Première étape"),
        " : Croise la définition d’objectifs et la gestion du temps pour préparer la réunion.",
        (s.italic, "Deuxième étape"),
        " : Utilise l’expertise en rédaction de comptes rendus pour documenter et diffuser le résultat. ",
    )
    st_space(size=1)
    st_write(s.project.doc.titles.h3, "2.1.8. Chatbot «Gestionnaire de Fournitures et Stocks»", tag=t.h3)
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_sm,
                (s.bold, "Expertise A"),
                " : Inventaire et suivi de stocks (entrées, sorties, niveaux de réserve) ",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_sm,
                (s.bold, "Expertise B"),
                " : Optimisation des coûts (comparer fournisseurs, négocier tarifs) ",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_sm,
                (s.bold, "Expertise C"),
                " : Gestion administrative des commandes (bons de commande, factures, relances) ",
            )
    st_write(
        s.project.doc.paragraphs.p_sm,
        (s.italic, "Première étape"),
        " : Évalue l’état du stock et propose une solution d’optimisation (réapprovisionnement, budget).",
        (s.italic, "Deuxième étape"),
        " : Génère ou coordonne la passation de commandes et le suivi administratif afférent. ",
    )
    st_space(size=1)
    st_write(s.project.doc.titles.h3, "2.1.9. Chatbot «Analyste de Présentations et Rapports»", tag=t.h3)
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_sm,
                (s.bold, "Expertise A"),
                " : Structuration de présentations (plan, fil conducteur) ",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_sm,
                (s.bold, "Expertise B"),
                " : Visuels et supports (choix d’infographies, supports adaptés) ",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_sm,
                (s.bold, "Expertise C"),
                " : Relecture critique et amélioration du contenu (cohérence, clarté, style) ",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_sm,
                (s.bold, "Expertise D"),
                " : Adaptation à l’audience (type d’informations, terminologie) ",
            )
    st_write(
        s.project.doc.paragraphs.p_sm,
        (s.italic, "Première étape"),
        " : Exploite la structuration et le choix des visuels pour concevoir une première mouture.",
        (s.italic, "Deuxième étape"),
        " : Applique la relecture critique et l’adaptation à l’audience pour peaufiner la présentation finale. ",
    )
    st_space(size=1)
    st_write(s.project.doc.titles.h3, "2.1.10. Chatbot «Support de Ressources Humaines Simplifié»", tag=t.h3)
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_sm,
                (s.bold, "Expertise A"),
                " : Information sur les procédures internes RH (congés, absences, demandes diverses) ",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_sm,
                (s.bold, "Expertise B"),
                " : Gestion de la communication confidentielle (respect de la vie privée, formulation) ",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_sm,
                (s.bold, "Expertise C"),
                " : Coordination avec les responsables (quand escalader une question, comment organiser un suivi) ",
            )
    st_write(
        s.project.doc.paragraphs.p_sm,
        (s.italic, "Première étape"),
        " : Combine le partage d’informations RH de base et la gestion de la confidentialité pour répondre à une question initiale.",
        (s.italic, "Deuxième étape"),
        " : Mobilise la coordination avec les responsables pour finaliser la solution ou l’action à entreprendre (par exemple, planifier un entretien ou un suivi). ",
    )
    st_space(size=1)
    st_write(s.project.doc.titles.h2, "2.2. ChatBot Ideas - Ressources Humaines", tag=t.h2, toc_lvl="+1")
    st_space(size=1)
    st_write(s.project.doc.titles.h3, "2.2.1. Chatbot « Talent Scout »", tag=t.h3)
    st_write(s.project.doc.paragraphs.p_body + s.bold, "Expertises : ")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Rédaction d’offres d’emploi"),
                " (rédaction claire, accrocheuse et conforme aux réglementations).",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Analyse de CV"),
                " (extraction et classement des compétences pertinentes).",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Guidage pour les entretiens"),
                " (conseils sur les questions à poser et les points à vérifier).",
            )
    st_write(s.project.doc.paragraphs.p_body, "Petit scénario d’illustration")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Données spécifiques fournies à l’assistant"),
                "- Un ensemble de profils de candidats ainsi qu’une description détaillée du poste (missions, compétences requises, salaire proposé).",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Exemple de question"),
                (s.italic, "« Peux-tu me proposer une offre d’emploi attrayante pour un poste de Développeur Web junior, et me suggérer les critères de sélection prioritaires pour filtrer les CV ? » "),
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Exemple de réponse"),
                (s.italic, "Le Chatbot rédige l’offre d’emploi et identifie les principaux mots-clés. Il propose ensuite une courte grille d’évaluation pour trier les CV en fonction des compétences en front-end, back-end et des soft skills recherchées. Enfin, il explique comment, lors de l’entretien, valider les motivations et la capacité d’adaptation du candidat. "),
            )
    st_space(size=1)
    st_write(s.project.doc.titles.h3, "2.2.2. Chatbot « Onboarding Buddy »", tag=t.h3)
    st_write(s.project.doc.paragraphs.p_body + s.bold, "Expertises : ")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Gestion de l’intégration des nouveaux employés"),
                " (plan d’accueil et checklist administrative).",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Communication interculturelle"),
                " (conseils pour faciliter la collaboration avec différentes équipes).",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Création d’un parcours d’accueil personnalisé"),
                " (activités et ressources adaptées pour le poste concerné).",
            )
    st_write(s.project.doc.paragraphs.p_body, "Petit scénario d’illustration")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Données spécifiques fournies à l’assistant"),
                "- Politique interne d’onboarding (documents à transmettre, formations obligatoires), organigramme de l’entreprise.",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Exemple de question"),
                (s.italic, "« Pour un nouveau Commercial international, comment structurer ses premiers jours afin de le familiariser avec les équipes basées dans différents pays ? » "),
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Exemple de réponse"),
                (s.italic, "Le Chatbot génère un plan d’accueil (RDV clés, documents à consulter) et intègre quelques conseils interculturels pour travailler avec les filiales. Ensuite, il propose un parcours d’accueil personnalisé, incluant une visite virtuelle des sites étrangers et des séances de mentoring. "),
            )
    st_space(size=1)
    st_write(s.project.doc.titles.h3, "2.2.3. Chatbot « Payroll Pal »", tag=t.h3)
    st_write(s.project.doc.paragraphs.p_body + s.bold, "Expertises : ")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Calcul de la paie"),
                " (prise en compte des taux, heures supplémentaires, primes).",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Gestion des avantages sociaux"),
                " (assurances, plans de retraite, mutuelles).",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Vérification de la conformité légale"),
                " (respect des réglementations sur le salaire minimal et cotisations sociales).",
            )
    st_write(s.project.doc.paragraphs.p_body, "Petit scénario d’illustration")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Données spécifiques fournies à l’assistant"),
                "- Taux horaires des employés, règles d’attribution des primes, barèmes de cotisation.",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Exemple de question"),
                (s.italic, "« Comment calculer la paie d’un employé à temps partiel qui a effectué 10 heures supplémentaires ce mois-ci, et quels avantages ajouter à son bulletin ? » "),
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Exemple de réponse"),
                (s.italic, "Le Chatbot fournit d’abord un calcul détaillé (salaires de base + heures supplémentaires majorées). Ensuite, il contrôle la conformité aux règles légales et propose l’ajout ou la modification de certains avantages en fonction de la politique interne et de la situation de l’employé. "),
            )
    st_space(size=1)
    st_write(s.project.doc.titles.h3, "2.2.4. Chatbot « Performance Evaluator »", tag=t.h3)
    st_write(s.project.doc.paragraphs.p_body + s.bold, "Expertises : ")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Mise en place d’indicateurs de performance"),
                " (KPI, objectifs qualitatifs).",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Collecte et analyse de feedback"),
                " (méthodes pour recueillir et structurer les retours).",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Conseils pour l’entretien annuel"),
                " (recommandations d’évaluation et plan de développement).",
            )
    st_write(s.project.doc.paragraphs.p_body, "Petit scénario d’illustration")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Données spécifiques fournies à l’assistant"),
                "- Grille d’évaluation interne, historique de performance sur l’année écoulée, feedbacks collectés auprès de managers.",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Exemple de question"),
                (s.italic, "« Comment évaluer objectivement un employé qui travaille en mode hybride (télétravail + présentiel) sur les projets transverses ? » "),
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Exemple de réponse"),
                (s.italic, "Le Chatbot propose des indicateurs de performance spécifiques (implication dans les projets, respect des délais, collaboration à distance), puis suggère une manière de récolter des feedbacks auprès des équipes. Enfin, il explique comment structurer l’entretien annuel avec des questions pertinentes et un plan de développement individuel. "),
            )
    st_space(size=1)
    st_write(s.project.doc.titles.h3, "2.2.5. Chatbot « Formation Planner »", tag=t.h3)
    st_write(s.project.doc.paragraphs.p_body + s.bold, "Expertises : ")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Identification des besoins de formation"),
                " (analyse des écarts de compétences).",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Sélection des programmes de formation"),
                " (formats, durées, ressources internes ou externes).",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Évaluation du retour sur investissement (ROI) des formations"),
                " (mesure d’impact, satisfaction).",
            )
    st_write(s.project.doc.paragraphs.p_body, "Petit scénario d’illustration")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Données spécifiques fournies à l’assistant"),
                "- Liste des compétences actuelles et requises à moyen terme, catalogue de formations disponibles en interne et externe.",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Exemple de question"),
                (s.italic, "« L’équipe Support client doit améliorer sa gestion des situations conflictuelles ; quelles formations conseiller et comment mesurer l’efficacité de ces formations ? » "),
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Exemple de réponse"),
                (s.italic, "Le Chatbot propose d’abord une analyse rapide des écarts de compétences et sélectionne deux formations en gestion de conflit et communication. Ensuite, il décrit un plan de suivi post-formation (indicateurs de satisfaction, réduction du taux de réclamations) pour prouver l’impact sur la performance. "),
            )
    st_space(size=1)
    st_write(s.project.doc.titles.h3, "2.2.6. Chatbot « Internal Mobility Mentor »", tag=t.h3)
    st_write(s.project.doc.paragraphs.p_body + s.bold, "Expertises : ")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Analyse de la mobilité interne"),
                " (recensement des postes vacants et compétences associées).",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Matching profil/poste"),
                " (propositions d’évolution pour les employés).",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Accompagnement du changement de poste"),
                " (planning de transition, conseils de gestion de carrière).",
            )
    st_write(s.project.doc.paragraphs.p_body, "Petit scénario d’illustration")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Données spécifiques fournies à l’assistant"),
                "- Historique des postes occupés, aspirations des salariés, postes disponibles dans l’entreprise.",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Exemple de question"),
                (s.italic, "« Plusieurs collaborateurs souhaitent évoluer vers des responsabilités managériales. Comment identifier les opportunités internes et les accompagner au mieux ? » "),
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Exemple de réponse"),
                (s.italic, "Le Chatbot recense les postes managériaux vacants et compare les profils des collaborateurs. Puis, il suggère un plan de transition (formation, mentoring) pour passer d’un poste technique à un poste managérial, incluant un calendrier et les ressources nécessaires. "),
            )
    st_space(size=1)
    st_write(s.project.doc.titles.h3, "2.2.7. Chatbot « Social Dialogue Facilitator »", tag=t.h3)
    st_write(s.project.doc.paragraphs.p_body + s.bold, "Expertises : ")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Gestion des relations avec les représentants du personnel"),
                " (communication structurée, planification des réunions).",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Prévention et résolution des conflits"),
                " (médiation, proposition d’accords).",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Veille juridique en droit du travail"),
                " (mise à jour des réglementations, vérification de conformité).",
            )
    st_write(s.project.doc.paragraphs.p_body, "Petit scénario d’illustration")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Données spécifiques fournies à l’assistant"),
                "- Historique des dernières négociations avec les syndicats, principales revendications en cours, textes de loi à jour.",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Exemple de question"),
                (s.italic, "« Comment préparer la prochaine réunion avec les représentants du personnel pour discuter d’une nouvelle charte télétravail ? » "),
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Exemple de réponse"),
                (s.italic, "Le Chatbot propose d’abord une checklist de points à aborder, identifie les aspects légaux à respecter (durée légale de travail, obligations de l’employeur), puis fournit quelques pistes de médiation pour concilier intérêts de l’employeur et des salariés. "),
            )
    st_space(size=1)
    st_write(s.project.doc.titles.h3, "2.2.8. Chatbot « Legal Compliance Guardian »", tag=t.h3)
    st_write(s.project.doc.paragraphs.p_body + s.bold, "Expertises : ")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Suivi de la réglementation du travail"),
                " (exigences légales, obligations déclaratives).",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Vérification des contrats et des clauses"),
                " (conformité, clauses abusives).",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Préparation de documents officiels"),
                " (avenants, comptes rendus, notifications légales).",
            )
    st_write(s.project.doc.paragraphs.p_body, "Petit scénario d’illustration")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Données spécifiques fournies à l’assistant"),
                "- Modèles de contrats existants, mise à jour des lois locales et directives internes sur la rédaction contractuelle.",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Exemple de question"),
                (s.italic, "« Nous devons rédiger un avenant au contrat d’un employé pour inclure une nouvelle prime annuelle ; comment respecter les obligations légales ? » "),
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Exemple de réponse"),
                (s.italic, "Le Chatbot contrôle d’abord la rédaction proposée (clauses de non-concurrence, primes, durée du travail), puis vérifie la conformité avec la législation en vigueur. Enfin, il fournit un modèle d’avenant conforme et un récapitulatif des démarches à effectuer (signature, envoi, etc.). "),
            )
    st_space(size=1)
    st_write(s.project.doc.titles.h3, "2.2.9. Chatbot « Conflict Resolutor »", tag=t.h3)
    st_write(s.project.doc.paragraphs.p_body + s.bold, "Expertises : ")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Analyse de situation conflictuelle"),
                " (identification des causes, acteurs impliqués).",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Propositions de médiation"),
                " (techniques et étapes pour réduire la tension).",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Suivi post-conflit"),
                " (évaluation de la résolution et prévention de récidives).",
            )
    st_write(s.project.doc.paragraphs.p_body, "Petit scénario d’illustration")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Données spécifiques fournies à l’assistant"),
                "- Détails d’un conflit interne entre deux équipes (causes, historique, tentatives précédentes).",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Exemple de question"),
                (s.italic, "« Deux équipes se disputent la répartition des tâches sur un projet ; comment structurer une réunion de médiation pour résoudre ce conflit rapidement ? » "),
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Exemple de réponse"),
                (s.italic, "Le Chatbot évalue d’abord les causes profondes (charge de travail, manque de clarté sur les rôles). Ensuite, il propose une méthodologie de médiation (neutralité, écoute active, arbitrage). Enfin, il planifie un suivi post-conflit pour vérifier la bonne application des engagements pris. "),
            )
    st_space(size=1)
    st_write(s.project.doc.titles.h3, "2.2.10. Chatbot « Career Development Coach »", tag=t.h3)
    st_write(s.project.doc.paragraphs.p_body + s.bold, "Expertises : ")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Gestion des plans de carrière"),
                " (définition d’objectifs à moyen et long terme).",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Accompagnement à la mobilité externe"),
                " (conseils CV, préparation aux entretiens).",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Coaching professionnel"),
                " (conseils de posture, amélioration continue des soft skills).",
            )
    st_write(s.project.doc.paragraphs.p_body, "Petit scénario d’illustration")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Données spécifiques fournies à l’assistant"),
                "- Informations sur les ambitions d’un collaborateur, historique de son parcours, offres internes ou possibilités externes identifiées.",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Exemple de question"),
                (s.italic, "« Un employé envisage de quitter l’entreprise pour un poste plus stratégique ailleurs. Comment l’aider à clarifier son projet et à se préparer au mieux ? » "),
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Exemple de réponse"),
                (s.italic, "Le Chatbot propose d’abord des objectifs de carrière et suggère quelques pistes de postes en interne si possible. Il fournit ensuite des conseils de relecture de CV, de pitch d’entretien, et enfin un plan de coaching professionnel avec exercices pour développer des compétences transverses. "),
            )
    st_space(size=1)
    st_space(size=1)
    st_write(s.project.doc.titles.h2, "2.3. ChatBot Ideas - Juridique", tag=t.h2, toc_lvl="+1")
    st_space(size=1)
    st_write(s.project.doc.titles.h3, "2.3.1. ChatBot « Conseil Social & Contrats de Travail »", tag=t.h3)
    st_write(s.project.doc.paragraphs.p_body + s.bold, "Expertises : ")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(s.bold, "Groupe 1 : ")
        with lst.item():
            pass
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Groupe 2 :"),
                "3. ",
                (s.bold, "Ajustement final selon la réglementation en vigueur"),
                " (ex. validation de la conformité du contrat, des périodes d’essai, etc.)",
            )
    st_write(s.project.doc.paragraphs.p_body + s.bold, "Illustration d’un scénario concret : ")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Données spécifiques fournies au ChatBot :"),
                " un descriptif du poste à pourvoir, le profil du salarié, la convention collective applicable et les conditions souhaitées (période d’essai, salaire, durée de travail).",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Exemple de question :"),
                " « Comment rédiger une clause de non-concurrence dans ce contrat de travail pour un développeur logiciel, en respectant la convention collective du numérique ? »",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Exemple de réponse :"),
                " Le ChatBot analyse d’abord le cadre social et la convention pour suggérer des éléments de clause (délimitation géographique, durée, indemnisation). Ensuite, il fournit un modèle de formulation finalisé conforme à la réglementation locale.",
            )
    st_space(size=1)
    st_write(s.project.doc.titles.h3, "2.3.2. ChatBot « Assistant en Clauses Commerciales & Mise en Conformité »", tag=t.h3)
    st_write(s.project.doc.paragraphs.p_body + s.bold, "Expertises : ")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(s.bold, "Groupe 1 : ")
        with lst.item():
            pass
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Groupe 2 :"),
                "3. ",
                (s.bold, "Vérification réglementaire"),
                " (ex. contrôle de la licéité des clauses, validation des obligations d’information)4. ",
                (s.bold, "Conseil de mise en conformité"),
                " (ex. liste des documents et démarches complémentaires à effectuer)",
            )
    st_write(s.project.doc.paragraphs.p_body + s.bold, "Illustration d’un scénario concret : ")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Données spécifiques fournies au ChatBot :"),
                " historique de négociations, versions antérieures du contrat, dispositions légales pertinentes sur la vente de services en ligne.",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Exemple de question :"),
                " « Quels ajustements apporter aux clauses de résiliation pour être conforme à la législation sur l’e-commerce en Europe ? »",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Exemple de réponse :"),
                " Le ChatBot propose, en première étape, plusieurs formulations de clauses conformes aux objectifs commerciaux. Puis, il valide la légalité des modifications et émet un avis sur les obligations d’information précontractuelle et le droit de rétractation.",
            )
    st_space(size=1)
    st_write(s.project.doc.titles.h3, "2.3.3. ChatBot « Gestion des Contentieux & Médiation »", tag=t.h3)
    st_write(s.project.doc.paragraphs.p_body + s.bold, "Expertises : ")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(s.bold, "Groupe 1 : ")
        with lst.item():
            pass
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Groupe 2 :"),
                "3. ",
                (s.bold, "Stratégie de médiation ou de règlement amiable"),
                " (ex. formulation de compromis, plan d’actions pour éviter la procédure judiciaire)",
            )
    st_write(s.project.doc.paragraphs.p_body + s.bold, "Illustration d’un scénario concret : ")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Données spécifiques fournies au ChatBot :"),
                " copie d’échanges d’emails entre les parties en conflit, clauses pertinentes du contrat litigieux, historique du différend.",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Exemple de question :"),
                " « Comment puis-je entamer une médiation avec notre fournisseur pour éviter d’aller en justice, sachant que la clause de médiation n’est pas prévue dans notre contrat actuel ? »",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Exemple de réponse :"),
                " Le ChatBot examine les éléments du dossier et propose des arguments solides pour engager une discussion amiable. Il suggère ensuite une stratégie de médiation, incluant la rédaction d’un protocole d’accord provisoire.",
            )
    st_space(size=1)
    st_write(s.project.doc.titles.h3, "2.3.4. ChatBot « Analyse de Risques Juridiques & Prévention des Litiges »", tag=t.h3)
    st_write(s.project.doc.paragraphs.p_body + s.bold, "Expertises : ")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(s.bold, "Groupe 1 : ")
        with lst.item():
            pass
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Groupe 2 :"),
                "3. ",
                (s.bold, "Recommandations de prévention"),
                " (ex. actions internes, modifications contractuelles, procédures de suivi)",
            )
    st_write(s.project.doc.paragraphs.p_body + s.bold, "Illustration d’un scénario concret : ")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Données spécifiques fournies au ChatBot :"),
                " liste de contrats en cours, points de désaccord potentiels déjà identifiés, retours d’expérience sur des litiges passés.",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Exemple de question :"),
                " « Quels sont les principaux risques juridiques liés à nos contrats fournisseurs internationaux et comment les prévenir ? »",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Exemple de réponse :"),
                " Le ChatBot identifie la présence de clauses ambiguës sur la juridiction compétente et les pénalités de retard. Ensuite, il propose d’ajouter des avenants clarifiant les obligations et de mettre en place un calendrier de suivi pour réduire le risque de litiges.",
            )
    st_space(size=1)
    st_write(s.project.doc.titles.h3, "2.3.5. ChatBot « Support de Conformité RGPD »", tag=t.h3)
    st_write(s.project.doc.paragraphs.p_body + s.bold, "Expertises : ")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(s.bold, "Groupe 1 : ")
        with lst.item():
            pass
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Groupe 2 :"),
                "3. ",
                (s.bold, "Recommandations de mise en conformité RGPD"),
                " (ex. modifications des documents internes, mentions légales, formation du personnel)",
            )
    st_write(s.project.doc.paragraphs.p_body + s.bold, "Illustration d’un scénario concret : ")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Données spécifiques fournies au ChatBot :"),
                " description complète de l’outil collectant les données, politiques internes de confidentialité, liste des partenaires traitant les données.",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Exemple de question :"),
                " « Quelles sont les actions prioritaires pour rendre notre processus d’inscription en ligne conforme au RGPD ? »",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Exemple de réponse :"),
                " Le ChatBot identifie d’abord l’usage des données (nom, email, localisation). Il évalue ensuite les mesures de protection et propose de réviser la charte de confidentialité, de mettre en place un consentement explicite et de renforcer les droits d’accès et de suppression.",
            )
    st_space(size=1)
    st_write(s.project.doc.titles.h3, "2.3.6. ChatBot « Suivi des Échéances Contractuelles & Renouvellements »", tag=t.h3)
    st_write(s.project.doc.paragraphs.p_body + s.bold, "Expertises : ")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(s.bold, "Groupe 1 : ")
        with lst.item():
            pass
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Groupe 2 :"),
                "3. ",
                (s.bold, "Proposition de renégociation ou mise à jour contractuelle"),
                " (ex. conseils sur l’ajustement des conditions, clauses supplémentaires)",
            )
    st_write(s.project.doc.paragraphs.p_body + s.bold, "Illustration d’un scénario concret : ")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Données spécifiques fournies au ChatBot :"),
                " base de données de tous les contrats fournisseurs et clients, dates de signature et options de renouvellement.",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Exemple de question :"),
                " « Quels contrats arrivent à échéance dans les 60 prochains jours et quelles actions devrions-nous entreprendre pour chacun ? »",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Exemple de réponse :"),
                " Le ChatBot liste les contrats concernés, indique les démarches requises (envoyer un courrier, négocier une clause de renouvellement) et fournit des conseils pour optimiser la négociation avant la reconduction.",
            )
    st_space(size=1)
    st_write(s.project.doc.titles.h3, "2.3.7. ChatBot « Formation & Sensibilisation Juridique Interne »", tag=t.h3)
    st_write(s.project.doc.paragraphs.p_body + s.bold, "Expertises : ")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(s.bold, "Groupe 1 : ")
        with lst.item():
            pass
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Groupe 2 :"),
                "3. ",
                (s.bold, "Adaptation aux besoins spécifiques de l’entreprise"),
                " (ex. intégration de cas concrets internes, mise à jour du support en fonction des retours d’expérience)",
            )
    st_write(s.project.doc.paragraphs.p_body + s.bold, "Illustration d’un scénario concret : ")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Données spécifiques fournies au ChatBot :"),
                " politique interne de conformité, obligations légales clés, exemples d’erreurs récurrentes commises par les employés.",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Exemple de question :"),
                " « Comment puis-je former rapidement les nouvelles recrues sur les bonnes pratiques légales liées aux contrats de travail et à la protection des données ? »",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Exemple de réponse :"),
                " Le ChatBot propose un plan de formation en plusieurs modules, dont un quiz sur la protection des données. Il effectue ensuite une relecture finale pour vérifier la cohérence juridique et suggère d’ajouter des exemples issus des litiges internes passés.",
            )
    st_space(size=1)
    st_write(s.project.doc.titles.h3, "2.3.8. ChatBot « Audit de Conformité Globale »", tag=t.h3)
    st_write(s.project.doc.paragraphs.p_body + s.bold, "Expertises : ")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(s.bold, "Groupe 1 : ")
        with lst.item():
            pass
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Groupe 2 :"),
                "3. ",
                (s.bold, "Plan d’action d’amélioration"),
                " (ex. révision de certaines procédures, formation ciblée, nouvelles politiques internes)4. ",
                (s.bold, "Suivi et évaluation périodique"),
                " (ex. indicateurs de performance, tableau de bord de conformité)",
            )
    st_write(s.project.doc.paragraphs.p_body + s.bold, "Illustration d’un scénario concret : ")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Données spécifiques fournies au ChatBot :"),
                " organigramme complet de l’entreprise, manuel des procédures internes, principales normes (ISO, lois nationales) à respecter.",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Exemple de question :"),
                " « Quelles sont les étapes prioritaires pour mettre à jour notre manuel des procédures internes selon la nouvelle réglementation nationale ? »",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Exemple de réponse :"),
                " Le ChatBot identifie d’abord les processus sensibles (gestion des données clients, procédures d’embauche). Il dresse ensuite un plan d’action, incluant la mise à jour des sections concernées, la formation du personnel et la mise en place d’un tableau de suivi.",
            )
    st_space(size=1)
    st_write(s.project.doc.titles.h3, "2.3.9. ChatBot « Support Contentieux Employeur-Salarié »", tag=t.h3)
    st_write(s.project.doc.paragraphs.p_body + s.bold, "Expertises : ")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(s.bold, "Groupe 1 : ")
        with lst.item():
            pass
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Groupe 2 :"),
                "3. ",
                (s.bold, "Propositions d’accord amiable ou procédure disciplinaire"),
                " (ex. médiation interne, clauses de transaction, obligations formelles)",
            )
    st_write(s.project.doc.paragraphs.p_body + s.bold, "Illustration d’un scénario concret : ")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Données spécifiques fournies au ChatBot :"),
                " contrat de travail concerné, relevés de pointage, mails échangés, règlement intérieur.",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Exemple de question :"),
                " « Quelle stratégie adopter pour résoudre un litige relatif à un licenciement contesté par le salarié ? »",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Exemple de réponse :"),
                " Le ChatBot identifie les éventuelles irrégularités dans la procédure de licenciement. Il suggère d’abord une négociation amiable avec indemnités, puis détaille la procédure disciplinaire si aucun accord n’est trouvé.",
            )
    st_space(size=1)
    st_write(s.project.doc.titles.h3, "2.3.10. ChatBot « Veille Juridique & Alertes Réglementaires »", tag=t.h3)
    st_write(s.project.doc.paragraphs.p_body + s.bold, "Expertises : ")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(s.bold, "Groupe 1 : ")
        with lst.item():
            pass
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Groupe 2 :"),
                "3. ",
                (s.bold, "Aide à la mise en œuvre interne"),
                " (ex. checklist d’adaptation des contrats et processus internes)",
            )
    st_write(s.project.doc.paragraphs.p_body + s.bold, "Illustration d’un scénario concret : ")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Données spécifiques fournies au ChatBot :"),
                " liens vers des bases de données juridiques internes, liste des lois et règlements prioritaires, politiques internes à jour.",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Exemple de question :"),
                " « Quels sont les changements apportés par la dernière réforme sur le droit du travail, et comment devons-nous adapter nos contrats de travail ? »",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Exemple de réponse :"),
                " Le ChatBot recense les points clés de la réforme (durée maximale des CDD, calcul des indemnités). Il propose ensuite une liste d’actions, comme modifier les clauses standard et informer rapidement le service RH pour l’application concrète.",
            )
    st_space(size=1)
    st_space(size=1)
    st_write(s.project.doc.titles.h2, "2.4. ChatBot Ideas - Service Client", tag=t.h2, toc_lvl="+1")
    st_space(size=1)
    st_write(s.project.doc.titles.h3, "2.4.1. ChatBot « FAQ & Personnalisation »", tag=t.h3)
    st_space(size=1)
    st_write(s.project.doc.paragraphs.p_body, "Expertises")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Recherche dans la FAQ"),
                " (Première étape)Analyse la question pour identifier la section de la FAQ correspondante et proposer une réponse automatisée.",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Analyse du contexte utilisateur"),
                " (Première étape)Vérifie le statut client (nouveau client, client premium, etc.) et ajuste la réponse issue de la FAQ pour la rendre plus pertinente.",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Suggestions de réponses personnalisées"),
                " (Deuxième étape)Après la première réponse, affine la recommandation selon l’historique d’achat ou les interactions récentes du client.",
            )
    st_write(s.project.doc.paragraphs.p_body, "Scénario d’illustration")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Données spécifiques fournies à l’assistant intelligent"),
                " : Liste des articles de la FAQ, base de données clients avec historique d’achats et statut du compte.",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Exemple de question posée"),
                " : « Mon colis est indiqué livré, mais je ne l’ai pas reçu, que dois-je faire ? »",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Exemple de réponse du ChatBot"),
                " :",
            )
        with lst.item():
            pass
    st_space(size=1)
    st_write(s.project.doc.titles.h3, "2.4.2. ChatBot « Diagnostic Rapide & Redirection Technique »", tag=t.h3)
    st_space(size=1)
    st_write(s.project.doc.paragraphs.p_body, "Expertises")
    st_space(size=1)
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Identification du problème"),
                " (Première étape)Pose des questions ciblées pour comprendre le type de dysfonctionnement ou de demande.",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Proposition de dépannage simple"),
                " (Première étape)Offre des étapes de base pour résoudre les problèmes courants (redémarrage, vérification de paramètres, etc.).",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Escalade vers assistance avancée"),
                " (Deuxième étape)Si le problème persiste, oriente vers un service spécialisé ou envoie un ticket au support technique niveau 2.",
            )
    st_write(s.project.doc.paragraphs.p_body, "Scénario d’illustration")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Données spécifiques fournies à l’assistant intelligent"),
                " : Liste des problèmes techniques connus, procédures de dépannage de base, lien avec le système de tickets de support avancé.",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Exemple de question posée"),
                " : « Mon logiciel se ferme tout seul dès que je lance une impression, comment régler ça ? »",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Exemple de réponse du ChatBot"),
                " :",
            )
        with lst.item():
            pass
    st_space(size=1)
    st_write(s.project.doc.titles.h3, "2.4.3. ChatBot « Analyse de Sentiments & Proposition de Compensations »", tag=t.h3)
    st_space(size=1)
    st_write(s.project.doc.paragraphs.p_body, "Expertises")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Analyse sémantique de la requête client"),
                " (Première étape)Détecte l’émotion (colère, frustration, satisfaction) et l’importance du problème rapporté.",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Réponse empathique de premier niveau"),
                " (Première étape)Adapte la formulation initiale pour apaiser l’émotion ressentie.",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Proposition de geste commercial"),
                " (Deuxième étape)Après la réponse de premier niveau, propose un geste ou une compensation (réduction, avoir, cadeau) en fonction de l’historique client et de la gravité de la situation.",
            )
    st_write(s.project.doc.paragraphs.p_body, "Scénario d’illustration")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Données spécifiques fournies à l’assistant intelligent"),
                " : Historique de satisfaction client, règles de gestions commerciales (remises possibles, seuils pour compensations).",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Exemple de question posée"),
                " : « Je suis vraiment déçu, j’ai contacté le service quatre fois et personne ne m’a aidé ! »",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Exemple de réponse du ChatBot"),
                " :",
            )
        with lst.item():
            pass
    st_space(size=1)
    st_write(s.project.doc.titles.h3, "2.4.4. ChatBot « Classement des Retours & Reporting en Direct »", tag=t.h3)
    st_space(size=1)
    st_write(s.project.doc.paragraphs.p_body, "Expertises")
    st_space(size=1)
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Tag des demandes clients"),
                " (Première étape)Classe automatiquement chaque demande dans une catégorie (bug, question de facturation, demande d’information, etc.).",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Analyse de volume et tendances immédiates"),
                " (Première étape)Regroupe en temps réel les thématiques principales et détecte les pics de requêtes similaires.",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Génération de rapport simplifié"),
                " (Deuxième étape)Compile les informations collectées pour générer un compte-rendu ou un tableau de bord automatique.",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Recommandation d’actions"),
                " (Deuxième étape, optionnelle)Propose des pistes d’amélioration ou d’ajustement du service en fonction des tendances détectées.",
            )
    st_write(s.project.doc.paragraphs.p_body, "Scénario d’illustration")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Données spécifiques fournies à l’assistant intelligent"),
                " : Historique des conversations, catégories de tickets, règles de reporting interne.",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Exemple de question posée"),
                " : « Peux-tu me dire quelles sont les principales demandes en cours sur le service chat ? »",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Exemple de réponse du ChatBot"),
                " :",
            )
        with lst.item():
            pass
    st_space(size=1)
    st_write(s.project.doc.titles.h3, "2.4.5. ChatBot « Création d’Articles d’Aide & Révision Qualité »", tag=t.h3)
    st_space(size=1)
    st_write(s.project.doc.paragraphs.p_body, "Expertises")
    st_space(size=1)
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Extraction de contenu clé"),
                " (Première étape)Analyse les questions fréquentes pour extraire le contenu récurrent et repérer les lacunes de la base de connaissances.",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Génération automatique d’ébauches d’articles d’aide"),
                " (Première étape)Propose des versions initiales d’articles ou de tutos sur la base des besoins identifiés.",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Révision qualité et mise en forme"),
                " (Deuxième étape)Relit et reformule le contenu pour assurer une cohérence de style et une bonne lisibilité avant publication.",
            )
    st_write(s.project.doc.paragraphs.p_body, "Scénario d’illustration")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Données spécifiques fournies à l’assistant intelligent"),
                " : Historique des questions posées par les clients, guidelines internes pour la rédaction de contenus d’aide.",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Exemple de question posée"),
                " : « Comment résoudre un problème de mot de passe oublié sur l’appli mobile ? »",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Exemple de réponse du ChatBot"),
                " :",
            )
        with lst.item():
            pass
    st_space(size=1)
    st_write(s.project.doc.titles.h3, "2.4.6. ChatBot « Suivi des Commandes & Aide Live »", tag=t.h3)
    st_space(size=1)
    st_write(s.project.doc.paragraphs.p_body, "Expertises")
    st_space(size=1)
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Localisation de commande en temps réel"),
                " (Première étape)Interroge les systèmes logistiques pour donner le statut précis d’un colis ou d’une commande.",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Rappel du parcours client"),
                " (Première étape)Vérifie si le client a déjà contacté le support pour la même commande.",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Assistance en direct"),
                " (Deuxième étape)En fonction des informations recueillies (retard, problème de suivi), propose de contacter le transporteur ou de reprogrammer la livraison.",
            )
    st_write(s.project.doc.paragraphs.p_body, "Scénario d’illustration")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Données spécifiques fournies à l’assistant intelligent"),
                " : Système interne de tracking logistique, historique de contacts pour la commande en cours.",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Exemple de question posée"),
                " : « Où en est ma commande n°12345 ? Elle était censée arriver hier. »",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Exemple de réponse du ChatBot"),
                " :",
            )
        with lst.item():
            pass
    st_space(size=1)
    st_write(s.project.doc.titles.h3, "2.4.7. ChatBot « Découverte de Besoin & Up-Sell »", tag=t.h3)
    st_space(size=1)
    st_write(s.project.doc.paragraphs.p_body, "Expertises")
    st_space(size=1)
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Identification du besoin"),
                " (Première étape)Pose des questions pour clarifier ce que le client recherche (produit, fonctionnalité, gamme de prix, etc.).",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Proposition d’offre adaptée"),
                " (Première étape)Fait une première recommandation en se basant sur la gamme existante et l’historique d’achats.",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Up-sell ou cross-sell"),
                " (Deuxième étape)Après la première réponse, propose un produit/option supplémentaire ou plus avancé en soulignant les avantages.",
            )
    st_write(s.project.doc.paragraphs.p_body, "Scénario d’illustration")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Données spécifiques fournies à l’assistant intelligent"),
                " : Base de produits, promotions en cours, historique d’achat du client.",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Exemple de question posée"),
                " : « Je cherche un nouvel abonnement pour mon téléphone, qu’est-ce que vous conseillez ? »",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Exemple de réponse du ChatBot"),
                " :",
            )
        with lst.item():
            pass
    st_space(size=1)
    st_write(s.project.doc.titles.h3, "2.4.8. ChatBot « Détection d’Anomalies & Avertissement Proactif »", tag=t.h3)
    st_space(size=1)
    st_write(s.project.doc.paragraphs.p_body, "Expertises")
    st_space(size=1)
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Analyse prédictive des retours"),
                " (Première étape)Surveille les conversations en temps réel pour repérer une hausse inhabituelle de réclamations sur un sujet précis.",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Alerte automatique"),
                " (Première étape)Signale immédiatement aux équipes internes qu’un problème potentiel émerge (ex. défaut produit ou bug logiciel).",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Message proactif au client"),
                " (Deuxième étape)Après confirmation du problème, envoie un message aux clients concernés pour leur fournir un correctif ou une solution avant qu’ils ne se plaignent.",
            )
    st_write(s.project.doc.paragraphs.p_body, "Scénario d’illustration")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Données spécifiques fournies à l’assistant intelligent"),
                " : Flux d’interactions clients, seuils d’alerte définis, listes des clients impactés (numéros de série, versions logicielles).",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Exemple de question posée"),
                " : « Pourquoi mon appareil redémarre tout seul depuis ce matin ? »",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Exemple de réponse du ChatBot"),
                " :",
            )
        with lst.item():
            pass
    st_space(size=1)
    st_write(s.project.doc.titles.h3, "2.4.9. ChatBot « Support Multilingue & Validation de Qualité »", tag=t.h3)
    st_space(size=1)
    st_write(s.project.doc.paragraphs.p_body, "Expertises")
    st_space(size=1)
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Détection automatique de la langue"),
                " (Première étape)Identifie la langue du client et fournit une première réponse adaptée.",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Traduction de contenu"),
                " (Première étape)Traduit la demande du client et les réponses potentielles pour maintenir une conversation fluide.",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Vérification de la cohérence linguistique"),
                " (Deuxième étape)Relit la réponse finale et corrige d’éventuelles erreurs de traduction ou de terminologie avant de transmettre.",
            )
    st_write(s.project.doc.paragraphs.p_body, "Scénario d’illustration")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Données spécifiques fournies à l’assistant intelligent"),
                " : Accès à un module de traduction, glossaire des termes produits/entreprise dans différentes langues.",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Exemple de question posée"),
                " : « I ordered a product from Spain but can’t track it. Can you help me, please ? »",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Exemple de réponse du ChatBot"),
                " :",
            )
        with lst.item():
            pass
    st_space(size=1)
    st_write(s.project.doc.titles.h3, "2.4.10. ChatBot « Remontée d’Informations & Amélioration Produit »", tag=t.h3)
    st_space(size=1)
    st_write(s.project.doc.paragraphs.p_body, "Expertises")
    st_space(size=1)
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Collecte d’avis utilisateurs"),
                " (Première étape)À la fin de chaque conversation, recueille l’avis du client sur le produit ou le service.",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Traitement et synthèse des retours"),
                " (Première étape)Évalue la satisfaction globale et identifie les points bloquants ou les idées d’amélioration.",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Proposition d’innovations"),
                " (Deuxième étape)Sur la base des retours, propose des pistes d’évolution ou de nouvelles fonctionnalités du produit/service.",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Évaluation d’impact"),
                " (Deuxième étape, optionnelle)Estime le gain potentiel (satisfaction, réduction de coûts) si ces innovations sont mises en place.",
            )
    st_write(s.project.doc.paragraphs.p_body, "Scénario d’illustration")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Données spécifiques fournies à l’assistant intelligent"),
                " : Retours utilisateurs de sessions précédentes, priorités de l’équipe produit, grille d’évaluation de la satisfaction.",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Exemple de question posée"),
                " : « Quels sont les points principaux à améliorer selon nos clients après l’utilisation de l’appli ? »",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Exemple de réponse du ChatBot"),
                " :",
            )
        with lst.item():
            pass
    st_space(size=1)
    st_write(s.project.doc.titles.h3, "2.4.11. Chatbot « Réclamations Automatisées »", tag=t.h3)
    st_write(s.project.doc.paragraphs.p_body + s.bold, "Expertises (3 au total) :Groupe 1 (simultané) : ")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Analyse du contexte de réclamation"),
                " : Identification rapide du type de réclamation (garantie, retour produit, facture erronée, etc.).",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Proposition de solution préliminaire"),
                " : Génération automatique d’une réponse standardisée adaptée au type de réclamation.",
            )
    st_write(
        s.project.doc.paragraphs.p_body,
        (s.bold, "Groupe 2 (enchaîné à la suite) :"),
        "3. ",
        (s.bold, "Plan d’action pour le suivi"),
        " : Programmation d’un suivi automatique (notification interne, rappel client, etc.) en fonction de la réponse initiale.",
    )
    st_write(s.project.doc.paragraphs.p_body + s.bold, "Mini-scénario : ")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Données spécifiques fournies à l’assistant"),
                " : Historique des réclamations sur des produits électroniques sur les 6 derniers mois, classification des types de problèmes récurrents (panne, délai de livraison, etc.).",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Exemple de question posée"),
                " : « Je veux signaler que mon smartphone est tombé en panne au bout d’une semaine, comment puis-je faire valoir la garantie ? »",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Exemple de réponse du Chatbot"),
                " :« Je constate que votre smartphone est encore sous garantie constructeur. Je vous propose de remplir le formulaire en ligne pour déclencher la procédure de réparation gratuite. Nous allons également enregistrer votre dossier pour vous envoyer des alertes de suivi. »",
            )
    st_space(size=1)
    st_write(s.project.doc.titles.h3, "2.4.12. Chatbot « Assistant Retour & Analyse »", tag=t.h3)
    st_write(s.project.doc.paragraphs.p_body + s.bold, "Expertises (4 au total) :Groupe 1 (simultané) : ")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Évaluation de la recevabilité d’un retour"),
                " : Vérification instantanée des conditions de retour (délais, état du produit, politique de remboursement).",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Génération de la procédure de retour"),
                " : Rédaction personnalisée du mode d’emploi pour renvoyer le produit (étiquette, points relais, etc.).",
            )
    st_write(
        s.project.doc.paragraphs.p_body,
        (s.bold, "Groupe 2 (enchaîné à la suite) :"),
        "3. ",
        (s.bold, "Analyse des causes récurrentes"),
        " : Regroupement des retours similaires pour identifier des tendances (défaut de fabrication, mauvaise description, etc.).4. ",
        (s.bold, "Rapport de prévention"),
        " : Proposition d’actions préventives (amélioration de la fiche produit, contrôle qualité renforcé).",
    )
    st_write(s.project.doc.paragraphs.p_body + s.bold, "Mini-scénario : ")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Données spécifiques fournies à l’assistant"),
                " : Politique de retour interne, données logistiques sur la localisation des points de dépôt, historique des retours sur le dernier trimestre.",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Exemple de question posée"),
                " : « J’aimerais renvoyer un article car il est arrivé défectueux, comment procéder ? »",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Exemple de réponse du Chatbot"),
                " :« Votre produit est éligible au retour dans les 30 jours. Voici votre étiquette d’expédition prépayée à imprimer. Nous avons noté que plusieurs retours concernent ce même modèle : un rapport d’analyse va être transmis à notre service qualité pour investigation. »",
            )
    st_space(size=1)
    st_write(s.project.doc.titles.h3, "2.4.13. Chatbot « Support Technique Basique et Avancé »", tag=t.h3)
    st_write(s.project.doc.paragraphs.p_body + s.bold, "Expertises (3 au total) :Groupe 1 (simultané) : ")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Diagnostic rapide"),
                " : Identification des pannes ou erreurs courantes selon les mots-clés fournis par le client.",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Proposition de solution de dépannage"),
                " : Fourniture d’un tutoriel pas à pas pour résoudre l’incident si possible.",
            )
    st_write(
        s.project.doc.paragraphs.p_body,
        (s.bold, "Groupe 2 (enchaîné à la suite) :"),
        "3. ",
        (s.bold, "Escalade vers un support avancé"),
        " : Si le problème persiste, préparation d’un ticket détaillé pour un expert (logs, screenshots, références).",
    )
    st_write(s.project.doc.paragraphs.p_body + s.bold, "Mini-scénario : ")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Données spécifiques fournies à l’assistant"),
                " : Base de connaissances techniques (FAQ, guides de dépannage), historique d’incidents clients classés par thématique.",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Exemple de question posée"),
                " : « Mon imprimante refuse d’imprimer, j’ai un message d’erreur 508, comment faire ? »",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Exemple de réponse du Chatbot"),
                " :« L’erreur 508 indique généralement un bourrage papier ou un problème de cartouche. Essayez d’ouvrir le panneau arrière et de vérifier s’il y a un papier coincé. Si le problème n’est pas résolu, je génère un ticket pour notre équipe d’experts. »",
            )
    st_space(size=1)
    st_write(s.project.doc.titles.h3, "2.4.14. Chatbot « Analyse de la Satisfaction et Suivi Proactif »", tag=t.h3)
    st_write(s.project.doc.paragraphs.p_body + s.bold, "Expertises (3 au total) :Groupe 1 (simultané) : ")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Collecte et synthèse des retours"),
                " : Envoi de sondages post-interaction et regroupement des réponses clients.",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Analyse des sentiments"),
                " : Évaluation du sentiment positif ou négatif dans les commentaires.",
            )
    st_write(
        s.project.doc.paragraphs.p_body,
        (s.bold, "Groupe 2 (enchaîné à la suite) :"),
        "3. ",
        (s.bold, "Plan de suivi proactif"),
        " : Envoi de relances ou messages de remerciement et proposition d’améliorations si le sentiment est négatif.",
    )
    st_write(s.project.doc.paragraphs.p_body + s.bold, "Mini-scénario : ")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Données spécifiques fournies à l’assistant"),
                " : Ensemble des derniers sondages de satisfaction, historique de commentaires clients sur les réseaux sociaux.",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Exemple de question posée"),
                " : « Nous venons de recevoir 50 retours suite à notre nouveau service de livraison. Quelle est la tendance globale ? »",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Exemple de réponse du Chatbot"),
                " :« Sur 50 retours, 35 sont jugés positifs (70 %), mettant en avant la rapidité de livraison. Les 15 retours négatifs concernent principalement l’emballage insuffisant. Je recommande d’envoyer un message de suivi aux clients insatisfaits et de proposer un emballage renforcé. »",
            )
    st_space(size=1)
    st_write(s.project.doc.titles.h3, "2.4.15. Chatbot « Assistant Formation Client »", tag=t.h3)
    st_write(s.project.doc.paragraphs.p_body + s.bold, "Expertises (4 au total) :Groupe 1 (simultané) : ")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Conception de modules de formation"),
                " : Élaboration de mini-formations (textes, vidéos, quiz) en fonction des besoins identifiés.",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Planification des sessions"),
                " : Automatisation de la création d’un calendrier de formations et de l’envoi d’invitations.",
            )
    st_write(
        s.project.doc.paragraphs.p_body,
        (s.bold, "Groupe 2 (enchaîné à la suite) :"),
        "3. ",
        (s.bold, "Évaluation des acquis"),
        " : Création de questionnaires pour mesurer l’efficacité de la formation suivie.4. ",
        (s.bold, "Rapport de progression"),
        " : Génération d’un rapport individuel ou global sur la compréhension et les lacunes éventuelles.",
    )
    st_write(s.project.doc.paragraphs.p_body + s.bold, "Mini-scénario : ")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Données spécifiques fournies à l’assistant"),
                " : Guides de formation en PDF, modules vidéo déjà disponibles, planning de webinaires prévus.",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Exemple de question posée"),
                " : « Nos clients se plaignent de ne pas savoir utiliser notre application de paiement, peux-tu nous aider à leur proposer des formations ? »",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Exemple de réponse du Chatbot"),
                " :« J’ai créé un module “Découverte de l’application de paiement” avec 2 vidéos et un quiz rapide. Les sessions en direct sont programmées les jeudis à 10h. Après chaque session, un questionnaire sera envoyé pour évaluer l’acquisition des connaissances. »",
            )
    st_space(size=1)
    st_write(s.project.doc.titles.h3, "2.4.16. Chatbot « Automatisation des Communications de Fidélité »", tag=t.h3)
    st_write(s.project.doc.paragraphs.p_body + s.bold, "Expertises (3 au total) :Groupe 1 (simultané) : ")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Segmentation de la clientèle"),
                " : Identification des groupes de clients à fort potentiel de fidélisation.",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Personnalisation des offres"),
                " : Proposition d’offres ciblées en fonction des préférences détectées (historique d’achats, navigation, etc.).",
            )
    st_write(
        s.project.doc.paragraphs.p_body,
        (s.bold, "Groupe 2 (enchaîné à la suite) :"),
        "3. ",
        (s.bold, "Automatisation des campagnes"),
        " : Programmation des envois d’e-mails, SMS ou notifications pour entretenir la relation client (anniversaires, promotions, etc.).",
    )
    st_write(s.project.doc.paragraphs.p_body + s.bold, "Mini-scénario : ")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Données spécifiques fournies à l’assistant"),
                " : Historique d’achat, profils d’utilisation, liste des événements marketing prévus.",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Exemple de question posée"),
                " : « Nous voulons lancer une nouvelle promo pour nos clients fidèles. Peux-tu cibler ceux qui ont acheté plus de trois fois ce trimestre ? »",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Exemple de réponse du Chatbot"),
                " :« J’ai identifié 250 clients “Premium” qui ont acheté plus de trois fois. Je propose de leur envoyer un code promo exclusif et un message de remerciement personnalisé ce vendredi. »",
            )
    st_space(size=1)
    st_write(s.project.doc.titles.h3, "2.4.17. Chatbot « Générateur de Contenus de Webinaires et Supports »", tag=t.h3)
    st_write(s.project.doc.paragraphs.p_body + s.bold, "Expertises (3 au total) :Groupe 1 (simultané) : ")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Rédaction de scripts"),
                " : Génération automatique d’un script de webinaire ou d’atelier adapté à un sujet précis.",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Création de supports visuels"),
                " : Production de diapositives de présentation ou d’aides visuelles basées sur les points clés.",
            )
    st_write(
        s.project.doc.paragraphs.p_body,
        (s.bold, "Groupe 2 (enchaîné à la suite) :"),
        "3. ",
        (s.bold, "Plan de diffusion et invitations"),
        " : Détermination des canaux (mail, réseaux) et planification automatique des invitations et rappels.",
    )
    st_write(s.project.doc.paragraphs.p_body + s.bold, "Mini-scénario : ")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Données spécifiques fournies à l’assistant"),
                " : Thèmes de formation à couvrir (gestion des réclamations, utilisation du nouvel outil, etc.), charte graphique de l’entreprise.",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Exemple de question posée"),
                " : « Nous devons présenter le nouveau process de réclamation en interne, peux-tu préparer un webinaire d’une heure ? »",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Exemple de réponse du Chatbot"),
                " :« Voici un script en 3 parties (introduction, démonstration, session de questions-réponses). J’ai également généré 10 diapositives. Les invitations peuvent être envoyées dès demain, avec un rappel le jour même. »",
            )
    st_space(size=1)
    st_write(s.project.doc.titles.h3, "2.4.18. Chatbot « Analyse Automatique des Transcriptions et Retours d’Appels »", tag=t.h3)
    st_write(s.project.doc.paragraphs.p_body + s.bold, "Expertises (4 au total) :Groupe 1 (simultané) : ")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Transcription et classification"),
                " : Reconnaissance des mots-clés et des sujets abordés dans les appels client.",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Analyse de ton et sentiment"),
                " : Détection des émotions du client (irritation, satisfaction, confusion) pour chaque appel.",
            )
    st_write(
        s.project.doc.paragraphs.p_body,
        (s.bold, "Groupe 2 (enchaîné à la suite) :"),
        "3. ",
        (s.bold, "Diagnostic des récurrences"),
        " : Identification des problèmes ou questions récurrents (p. ex. bug produit, problème de facturation).4. ",
        (s.bold, "Recommandations d’amélioration"),
        " : Suggestion d’optimisations pour les scripts d’appel et la formation des agents.",
    )
    st_write(s.project.doc.paragraphs.p_body + s.bold, "Mini-scénario : ")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Données spécifiques fournies à l’assistant"),
                " : Enregistrements ou transcriptions d’appels des deux dernières semaines, historique d’actions correctives déjà menées.",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Exemple de question posée"),
                " : « Sur les 200 appels reçus la semaine dernière, quelles sont les causes principales de mécontentement ? »",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Exemple de réponse du Chatbot"),
                " :« Les mentions de “erreur de facture” reviennent 58 fois, associées à un ton irrité dans 45 cas. Je recommande de clarifier la procédure de facturation dans le script et de mettre à jour la formation des agents. »",
            )
    st_space(size=1)
    st_write(s.project.doc.titles.h3, "2.4.19. Chatbot « Suivi des Réclamations Complexes »", tag=t.h3)
    st_write(s.project.doc.paragraphs.p_body + s.bold, "Expertises (3 au total) :Groupe 1 (simultané) : ")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Collecte d’informations détaillées"),
                " : Questionnaire automatique pour comprendre la réclamation complexe (documents, photos, étapes déjà suivies).",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Calcul de la priorité"),
                " : Évaluation du degré d’urgence ou d’impact financier pour hiérarchiser le traitement.",
            )
    st_write(
        s.project.doc.paragraphs.p_body,
        (s.bold, "Groupe 2 (enchaîné à la suite) :"),
        "3. ",
        (s.bold, "Orchestration multi-équipes"),
        " : Envoi automatique de la réclamation au bon service (technique, légal, logistique) et suivi des délais de réponse.",
    )
    st_write(s.project.doc.paragraphs.p_body + s.bold, "Mini-scénario : ")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Données spécifiques fournies à l’assistant"),
                " : Procédure interne de priorisation (montant financier, impact client, ancienneté du problème), liste des interlocuteurs internes.",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Exemple de question posée"),
                " : « J’ai un client qui réclame un remboursement pour un service non rendu, mais il y a un litige sur les preuves. Comment gérer ? »",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Exemple de réponse du Chatbot"),
                " :« La réclamation est classée en “priorité moyenne” en raison du montant réclamé. Veuillez télécharger les justificatifs nécessaires (facture, échanges de mails). J’ai transmis le dossier au service légal et je lancerai des rappels automatiques si aucune réponse n’est donnée dans 48 heures. »",
            )
    st_space(size=1)
    st_write(s.project.doc.titles.h3, "2.4.20. Chatbot « Récompenses et Promotions sur Mesure »", tag=t.h3)
    st_write(s.project.doc.paragraphs.p_body + s.bold, "Expertises (3 au total) :Groupe 1 (simultané) : ")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Analyse des habitudes d’achat"),
                " : Identification des produits les plus achetés et fréquence d’achats récurrents.",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Proposition de récompenses personnalisées"),
                " : Génération de codes promotionnels ou de points de fidélité en fonction de ces habitudes.",
            )
    st_write(
        s.project.doc.paragraphs.p_body,
        (s.bold, "Groupe 2 (enchaîné à la suite) :"),
        "3. ",
        (s.bold, "Automatisation de l’envoi"),
        " : Création d’un planning d’envoi de ces offres via e-mail ou notifications push, en tenant compte des périodes de forte activité client.",
    )
    st_write(s.project.doc.paragraphs.p_body + s.bold, "Mini-scénario : ")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Données spécifiques fournies à l’assistant"),
                " : Historique de commandes, préférences produits, calendrier marketing (promotions saisonnières, fêtes, etc.).",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Exemple de question posée"),
                " : « Nous souhaitons offrir des réductions ciblées à nos clients qui achètent souvent des produits de beauté, peux-tu nous aider ? »",
            )
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Exemple de réponse du Chatbot"),
                " :« 120 clients ont acheté des produits de beauté au moins deux fois le mois dernier. Je propose de leur envoyer un bon de réduction de 15 % avec un message expliquant les nouveautés en gamme de soins. L’envoi peut se faire cette semaine pour coïncider avec la fête du printemps. »",
            )
    st_space(size=1)
    st_write(s.project.doc.titles.h2, "2.5. ChatBot Ideas - Service Communication", tag=t.h2, toc_lvl="+1")
    st_space(size=1)
    st_space(size=1)
    st_write(s.project.doc.titles.h3, "2.5.1. Chatbot « Rédaction de Newsletter Interne et Formation »", tag=t.h3)
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Finalité"),
                "Faciliter la création de newsletters internes et de modules de formation rapides et cohérents à destination des employés.",
            )
        with lst.item():
            st_write(s.bold, "Expertises ")
        with lst.item():
            pass
        with lst.item():
            st_write(s.bold, "Illustration d’un Scénario ")
        with lst.item():
            pass
    st_write(s.project.doc.titles.h3, "2.5.2. Chatbot « Analyse de Sondages et Engagement des Employés »", tag=t.h3)
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Finalité"),
                "Simplifier la création de questionnaires internes et exploiter les données recueillies pour améliorer l’engagement des employés.",
            )
        with lst.item():
            st_write(s.bold, "Expertises ")
        with lst.item():
            pass
        with lst.item():
            st_write(s.bold, "Illustration d’un Scénario ")
        with lst.item():
            pass
    st_space(size=1)
    st_write(s.project.doc.titles.h3, "2.5.3. Chatbot « Coordination d’Événements Internes et Feedback »", tag=t.h3)
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Finalité"),
                "Simplifier l’organisation d’événements internes (réunions, séminaires, ateliers) et analyser ensuite les retours pour améliorer les éditions suivantes.",
            )
        with lst.item():
            st_write(s.bold, "Expertises ")
        with lst.item():
            pass
        with lst.item():
            st_write(s.bold, "Illustration d’un Scénario ")
        with lst.item():
            pass
    st_space(size=1)
    st_write(s.project.doc.titles.h3, "2.5.4. Chatbot « Relations Publiques et Gestion de Crises »", tag=t.h3)
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Finalité"),
                "Aider à rédiger des contenus pour les relations médias et à anticiper ou gérer les crises réputationnelles.",
            )
        with lst.item():
            st_write(s.bold, "Expertises ")
        with lst.item():
            pass
        with lst.item():
            st_write(s.bold, "Illustration d’un Scénario ")
        with lst.item():
            pass
    st_space(size=1)
    st_write(s.project.doc.titles.h3, "2.5.5. Chatbot « Marketing de Contenu et Service Client »", tag=t.h3)
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Finalité"),
                "Générer du contenu marketing et répondre efficacement aux besoins des clients.",
            )
        with lst.item():
            st_write(s.bold, "Expertises ")
        with lst.item():
            pass
        with lst.item():
            st_write(s.bold, "Illustration d’un Scénario ")
        with lst.item():
            pass
    st_space(size=1)
    st_write(s.project.doc.titles.h3, "2.5.6. Chatbot « Synthèse de Réunions et Communication Interne »", tag=t.h3)
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Finalité"),
                "Aider les équipes à consolider les informations issues des réunions et à les transformer en messages clés pour la communication interne.",
            )
        with lst.item():
            st_write(s.bold, "Expertises ")
        with lst.item():
            pass
        with lst.item():
            st_write(s.bold, "Illustration d’un Scénario ")
        with lst.item():
            pass
    st_space(size=1)
    st_write(s.project.doc.titles.h3, "2.5.7. Chatbot « Gestion de la Réputation sur les Réseaux Sociaux »", tag=t.h3)
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Finalité"),
                "Surveiller les mentions de l’entreprise et fournir une stratégie de réponse adaptée pour protéger et développer la réputation en ligne.",
            )
        with lst.item():
            st_write(s.bold, "Expertises ")
        with lst.item():
            pass
        with lst.item():
            st_write(s.bold, "Illustration d’un Scénario ")
        with lst.item():
            pass
    st_space(size=1)
    st_write(s.project.doc.titles.h3, "2.5.8. Chatbot « Création de Contenus Publicitaires et Gestion de Campagnes »", tag=t.h3)
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Finalité"),
                "Générer des concepts publicitaires originaux et affiner ensuite la stratégie de diffusion pour toucher le bon public.",
            )
        with lst.item():
            st_write(s.bold, "Expertises ")
        with lst.item():
            pass
        with lst.item():
            st_write(s.bold, "Illustration d’un Scénario ")
        with lst.item():
            pass
    st_space(size=1)
    st_write(s.project.doc.titles.h3, "2.5.9. Chatbot « Récap Médias et Communication Externe »", tag=t.h3)
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Finalité"),
                "Rédiger des articles destinés à l’externe, produire des résumés de couverture médiatique et recommander des axes de communication.",
            )
        with lst.item():
            st_write(s.bold, "Expertises ")
        with lst.item():
            pass
        with lst.item():
            st_write(s.bold, "Illustration d’un Scénario ")
        with lst.item():
            pass
    st_space(size=1)
    st_write(s.project.doc.titles.h3, "2.5.10. Chatbot « Formation et Culture d’Entreprise »", tag=t.h3)
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write(
                s.project.doc.paragraphs.p_body,
                (s.bold, "Finalité"),
                "Favoriser le développement d’une culture d’entreprise forte via la formation continue et la communication interne sur les valeurs clés.",
            )
        with lst.item():
            st_write(s.bold, "Expertises ")
        with lst.item():
            pass
        with lst.item():
            st_write(s.bold, "Illustration d’un Scénario ")
        with lst.item():
            pass
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_write(s.project.doc.titles.h2, "2.6. ChatBot Ideas - Services Qualité et Conformité", tag=t.h2, toc_lvl="+1")
    st_space(size=1)
    st_write(s.project.doc.titles.h3, "2.6.1. ChatBot « Tests Automatisés & Rapports de Qualité »", tag=t.h3)
    st_write(s.project.doc.paragraphs.p_body, "Expertises :")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write("Groupe 1 :")
        with lst.item():
            pass
        with lst.item():
            st_write("Groupe 2 :3. Élaboration d’un plan d’actions correctives (par exemple, classer les défauts par priorité, suggérer des solutions).")
    st_write(s.project.doc.paragraphs.p_body, "Illustration d’un scénario concret :")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write("Données spécifiques fournies au ChatBot : Résultats d’une série de tests manuels, spécifications fonctionnelles détaillées, historique de défauts connus sur la version précédente.")
        with lst.item():
            st_write("Exemple de question : « Peux-tu générer un script de test automatisé pour vérifier la conformité de l’interface utilisateur et proposer un rapport de bugs potentiels ? »")
        with lst.item():
            st_write("Exemple de réponse : Le ChatBot rédige un ensemble de scénarios de test en langage pseudocode, identifie les anomalies attendues et produit un rapport listant les points critiques. Enfin, il suggère un plan d’actions pour résoudre rapidement les problèmes prioritaires.")
    st_space(size=1)
    st_write(s.project.doc.titles.h3, "2.6.2. ChatBot « Suivi des Normes & Audit de Conformité »", tag=t.h3)
    st_write(s.project.doc.paragraphs.p_body, "Expertises :")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write("Groupe 1 :")
        with lst.item():
            pass
        with lst.item():
            st_write("Groupe 2 :3. Rédaction de rapports d’écart et recommandations de mise à niveau (par exemple, détailler les manquements et proposer des axes d’amélioration).")
    st_write(s.project.doc.paragraphs.p_body, "Illustration d’un scénario concret :")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write("Données spécifiques fournies au ChatBot : Tableau des exigences d’une norme ISO spécifique, historique de conformité de l’entreprise, documents internes de qualité.")
        with lst.item():
            st_write("Exemple de question : « Quels sont nos principaux écarts par rapport à la dernière version de la norme ISO, et que dois-je faire pour les corriger ? »")
        with lst.item():
            st_write("Exemple de réponse : Le ChatBot compare les documents internes aux exigences, génère un tableau d’écart clair et propose ensuite des recommandations spécifiques pour combler les manquements, ainsi qu’un plan d’actions priorisées.")
    st_space(size=1)
    st_write(s.project.doc.titles.h3, "2.6.3. ChatBot « Documentation & Reporting Qualité en Continu »", tag=t.h3)
    st_write(s.project.doc.paragraphs.p_body, "Expertises :")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write("Groupe 1 :")
        with lst.item():
            pass
        with lst.item():
            st_write("Groupe 2 :3. Analyse et suggestion d’améliorations sur la base de ces documents (par exemple, propositions de révision des processus, idées pour optimiser la traçabilité).")
    st_write(s.project.doc.paragraphs.p_body, "Illustration d’un scénario concret :")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write("Données spécifiques fournies au ChatBot : Données de production mensuelles, historique des rapports qualité, liste de non-conformités ouvertes.")
        with lst.item():
            st_write("Exemple de question : « Pourrais-tu préparer un rapport mensuel sur les principaux KPI qualité et proposer des pistes d’amélioration ? »")
        with lst.item():
            st_write("Exemple de réponse : Le ChatBot assemble les informations en un document synthétique, met en évidence les points de friction et propose des ajustements concrets du process, par exemple l’ajout d’étapes de vérification intermédiaires.")
    st_space(size=1)
    st_write(s.project.doc.titles.h3, "2.6.4. ChatBot « Formation & Sensibilisation aux Normes »", tag=t.h3)
    st_write(s.project.doc.paragraphs.p_body, "Expertises :")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write("Groupe 1 :")
        with lst.item():
            pass
        with lst.item():
            st_write("Groupe 2 :3. Proposition de plans de formation personnalisés (par exemple, adapter le contenu selon le niveau de connaissance du public).")
    st_write(s.project.doc.paragraphs.p_body, "Illustration d’un scénario concret :")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write("Données spécifiques fournies au ChatBot : Politique interne de l’entreprise, extraits de la norme ISO concernée, historique des résultats des formations précédentes.")
        with lst.item():
            st_write("Exemple de question : « Peux-tu concevoir un module de formation rapide sur les points clés de la norme ISO 9001 et préparer un test de validation des acquis ? »")
        with lst.item():
            st_write("Exemple de réponse : Le ChatBot produit un module de formation au format texte, intégrant des exemples concrets, puis génère un questionnaire à choix multiples pour évaluer la compréhension et suggère un programme de suivi adapté.")
    st_space(size=1)
    st_write(s.project.doc.titles.h3, "2.6.5. ChatBot « Surveillance Réglementaire & Alerte »", tag=t.h3)
    st_write(s.project.doc.paragraphs.p_body, "Expertises :")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write("Groupe 1 :")
        with lst.item():
            pass
        with lst.item():
            st_write("Groupe 2 :3. Propositions de mesures de conformité (par exemple, recommandations pour adapter les procédures internes).")
    st_write(s.project.doc.paragraphs.p_body, "Illustration d’un scénario concret :")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write("Données spécifiques fournies au ChatBot : Historique des règlementations en vigueur, archives des alertes précédentes, documentation interne sur les pratiques d’entreprise.")
        with lst.item():
            st_write("Exemple de question : « Quelle est la dernière modification de la législation sur la sécurité des données et comment cela affecte-t-il notre politique interne ? »")
        with lst.item():
            st_write("Exemple de réponse : Le ChatBot fournit un résumé concis des changements réglementaires, explique leurs répercussions possibles sur les procédures en cours et propose plusieurs ajustements afin de rester conforme.")
    st_space(size=1)
    st_write(s.project.doc.titles.h3, "2.6.6. ChatBot « Audit Interne Automatisé & Conseils »", tag=t.h3)
    st_write(s.project.doc.paragraphs.p_body, "Expertises :")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write("Groupe 1 :")
        with lst.item():
            pass
        with lst.item():
            st_write("Groupe 2 :3. Production d’un rapport d’audit incluant des recommandations (par exemple, synthèse des observations, liste des priorités).")
    st_write(s.project.doc.paragraphs.p_body, "Illustration d’un scénario concret :")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write("Données spécifiques fournies au ChatBot : Check-lists existantes, notes prises lors d’audits précédents, procédure interne de l’entreprise.")
        with lst.item():
            st_write("Exemple de question : « Pourrais-tu préparer une check-list d’audit interne pour notre processus de contrôle qualité et générer ensuite un rapport à partir des observations recueillies ? »")
        with lst.item():
            st_write("Exemple de réponse : Le ChatBot compile rapidement la check-list adéquate et, après saisie des réponses d’audit, produit un rapport qui regroupe les points de conformité, les non-conformités détectées et propose un plan d’actions.")
    st_space(size=1)
    st_write(s.project.doc.titles.h3, "2.6.7. ChatBot « Gestion des Risques Opérationnels & Plans d’Action »", tag=t.h3)
    st_write(s.project.doc.paragraphs.p_body, "Expertises :")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write("Groupe 1 :")
        with lst.item():
            pass
        with lst.item():
            st_write("Groupe 2 :3. Rédaction de plans de mitigation et de suivi (par exemple, définir les étapes à mettre en place, synthétiser les mesures préventives).")
    st_write(s.project.doc.paragraphs.p_body, "Illustration d’un scénario concret :")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write("Données spécifiques fournies au ChatBot : Historique d’incidents passés, base de données d’événements risques, politiques internes de gestion de crise.")
        with lst.item():
            st_write("Exemple de question : « Quels sont nos risques majeurs dans la chaîne de production et comment pouvons-nous les gérer en priorité ? »")
        with lst.item():
            st_write("Exemple de réponse : Le ChatBot dresse une liste de risques potentiels (pannes machine, erreurs de contrôle qualité…), les classe selon leur probabilité et leur impact, puis propose un plan de mitigation avec étapes clés et suivi prédéfini.")
    st_space(size=1)
    st_write(s.project.doc.titles.h3, "2.6.8. ChatBot « Automatisation des Processus de Certification »", tag=t.h3)
    st_write(s.project.doc.paragraphs.p_body, "Expertises :")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write("Groupe 1 :")
        with lst.item():
            pass
        with lst.item():
            st_write("Groupe 2 :3. Conseils pour optimiser la préparation (par exemple, recommandations de ressources, mise à jour des données clés).")
    st_write(s.project.doc.paragraphs.p_body, "Illustration d’un scénario concret :")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write("Données spécifiques fournies au ChatBot : Référentiel d’audit pour une certification ISO, documents internes existants, planning de l’audit à venir.")
        with lst.item():
            st_write("Exemple de question : « Pourrais-tu générer le dossier de certification en regroupant nos procédures et nous indiquer les points à surveiller avant l’audit ? »")
        with lst.item():
            st_write("Exemple de réponse : Le ChatBot compile les procédures pertinentes en un dossier structuré, liste les exigences critiques et propose des conseils pratiques (par exemple, vérifier les enregistrements de formation) pour garantir la conformité.")
    st_space(size=1)
    st_write(s.project.doc.titles.h3, "2.6.9. ChatBot « Suivi des Actions Correctives & Préventives »", tag=t.h3)
    st_write(s.project.doc.paragraphs.p_body, "Expertises :")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write("Groupe 1 :")
        with lst.item():
            pass
        with lst.item():
            st_write("Groupe 2 :3. Propositions d’optimisation pour la clôture rapide (par exemple, suggestions d’étapes supplémentaires, recommandations de meilleures pratiques).")
    st_write(s.project.doc.paragraphs.p_body, "Illustration d’un scénario concret :")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write("Données spécifiques fournies au ChatBot : Liste d’actions correctives identifiées lors d’un audit, échéanciers prévus, personnes responsables.")
        with lst.item():
            st_write("Exemple de question : « Peux-tu me donner un état à jour des actions correctives encore en cours, et m’indiquer lesquelles sont prioritaires ? »")
        with lst.item():
            st_write("Exemple de réponse : Le ChatBot génère un tableau de suivi avec les délais à respecter, met en évidence les actions en retard et propose des solutions rapides (attribuer des ressources supplémentaires, planifier des revues plus fréquentes).")
    st_space(size=1)
    st_write(s.project.doc.titles.h3, "2.6.10. ChatBot « Analyse de la Qualité & Recommandations d’Amélioration Continue »", tag=t.h3)
    st_write(s.project.doc.paragraphs.p_body, "Expertises :")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write("Groupe 1 :")
        with lst.item():
            pass
        with lst.item():
            st_write("Groupe 2 :3. Élaboration de plans d’amélioration continue (par exemple, propositions de pistes d’innovation, ajustements organisationnels).")
    st_write(s.project.doc.paragraphs.p_body, "Illustration d’un scénario concret :")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write("Données spécifiques fournies au ChatBot : Rapports d’incidents, questionnaires de satisfaction client, enregistrements de plaintes sur une période donnée.")
        with lst.item():
            st_write("Exemple de question : « Pourrais-tu analyser les réclamations des clients de ces trois derniers mois et nous proposer un plan d’amélioration continue ? »")
        with lst.item():
            st_write("Exemple de réponse : Le ChatBot produit un résumé structuré des principaux problèmes rencontrés, indique les zones de friction récurrentes, puis suggère un plan d’actions centré sur la correction des processus et la formation du personnel afin d’améliorer la satisfaction client.")
    st_space(size=1)
    st_space(size=1)
