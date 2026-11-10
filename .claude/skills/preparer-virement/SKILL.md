---
name: preparer-virement
description: Prépare un virement à faire (facture d'un prestataire, salaire à valider, impôt, remboursement) - retrouve le montant et la référence dans les pièces, lit les soldes, et crée un brouillon de virement que l'humain envoie et approuve lui-même dans l'app de sa banque (exemple avec Revolut Business, en lecture et brouillons, jamais en paiement). Ne paie jamais. À utiliser quand on dit « prépare le virement », « paie la facture du comptable », « le salaire du mois », « qu'est-ce que je dois payer », ou quand l'index a un paiement à faire.
---

# Préparer un virement

**Cette skill ne paie jamais.** Elle lit et elle prépare. L'argent ne part que quand l'humain
envoie et approuve le brouillon dans l'app de sa banque.

L'exemple branché est Revolut Business, avec les scripts de `scripts/revolut/` (voir son
`README.md`) et un accès limité aux permissions `READ` et `WRITE` : lire les comptes, créer des
brouillons. Sans la permission `PAY`, aucun appel ne peut virer de l'argent. Si l'accès n'est
pas en place, ou si la banque n'a pas d'API, passe directement à l'étape 5 bis.

## 1. Ce qu'il faut payer

Lis `CLAUDE.md`, puis la source du paiement : la facture dans `data/`, le mail qui le demande,
la fiche du sujet. Note le montant, la devise, le bénéficiaire, son IBAN et la **référence
exacte** à reporter (numéro de facture, référence de paiement d'un avis). Le montant vient de la
pièce, jamais d'un résumé. Cite la pièce.

## 2. Le solde

`python3 scripts/revolut/auth.py accounts` : le compte à débiter a-t-il de quoi payer ? S'il
manque de l'argent, dis-le et arrête-toi.

## 3. Le bénéficiaire

`python3 scripts/revolut/brouillons.py beneficiaires` : le bénéficiaire existe-t-il, avec le
bon IBAN ? S'il manque, l'humain le crée lui-même dans l'app. La skill ne crée pas de
bénéficiaire.

## 4. Montrer et attendre

Montre le virement en une ligne : montant, devise, de quel compte, vers qui (nom et IBAN),
référence, pièce source. Attends un « oui ».

## 5. Le brouillon

Écris `data/brouillons/virement-<date>.csv` :

```
titre,montant,devise,reference,counterparty_id,account_id
<titre>,<montant>,<devise>,<référence>,<id du bénéficiaire>,<id de son compte>
```

Lance d'abord l'aperçu, puis la création :

```
python3 scripts/revolut/brouillons.py creer data/brouillons/virement-<date>.csv
python3 scripts/revolut/brouillons.py creer data/brouillons/virement-<date>.csv --oui
```

Un virement par référence : deux paiements ne se regroupent jamais en un seul.

## 5 bis. Sans accès à la banque

Écris les détails à recopier dans l'app de la banque : bénéficiaire, IBAN, montant, référence,
date. Rien d'autre.

## 6. Mettre à jour

- `CLAUDE.md` : la ligne du sujet passe à « brouillon de virement prêt, à approuver dans l'app ».
- `facturation.md` (« Ce qu'on me facture ») ou la fiche du sujet : la référence du brouillon.
- Au point suivant, vérifie sur le relevé (`statement.py`) que le virement est bien parti avant
  de passer le sujet en « soldé ».
