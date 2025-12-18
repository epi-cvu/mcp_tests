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
Après l'unification des structures des bases de données, pour le mapping, il est important d'ajouter du contexte. Pour répondre à cette problématique, nous allons utiliser l'IA afin d'ajouter ce contexte. 

Nous allons utiliser l'IA afin d'ajouter une descriptions pour chaque colonnes puis nous pourrons par la suite décider de valider ou non cette description. Pour ajouter une description précise, l'IA a quand même besoin d'un contexte général. 

## Requirements
Pour les requirements il faut installer tous les packages Python du fichier ```requirements.txt```. 

Avec uv il faut simplement activer l'environnement virtuel python que vous avez généré et ensuite lancer la commande:
```
uv pip install -r requirements.txt
```

## ```schema_enrichment.py```
Dans le fichier de configuration des serveurs mcp il faut indiquer le chemin absolu vers le dossier en question pour que cela fonctionne.
Le fichier ```schema_enrichment.py``` est la nouvelle version de ```schema_enrichment.py``` avec une simplification des tools et de la documentation. 
Voici un exemple du fichier de configuration 
```json
{
    "mcpServers": {
        "weather": {
            "command": "uv",
            "args": [
                "--directory",
                "C:\\Users\\Charles VU\\Documents\\GitHub\\mcp_tests\\schema_enrichment",
                "run",
                "schema_enrichment.py"
            ]
        }
    }
}
```

## Prompt
De la même manière que ```standardize_schema``` il faut autoriser le connecteur **Filesystem**. 

Il y a 3 choses à indiquer :
- Le chemin vers le fichier metadata.json qui vient d'être standardisé
- Le contexte de la base de données
- La langue de la descriptions (Fr ou En)

Supposons que nous avons un fichier de structure SQL d'une application pour le cancer du sein. Chez Epiconcept c'est ESIS-DOCS. Nous avons un fichier ```docs_metadata.json``` qui a été standardisé le prompt est alors ; 

> J'aimerai que tu me décrives les colonnes de ce metadata //Chemin absolu vers mon fichier//docs_metadata.json en français. Cette base de données concerne le dépistage du cancer du sein. 
> 