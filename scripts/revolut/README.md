# Revolut Business : lire tes comptes et préparer des virements en brouillon

Trois scripts, sans dépendance (Python 3 et `openssl`, déjà présent sur Mac et Linux) :

| Script | Fait | Permission Revolut |
|---|---|---|
| `auth.py` | la connexion, le contrôle de la société, la liste des comptes | `READ` |
| `statement.py` | les relevés CSV, soldes vérifiés ligne à ligne | `READ` |
| `brouillons.py` | la liste des bénéficiaires, les brouillons de virement | `READ`, `WRITE` |

**Aucun script ne peut payer.** Tu donnes à l'accès les permissions `READ` et `WRITE`, jamais
`PAY`. D'après la doc de Revolut, `READ` couvre les lectures, `WRITE` couvre la création de
brouillons de paiement, et `PAY` seul permet de lancer un virement. Un brouillon reste dans
l'app jusqu'à ce que tu l'envoies et l'approuves toi-même.

Ta banque n'est pas Revolut ? Garde l'idée : lecture seule, brouillons, approbation dans l'app.
Si ta banque n'a pas d'API, la skill `preparer-virement` te prépare les détails à recopier.

## Mettre en place l'accès (une fois)

Les étapes suivent la doc Revolut « Make your first API request ». Si un écran a changé, la doc
fait foi : https://developer.revolut.com/docs/guides/manage-accounts/get-started/make-your-first-api-request

1. **Crée ta clé et ton certificat**, dans le dossier des secrets (gitignoré) :

   ```
   mkdir -p secrets/revolut && cd secrets/revolut
   openssl genrsa -out privatecert.pem 2048
   openssl req -new -x509 -key privatecert.pem -out publiccert.cer -days 1825
   ```

   `privatecert.pem` ne sort jamais de ton ordinateur.

2. **Dépose le certificat chez Revolut.** Dans l'app web Revolut Business, choisis la bonne
   société si tu en as plusieurs, puis Paramètres, APIs, **Business API**, ajoute un certificat.
   Colle le contenu de `publiccert.cer` (lignes BEGIN et END comprises) et donne une adresse de
   redirection (une page à toi, par exemple ton site). Revolut te donne un **client ID**.

3. **Remplis `secrets/revolut/config.json`** :

   ```json
   {
     "client_id": "<le client ID donné par Revolut>",
     "iss": "<le domaine de ton adresse de redirection, sans https://>",
     "redirect_uri": "<l'adresse de redirection, au caractère près>",
     "iban": "<l'IBAN de ton compte principal>",
     "accounts": {},
     "default_account": "principal",
     "history_from": "2026-01-01"
   }
   ```

   L'IBAN sert de contrôle : si le jeton ouvre une autre société, les scripts s'arrêtent.

4. **Donne ton accord** :

   ```
   python3 scripts/revolut/auth.py consent-url
   ```

   Ouvre l'URL affichée. Elle demande `READ,WRITE` seulement. Valide. Revolut te renvoie sur ton
   adresse de redirection avec `?code=...` dans la barre d'adresse. Copie ce code.

5. **Échange le code tout de suite** (il expire vite) :

   ```
   python3 scripts/revolut/auth.py exchange <code>
   ```

6. **Déclare tes comptes** : `python3 scripts/revolut/auth.py accounts` liste leurs ids. Mets-les
   dans `accounts` de `config.json`, par exemple `{"principal": "<id>"}`. Puis
   `python3 scripts/revolut/statement.py list` vérifie qu'aucun compte n'a été oublié.

Le jeton d'accès dure 40 minutes et se renouvelle tout seul. Plusieurs sociétés : un dossier
par société, et `REVOLUT_DIR=secrets/revolut-autre python3 scripts/revolut/...`.

## Usage courant

```
python3 scripts/revolut/auth.py accounts                           # soldes
python3 scripts/revolut/statement.py all 2026-01-01 2026-03-31 data/releves
python3 scripts/revolut/brouillons.py beneficiaires
python3 scripts/revolut/brouillons.py creer data/virements/2026-01.csv        # aperçu
python3 scripts/revolut/brouillons.py creer data/virements/2026-01.csv --oui  # crée
python3 scripts/revolut/brouillons.py liste
```

## Pannes courantes

| Message | Remède |
|---|---|
| `Il manque .../config.json` | Étape 3. |
| `Revolut refuse le jeton : HTTP 400` à l'échange | Le code a expiré ou a déjà servi : refais l'étape 4. |
| `Le jeton n'ouvre pas la société attendue` | Tu as donné ton accord sur une autre société. Change de société dans l'app, refais l'étape 4. |
| `Comptes non déclarés avec des mouvements` | Ajoute ces ids dans `accounts` (une épargne, souvent). |
| `Soldes non chaînés` | Une transaction manque dans la période lue. Relance ; si ça persiste, compare au relevé PDF de l'app. |
