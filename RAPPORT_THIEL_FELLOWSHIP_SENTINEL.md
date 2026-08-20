# Dossier technique et feuille de route matérielle — Sentinel

**Version de travail pour candidature Thiel Fellowship — 20 août 2026**

> **Avertissement financier et stratégique.** Je suis une IA, pas un conseiller financier, fiscal ou juridique. Ce document est une analyse de préparation de candidature et de planification budgétaire, non une garantie d’obtention du financement ni un conseil personnalisé. Les achats importants, les conditions de versement, la fiscalité, les douanes et les engagements contractuels doivent être vérifiés avec la Thiel Foundation, un comptable et, si nécessaire, un conseiller local.

## 1. Résumé exécutif

Sentinel est aujourd’hui un **noyau expérimental d’agent autonome orchestré dans le cloud**, et non une intelligence générale artificielle démontrée. Sa valeur technique ne réside pas dans le simple fait de lancer un script à intervalles réguliers. Elle réside dans l’assemblage d’une boucle vérifiable qui collecte des observations, calcule un feedback, conserve un état stratégique, choisit une prochaine action, formule des expériences, teste des candidats de code dans un environnement isolé et ne promeut une modification que si les garde-fous et les tests l’acceptent.

L’état du dépôt est vérifiable. Au 20 août 2026, la branche distante `main` est propre et pointe vers le commit `21b8335`, quatre workflows GitHub Actions sont présents, seize fichiers de tests sont recensés et vingt-huit fonctions de test sont détectées par le dépôt. La commande GitHub Actions utilisée pour l’audit rend visibles **802 exécutions** sur la fenêtre accessible avec `gh run list --limit 1000`. Les derniers runs observés, dont le worker rapide de 10:57 UTC et le noyau autonome de 10:32 UTC, sont marqués `success`.

Cette preuve doit toutefois être formulée honnêtement dans le dossier. Les 802 lancements démontrent une **activité opérationnelle et une continuité d’orchestration** ; ils ne démontrent pas, à eux seuls, 802 progrès cognitifs ni 802 améliorations de code. Le dernier cycle détaillé précédemment a retourné `NO_CHANGE_NEEDED`, avec un score baseline et candidat identiques à **0,663**, et `auto_code=PROVIDER_ERROR`. Sentinel a donc correctement refusé de prétendre avoir évolué. L’étape suivante est de produire une série de patches source promus et reproductibles, avec gain mesuré sur des tâches nouvelles et transfert vérifié.

## 2. Positionnement approprié pour la candidature

La formulation recommandée n’est pas « j’ai déjà construit une AGI autonome ». Elle serait techniquement trop forte et exposerait le dossier à une objection immédiate. La formulation défendable est la suivante :

> **Sentinel est un noyau expérimental d’agent général qui transforme une boucle GitHub Actions en système d’apprentissage vérifiable : il observe des sources, mémorise des épisodes, compare des politiques, planifie des objectifs, expérimente des modifications de code dans une copie isolée et conserve uniquement les changements validés. Le projet vise à mesurer jusqu’où cette architecture peut progresser vers un agent général autonome, sans confondre activité automatique et intelligence générale démontrée.**

Cette présentation correspond mieux à l’esprit de la Thiel Fellowship, qui soutient des jeunes personnes souhaitant construire de nouvelles choses et indique que les candidats doivent démontrer un progrès significatif vers une vision concrète [1]. La FAQ officielle précise que la Fellowship est un financement de 250 000 dollars réparti sur deux ans, sans prise de participation, mais qu’un candidat doit être âgé de 22 ans ou moins et ne pas avoir de diplôme universitaire pour être éligible ; une personne encore à l’université doit abandonner ses études si elle est sélectionnée [2]. Ces conditions d’éligibilité doivent être confirmées avant de présenter le financement comme acquis.

## 3. État technique actuel de Sentinel V3

### 3.1. Boucle d’orchestration

