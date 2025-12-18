# mcp_tests
> Ce projet contient plusieurs petits projets de serveurs MCP. Il me permet d'en apprendre plus sur la programmation de serveurs MCP sous Python.

## Général
Le Model Context Protocol permet de fournir du contexte aux LLM dans un format standard. Cela permet notamment de mettre à disposition des outils aux LLM que nous utilisons afin de simplfier certaines tâches. Le but de ce projet est avant tout, une première exploration de développement d'un serveur MCP. Des premiers essais de serveur MCP passant par simplification de la migration/reprise de données ainsi que la saisie des temps dans Fitnet à partir des événements Google Calendar.

## Requis
En ce qui concerne les requis afin de faire fonctionner les serveurs MCP il faut suivre la documentation sur [Github](https://github.com/modelcontextprotocol/python-sdk?tab=readme-ov-file#mcp-python-sdk).

Ici, ils recommandent d'utilise [uv](https://docs.astral.sh/uv/) qui est un package manager un peu comme pip mais en mieux.

Le sous-projet ```weather``` suit directement le "Build an MCP server" de la [documentation](https://modelcontextprotocol.io/docs/develop/build-server).

> [!WARNING]
> Attention en fonction de votre système d'exploitation, il faut installer et mettre en place correctement uv. De plus, pour les utilisateurs de Windows vous ne pourrez pas passer par WSL2 (en tout cas dans mon expérience) pour faire fonctionner le serveur MCP avec les LLM. Il faut indiquer le chemin Windows vers le dossier dans le fichier de configuration des serveurs mcp de votre outils LLM.

De mon côté, j'utilise Claude Desktop pour utiliser et tester mes fonctionnalités et serveurs. Cependant libre à vous d'utiliser l'outil que vous voulez! 

## Présentation des différents projets
En fonction des projets, il faut mettre en place des venv Python différents et installer des packages différents. Cependant pour tous les venv, il faut installer ```mcp[cli]``` comme la documentation nous l'indique.

### Projet ```weather``` & ```my_first_mcp_server```
Le projet weather est le premier projet proposé par la documentation afin de comprendre le fonctionnement et comment développer un serveur MCP. Il n'est pas spécialement intéressant car il est identique à celui de la documentation.


### Projet ```standardize_schema```
Dans ce projet se trouve la première étape de la méthodologie de reprise/migration de données. C'est la standardisation des fichiers de structures des bases de données **sources** et **cibles**. 

Pour en apprendre plus : [README](./standardize_schema/README.md)

### Projet ```schema_enrichment```
Ce projet représente la deuxième étape de la méthodologie de reprise/migration de données. Les ajouts des commentaires selon le context aux fichiers de structures standardisés. 

Pour en apprendre plus : [README](./schema_enrichment/README.md)

### Projet ```fitnet_mcp```
Ce projet n'appartient pas à la méthodologie de reprise/migration de données. Il est une continuation d'un outil qui permet récupérer les événements Google Calendar de la semaine passée et de faire la conversion H-m/100. 

Après avoir récupéré le fichier ```.xls``` sur Fitnet, en le fournissant au LLM il va récupérer les événements sur votre Calendrier Google et essayer de les attribuer à vos affaires/projets. 

Pour en apprendre plus : [README](./fitnet_mcp/README.md)

## Debug et tests
Comme la documentation, pour tester debugguer vos serveurs MCP il y a plusieurs moyens. J'utilise [MCP Inspector](https://modelcontextprotocol.io/docs/tools/inspector) qui est un outil parmis la documentation de [debugging](https://modelcontextprotocol.io/legacy/tools/debugging) et qui permet d'avoir une interface web qui permet des tester les tools de nos serveurs en local.

> [!TIP]
> Pour les personnes sur Windows il va falloir installer node pour pouvoir faire fonctionner MCP Inspector. 
> Il faut indiquer le chemin vers le dossier de la même manière que dans le fichier de configuration des serveurs MCP : 
> ```bash
> npx @modelcontextprotocol/inspector uv --directory "C:...." run machin.py
> ```
