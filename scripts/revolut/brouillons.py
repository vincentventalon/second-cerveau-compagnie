#!/usr/bin/env python3
"""Brouillons de virement Revolut Business : permission WRITE, jamais PAY.

Un brouillon ne bouge pas d'argent. Il apparaît dans l'app Revolut Business et
ne part que quand un humain l'envoie et l'approuve dans l'app. Le jeton n'a pas
la permission PAY : aucun script de ce dossier ne peut virer de l'argent.

Ce script n'ajoute pas de bénéficiaire : tu les crées toi-même dans l'app, puis
« beneficiaires » te donne leurs identifiants pour le CSV.

Usage :
  python3 scripts/revolut/brouillons.py beneficiaires              # bénéficiaires enregistrés
  python3 scripts/revolut/brouillons.py liste                      # brouillons en attente
  python3 scripts/revolut/brouillons.py creer <fichier.csv> [--depuis <compte>] [--oui]
      sans --oui : affiche ce qui serait créé et ne crée rien

Le CSV (en-tête obligatoire, un brouillon par ligne) :
  titre,montant,devise,reference,counterparty_id,account_id
  Honoraires T1,0.00,EUR,FACTURE-0000,<id du bénéficiaire>,<id de son compte>
Le compte débité est « default_account » de config.json, ou --depuis.
Deux lignes avec la même référence sont refusées : un virement par référence.
"""
from __future__ import annotations

import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from revolut.auth import Client  # noqa: E402

COLONNES = ["titre", "montant", "devise", "reference", "counterparty_id", "account_id"]


def beneficiaires(rv: Client):
    for c in rv.get("/counterparties"):
        for a in c.get("accounts", []):
            print(f"counterparty_id {c['id']}  account_id {a['id']}  {c.get('name', '')[:38]:40} {a.get('iban', '')}")


def liste(rv: Client):
    n = 0
    for d in rv.get("/payment-drafts").get("payment_orders", []):
        full = rv.get(f"/payment-drafts/{d['id']}")
        for p in full.get("payments", []):
            a = p.get("amount")
            montant = float(a["amount"]) if isinstance(a, dict) else float(a or 0)
            devise = a.get("currency") if isinstance(a, dict) else p.get("currency", "")
            n += 1
            print(f"{d['id']}  {montant:>10.2f} {devise}  réf. {p.get('reference', '-')}  {full.get('title', '')}")
    print(f"{n} paiement(s) en brouillon, à envoyer et approuver dans l'app Revolut Business.")


def creer(rv: Client, path: str, compte: str, oui: bool):
    src = rv.account(compte)
    with open(path, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    if not rows:
        sys.exit("CSV vide.")
    manquantes = [c for c in COLONNES if c not in rows[0]]
    if manquantes:
        sys.exit(f"Colonnes manquantes dans le CSV : {manquantes}")
    refs = [r["reference"].strip() for r in rows]
    if len(set(refs)) != len(refs):
        sys.exit("Deux lignes ont la même référence : un virement par référence.")
    print(f"{len(rows)} brouillon(s), débités du compte {compte} ({src}) :")
    for r in rows:
        print(f"  {float(r['montant']):>10.2f} {r['devise']}  réf. {r['reference']:20} {r['titre']}")
    if not oui:
        print("\nRien n'a été créé. Relance avec --oui pour créer les brouillons.")
        return
    for r in rows:
        body = {"title": r["titre"],
                "payments": [{"account_id": src,
                              "receiver": {"counterparty_id": r["counterparty_id"],
                                           "account_id": r["account_id"]},
                              "amount": float(r["montant"]), "currency": r["devise"],
                              "reference": r["reference"].strip()}]}
        d = rv.post("/payment-drafts", body)
        print(f"  brouillon {d['id']}  réf. {r['reference']}")
    print("\nRien n'est parti. Ouvre l'app Revolut Business pour relire, envoyer et approuver.")


def main():
    a = sys.argv[1:]
    if not a or a[0] in ("-h", "--help"):
        print(__doc__)
        return
    rv = Client()
    if a[0] == "beneficiaires":
        beneficiaires(rv)
    elif a[0] == "liste":
        liste(rv)
    elif a[0] == "creer" and len(a) > 1:
        compte = a[a.index("--depuis") + 1] if "--depuis" in a else rv.config.get("default_account", "principal")
        creer(rv, a[1], compte, "--oui" in a)
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main()
