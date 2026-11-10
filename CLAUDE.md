# Mon second cerveau : l'index

> **Claude : lis ce fichier en premier, à chaque session. Mets-le à jour en dernier, avant de
> rendre la main.** Si un fait n'est ni ici ni dans un fichier lié, il n'existe pas : va le
> chercher dans les mails, puis range-le.
>
> Les lignes marquées « (exemple) » sont fictives. Remplace-les par les vraies, puis supprime-les.

## Qui je suis

- **Activité** : <freelance, société, forme juridique> (exemple : ACME Conseil, entreprise individuelle)
- **Ce que je fais, en une ligne** : <ton métier>
- **Mes mails** : <adresse>, branchée par le connecteur Gmail
- **Ma banque pro** : <banque>, en lecture seule
- **Mon comptable** : <cabinet>, voir `journal-des-mails.md` pour l'historique

## Échéances dures

Ce qui a une date qu'on ne peut pas rater. La plus proche en haut.

| Date | Quoi | Sujet |
|---|---|---|
| 2026-01-15 (exemple) | Déclaration de TVA du trimestre, à déposer par le Cabinet Dupont | S1 |

## Sujets ouverts

Une ligne par sujet. Le détail vit dans le fichier lié, jamais ici.

| # | Sujet | Statut | Où ça en est | Prochaine action | Qui | Date limite | Détail |
|---|---|---|---|---|---|---|---|
| S1 | TVA du trimestre (exemple) | attend quelqu'un | Relevés envoyés au Cabinet Dupont le 06/01 | Vérifier que la déclaration est déposée | le comptable | 2026-01-15 | `journal-des-mails.md` |
| S2 | Facture de décembre à ACME SAS (exemple) | à moi | Brouillon prêt, pas envoyé | Relire et envoyer le mail | moi | 2026-01-05 | `facturation.md` |
| S3 | Retard de paiement ACME SAS (exemple) | en cours | Relance envoyée le 10/01, pas de réponse | Relancer une 2e fois le 20/01 | moi | 2026-01-20 | `sujets/exemple-retard-de-paiement.md` |

Statuts : **à moi** (j'ai une action), **attend quelqu'un**, **en cours**, **soldé**. Un sujet
soldé reste ici un mois, puis il ne vit plus que dans le journal.

## Où est quoi

| Fichier | Contient | Quand l'ouvrir |
|---|---|---|
| `journal-des-mails.md` | qui m'a écrit, quand, ce qui a été décidé | pour retrouver un échange, avant de répondre à quelqu'un |
| `facturation.md` | clients, numérotation, factures émises et payées | facture, relance, chiffre d'affaires |
| `identifiants.md` | tous mes numéros, chacun avec la pièce qui fait foi | **avant de chercher un numéro dans les mails** |
| `sujets/` | une fiche par dossier de fond | quand une ligne ci-dessus renvoie vers une fiche |
| `data/` | PDF, relevés, pièces jointes (jamais versionné) | pour lire un montant à la source |
| `.claude/skills/` | les tâches qui reviennent | voir la liste plus bas |
| `scripts/` | Gmail par l'API : chercher, lire un fil, télécharger les pièces, brouillon | quand le connecteur ne suffit pas (pièces jointes) |
| `scripts/revolut/` | soldes, relevés, brouillons de virement | pour la banque, voir son `README.md` |
| `secrets/` | mes accès Google et banque (jamais versionné) | jamais : ne lis pas, ne recopie pas son contenu |

Les scripts Gmail tournent avec `.venv/bin/python scripts/gmail_cli.py <commande>` (`--help` pour
la liste). Les scripts Revolut avec `python3 scripts/revolut/<script>.py`.

## Comment travailler

- **Début de session** : lis cet index, puis le fichier du sujet dont on parle.
- **Fin de session** : mets à jour la ligne du sujet (statut, où ça en est, prochaine action,
  date), ajoute les nouveaux échanges en bas du journal, date du jour.
- **Un numéro trouvé** (fiscal, TVA, client, dossier) va dans `identifiants.md` dans la même
  session, avec la pièce qui fait foi.
- **Les montants ne s'écrivent pas en prose ici** : ils vivent dans `facturation.md` ou dans la
  fiche du sujet. L'index dit où ils sont.
- **Ne devine pas.** Un fait non confirmé s'écrit « à vérifier », avec ce qui manque.
- **Un PDF compte plus qu'un mail** : si un mail résume une pièce jointe, lis la pièce.
- Ce fichier reste sous 200 lignes. Au-delà, déplace le détail dans `sujets/`.

## Ce que tu as le droit de faire

| Oui | Non |
|---|---|
| Lire mes mails et la liste des pièces jointes | Envoyer, répondre ou transférer un mail |
| Écrire des brouillons dans Gmail | Supprimer ou archiver un mail sans me demander |
| Lire mes soldes et mes opérations | Payer, valider ou envoyer un virement |
| Créer un brouillon de virement, si l'accès existe | Écrire un mot de passe, un token ou une clé dans un fichier |
| Écrire dans les fichiers de ce dossier | Pousser ce dossier sur un repo public |

Tu prépares, j'approuve. Quand un brouillon est prêt, dis-le moi avec son objet et son
destinataire : c'est moi qui l'envoie.

## Les skills

| Skill | Je dis |
|---|---|
| `facture-du-mois` | « fais la facture d'octobre » |
| `point-comptable` | « fais le point avec le comptable » |
| `preparer-virement` | « prépare le virement de <quoi> » |

Lancer une skill tout seul : `AUTOMATIQUE.md`.
