#!/usr/bin/env python3
"""Accès à l'API Revolut Business, en lecture et brouillons : permissions READ,WRITE, jamais PAY.

Aucune dépendance : le JWT est signé avec openssl, les appels passent par urllib.

Les secrets vivent dans secrets/revolut/ (gitignoré), ou dans le dossier donné par
la variable d'environnement REVOLUT_DIR (une société = un dossier) :
    config.json       client_id, iss, iban attendu, comptes déclarés (voir README.md)
    privatecert.pem   ta clé privée, ne la donne à personne
    publiccert.cer    le certificat que tu as déposé chez Revolut
    tokens.json       écrit par ce script (le jeton d'accès dure 40 minutes)

Avant chaque premier appel, le script vérifie que le jeton ouvre bien la société
attendue : l'IBAN de config.json doit être parmi les comptes renvoyés par l'API.
Sinon il s'arrête sans rien lire.

Usage :
  python3 scripts/revolut/auth.py consent-url        # l'URL de consentement READ,WRITE à ouvrir
  python3 scripts/revolut/auth.py exchange <code>    # une fois, juste après le consentement
  python3 scripts/revolut/auth.py accounts           # comptes et soldes (vérifiés)
  python3 scripts/revolut/auth.py token              # un jeton d'accès valide
  python3 scripts/revolut/auth.py refresh            # force le rafraîchissement

En Python :
  from revolut.auth import Client
  rv = Client(); rv.get("/accounts")
"""
from __future__ import annotations

import base64
import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

API = "https://b2b.revolut.com/api/1.0"
AUD = "https://revolut.com"
ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DIR = ROOT / "secrets" / "revolut"


def b64url(b: bytes) -> str:
    return base64.urlsafe_b64encode(b).rstrip(b"=").decode()


