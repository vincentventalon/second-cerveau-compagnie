---
name: point-comptable
description: Fait le point avec le comptable (ou tout prestataire qui écrit souvent) - lit les mails reçus depuis la dernière ligne du journal, lit les pièces jointes, met à jour le journal, l'index et les fiches, range les numéros trouvés, et prépare les réponses en brouillon. N'envoie jamais rien. À utiliser quand on dit « fais le point avec le comptable », « qu'est-ce que le comptable m'a demandé », « où on en est de la TVA », « réponds au comptable », « il y a du nouveau ? », ou au lancement mensuel automatique.
---

# Le point avec le comptable

Le principe : on part de ce que le dossier sait déjà, on lit seulement ce qui est nouveau, et
on finit par mettre l'index à jour.

## 1. Où on en était

- `CLAUDE.md` : les sujets ouverts qui attendent le comptable, les échéances.
- `journal-des-mails.md` : la date de la dernière ligne, et l'adresse du comptable dans
  « Contacts ».

## 2. Ce qui est nouveau

Cherche les mails échangés avec le comptable depuis cette date, reçus et envoyés.

- Avec les scripts Gmail :
  `.venv/bin/python scripts/gmail_cli.py search "(from:<adresse> OR to:<adresse>) after:<AAAA/MM/JJ>"`, puis
  `.venv/bin/python scripts/gmail_cli.py thread <id_du_fil>` pour chaque fil, en entier.
- Avec le connecteur Gmail : la même recherche, et lis les fils en entier, pas les aperçus.

Lis aussi les pièces jointes : un relevé, une facture ou un avis n'est jamais résumé à partir du
texte du mail.

- Avec les scripts :
  `.venv/bin/python scripts/gmail_cli.py grab "from:<adresse> has:attachment after:<AAAA/MM/JJ>" --out data/pieces --ext .pdf`,
  puis lis les PDF dans `data/pieces/`.
- Avec le connecteur seul : liste les pièces (date, objet, nom) et demande à l'humain de les
  télécharger dans `data/pieces/`. Attends qu'elles y soient avant de conclure.

## 3. Mettre à jour le dossier

- `journal-des-mails.md` : une ligne par échange qui compte, en bas, avec ce qui a été décidé ou
  demandé et le lien du fil.
- `CLAUDE.md` : pour chaque sujet touché, le statut, où ça en est, la prochaine action, la date
  limite. Une nouvelle échéance va dans « Échéances dures ».
- Une fiche dans `sujets/` si un sujet ne tient plus en une ligne.
- Un numéro nouveau va dans `identifiants.md`, avec sa pièce.
- Un montant dû va dans `facturation.md` (« Ce qu'on me facture ») ; s'il faut payer, propose la
  skill `preparer-virement`.

## 4. Les réponses, en brouillon

Pour chaque question du comptable :

- la réponse est dans le dossier : écris-la, cite la source, prépare le brouillon dans le fil
  (`gmail_cli.py draft --reply-to <id_du_message> ...`, ou le connecteur) ;
- la réponse n'y est pas : ne l'invente pas, mets la question dans la liste pour l'humain.

Une seule question par mail au comptable, courte, sans rien qu'on puisse trouver soi-même.

## 5. Rendre la main

Termine par :

1. ce qui a changé (trois lignes au plus) ;
2. les brouillons prêts : objet et destinataire de chacun, à relire et envoyer ;
3. les questions pour l'humain ;
4. la prochaine échéance.