Le fichier `sentinel_v3_core.py` orchestre le cycle V3. Le système collecte d’abord les données, évalue l’observation, consulte la matrice IA, exécute le feedback adaptatif, avance le noyau d’autonomie, sélectionne un objectif, construit un plan, appelle le moteur d’auto-modification puis enregistre l’épisode de l’agent général. La persistance est conditionnelle : un changement important, une promotion, un rejet documenté ou un heartbeat périodique peuvent être conservés ; une observation répétée sans nouveauté ne doit pas fabriquer un commit artificiel.

Le workflow rapide est planifié toutes les quinze minutes avec `*/15 * * * *`, possède la permission `contents: write`, installe Python 3.12 et les dépendances nécessaires, compile les moteurs puis exécute `python sentinel_v3_core.py`. Il publie ensuite les rapports, les états et la base SQLite comme artefacts. Le noyau autonome séparé s’exécute sur une cadence horaire, et un workflow quotidien prépare le rapport Discord.

### 3.2. Feedback adaptatif et mémoire

`feedback_learning.py` constitue l’un des éléments les plus solides de l’architecture. Il crée une représentation reproductible des observations, calcule un hash pour identifier les répétitions, compare le score baseline au score candidat, valide les politiques et enregistre l’historique dans SQLite. Une observation identique peut être reconnue comme `NO_CHANGE_NEEDED` au lieu d’être comptée plusieurs fois comme un nouvel apprentissage.

La mémoire n’est donc pas uniquement un dossier de logs. Elle comprend une base SQLite, des rapports JSON, un historique de décisions, des scores, des états de politique et des événements d’autonomie. Cette structure permet de poser des questions mesurables : quelles observations ont déjà été rencontrées, quels essais ont été rejetés, quelle politique a été utilisée et quel score a été obtenu.

### 3.3. Noyau d’autonomie

`autonomy_kernel.py` possède une mémoire stratégique persistante avec objectifs actifs, confiance, résultat du dernier cycle, prochaines actions et compteurs d’expériences réussies ou rejetées. Il migre automatiquement les anciennes bases SQLite, active le mode WAL, crée des index utiles et purge les événements anciens au-delà d’un seuil afin de limiter la croissance indéfinie de la base.

La confiance n’est pas présentée comme une conscience ou une intelligence générale. Elle constitue un indicateur interne d’expérimentation. Une promotion augmente progressivement la confiance, un rejet la diminue et une absence de nouveauté conserve la politique courante. Le heartbeat est configuré par `SENTINEL_HEARTBEAT_COMMIT_HOURS`, avec une valeur par défaut de six heures, afin de ne pas confondre présence du système et progrès cognitif.

### 3.4. Agent général expérimental

`agent_general_kernel.py` fournit les primitives qui manquent à un worker statique : objectifs persistants, plans en cinq étapes, épisodes, registre de compétences et tests de transfert sur des variantes non vues. Le plan comprend la formalisation de l’objectif, la récupération de la mémoire pertinente, l’action ou l’expérimentation isolée, l’évaluation sur une nouvelle variante et la consolidation ou l’enregistrement de l’échec.

Le transfert est volontairement difficile à valider. Une compétence n’est promue que si son score de compétence et son score moyen de transfert franchissent un seuil. Dans les rapports actuels, `transfer_verified` reste à considérer comme une métrique à démontrer sur des tâches réelles et variées, pas comme une propriété déjà acquise du système.

### 3.5. Auto-modification source et garde-fous

Le moteur `self_modification.py` limite les fichiers autorisés, cible un seul fichier par cycle selon la configuration actuelle, segmente le prompt, demande un objet JSON structuré et gère les réponses trop volumineuses par des tentatives compactes. Il traite les erreurs HTTP 413 et 429, conserve un cooldown fournisseur persistant et sélectionne automatiquement un fournisseur disponible lorsque la configuration le permet.

