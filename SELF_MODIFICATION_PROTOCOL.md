# Protocole d’auto-modification source de Sentinel

Sentinel peut proposer des modifications de son propre code source, mais uniquement selon une boucle vérifiable : **hypothèse → patch candidat → compilation → tests → score → promotion ou rejet → mémoire**.

## Périmètre actuel

Les fichiers modifiables automatiquement sont limités à `learning_engine.py`, `feedback_learning.py` et `autonomy_kernel.py`. Les workflows, permissions, secrets, mécanismes de rollback et le moteur d’auto-modification lui-même ne sont pas modifiables par le générateur.

## Fonctionnement

Le moteur `self_modification.py` lit la politique et les rapports précédents, demande éventuellement à un fournisseur configuré de proposer au maximum deux fichiers complets, vérifie la structure de la réponse et rejette les chemins hors périmètre. Le candidat est copié dans un répertoire temporaire isolé; il est compilé et testé sans toucher au dépôt de production.

Un candidat n’est promu que si les tests ciblés réussissent et que son score dépasse la baseline. Le moteur écrit alors `self_modification_report.json`; le noyau v3 peut versionner le patch et ce rapport dans un commit identifiable. Si le modèle n’est pas configuré, le résultat explicite est `MODEL_UNAVAILABLE`; Sentinel ne fabrique pas de mutation fictive.

## Configuration optionnelle

Pour activer une génération effective de patches, Sentinel utilise `SELF_MODIFICATION_MODEL_URL` si ce secret est défini. En mode `SELF_MODIFICATION_PROVIDER=auto`, elle choisit automatiquement `NVIDIA_API_KEY`, puis `GROQ_API_KEY`, puis `MODEL_API_KEY`/`SELF_MODIFICATION_API_KEY`, puis `HF_API_KEY`. Les endpoints par défaut sont NVIDIA NIM (`https://integrate.api.nvidia.com/v1/chat/completions`), Groq (`https://api.groq.com/openai/v1/chat/completions`) et Hugging Face Inference. Une installation Ollama peut être sélectionnée avec `SELF_MODIFICATION_MODEL_URL` ou `OLLAMA_BASE_URL`.

Les offres gratuites NVIDIA et Groq sont utiles pour tester, mais leurs quotas et leur disponibilité ne garantissent pas un fournisseur permanent ou illimité. Pour une autonomie continue, utiliser un endpoint GPU persistant ou Ollama/vLLM sur une machine toujours active. Sans fournisseur disponible ou si l’API échoue, le résultat explicite est `MODEL_UNAVAILABLE` ou `PROVIDER_ERROR`; la boucle reste alors opérationnelle pour l’évaluation, la mémoire et le diagnostic, mais elle ne génère pas de code.

## Critère de réalité

Un patch n’est pas considéré comme une évolution parce qu’un modèle l’a proposé. Il doit modifier réellement un fichier autorisé, compiler, passer les tests et fournir une preuve persistée. Un échec ou une absence de fournisseur doit rester visible dans le rapport et ne doit pas être présenté comme une amélioration.
