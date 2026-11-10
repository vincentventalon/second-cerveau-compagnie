#!/usr/bin/env python3
"""Relevés CSV de tes comptes Revolut Business, tirés de l'API (lecture seule).

Les comptes se déclarent dans config.json (« accounts » : un nom logique par
compte). Certains comptes d'épargne n'apparaissent pas dans /accounts : leur id
ne se voit que dans les mouvements. La commande « list » les signale.

Période : <du> et <au> sont des jours inclus tous les deux, sur la date affichée
dans l'app (completed_at). L'API filtre sur created_at : le script élargit la
fenêtre de 3 jours de chaque côté, puis coupe sur la date affichée.

Le script s'arrête au lieu de se tromper en silence :
- les soldes sont chaînés ligne à ligne (solde précédent + montant = solde) :
  une transaction manquante, en double ou mal ordonnée fait tout échouer ;
- un doublon dans la pagination fait tout échouer ;
- « all » et « list » refusent un compte non déclaré qui a des mouvements.

Usage :
  python3 scripts/revolut/statement.py list                         # comptes, solde, contrôle
  python3 scripts/revolut/statement.py <compte> <du> <au> [out.csv] # un compte
  python3 scripts/revolut/statement.py all <du> <au> [dossier]      # tous les comptes déclarés
  # <compte> : un nom de config.json (principal, epargne...) ou son UUID
  # dates au format AAAA-MM-JJ, par exemple : all 2026-01-01 2026-03-31 data/releves
"""
from __future__ import annotations

import csv
import datetime
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from revolut.auth import Client  # noqa: E402


def _shift(day: str, days: int) -> str:
    return (datetime.date.fromisoformat(day) + datetime.timedelta(days=days)).isoformat()


def _transactions(rv: Client, dfrom: str, dto_excl: str):
    """Transactions dont created_at est dans [dfrom, dto_excl), page par page."""
    out, seen, to = [], set(), dto_excl
    while True:
        page = rv.get(f"/transactions?from={dfrom}&to={to}&count=1000")
        for t in page:
            if t["id"] in seen:
                raise RuntimeError(f"Transaction en double dans la pagination : {t['id']}")
            seen.add(t["id"])
        out += page
        if len(page) < 1000:
            return out
        to = page[-1]["created_at"]  # horodatage complet, « to » est exclusif


def fetch_legs(rv: Client, account_id: str, dfrom: str, dto: str, txs=None):
    """Mouvements terminés d'un compte, dans l'ordre, soldes chaînés et vérifiés."""
    rows = []
    for t in (txs if txs is not None else _transactions(rv, _shift(dfrom, -3), _shift(dto, 3))):
        if t["state"] != "completed":
            continue
        for leg in t["legs"]:
            if leg["account_id"] == account_id:
                rows.append({
                    "date": (t.get("completed_at") or t["created_at"])[:10],
                    "type": t["type"],
                    "description": leg.get("description") or t.get("reference") or "",
                    "amount": leg["amount"],
                    "balance": leg["balance"],
                    "currency": leg["currency"],
                    "created_at": t["created_at"],
                    "completed_at": t.get("completed_at") or t["created_at"],
                    "id": t["id"],
                })
    # Tri par exécution, pas par création : des virements créés d'affilée peuvent
    # s'exécuter dans un autre ordre, et le solde est posé à l'exécution.
    rows.sort(key=lambda r: (r["completed_at"], r["created_at"]))
    rows = [r for r in rows if dfrom <= r["date"] <= dto]
    for prev, cur in zip(rows, rows[1:]):
        if abs(prev["balance"] + cur["amount"] - cur["balance"]) > 0.005:
            raise RuntimeError(
                f"Soldes non chaînés sur {account_id} : "
                f"{prev['date']} solde {prev['balance']:.2f} + {cur['amount']:.2f} "
                f"≠ {cur['balance']:.2f} ({cur['date']}, transaction {cur['id']}). "
                f"Transaction manquante, en double ou mal ordonnée.")
    return rows


def write_statement(rv: Client, name: str, dfrom: str, dto: str, out=None, txs=None) -> str | None:
    """Écrit le CSV d'un compte. Renvoie None s'il n'y a aucun mouvement."""
    legs = fetch_legs(rv, rv.account(name), dfrom, dto, txs=txs)
    if not legs:
        return None
    out = Path(out or f"releve_{name}_{dfrom}_{dto}.csv")
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["Date", "Type", "Description", "Sortie", "Entrée", "Solde", "Devise"])
        for r in legs:
            amt = r["amount"]
            w.writerow([r["date"], r["type"], r["description"],
                        f"{-amt:.2f}" if amt < 0 else "",
                        f"{amt:.2f}" if amt >= 0 else "",
                        f"{r['balance']:.2f}",
                        r["currency"]])
    opening = legs[0]["balance"] - legs[0]["amount"]
    print(f"{out} : {len(legs)} mouvements, ouverture {opening:.2f}, clôture {legs[-1]['balance']:.2f} {legs[-1]['currency']}")
    return str(out)


def _refuse_unknown(rv: Client, txs):
    known = set(rv.config.get("accounts", {}).values())
    unknown = {leg["account_id"] for t in txs for leg in t["legs"]
               if t["state"] == "completed" and leg["account_id"] not in known}
    if unknown:
        raise RuntimeError(
            f"Comptes non déclarés avec des mouvements : {sorted(unknown)}. "
            f"Ajoute-les à « accounts » dans config.json : rien n'est omis en silence.")


def write_all(rv: Client, dfrom: str, dto: str, outdir="."):
    """Un CSV par compte déclaré, en une seule lecture de l'API."""
    txs = _transactions(rv, _shift(dfrom, -3), _shift(dto, 3))
    _refuse_unknown(rv, txs)
    outdir = Path(outdir)
    return {n: write_statement(rv, n, dfrom, dto, outdir / f"releve_{n}_{dfrom}_{dto}.csv", txs=txs)
            for n in rv.config.get("accounts", {})}


def main():
    args = sys.argv[1:]
    if args and args[0] in ("-h", "--help"):
        print(__doc__)
        return
    rv = Client()
    today = datetime.date.today().isoformat()
    since = rv.config.get("history_from", _shift(today, -365))
    if not args or args[0] == "list":
        print(f"Société vérifiée : {rv.verify()}")
        txs = _transactions(rv, since, _shift(today, 3))
        for n, aid in rv.config.get("accounts", {}).items():
            legs = fetch_legs(rv, aid, since, today, txs=txs)
            bal = f"{legs[-1]['balance']:.2f} {legs[-1]['currency']}" if legs else "aucun mouvement"
            print(f"{n:12} {aid}  {bal}  ({len(legs)} mouvements, soldes chaînés)")
        extra = {leg["account_id"] for t in txs for leg in t["legs"]
                 if leg["account_id"] not in set(rv.config.get("accounts", {}).values())}
        if extra:
            raise RuntimeError(f"Comptes absents de config.json avec des mouvements : {sorted(extra)}")
    elif args[0] == "all" and len(args) >= 3:
        write_all(rv, args[1], args[2], args[3] if len(args) > 3 else ".")
    elif len(args) >= 3:
        if not write_statement(rv, args[0], args[1], args[2], args[3] if len(args) > 3 else None):
            sys.exit(f"Aucun mouvement sur {args[0]} entre {args[1]} et {args[2]}")
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main()