Le candidat reçu est analysé, les chemins absolus et les échappements de répertoire sont refusés, les fichiers trop volumineux sont rejetés et plusieurs effets secondaires structurellement dangereux sont bloqués. Le contenu candidat est copié dans un répertoire temporaire, puis compilé et testé avant toute promotion. En cas de succès, seuls les fichiers autorisés sont remplacés et le rapport de promotion contient l’hypothèse, le gain attendu, les scores, les fichiers modifiés et le résultat des tests.

Une réserve importante doit apparaître dans le dossier : le score actuel du moteur est encore un **score de qualité de pipeline**, pas une mesure complète de performance de l’agent. Il accorde une base de 0,75 lorsque la compilation et les tests ciblés réussissent, puis ajoute une valeur par changement significatif. Il faudra remplacer ou compléter cette heuristique par des benchmarks externes : taux de réussite sur tâches inédites, régressions, coût par expérience, durée, qualité des plans et transfert.

## 4. Forces techniques démontrables

| Force | Preuve dans le code ou l’exécution | Valeur pour le dossier |
|---|---|---|
| Boucle non statique | Orchestration observation → feedback → autonomie → plan → expérimentation → persistance dans `sentinel_v3_core.py` | Montre une architecture de recherche, pas seulement une tâche cron. |
| Mémoire structurée | SQLite, états JSON, rapports, hash d’observation et déduplication | Permet de reconstruire les décisions et de mesurer les progrès. |
| Auto-évaluation | Baseline, candidat, décisions `PROMOTED`, `REJECTED`, `NO_CHANGE_NEEDED` | Évite de qualifier toute sortie de progrès. |
| Auto-modification limitée | Fichiers autorisés, JSON, tests isolés, compilation et promotion conditionnelle | Rend l’évolution source expérimentale mais vérifiable. |
| Résilience fournisseur | Cooldown HTTP 429, retries HTTP 413, sélection automatique | Évite qu’une panne de fournisseur bloque silencieusement toute la boucle. |
| Autonomie stratégique | Objectifs, confiance, prochaines actions, heartbeat de six heures | Permet à Sentinel de choisir ce qu’elle doit faire ensuite dans un cadre défini. |
| Agent général expérimental | Plans en cinq étapes, épisodes, compétences et tests de transfert | Constitue une base pour étudier la généralisation. |
| Opération cloud | 802 runs visibles dans l’audit, workers rapides et noyau horaire | Prouve une première continuité expérimentale indépendante de l’ordinateur local. |
| Traçabilité | Commits, rapports Discord, artefacts GitHub Actions et tests | Permet à un mentor ou investisseur de vérifier les affirmations. |

## 5. Limites à traiter avant de parler d’AGI démontrée

La première limite est la disponibilité du fournisseur IA. Groq a provoqué des réponses HTTP 429 ; le cooldown est maintenant persistant, mais un fournisseur secondaire fiable doit encore être configuré et testé en conditions réelles. Le système peut donc continuer à tourner sans mentir, mais il ne peut pas générer une auto-modification source lorsque tous les fournisseurs sont indisponibles.

La deuxième limite concerne le transfert. Les primitives de transfert sont présentes et testées, mais la preuve expérimentale doit être enrichie avec un jeu de tâches inédites, un baseline fixe, des variantes cachées, des critères de réussite définis à l’avance et une publication des résultats. Tant que cette batterie n’existe pas, le terme « agent général » doit rester qualifié d’expérimental.

La troisième limite concerne la profondeur des tests. Les tests locaux ont réussi lors de la dernière validation, et le dépôt contient seize fichiers de test. Cependant, plusieurs tests sont unitaires ou de fumée ; ils ne remplacent pas un benchmark de bout en bout sur plusieurs semaines. Il faudra ajouter des tests de non-régression, des simulations de fournisseur, des tests de concurrence Git et des audits de sécurité des prompts et des patches.

La quatrième limite concerne l’architecture cloud elle-même. GitHub Actions est très utile pour des cycles périodiques, mais il ne s’agit pas d’un serveur permanent avec GPU garanti. La future architecture devra séparer l’orchestrateur, les fournisseurs de modèles, la mémoire, les benchmarks et les tâches longues, avec une stratégie de reprise après interruption et un budget de calcul documenté.

