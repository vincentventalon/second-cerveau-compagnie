# Les fiches de fond

Un sujet qui ne tient pas en une ligne de l'index a sa fiche ici : un litige, un contrôle, un
retard de paiement, un prêt, un changement de statut. Un fichier par sujet, nommé par ce qu'il
est (`retard-acme.md`, `controle-tva-2025.md`).

L'index garde une ligne et renvoie ici. La fiche garde tout le reste.

## La forme d'une fiche

```
# <Le sujet>

**En trois lignes** : ce qui se passe, ce qui est en jeu, ce qui bloque.

**Où ça en est** (au <date>) : <l'état>.
**Prochaine action** : <qui fait quoi, avant quand>.

## Chronologie
| Date | Ce qui s'est passé | Source |

## Les pièces
<les PDF dans data/, ce que chacun prouve>

## Ce qui reste flou
<ce qu'on ne sait pas encore, et qui peut répondre>
```

Un sujet soldé garde sa fiche : on ajoute « Soldé le <date> » en tête, et l'index retire sa ligne
au bout d'un mois.
