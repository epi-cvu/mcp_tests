# fitnet_mcp 
Fitnet est un outil de saisie de temps au sein d'Epiconcept. Cette saisie Fitnet est une tâche que tout collaborateur d'Epiconcept doit faire afin de saisir les heures passées et sur les affaires et/ou projets. Lorsqu'il y a peu d'affaires, la saisie reste assez simple cependant lorsque la quantité de projets et d'affaires augmentent et le nombre d'événements liés aussi, la complexité de la saisie l'est également. 

Le but de ce serveur MCP est de simplifier la saisie des temps en utilisant l'IA pour attribuer les événements Google Calendar aux affaires et projets de Fitnet. 

## Comment ça marche ?
Actuellement le serveur MCP n'a pas la possibilité d'accéder aux APIs de Fitnet (question de sécurité et compte admin pour accéder aux API de Fitnet). De ce fait, nous utilisons l'IA plutôt pour mapper les affaires et les projets directement aux événements Google Calendar. 

Dans un premier temps, nous allons utiliser l'API de Google pour accéder à notre emploi du temps en **read_only**. Le mode **read_only** est important car il de garder cette sécurité et de ne pas utiliser au délà l'API Google. Avant de pouvoir accéder à votre API, vous aurez une page qui va demander l'autorisation d'accès à votre compte Google. Cela va générer un fichier ```token.json``` dans le dossier ```fitnet_mcp```.

> [!CAUTION]
> NE PARTAGEZ SURTOUT PAS LE FICHIER ```TOKEN.JSON```

> [!IMPORTANT]
> Il faut noter que l'API n'a accès seulement et SEULEMENT à votre emploi du temps il ne va en aucun chercher ou regarder le calendrier d'un autre collaborateur. 

Ensuite, il faut une petite action de notre côté afin d'aller chercher les projets et affaires. Pour cela il faut aller sur Fitnet et récupérer le fichier ```.xls```. Dans ce fichier, l'outil du serveur MCP va récuppérer la colonne ```Affaires``` et utiliser l'IA pour mapper les événements directements à ces affaires.

> [!TIP]
> Pour récuppérer le fichier en question il faut :
> -> Feuille de temps -> ... (trois petits points) -> Export Excel

L'IA peut se tromper mal mapper, actuellement le prompt interne (celui qui permet de demander le mapping) est assez spécifique. L'objectif est de demander la validation de l'utilisateur qui permettrait ensuite d'ajouter du contexte. 

Imaginons : Une ```réunion staff``` de 2h à été mappée à ```TNA``` (Temps Non Attribué) au lieu de ```Epiconcept```. Nous pourrions l'invalider et ajouter la précision à l'IA et lui dire que ```réunion staff``` devra être mappé à ```Epiconcept```. Cette information serait ensuite stocké dans un fichier texte qui pourrait être lu par l'IA avant de mapper les événements. (Cela pourriat jouer comme une sorte de mémoire).

## Requirements
Pour les requirements il faut installer tous les packages Python du fichier ```requirements.txt```. 

Avec uv il faut simplement activer l'environnement virtuel python que vous avez généré et ensuite lancer la commande:
```
uv pip install -r requirements.txt
```

Récupérer le fichier ```credentials.json``` pour pouvoir accéder à l'API de Google. Lors de la première utilisation, vous devrez autoriser l'accès à votre compte Google et récupérer le fichier ```token.json``` qui s'écrira automatiquement dans ce dossier.

## ```fitnet-helper.py```
Dans le fichier de configuration des serveurs mcp il faut indiquer le chemin absolu vers le dossier en question pour que cela fonctionne.
```json
{
    "mcpServers": {
        "weather": {
            "command": "uv",
            "args": [
                "--directory",
                "C:\\Users\\Charles VU\\Documents\\GitHub\\mcp_tests\\fitnet_mcp",
                "run",
                "fitnet-helper.py"
            ]
        }
    }
}
```

## tools 
Dans le dossier tools se trouve le programme originel ```main.py``` en CLI pour récupérer les informations sur l'API Google Calendar. 

## Prompt 
Après avoir récupéré la feuille d'activité sur Google Calendar et avoir autorisé **Filesystem** à accéder à **Bureau/easy_access/fitnet_tests_mcp** (ou votre dossier où se trouve le fichier Excel). 

Vous allez pouvoir utiliser ce prompt :
> Salut je voudrais que tu me mappes mes événements google calendar de la semaine dernière aux affaires Fitnet de ce fichier : "//Chemin absolu vers le fichier//PageactivitesByCollaborateurCrossDataXLS.xls"

Vous allez pouvoir demander par la suite les corrections ou valider le mapping.