# Retard de paiement ACME SAS (exemple fictif)

**En trois lignes** : la facture 2025-012 (novembre 2025) devait être payée le 31/12/2025. Elle
ne l'est pas au 10/01/2026. Une relance est partie, sans réponse.

**Où ça en est** (au 2026-01-10) : relance envoyée, on attend.
**Prochaine action** : moi, deuxième relance le 20/01 si rien n'est arrivé sur le compte.

## Chronologie

| Date | Ce qui s'est passé | Source |
|---|---|---|
| 2025-11-30 | Facture 2025-012 envoyée, 6 000,00 € TTC, échéance 31/12 | `facturation.md`, lien Gmail du fil |
| 2026-01-02 | Rien sur le compte (relevé lu) | `data/releves/` |
| 2026-01-10 | Relance polie à factures@acme.example | `journal-des-mails.md` |

## Les pièces

- `data/factures/2025-012.pdf` : la facture envoyée
- le bon de commande du 2025-09-01 : le numéro de commande à reporter (voir `identifiants.md`)

## Ce qui reste flou

- La facture est-elle bloquée chez eux pour un numéro de commande manquant ? À demander dans la
  deuxième relance.
