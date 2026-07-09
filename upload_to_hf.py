from huggingface_hub import upload_folder
import os

# Ton nouveau token (pas l'ancien!)
HF_TOKEN = "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  "

# Upload tout le dossier
print("Uploading Sentinel to Hugging Face...")
upload_folder(
    folder_path=".",  # Dossier courant
    repo_id="sobkasimplice/sentinel-ai",
    repo_type="space",
    token=HF_TOKEN,
    commit_message="Upload complete Sentinel system"
)
print(" Upload complete!")
