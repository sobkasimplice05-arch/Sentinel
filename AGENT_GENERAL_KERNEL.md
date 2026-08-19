# Noyau expérimental d’agent général

Sentinel dispose maintenant d’un noyau expérimental d’agent général dans `agent_general_kernel.py`. Ce noyau ne prétend pas être une AGI complète; il fournit les primitives permettant de tester une évolution vers un agent général.

## Boucle cognitive

Chaque cycle suit la séquence : **sélectionner un objectif → construire un plan multi-étapes → récupérer la mémoire pertinente → agir ou expérimenter → mesurer le résultat → tester le transfert → consolider ou rejeter la compétence**.

Les objectifs persistants sont stockés dans `agent_objectives`. Les compétences sont versionnées dans `agent_skills`, les épisodes dans `agent_episodes` et les tests de transfert dans `agent_transfer_tests`. L’état lisible est publié dans `agent_general_state.json` et le rapport du cycle dans `agent_general_report.json`.

## Compétence et transfert

Une amélioration locale n’est pas considérée comme une compétence générale. Pour être promue, elle doit obtenir un score supérieur à la baseline sur au moins une variante de tâche non vue. Le rapport distingue donc `OBSERVATION_SKILL_UPDATED`, `NOT_MEASURED`, `PROMOTED` et `REJECTED`.

Tant qu’aucun test de variante nouvelle n’est exécuté, `transfer_verified` reste `false`. Cette distinction évite de confondre une mémoire plus grande ou un cycle réussi avec une intelligence générale.

## Relation avec l’auto-modification

Le noyau d’agent général peut demander une expérimentation de modification source via `self_modification.py`. Les patches restent isolés, compilés, testés et comparés à une baseline avant promotion. Le planificateur peut donc apprendre à utiliser la modification de code comme une compétence, mais le système ne considère pas une proposition non testée comme une connaissance acquise.
