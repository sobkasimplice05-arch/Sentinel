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