## 6. Hypothèse de financement et discipline de trésorerie

La page officielle de la Fellowship décrit un financement de 250 000 dollars réparti sur deux ans [1] [2]. Elle ne garantit pas, dans les pages consultées, que le versement sera exactement égal chaque mois. Le montant de référence proposé par l’utilisateur est donc une **hypothèse de planification**, non une clause contractuelle.

Un étalement parfaitement uniforme donnerait :

| Calcul | Montant |
|---|---:|
| Grant total | 250 000 $ |
| Durée | 24 mois |
| Moyenne mathématique mensuelle | 10 416,67 $ |
| Équivalent utilisé par l’utilisateur | 5 900 000 FCFA/mois |
| Taux implicite de cette conversion | 566,40 FCFA/$ |
| Total correspondant à 5 900 000 FCFA × 24 | 141 600 000 FCFA |

Le dossier doit éviter de présenter 10 400 dollars ou 5,9 millions de FCFA comme un montant garanti tant que la convention de financement n’a pas confirmé le calendrier, les retenues éventuelles, les obligations de reporting, les règles de dépenses et les modalités de transfert international. Une réserve de trésorerie est indispensable, car l’achat au Tchad peut ajouter transport, douanes, taxes, garantie internationale, conversion monétaire et délais d’approvisionnement.

Je déconseille également de consacrer l’intégralité des 250 000 dollars au matériel. Un poste local puissant ne prouvera pas à lui seul la généralité de Sentinel. Une allocation plus saine serait de réserver environ **75 000 à 115 000 dollars** à l’infrastructure matérielle, à l’énergie, au stockage et aux sauvegardes, puis de conserver environ **135 000 à 175 000 dollars** pour le développement, les fournisseurs de modèles, les données, les benchmarks, les déplacements, l’assistance technique, les taxes, les remplacements et la survie du projet sur 24 mois.

## 7. Matériel recommandé

### 7.1. Outil de travail principal

Le produit Apple actuellement documenté n’est pas un MacBook Pro « M5 Ultra ». Les pages officielles Apple consultées documentent le MacBook Pro 14 et 16 pouces avec les puces **M5 Pro et M5 Max**. La configuration M5 Max 40 cœurs GPU peut être équipée de 128 Go de mémoire unifiée et d’un SSD de 8 To [3] [4]. Le « M5 Ultra » doit donc être présenté dans le dossier comme une **hypothèse ou un futur produit à confirmer**, pas comme une disponibilité actuelle garantie.

La configuration M5 Max 128 Go / 8 To est un excellent poste de développement, de compilation, de documentation, de tests locaux, d’inférence quantifiée et de pilotage des workers. Elle ne doit toutefois pas être décrite comme le serveur idéal pour entraîner de très grands modèles : l’écosystème CUDA et la mémoire GPU dédiée d’un poste NVIDIA sont plus adaptés à cette fonction.

| Équipement principal | Spécification cible | Usage Sentinel | Budget de planification |
|---|---|---|---:|
| MacBook Pro 16 pouces M5 Max | 40-core GPU, 128 Go mémoire unifiée, 8 To SSD, écran nano-texture si utile | Développement, orchestration, compilation, tests, documentation, inférence locale raisonnable | Réserver 10 000–11 500 $, à confirmer au moment de l’achat |
| Moniteur externe | 27–32 pouces, 4K, USB-C/DisplayPort | Logs, dashboards, IDE et métriques simultanés | 500–1 200 $ |
| Dock Thunderbolt 5 | Alimentation, réseau, écrans, SSD externes | Réduire les branchements et fiabiliser le bureau | 300–700 $ |
| SSD externes chiffrés | Deux unités de 4–8 To | Sauvegarde locale et rotation hors ligne | 600–1 800 $ |
| Garantie et câbles de rechange | AppleCare ou garantie équivalente, câbles certifiés | Réduire le risque d’arrêt du projet | 500–1 500 $ |