class Client:
    def __init__(self, directory: str | os.PathLike | None = None):
        self.dir = Path(directory or os.environ.get("REVOLUT_DIR") or DEFAULT_DIR)
        cfg = self.dir / "config.json"
        if not cfg.exists():
            raise SystemExit(f"Il manque {cfg} : voir scripts/revolut/README.md, étape 3.")
        self.config = json.loads(cfg.read_text())
        for key in ("client_id", "iss", "iban"):
            if not self.config.get(key):
                raise SystemExit(f"{cfg} : la clé {key!r} est vide (voir README.md).")
        self._verified = False
        self._ibans: list[str] = []

    # --- secrets ---------------------------------------------------------
    @property
    def _tokens_path(self) -> Path:
        return self.dir / "tokens.json"

    def load_tokens(self) -> dict:
        p = self._tokens_path
        return json.loads(p.read_text()) if p.exists() else {}

    def _save_tokens(self, tokens: dict):
        tmp = self._tokens_path.with_suffix(".tmp")
        tmp.write_text(json.dumps(tokens, indent=2))
        tmp.chmod(0o600)
        os.replace(tmp, self._tokens_path)

    def account(self, name: str) -> str:
        """Nom logique (principal, epargne...) ou UUID d'un compte déclaré dans config.json."""
        accounts = self.config.get("accounts", {})
        if name in accounts:
            return accounts[name]
        if name in accounts.values():
            return name
        raise KeyError(f"Compte {name!r} inconnu. Comptes déclarés : {sorted(accounts)}")

    # --- OAuth -----------------------------------------------------------
    def _client_assertion(self) -> str:
        header = b64url(json.dumps({"alg": "RS256", "typ": "JWT"}).encode())
        payload = b64url(json.dumps({
            "iss": self.config["iss"], "sub": self.config["client_id"], "aud": AUD,
            "exp": int(time.time()) + 300,
        }).encode())
        signing_input = f"{header}.{payload}".encode()
        sig = subprocess.run(
            ["openssl", "dgst", "-sha256", "-sign", str(self.dir / "privatecert.pem")],
            input=signing_input, capture_output=True, check=True,
        ).stdout
        return f"{header}.{payload}.{b64url(sig)}"

    def _post_token(self, extra: dict) -> dict:
        data = {
            "client_assertion_type": "urn:ietf:params:oauth:client-assertion-type:jwt-bearer",
            "client_assertion": self._client_assertion(),
            **extra,
        }
        req = urllib.request.Request(
            f"{API}/auth/token",
            data=urllib.parse.urlencode(data).encode(),
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        try:
            with urllib.request.urlopen(req) as r:
                out = json.loads(r.read())
        except urllib.error.HTTPError as e:
            raise SystemExit(f"Revolut refuse le jeton : HTTP {e.code} {e.read().decode()[:400]}") from None
        out["obtained_at"] = int(time.time())
        tokens = self.load_tokens()
        tokens.update(out)
        self._save_tokens(tokens)
        return out

    def exchange(self, code: str):
        """Échange le code de consentement, puis vérifie la société. Efface les jetons sinon."""
        self._post_token({"grant_type": "authorization_code", "code": code})
        try:
            self.verify()
        except RuntimeError:
            self._tokens_path.unlink()
            raise

    def refresh(self) -> dict:
        return self._post_token({"grant_type": "refresh_token",
                                 "refresh_token": self.load_tokens()["refresh_token"]})

    def token(self) -> str:
        t = self.load_tokens()
        if not t.get("refresh_token") and not t.get("access_token"):
            raise SystemExit("Pas de jeton : lance d'abord `auth.py consent-url`, puis `auth.py exchange <code>`.")
        if time.time() < t.get("obtained_at", 0) + t.get("expires_in", 0) - 60:
            return t["access_token"]
        return self.refresh()["access_token"]

    # --- HTTP ------------------------------------------------------------
    def _request(self, method: str, path: str, body=None):
        req = urllib.request.Request(
            f"{API}{path}", method=method,
            data=json.dumps(body).encode() if body is not None else None,
            headers={"Authorization": f"Bearer {self.token()}",
                     **({"Content-Type": "application/json"} if body is not None else {})},
        )
        try:
            with urllib.request.urlopen(req) as r:
                return json.loads(r.read())
        except urllib.error.HTTPError as e:
            raise RuntimeError(f"HTTP {e.code} sur {method} {path} : {e.read().decode()[:400]}") from None

    def verify(self) -> list[str]:
        """L'IBAN attendu doit être parmi ceux des comptes que le jeton ouvre. Une fois par lancement."""
        if self._verified:
            return self._ibans
        ibans: list[str] = []
        for a in self._request("GET", "/accounts"):
            for d in self._request("GET", f"/accounts/{a['id']}/bank-details"):
                if d.get("iban") and d["iban"] not in ibans:
                    ibans.append(d["iban"])
        if self.config["iban"] not in ibans:
            raise RuntimeError(
                f"Le jeton n'ouvre pas la société attendue (IBAN {self.config['iban']}). "
                f"IBAN vus : {ibans}. Consentement donné sur une autre société ? Rien n'a été lu.")
        self._verified, self._ibans = True, ibans
        return ibans

    def get(self, path: str):
        self.verify()
        return self._request("GET", path)

    def post(self, path: str, body: dict):
        self.verify()
        return self._request("POST", path, body)

    def consent_url(self) -> str:
        q = urllib.parse.urlencode({"client_id": self.config["client_id"],
                                    "redirect_uri": self.config.get("redirect_uri", f"https://{self.config['iss']}"),
                                    "response_type": "code", "scope": "READ,WRITE"}, safe=",")
        return f"https://business.revolut.com/app-confirm?{q}"


def main():
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help"):
        print(__doc__)
        return
    rv, cmd = Client(), sys.argv[1]
    if cmd == "consent-url":
        print(rv.consent_url())
    elif cmd == "exchange" and len(sys.argv) > 2:
        rv.exchange(sys.argv[2])
        print(f"OK : société vérifiée ({rv.config['iban']}). Jetons dans {rv._tokens_path}")
    elif cmd == "refresh":
        rv.refresh()
        print("OK")
    elif cmd == "token":
        print(rv.token())
    elif cmd == "accounts":
        print(f"IBAN vérifiés : {rv.verify()}")
        for a in rv.get("/accounts"):
            print(f"{a['id']}  {a.get('name') or '':24} {a['balance']:>12.2f} {a['currency']}  {a['state']}")
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main()
