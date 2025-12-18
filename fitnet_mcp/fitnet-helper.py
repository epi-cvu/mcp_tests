from mcp.server.fastmcp import FastMCP
import os
import json
import pandas as pd

from tools.main import retrieve_data

mcp = FastMCP("fitnet_helper")

def get_projects(xls_path):
    """Extrait les projets et affaires du fichier HTML déguisé en XLS"""
    try:
        df_list = pd.read_html(xls_path)
        df = df_list[0]
        
        # Vérifier que les colonnes existent
        if "Projet" not in df.columns or "Affaire" not in df.columns:
            available_cols = ", ".join(df.columns.tolist())
            raise ValueError(f"Colonnes 'Projet' ou 'Affaire' introuvables. Colonnes disponibles : {available_cols}")
        
        # Filtrer les lignes où Projet n'est pas nul
        result = list(df["Affaire"][df["Affaire"].notna()])
        final_list = result + ["Epiconcept", "Formation Interne", "Temps Non Attribué (TNA)", "Temps de déplacement"] 
        
        return final_list
        
    except Exception as e:
        raise Exception(f"Erreur lors de la lecture du fichier : {str(e)}")

@mcp.tool()
async def simplify_calendar_fitnet(
    input_path: str,
) -> str:
    """Va chercher les actions, réunions et ce qui a été fait la semaine 
    dernière pour en faire des calculs horaires. Cela va permettre de faciliter
    la saisie dans fitnet.

    Args:
        input_path (str): chemin vers le fichier xls téléchargé sur Fitnet qui 
        indique les différents projets et affaires assignés à moi.

    Returns:
        str: Message qui indique les calculs des temps ainsi que la liste avec
        les projets à relier vers les temps calculés.
    """
    if not os.path.exists(input_path):
        return f"Erreur : Le fichier '{input_path}' n'existe pas"
    
    try:
        # Récupération des données temporelles
        info_to_compare = retrieve_data()
        
        # Récupération des projets et affaires
        list_of_projects = get_projects(input_path)
        
        return f"""✅ Récupération des heures de la semaine dernière réussie

📊 Calcul des temps :
{info_to_compare}

📋 Liste des affaires :
{list_of_projects}
"""
        
    except Exception as e:
        return f"❌ Erreur lors de la récupération des informations : {str(e)}"
    

@mcp.tool()
async def map_calendar_to_projects(
    input_calendar: dict,
    input_project_list: list
):
    """Utilise l'IA pour mapper les événements de Google Calendar aux projets Fitnet attribué.

    Args:
        input_calendar (dict): dictionnaire des événements récuppérés sur le Google Calender + le calcul des temps
        input_project_list (list): Liste des projets Fitnets actuels

    Returns:
        Message décrivant les attributions des évnénements Google Calendar à des projets Fitnet.
    """
    try:
        prompt = (
            f"Tu est un assistant qui aide à mapper des événements de calendrier vers des projets Fitnet.\n\n"
            f"Voici le calendrier des événements ainsi que le nombre d'heures : {input_calendar}.\n"
            f"Voici une liste des projets Fitnet qui me sont attribués : {input_project_list}.\n"
            f"Pour chaque événement du calendrier, tu dois déterminer quel projet Fitnet correspond le mieux.\n\n"
            f"Règles importantes:\n"
            f"1. Si tu ne sais pas où mapper l'événement ou s'il s'agit d'activité générales, mappe le vers TNA.\n"
            f"2. Pour ce qui est du temps Epiconcept, cela concerne : cela concerne principalement les réunions staff.\n"
            f"3. Tout ce qui est en rapport avec Neha/NEHA ou SDV appartient à DOFI/ Données fictives.\n\n"
            f"Répond UNIQUEMENT avec un JSON valide (sans markdown, sans preamble) au format :\n"
            f"{{'day': {{'event_name': 'projet_fitnet_correspondant', 'temps' : 'temps_inscrit', 'total_journee': 'temps_total_journee'}}}}\n\n"
            f"Donne moi un JSON de la réponse."
            )
        return (
            f"{prompt}"
        )
        
    except Exception as e:
        return f"Erreur lors mapping : {str(e)}."

def main():
    """ Point d'entrée du serveur MCP
    """
    mcp.run(transport='stdio')

# Démarrage du serveur
if __name__ == "__main__":
    main()