#!/usr/bin/env python3
"""Gmail en ligne de commande : chercher, lire, télécharger les pièces jointes, brouillon.

Pourquoi : le connecteur Gmail de Claude lit les mails mais pas le contenu des
pièces jointes. Ce script passe par l'API Gmail avec ton propre accès
(secrets/google/token.json) : il télécharge les PDF pour que Claude les lise.
Il n'envoie jamais rien : la commande « draft » crée un brouillon, c'est toi qui
l'envoies depuis Gmail.

Exemples (la requête suit la syntaxe de recherche de Gmail) :
    python3 scripts/gmail_cli.py search "from:compta@cabinet-dupont.example newer_than:30d"
    python3 scripts/gmail_cli.py msg <id_du_message>
    python3 scripts/gmail_cli.py thread <id_du_fil>
    python3 scripts/gmail_cli.py grab "has:attachment facture newer_than:90d" --out data/pieces --ext .pdf
    python3 scripts/gmail_cli.py pdftext data/pieces/*.pdf
    python3 scripts/gmail_cli.py draft --to client@acme.example --subject "Facture" \\
        --body-file data/brouillons/mail.txt --attach data/factures/facture.pdf

L'id d'un message sert aussi de lien : https://mail.google.com/mail/u/0/#all/<id>
"""
from __future__ import annotations

import argparse
import base64
import mimetypes
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gmail_lib import download_attachment, iter_parts, service  # noqa: E402

LINK = "https://mail.google.com/mail/u/0/#all/{}"


def _headers(msg):
    return {x["name"].lower(): x["value"] for x in msg.get("payload", {}).get("headers", [])}


def _attachments(msg):
    return [p["filename"] for p in iter_parts(msg.get("payload", {})) if p.get("filename")]


def _plaintext(msg) -> str:
    """Le corps du message en texte brut, au mieux."""
    html = None
    for part in iter_parts(msg.get("payload", {})):
        data = part.get("body", {}).get("data")
        if not data:
            continue
        mime = part.get("mimeType", "")
        text = base64.urlsafe_b64decode(data).decode("utf-8", "replace")
        if mime == "text/plain":
            return text
        if mime == "text/html" and html is None:
            html = text
    if html:
        html = re.sub(r"(?is)<(script|style).*?</\1>", "", html)
        return re.sub(r"\s{3,}", "\n", re.sub(r"(?s)<[^>]+>", " ", html))
    return ""


def _ids(svc, query: str, limit: int):
    out, token = [], None
    while len(out) < limit:
        resp = (
            svc.users()
            .messages()
            .list(userId="me", q=query, pageToken=token, maxResults=min(100, limit - len(out)))
            .execute()
        )
        out += resp.get("messages", [])
        token = resp.get("nextPageToken")
        if not token:
            break
    return out[:limit]


def cmd_search(svc, args):
    for ref in _ids(svc, args.query, args.max):
        msg = svc.users().messages().get(userId="me", id=ref["id"], format="full").execute()
        h = _headers(msg)
        pj = "[pj]" if _attachments(msg) else "    "
        print(f"{h.get('date', '')[:22]:24} {pj} {h.get('from', '')[:34]:36} {h.get('subject', '')[:62]}")
        print(f"    message {ref['id']}  fil {ref['threadId']}  {LINK.format(ref['id'])}")


def cmd_msg(svc, args):
    msg = svc.users().messages().get(userId="me", id=args.id, format="full").execute()
    h = _headers(msg)
    print(f"De : {h.get('from')}\nÀ : {h.get('to')}\nCc : {h.get('cc', '')}")
    print(f"Date : {h.get('date')}\nObjet : {h.get('subject')}\nLien : {LINK.format(args.id)}\n")
    for name in _attachments(msg):
        print(f"[pièce jointe] {name}")
    print("\n" + _plaintext(msg).strip())


def cmd_thread(svc, args):
    th = svc.users().threads().get(userId="me", id=args.id, format="full").execute()
    for msg in th.get("messages", []):
        h = _headers(msg)
        print("=" * 78)
        print(f"{h.get('date', '')}  |  {h.get('from', '')}")
        print(f"{h.get('subject', '')}   [{msg['id']}]")
        for name in _attachments(msg):
            print(f"[pièce jointe] {name}")
        body = _plaintext(msg).strip()
        print("\n" + (body[: args.chars] if args.chars else body))