### 7.2. Serveur GPU local

Pour faire tourner des modèles localement, le meilleur complément n’est pas un deuxième ordinateur Apple mais un serveur Linux équipé d’un GPU NVIDIA. La GeForce RTX 5090 possède 32 Go de GDDR7, un prix de départ officiel annoncé de 1 999 dollars et une recommandation d’alimentation minimale de 850 W pour la carte, hors marge du système [5]. Une seule RTX 5090 conviendra à l’inférence et au fine-tuning de modèles quantifiés de taille limitée, mais pas à l’entraînement d’un modèle général de frontière.

Pour des modèles plus volumineux, la RTX PRO 6000 Blackwell Workstation, annoncée avec 96 Go de GDDR7 ECC, représente une classe professionnelle plus adaptée, mais son prix, sa disponibilité et les coûts d’importation doivent faire l’objet d’un devis fournisseur avant de l’inscrire comme achat ferme. [6]

| Nœud | Configuration cible | Rôle | Budget de planification |
|---|---|---|---:|
| Serveur GPU niveau 1 | CPU 16–24 cœurs, 128 Go ECC, RTX 5090 32 Go, 2 × NVMe 2 To en miroir, alimentation 1,6–2,0 kW, Linux | Inférence locale, évaluation, agents parallèles limités, benchmarks | 7 000–12 000 $ |
| Serveur GPU niveau 2 | CPU serveur, 256 Go ECC, RTX PRO 6000 96 Go ou GPU équivalent, NVMe entreprise, alimentation redondante | Modèles plus lourds, expérimentation avancée, tâches concurrentes | 15 000–30 000 $ selon devis |
| Serveur de contrôle | 8–16 cœurs, 64–128 Go ECC, 2 × NVMe miroir | Orchestration locale, observabilité, registre d’expériences, Git miroir | 2 500–6 000 $ |
| Pièces de rechange | Ventilateurs, câbles, SSD, alimentation, GPU de secours si disponible | Diminuer les arrêts prolongés au Tchad | 2 000–5 000 $ |

La recommandation est de commencer par **un seul serveur RTX 5090**, puis de mesurer les tailles de modèles réellement utiles avant d’acheter une carte professionnelle très coûteuse. L’argent économisé doit financer les données, les évaluations et les mois de fonctionnement.

### 7.3. Stockage souverain et sauvegardes

Le stockage doit suivre une stratégie 3-2-1 : trois copies des données importantes, sur au moins deux supports différents, dont une copie hors site. Un NAS ECC avec réseau 10 GbE constitue une bonne base. Le Synology DS1823xs+ documente huit baies SATA, 8 Go de mémoire DDR4 ECC extensible à 32 Go, deux emplacements NVMe et un port 10 GbE [7]. Une configuration avec huit disques d’entreprise de 12 ou 16 To en RAID6 fournirait une capacité brute importante tout en conservant une tolérance à deux pannes, mais la capacité utile finale dépendrait du système de fichiers, de la parité et des réserves.

| Couche | Matériel | Usage | Budget de planification |
|---|---|---|---:|
| NAS principal | NAS 8 baies ECC, 10 GbE | Mémoire Sentinel, datasets, artefacts, images de machines | 1 500–3 000 $ hors disques |
| Disques principaux | 8 × 12–16 To entreprise, RAID6 | Stockage local résilient | 4 000–9 000 $ |
| Cache ou volume rapide | 2 × NVMe entreprise en miroir | SQLite, index, logs et petits datasets | 800–2 000 $ |
| Sauvegarde hors ligne | 2–4 disques externes 16–20 To chiffrés | Rotation mensuelle et protection contre ransomware | 1 200–3 500 $ |
| Copie hors site | NAS secondaire, disque conservé dans un autre lieu ou stockage objet chiffré | Reprise après incendie, vol ou panne totale | 1 000–4 000 $ initialement, puis coût récurrent |

