# Facturation

Tout ce qu'il faut pour faire une facture sans rien chercher, et savoir ce qui est payé. Les
montants vivent ici, pas dans l'index. Les PDF des factures sont dans `data/factures/`.

## Mes clients

| Client | Contact facturation | Tarif | Unité | Conditions | Où envoyer la facture |
|---|---|---|---|---|---|
| ACME SAS (exemple) | factures@acme.example | 500 € HT | jour | 30 jours fin de mois | par mail, PDF joint, n° de commande 0000 en objet |

## Comment je fais une facture

- **Outil** : <ton logiciel de facturation, un tableur copié du mois d'avant, un traitement de
  texte> (exemple : je copie la facture du mois précédent et je change les lignes)
- **Numérotation** : <ta règle> (exemple : `AAAA-NNN`, un compteur qui ne revient jamais en arrière)
- **Dernier numéro utilisé** : 2025-012 (exemple)
- **Mentions obligatoires** : <celles de ton pays et de ton statut, à demander à ton comptable>
- **TVA** : <taux, ou la mention d'exonération qui s'applique à toi>

## Factures émises

Une ligne par facture. Statut : brouillon, envoyée, payée, en retard.

| N° | Date | Client | Période | HT | TVA | TTC | Statut | Payée le | Pièce |
|---|---|---|---|---|---|---|---|---|---|
| 2025-012 (exemple) | 2025-11-30 | ACME SAS | novembre 2025 | 5 000,00 € | 1 000,00 € | 6 000,00 € | en retard | | `data/factures/2025-012.pdf` |

## Ce qu'on me facture

Les fournisseurs qui reviennent : comptable, logiciels, assurance, banque.

| Fournisseur | Quoi | Montant | Fréquence | Comment je paie | Dernière facture |
|---|---|---|---|---|---|
| Cabinet Dupont (exemple) | tenue des comptes | 150,00 € HT | mois | virement | 2026-01 |