def cmd_grab(svc, args):
    """Télécharge toutes les pièces jointes des messages qui répondent à la requête."""
    os.makedirs(args.out, exist_ok=True)
    saved = 0
    for ref in _ids(svc, args.query, args.max):
        msg = svc.users().messages().get(userId="me", id=ref["id"], format="full").execute()
        h = _headers(msg)
        for part in iter_parts(msg.get("payload", {})):
            name = part.get("filename")
            aid = part.get("body", {}).get("attachmentId")
            if not name or not aid:
                continue
            if args.ext and not name.lower().endswith(tuple(e.lower() for e in args.ext)):
                continue
            safe = re.sub(r"[^\w.\-]+", "_", name)
            path = os.path.join(args.out, f"{ref['id']}__{safe}")
            if not os.path.exists(path):
                with open(path, "wb") as f:
                    f.write(download_attachment(svc, ref["id"], aid))
            saved += 1
            print(f"{path}\n    {h.get('date', '')[:22]} | {h.get('from', '')[:40]} | {h.get('subject', '')[:50]}")
    print(f"\n{saved} pièce(s) jointe(s) dans {args.out}")


def cmd_pdftext(_svc, args):
    for path in args.paths:
        print("=" * 78)
        print(path)
        try:
            print(subprocess.run(["pdftotext", "-layout", path, "-"],
                                 capture_output=True, text=True, check=True).stdout)
        except FileNotFoundError:
            print("[pdftotext introuvable : installe poppler, par exemple `brew install poppler`]")
        except subprocess.CalledProcessError as exc:
            print(f"[échec de pdftotext : {exc}]")


def cmd_draft(svc, args):
    """Crée un brouillon dans Gmail. N'envoie rien."""
    from email.message import EmailMessage

    mail = EmailMessage()
    mail["To"] = ", ".join(args.to)
    if args.cc:
        mail["Cc"] = ", ".join(args.cc)
    mail["Subject"] = args.subject
    with open(args.body_file, encoding="utf-8") as f:
        mail.set_content(f.read())

    for path in args.attach or []:
        ctype, _ = mimetypes.guess_type(path)
        maintype, subtype = (ctype or "application/octet-stream").split("/", 1)
        with open(path, "rb") as f:
            mail.add_attachment(f.read(), maintype=maintype, subtype=subtype,
                                filename=os.path.basename(path))

    body = {"message": {}}
    if args.reply_to:
        src = svc.users().messages().get(userId="me", id=args.reply_to, format="metadata").execute()
        h = _headers(src)
        mail["In-Reply-To"] = h.get("message-id", "")
        mail["References"] = h.get("message-id", "")
        body["message"]["threadId"] = src["threadId"]
    body["message"]["raw"] = base64.urlsafe_b64encode(mail.as_bytes()).decode()

    draft = svc.users().drafts().create(userId="me", body=body).execute()
    print(f"Brouillon {draft['id']} créé. Relis-le dans Gmail avant de l'envoyer.")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("search", help="liste les messages qui répondent à une requête Gmail")
    p.add_argument("query")
    p.add_argument("--max", type=int, default=25)
    p.set_defaults(func=cmd_search)

    p = sub.add_parser("msg", help="affiche un message et le nom de ses pièces jointes")
    p.add_argument("id")
    p.set_defaults(func=cmd_msg)

    p = sub.add_parser("thread", help="affiche un fil entier")
    p.add_argument("id")
    p.add_argument("--chars", type=int, default=0, help="coupe chaque message à N caractères")
    p.set_defaults(func=cmd_thread)

    p = sub.add_parser("grab", help="télécharge les pièces jointes des messages trouvés")
    p.add_argument("query")
    p.add_argument("--out", default="data/pieces")
    p.add_argument("--max", type=int, default=100)
    p.add_argument("--ext", nargs="*", help="filtre par extension, par exemple --ext .pdf")
    p.set_defaults(func=cmd_grab)

    p = sub.add_parser("pdftext", help="affiche le texte d'un PDF (demande pdftotext, de poppler)")
    p.add_argument("paths", nargs="+")
    p.set_defaults(func=cmd_pdftext)

    p = sub.add_parser("draft", help="crée un brouillon Gmail à partir d'un fichier texte")
    p.add_argument("--to", nargs="+", required=True)
    p.add_argument("--cc", nargs="*")
    p.add_argument("--subject", required=True)
    p.add_argument("--body-file", required=True)
    p.add_argument("--reply-to", help="id du message auquel répondre (le brouillon rejoint son fil)")
    p.add_argument("--attach", nargs="*", help="fichiers à joindre")
    p.set_defaults(func=cmd_draft)

    args = ap.parse_args()
    args.func(None if args.cmd == "pdftext" else service(), args)


if __name__ == "__main__":
    sys.exit(main())