Le NAS ne doit pas être considéré comme une sauvegarde unique. Le RAID protège principalement contre certaines pannes de disques ; il ne protège pas contre la suppression accidentelle, le chiffrement malveillant, le vol ou une surtension majeure.

### 7.4. Réseau et sécurité

Le réseau local devrait être construit autour d’un routeur pare-feu administrable, d’un switch 10 GbE pour les serveurs, d’un switch 1 GbE ou 2,5 GbE pour les équipements courants et d’une liaison WAN de secours. Une connexion principale fixe peut être complétée par un modem 4G/5G avec bascule automatique. Les réseaux de production, d’administration, de sauvegarde et d’objets connectés doivent être séparés par VLAN.

| Équipement | Spécification cible | Budget de planification |
|---|---|---:|
| Routeur pare-feu | VLAN, VPN, journaux, mise à jour suivie, double WAN | 500–1 500 $ |
| Switch principal | 10 GbE cuivre ou SFP+, gestion VLAN, capacité PoE si nécessaire | 800–2 500 $ |
| Liaison de secours | Modem 4G/5G, antenne externe si nécessaire, SIM distincte | 300–1 200 $ plus abonnement |
| Rack et câblage | Petit rack ventilé, câbles Cat6A ou fibre, étiquetage | 800–2 000 $ |
| Sécurité physique | Serrure, caméra locale, contrôle d’accès, détecteur de fumée/température | 500–2 000 $ |
| Sécurité numérique | Clés matérielles FIDO2, coffre de secrets, ordinateur d’administration séparé | 200–1 000 $ |

### 7.5. Énergie et continuité au Tchad

La continuité électrique est une priorité avant l’achat d’un second GPU. Un serveur RTX 5090, un NAS, un réseau et un poste de travail peuvent dépasser plusieurs centaines de watts en régime normal et beaucoup plus pendant les pics. La solution doit être dimensionnée sur la puissance mesurée du site, la durée d’autonomie souhaitée, la qualité du réseau électrique et la possibilité d’une production solaire.

| Couche d’énergie | Recommandation | Budget de planification |
|---|---|---:|
| Protection immédiate | Parasurtenseur, mise à la terre contrôlée, régulateur et multiprise professionnelle | 300–1 000 $ |
| UPS informatique | UPS online double conversion de 3 kVA minimum pour réseau/NAS/contrôle | 1 500–4 000 $ |
| UPS serveur GPU | UPS séparé dimensionné avec un électricien, arrêt automatique propre | 2 000–6 000 $ |
| Batterie de secours | Batterie LiFePO4 de 5–10 kWh selon étude de charge | 3 000–8 000 $ |
| Solaire et onduleur | 3–5 kW de production et onduleur adapté au site, selon étude | 5 000–15 000 $ |
| Groupe électrogène de secours | Option de dernier recours avec stockage sécurisé et entretien | 1 500–5 000 $ |

Ces montants sont des enveloppes de planification, pas des devis. L’installation électrique, la terre, la ventilation, la protection contre la chaleur et le choix de batteries doivent être réalisés avec un professionnel local qualifié.

## 8. Feuille de route d’achat sur 24 mois

Le calendrier ci-dessous suppose une moyenne de 10 416,67 dollars par mois, mais il doit rester flexible tant que le contrat de versement n’est pas confirmé. Les montants sont des plafonds de planification et non des dépenses obligatoires. Les mois 1 à 12 constituent le socle ; les achats des mois 13 à 24 sont conditionnels aux résultats, à la disponibilité locale et au niveau réel des allocations.

