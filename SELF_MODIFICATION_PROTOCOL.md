# Protocole d’auto-modification source de Sentinel

Sentinel peut proposer des modifications de son propre code source, mais uniquement selon une boucle vérifiable : **hypothèse → patch candidat → compilation → tests → score → promotion ou rejet → mémoire**.

## Périmètre actuel

Les fichiers modifiables automatiquement sont limités à `learning_engine.py`, `feedback_learning.py` et `autonomy_kernel.py`. Les workflows, permissions, secrets, mécanismes de rollback et le moteur d’auto-modification lui-même ne sont pas modifiables par le générateur.

## Fonctionnement

Le moteur `self_modification.py` lit la politique et les rapports précédents, demande éventuellement à un fournisseur configuré de proposer au maximum deux fichiers complets, vérifie la structure de la réponse et rejette les chemins hors périmètre. Le candidat est copié dans un répertoire temporaire isolé; il est compilé et testé sans toucher au dépôt de production.

Un candidat n’est promu que si les tests ciblés réussissent et que son score dépasse la baseline. Le moteur écrit alors `self_modification_report.json`; le noyau v3 peut versionner le patch et ce rapport dans un commit identifiable. Si le modèle n’est pas configuré, le résultat explicite est `MODEL_UNAVAILABLE`; Sentinel ne fabrique pas de mutation fictive.

## Configuration optionnelle

Pour activer une génération effective de patches, Sentinel utilise `SELF_MODIFICATION_MODEL_URL`, `MODEL_API_URL` ou `OLLAMA_BASE_URL` lorsqu’un endpoint est défini. En mode `SELF_MODIFICATION_PROVIDER=auto`, elle essaie d’abord l’endpoint configuré, puis Cloudflare Workers AI, NVIDIA, Google Gemini, Groq, Replicate si un modèle/version est configuré, un endpoint générique et enfin Hugging Face, en ignorant les fournisseurs en cooldown. Les endpoints par défaut sont Cloudflare Workers AI (`https://api.cloudflare.com/client/v4/accounts/{account_id}/ai/run/{model}`), NVIDIA NIM (`https://integrate.api.nvidia.com/v1/chat/completions`), Gemini (`https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent`), Groq (`https://api.groq.com/openai/v1/chat/completions`) et Hugging Face Inference. Une installation Ollama peut être sélectionnée avec `SELF_MODIFICATION_MODEL_URL` ou `OLLAMA_BASE_URL`. Cloudflare nécessite `CLOUDFLARE_API_TOKEN` et `CLOUDFLARE_ACCOUNT_ID`; le modèle par défaut est `@cf/qwen/qwen2.5-coder-32b-instruct`.

Les offres gratuites NVIDIA, Google, Groq, Replicate et Hugging Face sont utiles pour tester, mais leurs quotas, leurs politiques et leur disponibilité ne garantissent pas un fournisseur permanent ou illimité. Pour une autonomie continue, utiliser Ollama ou vLLM sur une machine toujours active et exposer uniquement un endpoint privé authentifié. Un runner GitHub Actions est éphémère : il ne peut pas héberger durablement les poids Qwen ni maintenir un serveur Ollama entre deux cycles. Sans fournisseur disponible ou si l’API échoue, le résultat explicite est `MODEL_UNAVAILABLE` ou `PROVIDER_ERROR`; la boucle reste alors opérationnelle pour l’évaluation, la mémoire et le diagnostic, mais elle ne génère pas de code.

## Segmentation et reprise HTTP 413

Le générateur ne transmet plus tous les modules dans une seule requête. Il sélectionne un fichier autorisé par tentative, réduit les métadonnées et limite le budget de sortie. En cas de réponse `HTTP_413`, Sentinel réessaie jusqu’à trois fois avec un contexte et un budget de sortie réduits. Chaque tentative est enregistrée dans `self_modification_report.json`, avec le fichier cible, la taille du prompt, le budget de sortie et le fournisseur utilisé.

La segmentation ne transforme pas une réponse incomplète en succès : si le modèle reçoit un code tronqué, si le JSON est invalide ou si les tests échouent, le candidat est rejeté et aucun fichier source n’est promu.

## Critère de réalité

Un patch n’est pas considéré comme une évolution parce qu’un modèle l’a proposé. Il doit modifier réellement un fichier autorisé, compiler, passer les tests et fournir une preuve persistée. Un échec ou une absence de fournisseur doit rester visible dans le rapport et ne doit pas être présenté comme une amélioration.
