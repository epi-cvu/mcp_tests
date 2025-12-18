# shema_enrichment
## Général
La reprise et la migration de données est un travail long et complexe il existe plusieurs façon de traiter la problématique. Le CT propose un méthodologie aliant l'utilisation des IA et la validation humaine afin d'accélérer ce processus. 
- La **standardisation** : mettre les différentes structures des bases de données sous un format commun.
- L'**enrichissement** : demander à l'IA d'interpréter les colonnes selon le contexte et de mettre un commentaire sur la signification (sur le nom de la colonne).
- La **1ere validatation** : En fonction de la quantité de donnée un humain peut confirmer la signification métier des colonnes commentées
- Le **Minimum Viable Data** (MVD) : Dans le cas d'un très grand nombre de variables, les équipes métiers peuvent se concerter et définir un MVD. Le MVD représente les varaibles minimum à reprendre pour que l'application fonctionne ainsi que donner la possibilité au client de travailler. 
- Le **Mapping des variables** : à partir du MVD nous allons demander à l'IA de mapper les variables de l'application source (dont on ne connaît pas forcément la structure et/ou les significations) vers les variables de l'application cible (dont on possède les connaissances métiers).
- La **2ème validation humaine** : Après le mapping nous allons avec les équipes métier confirmer le mapping des variables et passer aux indications de transformations.
- La **transformation** : les équipes métiers vont se réunir afin de définir les transformations possibles sur les données en fonction des mappings. Cela peut être un changement de dictionnaire 1->a ou encore des modifications textes ou autres. 

L'import reste à la charge de l'équipe pour laquel les données ont été transformées. 

Cette méthodologie suit une sorte de workflow ETL qui ajoute l'IA pour le mapping. 

## L'enrichissment des schémas.
Après l'unification des structures des bases de données