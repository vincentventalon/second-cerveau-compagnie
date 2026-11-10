# Lancer une skill en automatique

Exemple : le point avec le comptable, le 1er de chaque mois à 9 h. La skill tourne seule, met le
dossier à jour et prépare les brouillons. Toi, tu relis et tu envoies.

Il y a trois façons de faire. Pour ce dossier, la première est la bonne : la tâche a besoin de
tes fichiers locaux.

## 1. Une tâche planifiée locale, dans l'app de bureau Claude

C'est la voie conseillée. La tâche tourne sur ton ordinateur, dans ce dossier, avec tes fichiers
et tes connecteurs ([doc](https://code.claude.com/docs/en/desktop-scheduled-tasks)).

1. Dans l'app de bureau Claude, onglet **Code**, ouvre **Scheduled** (ou **Routines** si ton app
   affiche encore l'ancien nom), puis **New task**.
2. Nom : `point-comptable-mensuel`. Instructions : « Utilise la skill point-comptable de ce
   dossier. Rends-moi la liste des brouillons prêts et des questions pour moi. »
3. Dans **Advanced settings**, active **Only on this computer** et choisis ce dossier.
4. Mode de permission : garde celui qui te demande avant d'agir.
5. Crée la tâche, puis ouvre **Edit** et choisis **Custom** avec l'expression
   `0 9 1 * *` (le 1er du mois à 9 h, heure locale).
6. Clique **Run now** une première fois et réponds aux demandes de permission : les lancements
   suivants s'arrêteront moins souvent.

À savoir :

- la tâche ne tourne que si l'app est ouverte et l'ordinateur allumé et réveillé ; si
  l'ordinateur dormait, elle rattrape le dernier lancement manqué à son réveil ;
- si elle attend une permission, elle reste bloquée : ouvre sa session dans l'historique de la
  tâche et réponds ;
- tu peux aussi la créer en écrivant dans une session de l'app : « tous les 1er du mois à 9 h,
  lance /point-comptable dans ce dossier ».

## 2. Une tâche planifiée dans le cloud

Elle tourne même ordinateur éteint, créée avec `/schedule` ou sur claude.ai/code/routines
([doc](https://code.claude.com/docs/en/routines)). Mais elle part d'une copie fraîche d'un repo
GitHub, pas de ton ordinateur : ton dossier `data/` et tes `secrets/` n'y sont pas, et il
faudrait pousser ton dossier rempli sur GitHub. **Pour ce dossier, évite.** Elle peut servir
plus tard pour une tâche qui n'a besoin que des connecteurs (lire les mails et te faire un
résumé).

## 3. `claude -p` dans un cron

Pour ceux qui ont l'habitude du terminal. `claude -p` lance Claude sans fenêtre, et une skill se
lance en écrivant `/nom-de-la-skill` dans le prompt
([doc](https://code.claude.com/docs/en/headless)) :

```
0 9 1 * * cd /chemin/vers/mon-second-cerveau && claude -p "/point-comptable" >> data/automatique.log 2>&1
```

Sans fenêtre, personne ne répond aux demandes de permission : ce qui en demande une est refusé.
Il faut donc autoriser à l'avance ce dont la skill a besoin (`--allowedTools`, voir la doc), et
rien de plus. Ne mets jamais d'outil d'envoi de mail ou de paiement dans cette liste.
