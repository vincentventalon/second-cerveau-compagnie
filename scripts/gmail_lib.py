"""Fonctions Gmail partagées par auth_gmail.py et gmail_cli.py.

Accès : un token dédié, secrets/google/token.json (gitignoré), écrit une fois par
auth_gmail.py puis rafraîchi ici tout seul. Le client OAuth (type « Desktop app »)
est secrets/google/client_secret.json, que tu télécharges depuis la console
Google Cloud (voir le README du repo).

Scopes demandés :
- gmail.readonly : lire les mails et les pièces jointes ;
- gmail.compose : créer des brouillons.
gmail.compose permettrait aussi d'envoyer : aucun script de ce dossier n'envoie,
par règle. Ici, on écrit des brouillons, l'humain envoie.

    from gmail_lib import service
    svc = service()

Pour changer de dossier de secrets : variable d'environnement GMAIL_SECRETS_DIR.
"""
from __future__ import annotations

import base64
import os

from googleapiclient.discovery import build

SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.compose",
]
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SECRETS_DIR = os.environ.get("GMAIL_SECRETS_DIR", os.path.join(ROOT, "secrets", "google"))
TOKEN_PATH = os.path.join(SECRETS_DIR, "token.json")
CLIENT_SECRET_PATH = os.path.join(SECRETS_DIR, "client_secret.json")


def _token_creds():
    """Lit token.json, le rafraîchit s'il a expiré et le réécrit."""
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials

    creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
    if not creds.valid:
        creds.refresh(Request())
        with open(TOKEN_PATH, "w") as f:
            f.write(creds.to_json())
    return creds


def service():
    """Renvoie un client Gmail API authentifié."""
    if not os.path.exists(TOKEN_PATH):
        raise SystemExit(
            f"Pas de token Gmail ({TOKEN_PATH}).\n"
            "Lance d'abord : .venv/bin/python scripts/auth_gmail.py"
        )
    return build("gmail", "v1", credentials=_token_creds(), cache_discovery=False)


def iter_parts(payload):
    """Parcourt toutes les parties MIME d'un message."""
    yield payload
    for part in payload.get("parts", []) or []:
        yield from iter_parts(part)


def download_attachment(svc, message_id: str, attachment_id: str) -> bytes:
    """Télécharge une pièce jointe et renvoie ses octets."""
    att = (
        svc.users()
        .messages()
        .attachments()
        .get(userId="me", messageId=message_id, id=attachment_id)
        .execute()
    )
    return base64.urlsafe_b64decode(att["data"])


def whoami():
    """Test de l'accès : affiche l'adresse de la boîte et son nombre de messages."""
    svc = service()
    prof = svc.users().getProfile(userId="me").execute()
    print(f"OK : {prof['emailAddress']} ({prof['messagesTotal']} messages)")


if __name__ == "__main__":
    whoami()
