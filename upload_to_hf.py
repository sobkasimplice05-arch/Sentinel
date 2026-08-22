#!/usr/bin/env python3
"""Publie le projet Sentinel sur Hugging Face sans embarquer de secret."""
from __future__ import annotations

import os
from pathlib import Path

from huggingface_hub import upload_folder


def main() -> None:
    token = os.environ.get("HF_TOKEN")
    if not token:
        raise SystemExit("HF_TOKEN est requis dans l'environnement; aucune clé n'est lue depuis le code.")

    project_root = Path(__file__).resolve().parent
    repo_id = os.environ.get("HF_REPO_ID", "sobkasimplice/sentinel-ai")
    upload_folder(
        folder_path=str(project_root),
        repo_id=repo_id,
        repo_type="space",
        token=token,
        commit_message="Upload complete Sentinel system",
    )
    print(f"Upload terminé vers {repo_id}.")


if __name__ == "__main__":
    main()


__all__ = ["main"]
