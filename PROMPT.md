# Le prompt à coller dans Claude Code

Ouvre Claude Code dans le dossier cloné (ou dans un dossier vide) et colle tout le bloc
ci-dessous. Claude s'arrête après chaque étape et attend ton accord.

```
Je veux monter mon second cerveau pour gérer mon activité : un dossier de fichiers texte,
rempli depuis mes mails, que tu lis au début de chaque session. On le monte en cinq étapes,
dans cet ordre. À la fin de chaque étape, tu t'arrêtes, tu me montres ce que tu as fait,
et tu attends mon « ok » pour la suivante.

0. Préparer le dossier.
   - Si ce dossier ne contient pas déjà le modèle, clone-le ici :
     git clone https://github.com/vincentventalon/second-cerveau-compagnie .
   - Lis CLAUDE.md, README.md, et les fichiers par sujet. Ce sont des modèles vides :
     les lignes marquées « (exemple) » sont fictives, tu les remplaceras par les miennes.
   - Débranche le dossier du repo public : git remote remove origin. Ce que tu vas
     écrire contient mes données, rien ne doit partir sur GitHub. Dis-moi que c'est fait.

1. Brancher mes mails.
   Il y a deux voies, explique-les-moi en deux lignes chacune et laisse-moi choisir :
   - Voie simple, le connecteur Gmail. Vérifie si tu as des outils Gmail. Sinon,
     dis-moi d'ajouter Gmail sur claude.ai/customize/connectors, de relancer Claude Code
     et de taper /mcp. Si /mcp ne montre aucun connecteur claude.ai, dis-moi de taper
     /status : il faut être connecté avec un compte Claude, pas une clé API.
     Limite : le connecteur ne lit pas le contenu des pièces jointes.
   - Voie complète, les scripts de scripts/ (API Gmail avec mon propre accès Google).
     Ils téléchargent les pièces jointes et créent des brouillons avec pièce jointe.
     Guide-moi pas à pas avec la section « Les scripts Gmail » du README : le projet
     Google Cloud, l'API Gmail, le client OAuth « Desktop app », le fichier
     secrets/google/client_secret.json, puis :
       python3 -m venv .venv && .venv/bin/pip install -r scripts/requirements.txt
       .venv/bin/python scripts/auth_gmail.py
       .venv/bin/python scripts/gmail_lib.py
     Je peux aussi faire les deux : le connecteur pour lire, les scripts pour les pièces.
   Ensuite, avec le connecteur : liste-moi ses outils qui envoient, répondent ou
   transfèrent un mail, et propose-moi une règle « deny » dans .claude/settings.local.json
   qui les interdit dans ce dossier. Montre-la-moi, pose-la après mon accord.
   Test : montre-moi l'expéditeur et l'objet de mes 5 derniers mails reçus.
   STOP.

2. Tout explorer, en profondeur.
   - Demande-moi sur quelle période (je te conseille de commencer par 6 mois) et s'il y a
     des adresses à ignorer.
   - Trouve les gens qui m'écrivent pour mon activité : comptable, clients, banque,
     administrations, assurance, fournisseurs. Cherche aussi par mots : facture, devis,
     avoir, TVA, impôt, déclaration, cotisations, relevé, contrat, échéance, relance,
     paiement, mise en demeure.
   - Lis les fils en entier, pas les aperçus.
   - Les pièces jointes comptent plus que les mails : un montant se lit dans le PDF.
     Avec les scripts : télécharge-les dans data/pieces/ (gmail_cli.py grab) et lis-les.
     Avec le connecteur seul : fais-moi la liste des pièces utiles dans
     data/a-telecharger.md (date, expéditeur, objet, nom de la pièce, pourquoi elle
     compte), je les télécharge dans data/pieces/, puis tu les lis.
   - Note ce que tu trouves au fur et à mesure dans data/exploration.md pour ne rien
     perdre. Si la boîte est grosse, avance période par période.
   - N'écris encore rien dans les fichiers du modèle. Montre-moi la carte : les sujets
     trouvés (une ligne chacun), les interlocuteurs, les numéros, les factures.
   STOP.

3. Consolider, un fichier par sujet.
   - journal-des-mails.md : une ligne par échange qui compte, du plus ancien au plus
     récent : qui, quand, ce qui a été décidé, le lien du fil. Les contacts en bas.
   - facturation.md : mes clients, mes tarifs, ma numérotation, les factures émises et
     leur statut, ce qu'on me facture.
   - identifiants.md : chaque numéro (fiscal, TVA, entreprise, IBAN, numéros client)
     avec la pièce qui fait foi. Aucun mot de passe, aucun code d'accès.
   - sujets/ : une fiche par dossier de fond, au format de sujets/README.md.
   - Supprime les lignes « (exemple) » et le fichier sujets/exemple-retard-de-paiement.md.
   - N'invente rien. Ce qui n'est pas sûr s'écrit « à vérifier », avec ce qui manque.
   Montre-moi un résumé de ce qui est écrit, fichier par fichier, et les points à vérifier.
   STOP.

4. L'index, CLAUDE.md.
   Remplis « Qui je suis », « Échéances dures » (la plus proche en haut) et « Sujets
   ouverts » : une ligne par sujet, son statut, où il en est, la prochaine action, qui la
   fait, la date limite, le fichier du détail. Garde les sections « Comment travailler »
   et « Ce que tu as le droit de faire ». Reste sous 200 lignes. Montre-moi l'index.
   Puis fais un commit local (git add, git commit), jamais de push.
   STOP.

5. Les skills.
   Regarde ce qui revient dans mes mails : une facture chaque mois, un salaire à valider,
   un virement à préparer, une déclaration chaque trimestre, des relances. Propose-moi
   3 à 5 skills, une ligne chacune (ce qu'elle fait, la phrase qui la lance). Pars des
   trois exemples de .claude/skills/ : adapte-les à mon cas, ou supprime ceux qui ne me
   servent pas. Règle pour toutes : tu prépares, j'approuve. Mails en brouillon, banque en
   lecture, jamais de paiement ni d'envoi.
   Pour la banque : si elle a une API, propose de suivre scripts/revolut/README.md (ou
   l'équivalent chez ma banque) avec des permissions en lecture et brouillons seulement.
   Sinon, la skill prépare les détails du virement à recopier.
   Après mon choix, écris les skills, puis dis-moi laquelle lancer en automatique et
   comment (AUTOMATIQUE.md). Commit local.
   STOP.

Pour finir : résume-moi l'index en cinq lignes, donne-moi les trois prochaines actions,
et rappelle-moi que ce dossier contient mes données : il reste privé.
```
