# standardize_schema 
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

## Standardisation 
La standardisation permet d'unifier les fichiers des structures de bases de données : 
- La structure de la base de données source (application inconnue ou non) 
- La structure de la base de données cible (application interne/connue)

Le format suit le format de Metadata de Synthetic Data Vault. Il décrit sous format **JSON** : les tables, le colonnes, les types au sein des colonnes et les relations entre les tables en précisant clés primaires et étrangères.

## Fichiers d'entrée 
L'outil est capable de standardiser certains types précis de fichier d'entrée : 
- fichier de structure **SQL**
- fichier de structure **XML**
- dossier contenant des **CSV** (tables + données)
- dossier **Voozanoo 3** venant du module d'export de William
- fichier **JSON Voozanoo 4** provenant d'Epicraft

## Requirements
Pour les requirements il faut installer tous les packages Python du fichier ```requirements.txt```. 

Avec uv il faut simplement activer l'environnement virtuel python que vous avez généré et ensuite lancer la commande:
```
uv pip install -r requirements.txt
```

Il faut aussi avoir accès à SDV enterprise pour avoir la version améliorer de la détection de tables CSV. Pour cela il faut contacter Charles pour avoir le package en question.

## ```modernized_standardizer.py```
Dans le fichier de configuration des serveurs mcp il faut indiquer le chemin absolu vers le dossier en question pour que cela fonctionne.
Le fichier ```modernized_standardizer.py``` est la nouvelle version de ```metadata_standardizer.py``` avec une simplification des tools et de la documentation. 
Voici un exemple du fichier de configuration 
```json
{
    "mcpServers": {
        "weather": {
            "command": "uv",
            "args": [
                "--directory",
                "C:\\Users\\Charles VU\\Documents\\GitHub\\mcp_tests\\standardize_schema",
                "run",
                "modernized_standardizer.py"
            ]
        }
    }
}
```
## Prompt
Pour utiliser le prompt il faut aussi autoriser sur Claude Desktop le connecteur **Filesystem** dans mon cas, je ne l'ai autorisé à accéder seulement mon dossier **Bureau/easy_access/tests_mcp**.

Il faut obligatoirement indiquer le chemin absolu vers le fichier d'entrée en question mais il n'est pas nécessaire d'indiquer quel est son type de fichier. 
Le fichier standardisé sera automatiquement enregistrer dans le dossier dans lequel vous avez indiqué le fichier source. Vous pouvez aussi lui indiquer le nom mais par défaut ce sera ```metadata.json```

> [!TIP]
> Je vous conseil fortement de donner un nom spécifique au fichier standardisé sinon les fichiers seront écrasés.

Par exemple supposons que j'ai un fichier de structure d'un projet **Voozanoo 4** (patient-visite). Mon prompt ressemblerait à :

> J'aimerai que tu me standardises ce fichier Voozanoo 4 //Chemin Absolu vers mon fichier//patient-visite-voo4.json et enregistre le sous le nom "standardized-voo4.json"
>