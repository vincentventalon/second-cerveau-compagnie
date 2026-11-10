"""Connexion Gmail, à faire une fois : écrit secrets/google/token.json.

Avant : télécharge ton client OAuth « Desktop app » depuis la console Google Cloud
et enregistre-le sous secrets/google/client_secret.json (voir le README du repo).

    .venv/bin/python scripts/auth_gmail.py

Un navigateur s'ouvre, tu choisis ton compte Google et tu acceptes. Le token est
ensuite rafraîchi tout seul par gmail_lib.py. Si ton app Google est en mode
« Test », l'accès expire au bout de 7 jours : relance ce script.
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gmail_lib import CLIENT_SECRET_PATH, SCOPES, SECRETS_DIR, TOKEN_PATH  # noqa: E402


def main():
    if len(sys.argv) > 1 and sys.argv[1] in ("-h", "--help"):
        print(__doc__)
        return
    if not os.path.exists(CLIENT_SECRET_PATH):
        raise SystemExit(
            f"Il manque {CLIENT_SECRET_PATH}\n"
            "Télécharge le JSON de ton client OAuth « Desktop app » (console Google Cloud,\n"
            "Google Auth Platform > Clients) et enregistre-le à cet endroit."
        )
    from google_auth_oauthlib.flow import InstalledAppFlow

    flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_PATH, SCOPES)
    creds = flow.run_local_server(port=0)
    os.makedirs(SECRETS_DIR, exist_ok=True)
    with open(TOKEN_PATH, "w") as f:
        f.write(creds.to_json())
    os.chmod(TOKEN_PATH, 0o600)
    print(f"Token enregistré : {TOKEN_PATH}")
    print("Test : .venv/bin/python scripts/gmail_lib.py")


if __name__ == "__main__":
    main()
