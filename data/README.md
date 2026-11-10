# data/

Tes pièces : PDF des factures, relevés bancaires, pièces jointes téléchargées, documents
officiels. **Rien de ce dossier n'est versionné** (voir `.gitignore`), sauf ce fichier.

Rangement proposé (Claude crée les dossiers au besoin) :

```
data/pieces/      les pièces jointes téléchargées depuis les mails
data/factures/    les factures émises, une par numéro
data/releves/     les relevés bancaires
data/brouillons/  les textes de mail et les CSV de virement préparés par Claude
```

Claude lit les PDF posés ici. Pour un PDF de plus de 10 pages, il lui faut `pdftoppm`
(installe poppler : `brew install poppler` sur Mac).