| Mois | Priorité | Achats ou dépenses recommandés | Plafond indicatif |
|---:|---|---|---:|
| 1 | Continuité et préparation | Étude électrique, parasurtenseur, UPS de contrôle, réseau de base, devis d’importation | 5 000 $ |
| 2 | Poste principal | MacBook Pro M5 Max 128 Go / 8 To si disponible ; ne pas attendre un M5 Ultra non annoncé | 11 500 $ |
| 3 | Données et sauvegarde | Deux SSD chiffrés, première sauvegarde hors ligne, coffre de secrets, clés FIDO2 | 4 000 $ |
| 4 | GPU local | Serveur RTX 5090, Linux, 128 Go ECC, NVMe miroir | 11 000 $ |
| 5 | Stockage souverain | NAS 8 baies ECC, 10 GbE, premières baies de disques | 7 000 $ |
| 6 | Résilience réseau | Switch 10 GbE, routeur pare-feu, modem 4G/5G, câblage et rack | 6 000 $ |
| 7 | Énergie serveur | UPS online serveur, arrêt automatique, monitoring de température | 6 000 $ |
| 8 | Stockage complet | Extension des disques NAS, RAID6, deuxième rotation de sauvegarde | 7 000 $ |
| 9 | Production locale | Mise en place des environnements reproductibles, registre d’expériences, observabilité | 4 000 $ |
| 10 | Énergie souveraine | Étude solaire, batterie LiFePO4 et devis d’installation | 8 000 $ |
| 11 | Backup hors site | NAS secondaire ou copie chiffrée conservée dans un autre lieu | 4 000 $ |
| 12 | Revue à mi-parcours | Mesure des coûts, température, pannes, taux de réussite et décision d’expansion | 2 500 $ |
| 13–14 | Deuxième nœud | Serveur de contrôle ou second nœud CPU/ECC pour tests parallèles | 8 000 $ |
| 15–16 | Extension GPU conditionnelle | RTX PRO 6000 ou équivalent uniquement si les benchmarks justifient 96 Go de VRAM | 20 000 $ |
| 17 | Sauvegarde et remplacement | Disques de rechange, ventilateurs, câbles, batteries et maintenance | 6 000 $ |
| 18 | Réseau avancé | Extension 10/25 GbE et segmentation de sécurité | 5 000 $ |
| 19–20 | Recherche et évaluations | Datasets, benchmarks de transfert, appels API, instrumentation et tests de sécurité | 12 000 $ |
| 21 | Continuité | Renouvellement batteries, maintenance solaire/UPS, solution de reprise | 7 000 $ |
| 22 | Documentation | Mesures reproductibles, rapport technique, démonstrations, préparation investisseurs | 4 000 $ |
| 23 | Réserve | Remplacement matériel, transport, douanes, réparations imprévues | 8 000 $ |
| 24 | Décision de phase suivante | Audit indépendant, mesure finale et décision : expansion, partenariat ou sobriété | 3 000 $ |

La somme des plafonds indicatifs de ce scénario maximal atteint **149 000 $**. Il ne s’agit pas d’un budget à engager automatiquement : il comprend des achats conditionnels, notamment le second nœud et la RTX PRO 6000. Pour protéger la trésorerie, la trajectoire recommandée est de plafonner la première architecture réellement nécessaire à **95 000–115 000 $** sur 24 mois, puis de ne libérer les dépenses supplémentaires qu’après validation des benchmarks. Cette trajectoire conserve environ **135 000–155 000 $** pour le développement, les fournisseurs IA, les données, les tests, les déplacements, les taxes et les réserves. L’intention est de **ne pas acheter le GPU professionnel avant d’avoir démontré son utilité** et de **ne pas sacrifier la continuité électrique, la sauvegarde ou les benchmarks au profit d’une machine prestigieuse**.

## 9. Jalons techniques à associer au financement

L’achat matériel doit être libéré par des résultats, pas seulement par le temps écoulé. Avant de financer une deuxième carte GPU, Sentinel devrait démontrer une exécution locale reproductible, une récupération après interruption, une sauvegarde restaurée avec succès, une mesure de coût par cycle et une batterie de tâches inédites.

