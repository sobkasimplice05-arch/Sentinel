# Evolution Lab v1

Evolution Lab v1 est la couche de preuve de l’autoévolution de Sentinel. Il sépare trois phénomènes qui étaient auparavant mélangés dans les compteurs et les commits : **l’adaptation d’une politique**, **l’expérimentation d’un patch de code** et **la promotion vérifiée d’une évolution source**.

## Contrat de promotion

Une expérience de code ne peut être enregistrée comme `PROMOTED` que si elle possède simultanément :

1. un diff de code non vide et limité aux fichiers autorisés ;
2. une validation réussie ;
3. un score candidat strictement supérieur au score de la baseline ;
4. une trace persistante avec l’hypothèse, les scores, la décision et les preuves.

Un score égal à la baseline signifie **absence de gain démontré**, même si les tests passent. Une adaptation de politique peut être promue, mais elle ne doit jamais être comptée comme une mutation de code.

## Mémoire

La table `evolution_experiments` conserve les expériences de politique, d’auto-modification et d’évolution source. Elle enregistre les hypothèses, les branches ou espaces candidats, les commits de base et candidats lorsqu’ils sont disponibles, les fichiers touchés, le statut des tests, les scores, le modèle utilisé, les décisions et les causes de rejet.

Les échecs sont conservés comme données d’apprentissage. Les rapports JSON peuvent être reconstruits depuis cette mémoire et doivent rester cohérents avec elle.

## Limites v1

Evolution Lab v1 ne prétend pas entraîner un modèle de base ni garantir une intelligence générale. Il fournit l’infrastructure minimale pour produire une preuve reproductible d’amélioration de code. Le benchmark doit continuer à être enrichi avec des tâches réelles, des tests cachés et des variantes de transfert avant d’augmenter les permissions autonomes.

Les workflows, secrets, permissions, protections Git et mécanismes de rollback restent hors du périmètre de modification automatique. Toute extension de ce périmètre doit faire l’objet d’une décision explicite et d’un test de sécurité dédié.

## Promotion Git sécurisée

Lorsqu’un cycle contient une expérience de code ou une évolution source, la persistance pousse par défaut le commit vers une branche `evolution-lab/<timestamp>` au lieu de pousser directement sur `main`. L’intégration dans `main` doit passer par une revue et une validation séparées. Le comportement historique de push direct ne peut être réactivé qu’avec la variable explicite `SENTINEL_ALLOW_DIRECT_MAIN_PUSH=true`, qui doit rester désactivée dans les workflows normaux.

## Evolution Lab v1.1 — mémoire cumulative et absorption

Evolution Lab conserve désormais trois registres supplémentaires dans `sentinel_memory.db` : `evolution_transactions`, `evolution_checkpoints` et `evolution_patterns`.

Une transaction est créée au début de chaque cycle avec l’objectif, son empreinte, l’observation, le commit de base et la branche de base. Un candidat de code publié est marqué `awaiting_review`; il ne devient jamais absorbé dans le même cycle. Lorsqu’un futur cycle observe le commit candidat dans le `HEAD` courant, `git merge-base --is-ancestor` vérifie sa présence et la transaction devient `absorbed`. Une fusion sur `main` est donc nécessaire avant de considérer une modification comme effectivement active.

Les checkpoints sont append-only et conservent les états `candidate_commit`, `awaiting_review`, `restart_reconcile` et `no_code_absorbed`. Chaque expérience porte aussi un manifeste de couverture des fichiers candidats : taille, SHA-256 et fichiers manquants. Une couverture incomplète est signalée et ne doit pas être présentée comme une revue complète.

Les rejets de promotion alimentent `evolution_patterns` par empreinte stable. Les occurrences récurrentes augmentent `count` et actualisent `last_seen` sans supprimer l’historique. Le digest de ces classes est réinjecté dans les cycles suivants comme contexte de recherche, jamais comme ordre de modification.

Le benchmark de transfert indépendant est exécuté dans la baseline et dans la copie candidate du moteur de self-modification. Une promotion exige compilation, tests ciblés, benchmark lisible et `candidate_score > baseline_score`. Une absence de benchmark ou un score non mesurable entraîne un rejet honnête.

Les statuts ont une signification stricte : une adaptation de politique peut être persistée sans constituer une autoévolution de code ; un commit candidat peut être valide sans être encore absorbé ; un échec ou un no-op devient une donnée de recherche plutôt qu’un succès artificiel.

## Contrat fournisseurs et HTTP 400

Le client de self-modification utilise désormais un contrat structuré adapté au fournisseur. NVIDIA reçoit `nvext.guided_json`, conformément à sa documentation de génération structurée, tandis que les endpoints OpenAI-compatibles conservent `response_format` lorsque cette option est supportée. Google reçoit `responseMimeType` en premier essai.

Lorsqu’un fournisseur renvoie HTTP 400, Sentinel effectue au maximum un retry contractuel en retirant uniquement les contrôles structurés incompatibles (`response_format`, `responseMimeType` ou `nvext`). Le JSON reste imposé par le prompt et validé localement par le parseur de proposition ; une réponse non conforme n’est jamais exécutée. En mode `auto`, le fournisseur qui échoue est ensuite placé en cooldown et le prochain fournisseur disponible est essayé.

Chaque tentative conserve uniquement un diagnostic borné : fournisseur, hôte de l’endpoint et indication d’un retry contractuel. Aucun secret ni corps de réponse n’est enregistré. Le diagnostic d’apprentissage contient désormais une variante HTTP 400 afin que la gestion des erreurs de contrat soit mesurée comme une compétence transférable.

Les modèles par défaut Cloudflare ont été alignés sur un modèle listé comme compatible avec JSON Mode dans la documentation officielle : [Cloudflare Workers AI JSON Mode](https://developers.cloudflare.com/workers-ai/features/json-mode/). Pour NVIDIA, la contrainte recommandée est décrite dans [NVIDIA NIM Structured Generation](https://docs.nvidia.com/nim/large-language-models/1.8.0/structured-generation.html).
