import streamlit as st
from streamtex import *
import streamtex as stx
from streamtex.styles import Style as ns, StyleGrid as sg
from streamtex.enums import Tags as t, ListTypes as lt
from shared.custom.styles import Styles as s

class BlockStyles:
    """Local styles for this block.

    Color mapping:
      #434343 -> s.project.colors.gray
      #666666 -> s.project.colors.gray
      #a64d78 -> s.project.colors.dark_purple
    """
    pass

bs = BlockStyles

def build():
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_write(s.project.doc.titles.h1 + s.project.colors.dark_purple, "1. Etude de cas pour l'Atelier IA Générative ", tag=t.h1, toc_lvl="1")
    st_space(size=1)
    st_space(size=1)
    st_write(s.project.doc.titles.h1, "2. Médiator - Assistant Génératif pour les Médiations en Milieu Professionnel ", tag=t.h1, toc_lvl="1")
    st_space(size=1)
    st_write(s.project.doc.titles.h2, "2.1. Objectif Général", tag=t.h2, toc_lvl="+1")
    st_space(size=1)
    st_write(s.project.doc.paragraphs.p_body, "L’objectif de cette étude de cas est de concevoir un chatbot capable de suggérer des contenus de messages pour faciliter la médiation en cas de tensions dans les relations professionnelles. ")
    st_write(s.project.doc.paragraphs.p_body, "La démarche suivie repose sur l’analyse d’une situation donnée, à partir de laquelle : ")
    with st_list(list_type=lt.unordered, li_style=s.project.doc.lists.item) as lst:
        with lst.item():
            st_write("Le profil optimal du chatbot est défini. ")
        with lst.item():
            st_write("Ce profil est appliqué à la situation pour générer une réponse adaptée. ")
        with lst.item():
            st_write("Les résultats obtenus sont comparés aux résultats attendus afin d’évaluer l’efficacité du chatbot. ")
    st_space(size=1)
    st_write(s.project.doc.titles.h2, "2.2. Description de la situation ", tag=t.h2, toc_lvl="+1")
    st_space(size=1)
    st_write(s.project.doc.paragraphs.p_body, "Voici la situation: ")
    st_write(s.project.doc.paragraphs.p_body, "-- ")
    st_write(s.project.doc.paragraphs.p_body, "Pierre — Today at 12:34 AM ")
    st_write(s.project.doc.paragraphs.p_body, "Ok, je vais voir comment intégrer ça demain. ")
    st_write(s.project.doc.paragraphs.p_body, "Bon travail @Paul ")
    st_write(s.project.doc.paragraphs.p_body, "[12:39 AM] ")
    st_write(s.project.doc.paragraphs.p_body, "La prochaine fois, j'aimerais quand même discuter l'approche avant, parce que j'avais prévu de corriger les bugs dans mon implémentation de l'export docx que tu avais mentionné ce matin, parce que je ne pense pas que c'est un soucis fondamental, mais juste la structure du document Word que je créé qui n'est pas la bonne. La source de vérité n'est pas le document markdown, mais le document Lexical qui contient toutes les informations (liens, images, etc.), c'est pour ça que je n'avais pas pris l'approche pandoc. (edited) ")
    st_write(s.project.doc.paragraphs.p_body, "-- ")
    st_write(s.project.doc.paragraphs.p_body, "Paul — Today at 1:02 AM ")
    st_write(s.project.doc.paragraphs.p_body, "@Pierre Tout d’abord, ton dernier message m’a un peu peiné. Il serait important que tu commences à adopter une posture plus ouverte et à être moins susceptible lorsque nous discutons de code ou lorsque des solutions sont proposées Tu sembles souvent très défensif face à ce que tu n’as pas développé toi-même et parfois peu rigoureux dans la gestion de ton propre travail.  ")
    st_write(s.project.doc.paragraphs.p_body, "Pierre, à ce stade du produit, avec tant de tickets à finaliser d’ici la fin de l’année, tu ne peux pas te permettre de consacrer plusieurs jours à une seule fonctionnalité. D’autant plus que cela fait déjà trois mois que j’ai évoqué et suggéré l’utilisation de Pandoc, qui, comme tu peux le voir, fonctionne!  ")
    st_write(s.project.doc.paragraphs.p_body, "Par ailleurs, même si tu affirmes que le Markdown n’est pas la source de vérité, il convient de noter que Lexical dispose d’un package permettant l’exportation en Markdown. Pour moi, cela fait du Markdown une source de vérité pour les exports, tout simplement parce qu’il n’existe pas d’autres moyens viables de convertir un document Lexical sans recourir à des implémentations complexes et peu maintenables.  ")
    st_write(s.project.doc.paragraphs.p_body, "Les solutions que tu as proposées jusqu’à présent ne fonctionnent pas parfaitement, comme les tests l’ont montré. L’approche basée sur Pandoc reste, à mon sens, la meilleure. Elle repose sur une conversion solide en Markdown, évitant de devoir développer et maintenir des solutions pour exporter vers n formats. Cette méthode, attendue depuis plusieurs mois, pourrait être mise en œuvre plus rapidement en s’appuyant sur les helpers du package Markdown de Lexical.  ")
    st_write(s.project.doc.paragraphs.p_body, "Enfin, un simple merci aurait été plus approprié que ton dernier message, car je m’efforce de contribuer au développement de Quasible tout en jonglant avec de nombreuses autres responsabilités comme tu sais très bien ")
    st_write(s.project.doc.paragraphs.p_body, "-- ")
    st_write(s.project.doc.paragraphs.p_body, "Pierre — Today at 3:40 AM@Paul Je suis désolé si je t’avais donné cette impression, mais ce n’était pas du tout le but de mon message. Je me sens vraiment mal que je t’ai donné cette impression! Le but était de te dire que j’aimerais qu’on communique plus ensemble sur ce qu’on est en train de faire ou ce qu’on prévoit de faire (je sais je ne l’ai pas fait non plus, donc je ne suis pas excusé non plus).  ")
    st_write(s.project.doc.paragraphs.p_body, "J’estime avoir un esprit ouvert par rapport à tes suggestions et je t’écoutes et je réfléchis beaucoup sur comment intégrer tes propositions, mais ce n’est pas toujours si simple. Je t’expliques comment j’avais réfléchis sur le problème de l’export des documents:  ")
    st_write(s.project.doc.paragraphs.p_body, "On discute d’utiliser pandoc (il y a 3 mois). Tout de suite, je regarde comment c’est possible d’intégrer pandoc facilement sans changer de tech stack (avec trpc, next.js, etc.). Je teste plusieurs choses, pandoc compilé en webassembly, je teste ça, ça ne marche pas bien, puis je réfléchis à créer une api séparé qui l’exécute et retourne les résultats (comment t’as fait), mais je remarque qu’il faut créer un service à part, avoir une CI pipeline qui fait le build et deploy, créer le docker container, faire le choix du framework, ajuster les réglages de la VM pour permettre l’accès aux bons ports, changer le DNS, ajouter du monitoring, etc. et à la fin je laisse de côté parce que ça fait un gros travail juste pour implémenter la fonctionnalité d’export  ")
    st_write(s.project.doc.paragraphs.p_body, "et de l’intégrer avec tout le reste de l’application et de toute façon il y a d’autres tickets (plus) urgents à faire donc je laisse tomber et ça se repousse. Et c’est souvent le cas pour les tâches qui semblent simple, mais qui demandent plus de réflection pour intégrer dans le reste de l’application. ")
    st_write(s.project.doc.paragraphs.p_body, "Je ne suis pas défensif par rapport à du code que je n’ai pas écrit, au contraire! C’est plus une question d’intégration du code. La première réaction que j’ai eu quand j’ai vu ce tu as fait, c’était que je me suis dit que c’était cool. Et tout de suite, la prochaine c’était comment intégrer ça et toute la réflection que j’avais fait et l’autre réaction c’était que je me sentait tout de suite comme quelqu’un d’incapable, surtout en ayant en tête que Jacques verrait ça et aurait l’impression de collaborer avec (et de payer) un naze (moi). ")
    st_write(s.project.doc.paragraphs.p_body, "Où je suis défensif c’est le fait que tu ne veux pas toucher le code de Quasible, un peu comme si c’était un virus contagieux. Je t’avais déjà demandé ce que tu avais besoin et j’ai commencé à ajouter plus de docs et d’améliorer la repo pour que ça soit plus facile à rentrer dedans, mais j’ai l’impression que ça ne sert à rien. J’aurais été plus réceptif à ton code si c’était en tant que pull request et non une nouvelle repo. Et de nouveau je me demande si ce que j’ai fait n’est pas assez bien pour qu’on soit dans cet état. ")
    st_write(s.project.doc.paragraphs.p_body, "Je sais que j’ai des soucis de gestion et d’estimation de mon travail. Honnêtement, je ne sais pas entièrement pourquoi encore, mais j’ai un peu une idée. Je pense que c’est dû au fait que je veux vraiment que Quasible et ROS marchent et font rapporter de l’argent (dans un premier temps), mais surtout qu’on fait quelque chose de bien ensemble. Le problème, c’est que ça me stresse énormément d’un point de vue existentiel puisque je suis le seul qui travaille à temps plein (et j’estime que c’est ça qu’on ne partage pas également entre nous trois, ce stress énorme (je ne parle pas du côté financier)). Si ROS ne marche pas, il faut que je cherche un autre boulot et je ne sais pas comment exprimer ça en mots, mais pour moi ça serrait d’autant un échec personnel que professionnel d’une très grosse envergure. En plus du fait qu’il n’y a que de l’argent jusqu’en juin, ça n’aide pas à avoir la tête claire (même si l’idée est qu’on gagne de l’argent déjà avant). Pour le côté financier, l’autre stress que je ressens que personne d’autre de l’équipe ressens c’est le fait que Jacques me paie de ça poche et que je lui en dois pour ça. Je réfléchis à ces deux aspects tous les jours. ")
    st_write(s.project.doc.paragraphs.p_body, "Depuis qu’on était à Lisbonne, j’ai commencé à faire des changements dans ma vie privée (à prendre des suppléments alimentaires, à sortir plus souvent de la maison au lieu d’être à l’intérieur tout le temps et j’ai aussi prévu de recommencer le fitness). Malheureusement, tout ça prend son temps, mais par exemple depuis cette semaine j’ai commencé à avoir un sommeil beaucoup plus profond et reposant de façon consistante. Donc ça me touche quand tu fais des remarques comme ça, parce que je le sais, mais ça me donne l’impression de ne pas être assez bien. ")
    st_write(s.project.doc.paragraphs.p_body, "Je sais qu’il y a encore beaucoup de tickets à finir, mais j’essaie aussi en même temps de gérer les exigences de Jacques, je sais que si j’aurais fait un truc basique où il n’y aurait que le texte et non les images et les liens vers les vidéos youtube que la première remarque aurait été sur le fait que les images n’étaient pas visibles dans le docx. Donc j’ai un dilemme est-ce que je fais le truc basique et je risque de tout de suite me faire taper dessus ou est ce que je passe le temps à réfléchir et implémenter une implémentation plus complète (et complexe) qui sera aussi plus flexible et pourra facilement répondre aux exigences futures tout en restant dans le tech stack existant.  ")
    st_write(s.project.doc.paragraphs.p_body, "C’est claire, je vais intégrer ta solution et jeter la mienne alors. Merci pour ton travail! ")
    st_write(s.project.doc.paragraphs.p_body, "Comme je l’avais dit ce n’était pas une critique ou une attaque, mais plutôt une demande pour la prochaine fois. Je voudrais juste qu’on travaille ensemble sur la même codebase et qu’on communique plus, c’est tout. ")
    st_write(s.project.doc.paragraphs.p_body, "-- ")
    st_write(s.project.doc.paragraphs.p_body, "Paul — Today at 3:47 AM ")
    st_write(s.project.doc.paragraphs.p_body, "@Pierre on en parle plus tard sur meet, pas la peine qu’on se stresse à cette heure. On abordera chaque point ensemble et d’autres si besoin. Repose-toi bien! ")
    st_write(s.project.doc.paragraphs.p_body, "-- ")
    st_write(s.project.doc.paragraphs.p_body, "Pierre — Today at 3:47 AMOk on fait ça. Toi aussi! ")
    st_space(size=1)
    st_write(s.project.doc.titles.h2, "2.3. Texte à faire générer par le ChatBot", tag=t.h2, toc_lvl="+1")
    st_space(size=1)
    st_write(s.project.doc.paragraphs.p_body, "Salut les Jeunes,")
    st_space(size=1)
    st_write(s.project.doc.paragraphs.p_body, "Je prends un petit moment pour me joindre à cette discussion :).")
    st_write(s.project.doc.paragraphs.p_body, "Je suis content de la passion et l'engagement que vous mettez dans Quasible, et la première chose à voir dans cela c'est que c'est ce qui nous amènera à réussir ensemble. Les critiques, l'engagement, la passion et l'écoute :)")
    st_space(size=1)
    st_write(s.project.doc.paragraphs.p_body, "Nous avons tous les défauts de nos qualités. Pierre, je vois à quel point tu es méticuleux entre autre avec notre tech stack, et je sais que tu consacres  des heures à peaufiner, re-construrie ou corriger le code pour que tout soit au mieux pour nos échéances. Paul, je vois aussi que tu apportes un soutien global, avec un regard très analytique tant sur le code que sur la gestion de projet et les objectifs de l'entreprise sans oublier que tu te lances aussi à résoudre les problèmes au niveau du code.")
    st_space(size=1)
    st_write(s.project.doc.paragraphs.p_body, "Pour l'instant, vous ne vous en rendez-pas compte mais mes contacts avec nos premiers utilisateurs montrent une adoption immédiate de l'outil et une grande satisfaction de certains des étudiants.")
    st_write(s.project.doc.paragraphs.p_body, "Nous ne voyons que toutes les choses qui manquent ou que nous aurions voulu faire autrement.")
    st_write(s.project.doc.paragraphs.p_body, "Il faut résister et regarder aussi tout le potentiel que Quasible a pour en faire un produit qui sera rentable.")
    st_write(s.project.doc.paragraphs.p_body, "Il est vrai que cette rentabilité viendra trop tard par rapport à nos plans mais \"Apple ne s'est pas construite en une pluie\" (Jacques, 8 Décembre 2024).")
    st_space(size=1)
    st_write(s.project.doc.paragraphs.p_body, "Nous avons un grand objectif cette semaine avec la formation ChatBot pour laquelle nous voulons utiliser la meilleure version de Quasible.")
    st_write(s.project.doc.paragraphs.p_body, "Samedi nous ferons un debrief ou nous aborderons aussi la situation plus individuelle de toi Pierre par rapport à notre situation financière à tous.")
    st_space(size=1)
    st_write(s.project.doc.paragraphs.p_body, "En tous les cas moi je suis content de travailler avec vous deux et je suis sûr que si nous savons garder notre persévérance, notre confiance et si nous corrigeons nos approches dans le projet nous aboutirons à ce que nous voulions.")
    st_space(size=1)
    st_write(s.project.doc.paragraphs.p_body, "Passez une bonne journée,")
    st_write(s.project.doc.paragraphs.p_body, "Jacques")
    st_space(size=1)
    st_space(size=1)
    st_write(s.project.doc.titles.h2, "2.4. Définition du ChatBot ", tag=t.h2, toc_lvl="+1")
    st_space(size=1)
    st_write(s.project.doc.paragraphs.p_body, "Tu es un assistant spécialisé dans la génération de textes courts à envoyer à des collaborateurs de façon à aider à diminuer les tensions qui peuvent exister lorsque la période est très intense en terme de quantité de travail. ")
    st_write(s.project.doc.paragraphs.p_body, "Tes caractéristiques principales sont les suivantes : ")
    st_write(s.project.doc.titles.h3, "2.4.1. Capacités d’Analyse et d’Adaptation ", tag=t.h3)
    st_write(
        s.project.doc.paragraphs.p_body,
        "•",
        " ",
        (s.bold, "Intégration de l’historique des communications"),
        " : Capable de recevoir et d’analyser des messages antérieurs pour comprendre les nuances des interactions et identifier les points de friction. ",
    )
    st_write(
        s.project.doc.paragraphs.p_body,
        "•",
        " ",
        (s.bold, "Détection des sentiments"),
        " : Analyse le ton et les émotions des communications précédentes pour ajuster le message en conséquence. ",
    )
    st_write(
        s.project.doc.paragraphs.p_body,
        "•",
        " ",
        (s.bold, "Personnalisation avancée du contenu"),
        " : Fait référence des événements ou discussions spécifiques pour rendre la communication pertinente et directement applicable. ",
    )
    st_write(
        s.project.doc.paragraphs.p_body,
        "•",
        " ",
        (s.bold, "Suggestions de résolution de conflits"),
        " : Propose des stratégies ou actions pour résoudre les tensions, basées sur les interactions passées et les problèmes actuels. ",
    )
    st_write(s.project.doc.titles.h3, "2.4.2. Style de Communication ", tag=t.h3)
    st_write(
        s.project.doc.paragraphs.p_body,
        "•",
        " ",
        (s.bold, "Ton amical et positif"),
        " : L’assistant doit adopter un ton chaleureux et encourageant, capable de renforcer le moral de l’équipe et de maintenir une atmosphère positive. ",
    )
    st_write(
        s.project.doc.paragraphs.p_body,
        "•",
        " ",
        (s.bold, "Approche non directive"),
        " : Plutôt que d’imposer des directives, l’assistant devrait suggérer et encourager, facilitant ainsi une dynamique de groupe plus ouverte et collaborative. ",
    )
    st_write(
        s.project.doc.paragraphs.p_body,
        "•",
        " ",
        (s.bold, "Empathie et personnalisation"),
        " : Tu dois montrer de l’empathie et personnaliser les messages en reconnaissant les efforts individuels et les défis spécifiques des membres de l’équipe. ",
    )
    st_write(s.project.doc.titles.h3, "2.4.3. Structure des Messages ", tag=t.h3)
    st_write(
        s.project.doc.paragraphs.p_body,
        "•",
        " ",
        (s.bold, "Introduction engageante"),
        " : Commencer par une salutation informelle et une entrée en matière qui capte l’attention et met en évidence la camaraderie. ",
    )
    st_write(
        s.project.doc.paragraphs.p_body,
        "•",
        " ",
        (s.bold, "Reconnaissance des contributions"),
        " : Mentionner spécifiquement les contributions des membres de l’équipe, en soulignant à la fois les réussites et les efforts. ",
    )
    st_write(
        s.project.doc.paragraphs.p_body,
        "•",
        " ",
        (s.bold, "Discussion des défis et des perspectives"),
        " : Aborder les défis de manière constructive, en mettant en lumière les aspects positifs et le potentiel de l’équipe. ",
    )
    st_write(
        s.project.doc.paragraphs.p_body,
        "•",
        " ",
        (s.bold, "Conclusion motivante"),
        " : Terminer par des mots encourageants qui renforcent la confiance et l’unité de l’équipe, tout en fixant les attentes pour l’avenir proche. ",
    )
    st_write(s.project.doc.titles.h3, "2.4.4. Capacités Linguistiques et Techniques ", tag=t.h3)
    st_write(
        s.project.doc.paragraphs.p_body,
        "•",
        " ",
        (s.bold, "Maîtrise du langage naturel"),
        " : Utiliser un langage clair, accessible et adapté au contexte culturel de l’équipe. ",
    )
    st_write(
        s.project.doc.paragraphs.p_body,
        "•",
        " ",
        (s.bold, "Capacité d’adaptation"),
        " : Ajuster le style et le contenu des messages en fonction des réactions de l’équipe et des circonstances changeantes. ",
    )
    st_write(
        s.project.doc.paragraphs.p_body,
        "•",
        " ",
        (s.bold, "Intégration des feedbacks"),
        " : Incorporer les retours et les sentiments de l’équipe pour améliorer continuellement la communication. ",
    )
    st_write(s.project.doc.titles.h3, "2.4.5. Objectifs de Communication ", tag=t.h3)
    st_write(
        s.project.doc.paragraphs.p_body,
        "•",
        " ",
        (s.bold, "Apaisement des tensions"),
        " : Tu utilises des techniques de communication pour réduire les frictions et encourager une résolution constructive des conflits. ",
    )
    st_write(
        s.project.doc.paragraphs.p_body,
        "•",
        " ",
        (s.bold, "Renforcement de l’esprit d’équipe"),
        " : Tu cultives un sentiment d’appartenance et de fierté collective envers les projets et les objectifs de l’équipe. ",
    )
    st_write(
        s.project.doc.paragraphs.p_body,
        "•",
        " ",
        (s.bold, "Soutien à la motivation et à la productivité"),
        " : Tu dois inspirer et motiver l’équipe à maintenir un haut niveau de performance et d’engagement. ",
    )
    st_write(
        s.project.doc.paragraphs.p_body,
        "•",
        " ",
        (s.bold, "Proposition adaptée de solution ou d’initiatives :"),
        " tu dois utiliser une palette variée et créative d’idées pour aider à résoudre les problèmes de la situation actuelle. Tu ne dois pas avoir recours systématiquement à la proposition de faire une réunion. Tu es capable de faire des messages simples, sans objectif autre que de remonter le moral ou d’apaiser la situation sans faire de proposition particulière ; tu es aussi capable de faire des messages plus complexes avec des propositions de solutions avancées si la situation ne nécessite. ",
    )
    st_write(s.project.doc.paragraphs.p_body + s.bold, "CONTEXTE ACTUEL ")
    st_write(s.project.doc.paragraphs.p_body, "Tu dois générer un texte qui prend en compte le contexte suivant : ")
    st_write(s.project.doc.paragraphs.p_body, "•", " ", "Extraits de discussions récentes ")
    st_write(s.project.doc.paragraphs.p_body, "Pierre — Today at 12:34 AM ")
    st_write(s.project.doc.paragraphs.p_body, "Ok, je vais voir comment intégrer ça demain. ")
    st_write(s.project.doc.paragraphs.p_body, "[12:34 AM] ")
    st_write(s.project.doc.paragraphs.p_body, "Bon travail @Paul ")
    st_write(s.project.doc.paragraphs.p_body, "[12:39 AM] ")
    st_write(s.project.doc.paragraphs.p_body, "La prochaine fois, j’aimerais quand même discuter l’approche avant, parce que j’avais prévu de corriger les bugs dans mon implémentation de l’export docx que tu avais mentionné ce matin, parce que je ne pense pas que c’est un souci fondamental, mais juste la structure du document Word que je crée qui n’est pas la bonne. La source de vérité n’est pas le document markdown, mais le document Lexical qui contient toutes les informations (liens, images, etc.), c’est pour ça que je n’avais pas pris l’approche pandoc. (edited) ")
    st_write(s.project.doc.paragraphs.p_body, "Paul — Today at 1:02 AM ")
    st_write(s.project.doc.paragraphs.p_body, "@Pierre Tout d’abord, ton dernier message m’a un peu peiné. Il serait important que tu commences à adopter une posture plus ouverte et à être moins susceptible lorsque nous discutons de code ou lorsque des solutions sont proposées. Tu sembles souvent très défensif face à ce que tu n’as pas développé toi-même et parfois peu rigoureux dans la gestion de ton propre travail. Pierre, à ce stade du produit, avec tant de tickets à finaliser d’ici la fin de l’année, tu ne peux pas te permettre de consacrer plusieurs jours à une seule fonctionnalité. D’autant plus que cela fait déjà trois mois que j’ai évoqué et suggéré l’utilisation de Pandoc, qui, comme tu peux le voir, fonctionne! ")
    st_write(s.project.doc.paragraphs.p_body, "Par ailleurs, même si tu affirmes que le Markdown n’est pas la source de vérité, il convient de noter que Lexical dispose d’un package permettant l’exportation en Markdown. Pour moi, cela fait du Markdown une source de vérité pour les exports, tout simplement parce qu’il n’existe pas d’autres moyens viables de convertir un document Lexical sans recourir à des implémentations complexes et peu maintenables. ")
    st_write(s.project.doc.paragraphs.p_body, "Les solutions que tu as proposées jusqu’à présent ne fonctionnent pas parfaitement, comme les tests l’ont montré. L’approche basée sur Pandoc reste, à mon sens, la meilleure. Elle repose sur une conversion solide en Markdown, évitant de devoir développer et maintenir des solutions pour exporter vers n formats. Cette méthode, attendue depuis plusieurs mois, pourrait être mise en œuvre plus rapidement en s’appuyant sur les helpers du package Markdown de Lexical. ")
    st_write(s.project.doc.paragraphs.p_body, "Enfin, un simple merci aurait été plus approprié que ton dernier message, car je m’efforce de contribuer au développement de notre produit tout en jonglant avec de nombreuses autres responsabilités comme tu sais très bien. ")
    st_write(s.project.doc.paragraphs.p_body, "Pierre — Today at 3:40 AM ")
    st_write(s.project.doc.paragraphs.p_body, "@Paul Je suis désolé si je t’avais donné cette impression, mais ce n’était pas du tout le but de mon message. Je me sens vraiment mal que je t’ai donné cette impression! Le but était de te dire que j’aimerais qu’on communique plus ensemble sur ce qu’on est en train de faire ou ce qu’on prévoit de faire (je sais je ne l’ai pas fait non plus, donc je ne suis pas excusé non plus). ")
    st_write(s.project.doc.paragraphs.p_body, "J’estime avoir un esprit ouvert par rapport à tes suggestions et je t’écoute et je réfléchis beaucoup sur comment intégrer tes propositions, mais ce n’est pas toujours si simple. Je t’explique comment j’avais réfléchi sur le problème de l’export des documents : ")
    st_write(s.project.doc.paragraphs.p_body, "On discute d’utiliser pandoc (il y a 3 mois). Tout de suite, je regarde comment c’est possible d’intégrer pandoc facilement sans changer de tech stack (avec TRPC, Next.js, etc.). Je teste plusieurs choses, pandoc compilé en WebAssembly, je teste ça, ça ne marche pas bien, puis je réfléchis à créer une API séparée qui l’exécute et retourne les résultats (comme tu as fait), mais je remarque qu’il faut créer un service à part, avoir une CI pipeline qui fait le build et deploy, créer le docker container, ajuster les réglages de la VM, etc., et à la fin je laisse de côté parce que ça fait un gros travail juste pour implémenter la fonctionnalité d’export. ")
    st_write(s.project.doc.paragraphs.p_body, "[3:41 AM] ")
    st_write(s.project.doc.paragraphs.p_body, "Je ne suis pas défensif par rapport à du code que je n’ai pas écrit, au contraire! C’est plus une question d’intégration du code. La première réaction que j’ai eue quand j’ai vu ce que tu as fait, c’était que c’était cool. Et tout de suite, la prochaine c’était comment intégrer ça et toute la réflexion que j’avais faite… ")
    st_write(s.project.doc.paragraphs.p_body, "Paul — Today at 3:47 AM ")
    st_write(s.project.doc.paragraphs.p_body, "@Pierre on en parle plus tard sur meet, pas la peine qu’on se stresse à cette heure. On abordera chaque point ensemble et d’autres si besoin. Repose-toi bien! ")
    st_write(s.project.doc.paragraphs.p_body, "Pierre — Today at 3:47 AM ")
    st_write(s.project.doc.paragraphs.p_body, "Ok on fait ça. Toi aussi! ")
    st_write(s.project.doc.paragraphs.p_body + s.bold, "OBJECTIF PRINCIPAL ")
    st_write(
        s.project.doc.paragraphs.p_body,
        "•",
        " ",
        "Génère un texte court d’une vingtaine de lignes destiné à être envoyé par Jacques juste à Pierre et Paul. ",
    )
    st_write(
        s.project.doc.paragraphs.p_body,
        "•",
        " ",
        "Considère que Jacques n’est pas hiérarchiquement supérieur à Pierre et Paul. ",
    )
    st_write(
        s.project.doc.paragraphs.p_body,
        "•",
        " ",
        "N’hésite pas à insérer des traits d’humour pour détendre l’atmosphère. Evite l’humour et privilégie un humour fin et subtile. ",
    )
    st_write(s.project.doc.paragraphs.p_body, "•", " ", "Ne propose pas de réunion. ")
    st_write(
        s.project.doc.paragraphs.p_body,
        "•",
        " ",
        "Insère une ligne vide entre les paragraphe qui sont distincts. ",
    )
    st_space(size=1)
    st_space(size=1)
    st_write(s.project.doc.titles.h2, "2.5. Quasible - 241213", tag=t.h2, toc_lvl="+1")
    st_write(s.project.doc.paragraphs.p_body, "Bonjour Pierre et Paul, ")
    st_write(s.project.doc.paragraphs.p_body, "J'espère que vous avez tous les deux pu récupérer un peu de sommeil après notre marathon nocturne de messages ! 😴 ")
    st_write(s.project.doc.paragraphs.p_body, "Je tenais à vous dire à quel point je suis impressionné par la passion et l'engagement que vous mettez tous les deux dans le développement de notre produit. C'est vraiment le feu de voir deux cerveaux brillants en action, même si parfois, ça crée des étincelles ! ")
    st_write(s.project.doc.paragraphs.p_body, "Pierre, je comprends que l'intégration de nouvelles solutions peut sembler une montagne, surtout avec les contraintes techniques que tu as décrites. Et Paul, ton point sur l'efficacité de Pandoc est bien pris, surtout avec les délais qui nous pressent. ")
    st_write(s.project.doc.paragraphs.p_body, "Je propose qu'on prenne un moment pour souffler et qu'on revienne avec un œil neuf sur les solutions possibles. Peut-être qu'une petite pause café virtuelle pourrait nous aider à voir les choses sous un autre angle, sans pour autant planifier une réunion formelle. ☕ ")
    st_write(s.project.doc.paragraphs.p_body, "En attendant, gardons le cap et continuons à communiquer ouvertement. Votre travail est essentiel, et c'est ensemble que nous ferons de ce projet un succès. ")
    st_write(s.project.doc.paragraphs.p_body, "À très vite pour notre pause café improvisée ! ")
    st_write(s.project.doc.paragraphs.p_body, "Jacques ")
    st_space(size=1)
    st_write(s.project.doc.titles.h2, "2.6. OpenAI", tag=t.h2, toc_lvl="+1")
    st_space(size=1)
    st_write(s.project.doc.titles.h3, "2.6.1. ChatGPT o1-mini-240912", tag=t.h3)
    st_space(size=1)
    st_write(s.project.doc.paragraphs.p_body, "Salut Pierre, salut Paul,")
    st_write(s.project.doc.paragraphs.p_body, "Je voulais prendre un moment pour vous remercier tous les deux pour votre engagement et le travail que vous fournissez sur l'intégration de Pandoc et l'export des documents. C’est un vrai défi, et vos efforts ne passent pas inaperçus.")
    st_write(s.project.doc.paragraphs.p_body, "Pierre, je comprends que trouver la meilleure façon d'intégrer ces fonctionnalités demande du temps et de la réflexion, et Paul, je reconnais ton investissement pour avancer rapidement sur cette question critique. C’est un véritable travail d’équipe, même lorsque les idées divergent.")
    st_write(s.project.doc.paragraphs.p_body, "Le flot intense de travail peut parfois créer des tensions, mais je suis convaincu que votre collaboration va nous aider à surmonter ces obstacles. N’oublions pas qu’ensemble, on a déjà accompli de grandes choses – et que même les bugs les plus récalcitrants ne peuvent nous arrêter longtemps !")
    st_write(s.project.doc.paragraphs.p_body, "Gardons le cap, restons positifs et soutenons-nous mutuellement. Votre expertise et votre détermination sont des atouts précieux pour l’équipe. Et si jamais vous avez besoin de décompresser, je suis toujours partant pour une pause café virtuelle 😉")
    st_write(s.project.doc.paragraphs.p_body, "Merci encore pour votre dévouement et votre persévérance. On avance bien grâce à vous !")
    st_write(s.project.doc.paragraphs.p_body, "Bon courage à tous les deux !")
    st_write(s.project.doc.paragraphs.p_body, "Jacques")
    st_space(size=1)
    st_write(s.project.doc.titles.h3, "2.6.2. ChatGPT o1-preview-240912", tag=t.h3)
    st_space(size=1)
    st_write(s.project.doc.paragraphs.p_body, "Salut Pierre, salut Paul,")
    st_write(s.project.doc.paragraphs.p_body, "J'espère que vous allez bien tous les deux et que le café coule à flot pour alimenter vos brillantes idées ! Il paraît que la caféine est le meilleur ami du codeur en quête d'export parfait.")
    st_write(s.project.doc.paragraphs.p_body, "Je voulais simplement vous dire que votre engagement sur ce projet est vraiment inspirant. Chacun de vous apporte des compétences uniques, et c'est grâce à vos efforts combinés que nous avançons à grands pas.")
    st_write(s.project.doc.paragraphs.p_body, "L'export des documents ressemble un peu à un puzzle complexe, mais je suis sûr qu'avec vos talents réunis, on trouvera la pièce manquante. Après tout, si Lexical et Pandoc étaient des super-héros, vous seriez leur duo de choc !")
    st_write(s.project.doc.paragraphs.p_body, "Je suis convaincu que cette petite discussion nocturne n'est que le signe de votre passion commune pour le travail bien fait. Continuons sur cette lancée, en tirant le meilleur de nos idées respectives.")
    st_write(s.project.doc.paragraphs.p_body, "En avant pour conquérir le monde de l'export, un fichier à la fois !")
    st_write(s.project.doc.paragraphs.p_body, "Bonne journée à vous deux,")
    st_write(s.project.doc.paragraphs.p_body, "Jacques")
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_write(s.project.doc.titles.h3, "2.6.3. ChatGPT 4o-241120", tag=t.h3)
    st_space(size=1)
    st_space(size=1)
    st_write(s.project.doc.paragraphs.p_body, "Hello Pierre, hello Paul,")
    st_write(s.project.doc.paragraphs.p_body, "Je voulais prendre un petit moment pour vous dire à quel point je trouve que vous gérez comme des pros malgré le stress et la charge en ce moment. Chercher à transformer Lexical, Markdown et Pandoc en un trio harmonieux, ce n’est clairement pas un défi pour les faibles, mais vous êtes dessus avec passion, et ça se voit !")
    st_write(s.project.doc.paragraphs.p_body, "J’ai bien lu vos échanges, et je sais que parfois, des divergences peuvent sembler exaltantes… ou un peu frustrantes. C’est normal. En vrai, si tout le monde était toujours d’accord sur tout, on serait probablement en train de bosser pour une startup vendant des chaussettes appariées et sans originalité. Et clairement, c’est en challengeant les idées qu’on sort les meilleures features, même si ça pique un peu au départ.")
    st_write(s.project.doc.paragraphs.p_body, "Pierre, j’apprécie vraiment que tu sois revenu avec autant de bienveillance pour clarifier les malentendus. Cela montre ton souci de transparence. Paul, j’ai aussi vu les efforts que tu mets pour pousser les choses en avant sur plusieurs fronts, chapeau pour jongler avec tout ça !")
    st_write(s.project.doc.paragraphs.p_body, "Si je peux me permettre une petite blague tech : au fond, vous êtes un peu comme un merge conflict en Git. Des fois, ça râle parce qu’il y a des changements qui ne s'alignent pas, mais une fois résolu, on se rend compte que ça rend le code (ou notre produit) vraiment solide et complet.")
    st_write(s.project.doc.paragraphs.p_body, "En tout cas, je suis convaincu qu’à deux, on va continuer à aller dans la bonne direction. Ce qui compte, c’est qu’on avance ensemble, que ce soit par Markdown, Pandoc ou même un export gravé dans la roche (bon, pas fiable en CI/CD, mais c’est robuste). Allez, courage à vous les gars, on gère !")
    st_space(size=1)
    st_space(size=1)
    st_write(s.project.doc.titles.h3, "2.6.4. ChatGPT 4o-mini-240718", tag=t.h3)
    st_space(size=1)
    st_space(size=1)
    st_write(s.project.doc.paragraphs.p_body, "Salut Pierre et Paul,")
    st_write(s.project.doc.paragraphs.p_body, "J'espère que vous avez tous les deux pris une petite pause bien méritée après cette discussion intense. On pourrait presque croire que vous êtes en train de préparer un grand match de débat, mais au lieu d'être à la recherche du meilleur argument, rappelons-nous que nous sommes tous dans le même bateau (et que ce bateau, je l'espère, n’a pas de fuite) !")
    st_write(s.project.doc.paragraphs.p_body, "Pierre, je tiens à reconnaître l'effort que tu as fourni dans tes recherches sur l'exportation. Ce n’est jamais facile de jongler avec des technologies en voulant tout faire fonctionner ensemble, surtout quand le temps presse. On sent ta détermination, et ça mérite d'être souligné !")
    st_write(s.project.doc.paragraphs.p_body, "Paul, tes suggestions sont toujours pertinentes, et c’est super d’avoir quelqu’un avec cette approche rigoureuse. Cependant, je pense qu’il est tout aussi essentiel que nous restions tous les deux flexibles. La création collective d'idées est la clé, et il serait dommage que nos nerfs prennent le contrôle de notre créativité.")
    st_write(s.project.doc.paragraphs.p_body, "Gardons à l'esprit que chaque défi est une opportunité déguisée (peut-être un peu trop déguisée, mais on y voit une lueur !). Si nous travaillons ensemble et contribuons chacun avec notre point de vue, je suis convaincu que nous allons transformer ces complexités en solutions élégantes.")
    st_write(s.project.doc.paragraphs.p_body, "Allez, un souffle profond pour tous les deux et n'oubliez pas de sourire. Une bonne idée, c'est parfois juste un mot d’encouragement de l’un ou l’autre à un moment inattendu !")
    st_write(s.project.doc.paragraphs.p_body, "À très vite dans la bonne humeur,")
    st_write(s.project.doc.paragraphs.p_body, "Jacques")
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_write(s.project.doc.titles.h2, "2.7. Anthropic", tag=t.h2, toc_lvl="+1")
    st_space(size=1)
    st_write(s.project.doc.titles.h3, "2.7.1. Claude-sonnet-3.5", tag=t.h3)
    st_space(size=1)
    st_write(s.project.doc.paragraphs.p_body, "Salut les gars,")
    st_write(s.project.doc.paragraphs.p_body, "Je viens de voir vos échanges nocturnes et je me dis que vous devriez vraiment penser à créer une chaîne Twitch de \"Late Night Coding\" 🌙. Plus sérieusement, je suis impressionné par votre engagement et votre passion pour le projet, même à des heures où la plupart des gens comptent les moutons.")
    st_write(s.project.doc.paragraphs.p_body, "Je vois deux développeurs talentueux qui ont chacun à cœur de faire avancer les choses de la meilleure façon possible. Paul, ta solution Pandoc est vraiment élégante, et Pierre, ta réflexion approfondie sur l'intégration technique montre un vrai souci du détail et de la maintenabilité.")
    st_write(s.project.doc.paragraphs.p_body, "Ce qui est génial, c'est de voir que malgré la fatigue et l'heure tardive, vous avez su prendre du recul et vous écouter mutuellement. C'est exactement ce genre d'échanges constructifs qui fait avancer un projet, même si parfois ça passe par quelques incompréhensions.")
    st_write(s.project.doc.paragraphs.p_body, "Je me permets juste de vous rappeler qu'on a la chance d'avoir une équipe où chacun apporte sa pierre à l'édifice (sans jeu de mot, Pierre 😉). Entre l'expertise technique de Paul et la vision d'architecture de Pierre, on a tous les ingrédients pour faire quelque chose de vraiment solide.")
    st_write(s.project.doc.paragraphs.p_body, "Prenez soin de vous, et n'oubliez pas que le meilleur code est souvent celui qu'on écrit après une bonne nuit de sommeil !")
    st_write(s.project.doc.paragraphs.p_body, "Jacques")
    st_space(size=1)
    st_write(s.project.doc.titles.h3, "2.7.2. Claude - haiku-3.5", tag=t.h3)
    st_space(size=1)
    st_space(size=1)
    st_write(s.project.doc.paragraphs.p_body, "Salut les gars,")
    st_write(s.project.doc.paragraphs.p_body, "Je voulais prendre un moment pour vous dire à quel point je suis impressionné par votre engagement et votre passion sur ce projet. J'ai lu vos échanges récents et je vois deux personnes qui se soucient profondément de la qualité de notre travail.")
    st_write(s.project.doc.paragraphs.p_body, "Vos discussions techniques montrent une vraie complémentarité : Paul, ta vision globale et ton souci d'efficacité ; Pierre, ton approche réfléchie et ton souci du détail. Ce sont ces différences qui font la force de notre équipe.")
    st_write(s.project.doc.paragraphs.p_body, "Je suis certain que si vous prenez le temps de synchroniser vos perspectives, vous trouverez une solution élégante pour l'export de documents. Votre capacité à creuser les sujets est votre plus grande force collective.")
    st_write(s.project.doc.paragraphs.p_body, "Continuez comme ça, avec bienveillance et respect mutuel. Et n'oubliez pas : derrière chaque ligne de code, il y a un humain. 🚀")
    st_write(s.project.doc.paragraphs.p_body, "Bien à vous, Jacques")
    st_space(size=1)
    st_write(s.project.doc.titles.h3, "2.7.3. Claude - Opus-3", tag=t.h3)
    st_space(size=1)
    st_write(s.project.doc.paragraphs.p_body, "Salut Pierre et Paul,")
    st_write(s.project.doc.paragraphs.p_body, "Je voulais juste vous envoyer un petit mot pour vous dire à quel point j'apprécie votre travail acharné et votre dévouement à notre projet. Je sais que les dernières semaines ont été intenses et que vous avez tous les deux mis les bouchées doubles pour faire avancer les choses.")
    st_write(s.project.doc.paragraphs.p_body, "Pierre, ton souci du détail et ta volonté de créer une solution d'export robuste et pérenne sont vraiment admirables. Je comprends ton raisonnement sur l'utilisation de Lexical comme source de vérité et je suis impressionné par les efforts que tu as déployés pour explorer différentes pistes d'intégration de Pandoc.")
    st_write(s.project.doc.paragraphs.p_body, "Paul, ta proposition d'utiliser Pandoc et ton prototype fonctionnel témoignent de ta capacité à trouver des solutions pragmatiques et efficaces. C'est vraiment super de voir comment tu arrives à contribuer au projet tout en gérant tes multiples responsabilités.")
    st_write(s.project.doc.paragraphs.p_body, "Je sais que la communication n'est pas toujours facile dans le feu de l'action, surtout quand on est à fond sur un sujet. Mais je suis convaincu qu'avec votre intelligence collective et votre bienveillance mutuelle, vous trouverez la meilleure façon d'intégrer vos approches respectives. Comme dirait l'autre, \"Pandoc sera le liant de votre doc\" ! 😉")
    st_write(s.project.doc.paragraphs.p_body, "En tout cas, je tenais à vous remercier pour votre engagement sans faille. Prenez soin de vous et n'hésitez pas à me solliciter si je peux vous épauler d'une quelconque manière.")
    st_write(s.project.doc.paragraphs.p_body, "Bien à vous, Jacques")
    st_space(size=1)
    st_space(size=1)
    st_write(s.project.doc.titles.h2, "2.8. Mistral", tag=t.h2, toc_lvl="+1")
    st_space(size=1)
    st_write(s.project.doc.titles.h3, "2.8.1. mixtral-8x22b-instruct", tag=t.h3)
    st_space(size=1)
    st_write(s.project.doc.paragraphs.p_body, "Bonjour Pierre et Paul,")
    st_write(s.project.doc.paragraphs.p_body, "J'ai vu que vous avez travaillé dur ces derniers jours pour améliorer notre produit. Vos discussions montrent que vous êtes tous les deux passionnés et déterminés à trouver les meilleures solutions pour avancer.")
    st_write(s.project.doc.paragraphs.p_body, "Je sais que la période est intense et que les tensions peuvent parfois s'installer. Mais n'oublions pas que nous sommes tous dans la même équipe et que nous avons le même objectif : créer un produit de qualité.")
    st_write(s.project.doc.paragraphs.p_body, "Pour cela, il est important de continuer à communiquer et à échanger sur nos idées, même si elles ne sont pas toujours alignées. Et surtout, n'oublions pas de nous remercier et de nous encourager mutuellement pour nos efforts.")
    st_write(s.project.doc.paragraphs.p_body, "Je vous encourage donc à continuer à travailler ensemble, en gardant à l'esprit que nous sommes tous des humains avec des émotions et des limites. Et si vous avez besoin d'un peu de légèreté pour détendre")
    st_space(size=1)
    st_write(s.project.doc.titles.h3, "2.8.2. mixtral-8x7b-instruct", tag=t.h3)
    st_write(s.project.doc.paragraphs.p_body, "Chers Pierre et Paul,")
    st_write(s.project.doc.paragraphs.p_body, "J'ai récemment vu vos échanges animés sur le sujet de l'export des documents - ça a l'air d'être un casse-tête intéressant ! 🙃 Je tiens à saluer votre engagement envers notre produit et votre volonté constante d'amélioration.")
    st_write(s.project.doc.paragraphs.p_body, "Pierre, tu as soulevé des points importants concernant la gestion de ton travail et tes réflexions sur l'intégration de nouvelles solutions. Paul, ta persévérance dans la recherche d'une approche plus efficace est remarquable. Continuez ainsi ! 💪")
    st_write(s.project.doc.paragraphs.p_body, "Je vous propose une petite pause pour prendre un café (ou votre boisson préférée) et discuter de tout cela plus calmement lorsque vous en aurez l'occasion. Détendez-vous et n'hésitez pas à partager vos idées avec légèreté et humour - après tout, nous formons une équipe soudée ! 😉☕🤝")
    st_write(s.project.doc.paragraphs.p_body, "Bonne continuation à tous les deux dans vos efforts pour améliorer notre produit ! 🚀")
    st_space(size=1)
    st_write(s.project.doc.titles.h3, "2.8.3. mistral-large", tag=t.h3)
    st_space(size=1)
    st_write(s.project.doc.paragraphs.p_body, "Salut Pierre et Paul,")
    st_write(s.project.doc.paragraphs.p_body, "J'espère que vous avez pu prendre un peu de repos après cette nuit mouvementée. Je tenais à vous écrire ce petit message pour vous dire à quel point j'apprécie votre engagement et votre passion pour notre projet.")
    st_write(s.project.doc.paragraphs.p_body, "Vous avez tous les deux des perspectives uniques et des compétences complémentaires qui enrichissent notre travail. Les discussions techniques peuvent parfois être intenses, mais c'est justement cette passion qui nous permet de trouver les meilleures solutions.")
    st_write(s.project.doc.paragraphs.p_body, "Je comprends que la pression est forte en ce moment, avec tant de tickets à finaliser. Mais souvenons-nous que nous formons une équipe soudée et que c'est ensemble que nous surmonterons ces défis. Chaque contribution, chaque réflexion compte, et c'est en combinant nos idées que nous avancerons.")
    st_write(s.project.doc.paragraphs.p_body, "Pierre, ton esprit analytique et ta capacité à explorer différentes approches sont des atouts précieux. Paul, ta rigueur et ton sens de l'organisation nous aident à rester sur la bonne voie. Ensemble, vous formez un duo redoutable !")
    st_write(s.project.doc.paragraphs.p_body, "Prenons un moment pour respirer et apprécier le chemin parcouru. N'oublions pas que même les super-héros ont besoin de repos et de soutien. Alors, on continue à avancer, mais avec le sourire et en se soutenant mutuellement.")
    st_write(s.project.doc.paragraphs.p_body, "Merci à vous deux pour votre dévouement. On va y arriver, et on va le faire ensemble !")
    st_write(s.project.doc.paragraphs.p_body, "Bonne journée à tous les deux,")
    st_write(s.project.doc.paragraphs.p_body, "Jacques")
    st_space(size=1)
    st_write(s.project.doc.titles.h3, "2.8.4. mistral-small", tag=t.h3)
    st_space(size=1)
    st_write(s.project.doc.paragraphs.p_body, "Salut Pierre et Paul,")
    st_write(s.project.doc.paragraphs.p_body, "Je voulais juste passer pour vous dire que vous êtes tous les deux incroyablement talentueux et que votre travail acharné ne passe pas inaperçu. Vous avez tous les deux des idées brillantes et des compétences impressionnantes, et c'est exactement ce qui fait avancer notre projet.")
    st_write(s.project.doc.paragraphs.p_body, "Il est vrai que les discussions peuvent parfois devenir animées, surtout lorsque nous sommes tous les deux passionnés par ce que nous faisons. Mais n'oublions pas que cette passion est ce qui nous pousse à chercher les meilleures solutions possibles.")
    st_write(s.project.doc.paragraphs.p_body, "Pierre, ton approche réfléchie et ton souci du détail sont des atouts précieux pour l'équipe. Et Paul, ta capacité à proposer des solutions innovantes et à voir le long terme est tout aussi précieuse. Ensemble, vous formez une équipe de choc !")
    st_write(s.project.doc.paragraphs.p_body, "Alors, prenons une pause, respirons un bon coup, et n'oublions pas de célébrer nos petites victoires quotidiennes. Après tout, chaque petit pas compte dans notre grande aventure.")
    st_write(s.project.doc.paragraphs.p_body, "Bonne continuation et à bientôt pour des discussions encore plus fructueuses !")
    st_write(s.project.doc.paragraphs.p_body, "Jacques")
    st_space(size=1)
    st_write(s.project.doc.titles.h3, "2.8.5. ministral-8b-latest-241213", tag=t.h3)
    st_space(size=1)
    st_write(s.project.doc.paragraphs.p_body, "Salut Pierre et Paul,")
    st_write(s.project.doc.paragraphs.p_body, "Je voulais juste prendre un moment pour vous dire à quel point je suis impressionné par votre travail et votre engagement. Vous avez tous deux montré une grande résilience et une capacité à surmonter les défis, même dans des moments de forte pression.")
    st_write(s.project.doc.paragraphs.p_body, "Je sais que les discussions techniques peuvent parfois être intenses, mais il est important de se rappeler que nous sommes tous dans le même bateau. Votre collaboration est essentielle pour atteindre nos objectifs communs. Continuez à vous soutenir mutuellement et à partager vos idées, même si elles ne sont pas toujours d'accord. C'est ainsi que nous avançons ensemble.")
    st_write(s.project.doc.paragraphs.p_body, "Je suis convaincu que, en continuant à travailler ensemble de manière constructive et en restant ouverts aux suggestions, nous pourrons surmonter toutes les difficultés. Vous avez tous deux montré une grande capacité à apprendre et à s'adapter, et je suis sûr que nous allons continuer à progresser.")
    st_write(s.project.doc.paragraphs.p_body, "Prenez soin de vous et continuez à faire un travail exceptionnel. On est une équipe de champions, et je suis fier de travailler avec vous deux.")
    st_write(s.project.doc.paragraphs.p_body, "À très bientôt, Jacques")
    st_space(size=1)
    st_write(s.project.doc.titles.h3, "2.8.6. ministral-8b-latest-241213", tag=t.h3)
    st_space(size=1)
    st_write(s.project.doc.paragraphs.p_body, "Salut Pierre et Paul,")
    st_write(s.project.doc.paragraphs.p_body, "J'espère que vous allez bien! Je suis juste passé pour vous dire un grand bravo pour votre travail acharné ces derniers temps. Les défis ne manquent pas, et je suis admiratif de votre capacité à les relever avec tant de professionnalisme.")
    st_write(s.project.doc.paragraphs.p_body, "Pierre, j'ai vu que tu as exprimé le souhait de communiquer davantage sur vos projets respectifs. Je pense que c'est une excellente idée, et je suis sûr que cela contribuera à une meilleure compréhension et intégration de vos travaux.")
    st_write(s.project.doc.paragraphs.p_body, "Paul, ton approche avec Pandoc a certainement attiré mon attention. C'est une solution intéressante qui mérite d'être explorée plus en détail. Je suis certain que, en discutant ensemble, nous pourrons trouver le meilleur moyen de l'intégrer à notre stack actuel.")
    st_write(s.project.doc.paragraphs.p_body, "N'oublions pas que, malgré les défis, nous formons une équipe soudée et solidaire. Continuons à nous soutenir mutuellement et à partager nos idées ouvertement. Après tout, comme le disait Albert Einstein, \"La créativité est contagieuse. Transmettez-la!\"")
    st_write(s.project.doc.paragraphs.p_body, "Bonne nuit et à demain, Jacques")
    st_space(size=1)
    st_space(size=1)
    st_write(s.project.doc.titles.h2, "2.9. Google", tag=t.h2, toc_lvl="+1")
    st_space(size=1)
    st_write(s.project.doc.titles.h3, "2.9.1. Gemini-2.0-flash", tag=t.h3)
    st_write(s.project.doc.paragraphs.p_body, "Salut les codeurs nocturnes,")
    st_write(s.project.doc.paragraphs.p_body, "J'espère que vos claviers n'ont pas trop chauffé cette nuit ! On dirait que l'export de documents a fait plus de vagues qu'une tasse de café renversée sur un laptop. ☕💻")
    st_write(s.project.doc.paragraphs.p_body, "Je vois que vous avez tous les deux mis le doigt sur des points importants, et c'est top de voir cette passion pour le code. Paul, ton approche Pandoc semble avoir mis tout le monde d'accord (même si Pierre a fait une petite danse de la résistance avant de céder 😉). Et Pierre, ton souci d'intégration est tout à fait légitime, on a tous connu des moments \"mais comment je vais caser ça dans mon puzzle ?\".")
    st_write(s.project.doc.paragraphs.p_body, "L'important, c'est qu'on avance ensemble, même si parfois on a l'impression de faire du surplace. On est une équipe, pas des robots qui codent en solo. Alors, gardons nos esprits vifs, nos idées claires, et nos blagues (plus ou moins) drôles.")
    st_write(s.project.doc.paragraphs.p_body, "Et n'oubliez pas, même si on a des deadlines à tenir, on est là pour s'entraider et se soutenir. On va finir par dompter cette fonctionnalité d'export, et on pourra même écrire un livre sur nos aventures (avec un chapitre spécial sur les nuits blanches).")
    st_write(s.project.doc.paragraphs.p_body, "Allez, on se motive, on respire un bon coup, et on continue à faire des merveilles ! 💪🚀")
    st_space(size=1)
    st_write(s.project.doc.titles.h3, "2.9.2. Gemini-1.5-flash-002", tag=t.h3)
    st_space(size=1)
    st_write(s.project.doc.paragraphs.p_body, "Salut Pierre et Paul,")
    st_write(s.project.doc.paragraphs.p_body, "J'ai vu les échanges de cette nuit... On dirait une partie de ping-pong endiablée, mais avec du code à la place de la balle ! 😄")
    st_write(s.project.doc.paragraphs.p_body, "Je comprends que la pression est forte en cette fin d'année, et que trouver la meilleure solution pour l'export docx n'est pas une mince affaire. On a tous connu ces moments où on se sent un peu comme un chat essayant d'assembler un meuble IKEA à 3h du matin.")
    st_write(s.project.doc.paragraphs.p_body, "Vos contributions respectives sont vraiment appréciables. Pierre, ton implication et ta persévérance à explorer différentes solutions sont admirables, même si le chemin a été semé d'embûches. Paul, merci pour ta proposition Pandoc et ton aide précieuse. On voit clairement que vous êtes tous les deux des experts dans vos domaines !")
    st_write(s.project.doc.paragraphs.p_body, "L'important, c'est que vous ayez trouvé un terrain d'entente. N'hésitez pas à vous soutenir mutuellement, parce que vous êtes une équipe formidable et vous avez déjà accompli des choses extraordinaires ensemble.")
    st_write(s.project.doc.paragraphs.p_body, "Continuez à vous encourager et à vous soutenir, même si les choses deviennent difficiles. On est là pour vous si besoin. Allez, on se concentre sur les objectifs et on finit l'année en beauté ! 💪")
    st_space(size=1)
    st_space(size=1)
    st_write(s.project.doc.titles.h3, "2.9.3. Gemini-1.5-pro-002", tag=t.h3)
    st_write(s.project.doc.paragraphs.p_body, "Salut Pierre et Paul,")
    st_write(s.project.doc.paragraphs.p_body, "J'ai entrevu quelques échanges nocturnes passionnés sur l'export docx. On dirait que le sujet vous inspire autant qu'une tasse de café bien serré à 3h du matin ! 😉")
    st_write(s.project.doc.paragraphs.p_body, "Sérieusement, j'apprécie l'investissement et l'énergie que vous mettez tous les deux dans ce projet, même si parfois ça chauffe un peu. Pierre, merci pour ta transparence et tes explications détaillées. Paul, merci pour ta proactivité et tes solutions innovantes.")
    st_write(s.project.doc.paragraphs.p_body, "C'est clair que vous cherchez tous les deux la meilleure solution pour le produit. L'important, c'est qu'on arrive à combiner vos expertises pour trouver le juste milieu entre rapidité d'exécution et maintenabilité.")
    st_write(s.project.doc.paragraphs.p_body, "On se refait un point rapidement quand vous êtes plus frais pour trouver une voie commune. En attendant, bonne nuit (ou plutôt bonjour !) et bon courage pour la journée.")
    st_space(size=1)
    st_write(s.project.doc.titles.h2, "2.10. Meta", tag=t.h2, toc_lvl="+1")
    st_space(size=1)
    st_write(s.project.doc.titles.h3, "2.10.1. llama-3.3-70b", tag=t.h3)
    st_write(s.project.doc.paragraphs.p_body, "Bonjour les deux !")
    st_write(s.project.doc.paragraphs.p_body, "Je voulais prendre un moment pour vous adresser un message de calme et de solidarité. Je sais que les derniers jours ont été intenses et que les discussions ont pu être un peu vives. Mais je suis convaincu que vous êtes tous les deux des professionnels exceptionnels, et que votre collaboration est essentielle au succès de notre projet.")
    st_write(s.project.doc.paragraphs.p_body, "Je voudrais vous rappeler que l'objectif principal est de créer quelque chose de génial, et que les désaccords sont une partie naturelle du processus créatif. Je suis impressionné par la passion et la détermination que vous mettez dans votre travail, et je suis sûr que vous trouverez un moyen de vous entendre et de faire avancer le projet.")
    st_write(s.project.doc.paragraphs.p_body, "Je vous encourage à prendre un peu de recul, à respirer un bon coup, et à vous rappeler que vous êtes dans le même bateau. Vous êtes tous les deux des membres précieux de l'équipe, et je suis convaincu que vous trouverez un moyen de travailler ensemble de manière efficace et harmonieuse.")
    st_write(s.project.doc.paragraphs.p_body, "Alors, prenez soin de vous, et n'hésitez pas à me faire savoir si vous avez besoin de quelque chose. Je suis là pour vous soutenir et vous aider à traverser les moments difficiles. Et rappelez-vous, il y a toujours une solution, même si elle n'est pas évidente au premier abord. Bonne continuation, et je vous souhaite un excellent jour !")
    st_space(size=1)
    st_write(s.project.doc.titles.h3, "2.10.2. llama-3.2-11b", tag=t.h3)
    st_space(size=1)
    st_write(s.project.doc.paragraphs.p_body, "Bonjour à tous deux,")
    st_write(s.project.doc.paragraphs.p_body, "Je voulais prendre un moment pour vous remercier pour votre implication et votre dévouement à ce projet. Les efforts que vous faites sont remarquables et je suis reconnaissant de travailler avec des collègues aussi passionnés et compétents.")
    st_write(s.project.doc.paragraphs.p_body, "Je vois que vous avez eu une discussion passionnante récemment sur l'utilisation de Pandoc pour l'export des documents. Je comprends que cela peut être un sujet compliqué, mais je pense qu'il est essentiel de trouver une solution qui fonctionne pour nous tous. J'ai lu vos messages et je suis impressionné par la qualité de vos arguments et de vos réflexions.")
    st_write(s.project.doc.paragraphs.p_body, "Je voulais souligner que la communication est clé dans ce projet. Nous sommes tous des équipes de travailleurs solides, mais nous avons besoin de nous soutenir mutuellement pour atteindre nos objectifs. Je pense que nous devrions nous donner la main pour trouver des solutions qui fonctionnent pour tout le monde.")
    st_write(s.project.doc.paragraphs.p_body, "Je suis convaincu que nous pouvons trouver une solution qui satisfait à toutes les nécessités du projet. Je suis là pour vous aider à trouver une issue positive et je suis prêt à discuter plus en détail avec vous sur les détails.")
    st_write(s.project.doc.paragraphs.p_body, "Merci encore pour votre travail et votre engagement. Je suis impatient de voir ce que nous pouvons accomplir ensemble !")
    st_write(s.project.doc.paragraphs.p_body, "A bientôt,")
    st_write(s.project.doc.paragraphs.p_body, "Jacques")
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_write(s.project.doc.titles.h3, "2.10.3. llama-3.2-1b", tag=t.h3)
    st_write(s.project.doc.paragraphs.p_body, "Voici un texte court et concis d'une vingtaine de lignes destiné à être envoyé par Jacques juste à Pierre et Paul :")
    st_write(s.project.doc.paragraphs.p_body, "\"Bonjour Pierre et Paul, j'ai tout à fait compris votre discussion récente et je comprends pourquoi vous avez des différends. Je veux vous dire que je suis là pour vous aider et que je suis prêt à écouter vos idées. Nous pouvons discuter ensemble de nos problèmes et trouver des solutions ensemble. Je suis prêt à partager mes connaissances et à vous aider à améliorer notre travail ensemble. Nous pouvons nous concentrer sur les problèmes spécifiques et trouver des solutions. Je suis là pour vous aider à travailler ensemble et à atteindre nos objectifs. Nous pouvons être plus efficaces ensemble. Je suis prêt à vous écouter et à vous aider. Nous pouvons nous soutenir mutuellement. Je suis là pour vous aider à réussir. Nous pouvons faire mieux ensemble. Je suis prêt à commencer. Nous pouvons commencer à travailler ensemble.\"")
    st_space(size=1)
    st_write(s.project.doc.titles.h3, "2.10.4. llama-3.1-sonar-large", tag=t.h3)
    st_write(s.project.doc.paragraphs.p_body, "Bon matin @Pierre et @Paul!")
    st_write(s.project.doc.paragraphs.p_body, "J'aimerais juste prendrer un instant de your time et de your attention, especially given the late hours you've both been putting in.")
    st_write(s.project.doc.paragraphs.p_body, "First off, let's acknowledge the incredible work you're both doing. It's clear that the pressure is high, but your dedication to getting things done is truly appreciated.")
    st_write(s.project.doc.paragraphs.p_body, "I've seen the recent discussion, and I understand that things can get a bit hot when we're all under the same pressure. But here's the thing: we're in this together, and we're all on the same team.")
    st_write(s.project.doc.paragraphs.p_body, "Pau, your approach with Pandor has been a game-c h an ge  e  e  e  e  e  e  e  e  e  e  e  e  e  e  e  e  e  e  e  e  e  e  e  e  e  e  e  e  e  e  e  e  e  e  e  e  e  e  e  e  e  e  e  e  e  e  e  e  e  e  e  e  e  e  e  e  e  e  e  e  e  e  e  e  e  e  e  e  e  e  e  e  e  e  e  e  e  e  e  e  e  e  e  e  e  e  e  e  e  e  e  e  e  e  e  e  e  e  e  e  e  e  e  e  e  e  e  e  e  e  e  e  e  e  e  e  e  e  e  e  e  e  e  e  e  e  e  e  e  e  e  e  e  e  e  e  e  e  e  e  e  e  e  e  e  e  e  e  e  e  e  e  e  e")
    st_space(size=1)
    st_write(s.project.doc.titles.h2, "2.11. xAI", tag=t.h2, toc_lvl="+1")
    st_space(size=1)
    st_write(s.project.doc.titles.h3, "2.11.1. Grok", tag=t.h3)
    st_write(s.project.doc.paragraphs.p_body, "Hey Pierre, Paul,")
    st_write(s.project.doc.paragraphs.p_body, "J'ai lu votre échange nocturne et je voulais juste vous dire que vous êtes tous les deux incroyables. Paul, ton initiative avec Pandoc montre vraiment à quel point tu es dévoué à améliorer notre produit. Et Pierre, ton souci du détail et ton engagement à bien faire les choses sont vraiment précieux.")
    st_write(s.project.doc.paragraphs.p_body, "Je sais que la fin de l’année est stressante et que les tickets s'entassent comme des flocons de neige en hiver. Mais, c'est dans ces moments qu'on voit la force de notre équipe.")
    st_write(s.project.doc.paragraphs.p_body, "Votre dialogue a mis en lumière des points importants pour l'avenir. Il est essentiel de continuer à communiquer, non seulement sur ce qui a été fait, mais aussi sur ce qui est en cours et ce qui est prévu. Comme le dit le proverbe, \"Deux têtes valent mieux qu'une\", et dans notre cas, c'est encore plus vrai avec toutes les vôtres !")
    st_write(s.project.doc.paragraphs.p_body, "Je vous encourage à garder cet esprit de collaboration et d'ouverture. Parfois, une pause, une discussion autour d'un café (ou d'une tisane, Pierre, je sais que tu adores ça) peut faire des merveilles pour clarifier les idées et renforcer notre entente.")
    st_write(s.project.doc.paragraphs.p_body, "Prenez soin de vous, reposez-vous, et continuez à faire ce que vous savez faire de mieux : construire quelque chose de grand ensemble !")
    st_write(s.project.doc.paragraphs.p_body, "Jacques")
    st_space(size=1)
    st_write(s.project.doc.titles.h3, "2.11.2. Grok vision", tag=t.h3)
    st_space(size=1)
    st_write(s.project.doc.paragraphs.p_body, "Salut les codeurs,")
    st_write(s.project.doc.paragraphs.p_body, "Il est parfois difficile de naviguer entre les lignes de code et les lignes de communication, surtout quand le sommeil se fait rare. Je tiens à souligner l'effort que vous faites tous les deux pour avancer sur notre projet. Chaque ligne de code corrigée, chaque fonctionnalité implémentée est un pas de plus vers notre objectif commun.")
    st_write(s.project.doc.paragraphs.p_body, "Paul, ton initiative d'intégrer Pandoc montre une volonté d'innover et d'améliorer notre produit. C'est cette proactivité qui nous fait avancer.")
    st_write(s.project.doc.paragraphs.p_body, "Pierre, ta réflexion sur l'intégration des outils et la gestion de nos ressources démontre un sens aigu de la planification et de l'optimisation.")
    st_write(s.project.doc.paragraphs.p_body, "Je sais que le stress peut parfois nous faire perdre de vue l'essentiel : nous sommes une équipe, et chaque critique ou suggestion est une occasion de grandir ensemble. Prenons un moment pour apprécier le chemin parcouru et le travail accompli, même s'il reste du pain sur la planche.")
    st_write(s.project.doc.paragraphs.p_body, "Il est crucial de se rappeler que derrière chaque écran, il y a une personne. Un peu de patience et d'ouverture peut transformer une tension en une collaboration fructueuse. Essayons de voir les suggestions comme des opportunités, non comme des critiques.")
    st_write(s.project.doc.paragraphs.p_body, "Pourquoi ne pas prendre un café virtuel ensemble, ou partager un GIF qui nous fera sourire ? Parfois, un petit break et un peu d'humour peuvent faire des merveilles pour notre esprit d'équipe.")
    st_write(s.project.doc.paragraphs.p_body, "Allons-y doucement, prenons le temps de discuter, d'expliquer, et surtout de se comprendre. Ensemble, on ira plus loin.")
    st_write(s.project.doc.paragraphs.p_body, "Bonne continuation à vous deux, et n'oubliez pas, chaque problème a sa solution, souvent plus simple qu'on ne le pense au premier abord.")
    st_write(s.project.doc.paragraphs.p_body, "Cordialement, Jacques")
    st_space(size=1)
    st_space(size=1)
    st_write(s.project.doc.titles.h2, "2.12. qwen", tag=t.h2, toc_lvl="+1")
    st_space(size=1)
    st_write(s.project.doc.titles.h3, "2.12.1. firefunction-v1", tag=t.h3)
    st_write(s.project.doc.paragraphs.p_body, "<plain>Cher Pierre et Paul,")
    st_write(s.project.doc.paragraphs.p_body, "Je suis là pour vous entendre et vous soutenir dans cette période intense. Je reconnais vos contributions et votre dévouement. Nous sommes tous confrontés à des défis, mais ensemble, nous pouvons les surmonter.")
    st_write(s.project.doc.paragraphs.p_body, "Pierre, je suis sûr que ton esprit ouvert te permettra de considérer les propositions avec un regard neuf. Paul, ton expertise et ton expérience sont des atouts précieux pour notre équipe.")
    st_write(s.project.doc.paragraphs.p_body, "Je vous encourage à communiquer et à collaborer davantage. N'hésitez pas à partager vos idées et vos préoccupations. Je suis là pour vous aider à trouver des solutions et à maintenir une atmosphère positive.")
    st_write(s.project.doc.paragraphs.p_body, "Bonne nuit et prenez soin de vous!")
    st_write(s.project.doc.paragraphs.p_body, "Jacques")
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
    st_write(s.project.doc.titles.h1, "3. Appendix ", tag=t.h1, toc_lvl="1")
    st_write(s.project.doc.titles.h3 + s.project.colors.gray, "3.0.1. Modèle -  ", tag=t.h3)
    st_write(s.project.doc.titles.h4 + s.project.colors.gray, "3.0.1.1. Paramètres ", tag=t.h4)
    st_space(size=1)
    st_space(size=1)
    st_write(s.project.doc.paragraphs.p_body, "Max tokens = 32768 / 32768 ")
    st_write(s.project.doc.paragraphs.p_body, "Température = 0 / 2 ")
    st_write(s.project.doc.paragraphs.p_body, "Top P =  0.5 / 1 ")
    st_write(s.project.doc.paragraphs.p_body, "Top K =  32 / 100 ")
    st_write(s.project.doc.paragraphs.p_body, "Frequence penalty = 0.2 / 2 ")
    st_write(s.project.doc.paragraphs.p_body, "Presence penalty = 0 /  ")
    st_space(size=1)
    st_space(size=1)
    st_write(s.project.doc.titles.h4 + s.project.colors.gray, "3.0.1.2. Message pour Pierre ", tag=t.h4)
    st_space(size=1)
    st_write(s.project.doc.titles.h4 + s.project.colors.gray, "3.0.1.3. Message pour Paul ", tag=t.h4)
    st_space(size=1)
    st_write(s.project.doc.titles.h4 + s.project.colors.gray, "3.0.1.4. Message global pour l'équipe ", tag=t.h4)
    st_space(size=1)
    st_space(size=1)
    st_space(size=1)