| Période | Jalon de preuve | Critère de décision |
|---|---|---|
| Mois 1–3 | Développement et sauvegarde locale | Un environnement peut être restauré sur une nouvelle machine et les tests passent. |
| Mois 4–6 | Première boucle GPU locale | Un modèle local ou fournisseur API répond, les observations sont mémorisées et les rapports sont reproductibles. |
| Mois 7–9 | Résilience | Une coupure simulée, un rollback et une restauration ne détruisent pas l’état. |
| Mois 10–12 | Benchmark de transfert | Les tâches inédites, les baselines et les scores sont publiés dans un format reproductible. |
| Mois 13–18 | Auto-évolution mesurée | Au moins plusieurs promotions de patches source validés, avec absence de régression et gains mesurables. |
| Mois 19–24 | Preuve de valeur | Démonstration publique ou utilisateurs pilotes, métriques de coût, fiabilité et utilité. |

## 10. Conclusion pour le dossier

Sentinel présente une base technique crédible pour une candidature de recherche entrepreneuriale : l’architecture est vivante, l’exécution cloud est régulière, la mémoire et le feedback sont persistants, l’auto-modification est limitée et testée, et les résultats négatifs sont conservés au lieu d’être maquillés en progrès. C’est une force importante : le système possède déjà un mécanisme de vérification interne qui distingue une observation répétée, une erreur fournisseur, un rejet et une promotion.

La thèse de financement doit cependant porter sur **la construction et la mesure de la prochaine étape**, pas sur une AGI déjà achevée. Les 24 mois peuvent être consacrés à transformer ce noyau en plateforme expérimentale plus robuste : fournisseur local ou multi-fournisseur, benchmarks de transfert, calcul local, énergie résiliente, sauvegarde souveraine, sécurité et démonstrations reproductibles.

La demande matérielle la plus défendable commence donc par le MacBook Pro M5 Max 128 Go / 8 To officiellement documenté, un serveur RTX 5090 plus abordable, un NAS ECC 10 GbE, une stratégie de sauvegarde 3-2-1 et une continuité électrique adaptée au contexte local. Le futur « M5 Ultra » peut être mentionné comme option conditionnelle, mais ne doit pas être présenté comme un produit disponible ou un prix garanti tant qu’Apple ne l’a pas officiellement annoncé.

## Références

[1]: https://thielfellowship.org/ "Thiel Fellowship — présentation officielle"

[2]: https://thielfellowship.org/faq "Thiel Fellowship — FAQ officielle"

[3]: https://www.apple.com/newsroom/2026/03/apple-introduces-macbook-pro-with-all-new-m5-pro-and-m5-max/ "Apple Newsroom — MacBook Pro avec M5 Pro et M5 Max"

[4]: https://support.apple.com/en-us/126318 "Apple Support — spécifications MacBook Pro 14 pouces M5 Pro ou M5 Max"

[5]: https://www.nvidia.com/en-us/geforce/graphics-cards/50-series/rtx-5090/ "NVIDIA — GeForce RTX 5090"

[6]: https://www.nvidia.com/en-us/products/workstations/professional-desktop-gpus/rtx-pro-6000/ "NVIDIA — RTX PRO 6000 Blackwell Workstation"

[7]: https://www.synology.com/en-us/products/DS1823xs+ "Synology — DiskStation DS1823xs+"

### Disclosure de l’analyse

**Base :** les métriques Sentinel sont définies par les fichiers du dépôt, les rapports JSON, SQLite, les tests et les exécutions visibles GitHub Actions ; un lancement n’est pas assimilé à une amélioration cognitive. **Temps :** audit du dépôt et des runs au 20 août 2026 ; les prix et disponibilités doivent être revalidés au moment de l’achat. **Hypothèses :** versement planifié à titre indicatif selon 250 000 dollars / 24 mois, taux implicite de 566,40 FCFA/$ pour convertir l’exemple de l’utilisateur, et enveloppes matérielles hors devis locaux, transport, douanes et taxes. **Sources et confiance :** critères Thiel et caractéristiques Apple, NVIDIA et Synology issus de pages officielles ; les prix d’infrastructure et d’importation sont des estimations de planification à remplacer par des devis. **Conformité :** This is research and analysis only, not personalized financial advice.
