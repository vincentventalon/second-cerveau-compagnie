---
name: facture-du-mois
description: Prépare la facture mensuelle d'un client à partir de facturation.md (tarif, numérotation, dernier numéro), fait valider le calcul, produit la facture et le mail au client en brouillon, puis met à jour facturation.md et l'index. N'envoie jamais rien. À utiliser quand on dit « fais la facture du mois », « la facture d'octobre », « facture ACME », « j'ai oublié de facturer », ou quand l'index a une facture à faire.
---

# La facture du mois

Claude prépare, l'humain approuve. Rien ne part sans son accord, et c'est lui qui envoie.

## 1. Lire avant de calculer

- `CLAUDE.md` (l'index) : la ligne de la facture, s'il y en a une.
- `facturation.md` : le client, son tarif, ses conditions, la règle de numérotation, le dernier
  numéro utilisé, la façon de faire la facture, la dernière facture émise pour ce client.
- `identifiants.md` : les numéros à reporter (numéro de commande, TVA du client).

Il manque le mois ? Prends le mois qui vient de finir et dis-le.

## 2. La quantité

Demande la quantité du mois (jours, heures, forfait) si elle n'est écrite nulle part. Si
`facturation.md` dit où la lire (un mail de validation, un portail client, un relevé de
temps), va la lire et cite la source.

## 3. Montrer le calcul et attendre

Montre un tableau, puis attends un « oui » :

| N° | Date | Client | Période | Quantité × tarif | HT | TVA | TTC |

Le numéro est le dernier numéro + 1, selon la règle. Un écart avec le mois précédent (tarif,
taux, client) se signale, il ne se corrige pas en silence.

## 4. Faire la facture

Là où `facturation.md` dit qu'elle se fait :

- un logiciel de facturation : donne les lignes à saisir, champ par champ ;
- un document copié du mois d'avant : copie-le, change les lignes, montre le résultat ;
- rien de défini : écris la facture dans `data/factures/<n°>.md` avec les mentions de
  `facturation.md`, et dis comment l'exporter en PDF.

Le PDF final se range dans `data/factures/<n°>.pdf`.

## 5. Le mail au client, en brouillon

- Avec les scripts Gmail (`scripts/`, voir le README) : écris le texte dans
  `data/brouillons/facture-<n°>.txt`, puis
  `.venv/bin/python scripts/gmail_cli.py draft --to <contact> --subject "<objet>" --body-file data/brouillons/facture-<n°>.txt --attach data/factures/<n°>.pdf`.
  Le brouillon porte le PDF.
- Avec le connecteur Gmail seul : crée le brouillon sans pièce jointe, et dis à l'humain de
  joindre le PDF avant d'envoyer.

Jamais d'envoi. Dis : « le brouillon est dans Gmail, objet <...>, pour <...> ».

## 6. Mettre à jour

- `facturation.md` : nouvelle ligne dans « Factures émises » (statut brouillon), dernier numéro
  utilisé.
- `CLAUDE.md` : la ligne du sujet (« brouillon prêt, à envoyer »), et une échéance de paiement
  dans « Échéances dures » si le client paie en retard d'habitude.
