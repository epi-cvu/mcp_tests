from mcp.server.fastmcp import FastMCP
import os
import json
import pandas as pd
from datetime import datetime
from pathlib import Path

from tools.main import retrieve_data

mcp = FastMCP("fitnet_helper")

MEMORY_FILE = Path("fitnet_mapping_memory.json")

# REGLES PAR DEFAUT
DEFAULT_MAPPINGS = {
    "event_patterns": {
        "neha": {
            "project": "DOFI",
            "affaire": "Données fictives",
            "notes": "Projet DOFI/SDV - Règle par défaut",
            "added_at": "2024-12-19T00:00:00",
            "usage_count": 0
        },
        "sdv": {
            "project": "DOFI",
            "affaire": "Données fictives",
            "notes": "Synthetic Data Vault - Règle par défaut",
            "added_at": "2024-12-19T00:00:00",
            "usage_count": 0
        },
        "synthetic data": {
            "project": "DOFI",
            "affaire": "Données fictives",
            "notes": "Synthetic Data - Règle par défaut",
            "added_at": "2024-12-19T00:00:00",
            "usage_count": 0
        },
        "reunion staff": {
            "project": "Epiconcept",
            "affaire": "Epiconcept",
            "notes": "Réunion staff - Règle par défaut",
            "added_at": "2024-12-19T00:00:00",
            "usage_count": 0
        },
        "réunion staff": {
            "project": "Epiconcept",
            "affaire": "Epiconcept",
            "notes": "Réunion staff - Règle par défaut",
            "added_at": "2024-12-19T00:00:00",
            "usage_count": 0
        },
        "staff meeting": {
            "project": "Epiconcept",
            "affaire": "Epiconcept",
            "notes": "Staff meeting - Règle par défaut",
            "added_at": "2024-12-19T00:00:00",
            "usage_count": 0
        },
        "staff": {
            "project": "Epiconcept",
            "affaire": "Epiconcept",
            "notes": "Staff - Règle par défaut",
            "added_at": "2024-12-19T00:00:00",
            "usage_count": 0
        },
        "admin": {
            "project": "TNA",
            "affaire": "Temps Non Attribué (TNA)",
            "notes": "Tâches administratives",
            "added_at": "2024-12-19T00:00:00",
            "usage_count": 0
        },
        "formation": {
            "project": "FORM",
            "affaire": "Formation Interne",
            "notes": "Formation",
            "added_at": "2024-12-19T00:00:00",
            "usage_count": 0
        },
        "déplacement": {
            "project": "DEPL",
            "affaire": "Temps de déplacement",
            "notes": "Déplacements professionnels",
            "added_at": "2024-12-19T00:00:00",
            "usage_count": 0
        },
        "trajet": {
            "project": "DEPL",
            "affaire": "Temps de déplacement",
            "notes": "Trajets - Règle par défaut",
            "added_at": "2024-12-19T00:00:00",
            "usage_count": 0
        },
        "temps non attribué (tna)": {
            "project": "TNA",
            "affaire": "Temps Non Attribué (TNA)",
            "notes": "TNA automatique",
            "added_at": "2024-12-19T00:00:00",
            "usage_count": 0
        },
        "tna": {
            "project": "TNA",
            "affaire": "Temps Non Attribué (TNA)",
            "notes": "TNA automatique",
            "added_at": "2024-12-19T00:00:00",
            "usage_count": 0
        }
    },
    "keywords": {
        "neha": ["Données fictives"],
        "sdv": ["Données fictives"],
        "synthetic": ["Données fictives"],
        "staff": ["Epiconcept"],
        "reunion": ["Epiconcept"],
        "réunion": ["Epiconcept"],
        "admin": ["Temps Non Attribué (TNA)"],
        "formation": ["Formation Interne"],
        "déplacement": ["Temps de déplacement"],
        "trajet": ["Temps de déplacement"],
        "dofi": ["Données fictives"],
        "données": ["Données fictives"],
        "fictives": ["Données fictives"],
        "tna": ["Temps Non Attribué (TNA)"]
    },
    "history": [],
    "last_updated": None
}

def load_mapping_memory():
    """Charge la mémoire des mappings, crée avec défauts si inexistant"""
    if MEMORY_FILE.exists():
        with open(MEMORY_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    else:
        print("[INFO] Creation du fichier de memoire avec regles par defaut...")
        memory = DEFAULT_MAPPINGS.copy()
        memory["history"].append({
            "action": "init",
            "message": "Initialisation avec règles par défaut",
            "timestamp": datetime.now().isoformat()
        })
        save_mapping_memory(memory)
        return memory

def save_mapping_memory(memory):
    """Sauvegarde la mémoire dans le fichier"""
    memory["last_updated"] = datetime.now().isoformat()
    with open(MEMORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(memory, f, indent=2, ensure_ascii=False)

def get_projects(xls_path):
    """Extrait les affaires du fichier HTML déguisé en XLS"""
    try:
        df_list = pd.read_html(xls_path)
        df = df_list[0]
        
        if "Affaire" not in df.columns:
            available_cols = ", ".join(df.columns.tolist())
            raise ValueError(f"Colonne 'Affaire' introuvable. Colonnes disponibles : {available_cols}")
        
        result = list(df["Affaire"][df["Affaire"].notna()])
        final_list = result + ["Epiconcept", "Formation Interne", "Temps Non Attribué (TNA)", "Temps de déplacement"] 
        
        return final_list
        
    except Exception as e:
        raise Exception(f"Erreur lors de la lecture du fichier : {str(e)}")

# ============================================================================
# RESOURCES
# ============================================================================

# RESOURCE : Expose la mémoire des mappings
@mcp.resource("fitnet://memory/mappings")
async def get_mapping_memory() -> str:
    """Mémoire des mappings d'événements vers projets Fitnet.
    
    Contient l'historique des corrections et patterns appris pour
    améliorer les mappings futurs automatiquement.
    """
    memory = load_mapping_memory()
    return json.dumps(memory, indent=2, ensure_ascii=False)

# RESOURCE : Format de sortie attendu pour le mapping - VERSION PAR JOUR
@mcp.resource("fitnet://schema/mapping-output")
async def get_mapping_output_schema() -> str:
    """Schéma JSON du format de sortie attendu pour le mapping d'événements.
    
    Ce format doit être utilisé pour tous les mappings d'événements vers affaires Fitnet.
    Structure organisée par jour.
    """
    schema = {
        "description": "Format de sortie pour le mapping d'événements calendrier vers affaires Fitnet (par jour)",
        "format": "JSON",
        "heures_format": "Décimal Fitnet (0.25=15min, 0.5=30min, 0.75=45min, 1.0=1h)",
        "structure_par_jour": {
            "date_key (YYYY-MM-DD)": {
                "date": "string - Date au format YYYY-MM-DD",
                "day_name": "string - Nom du jour (Monday, Tuesday, etc.)",
                "events": [
                    {
                        "event_name": "string - Nom de l'événement Google Calendar",
                        "affaire": "string - Nom exact de l'affaire Fitnet",
                        "hours": "number - Heures en format décimal (ex: 1.5, 2.25)",
                        "confidence": "string - high|medium|low|unknown",
                        "reasoning": "string - Explication du mapping"
                    }
                ],
                "total_day_hours": "number - Total d'heures pour la journée"
            }
        },
        "exemple_complet": {
            "2024-12-16": {
                "date": "2024-12-16",
                "day_name": "Monday",
                "events": [
                    {
                        "event_name": "Réunion staff",
                        "affaire": "Epiconcept",
                        "hours": 1.0,
                        "confidence": "high",
                        "reasoning": "Mapping exact depuis memoire"
                    },
                    {
                        "event_name": "Neha - Point projet",
                        "affaire": "Données fictives",
                        "hours": 2.5,
                        "confidence": "high",
                        "reasoning": "Mapping exact depuis memoire"
                    },
                    {
                        "event_name": "Temps Non Attribué (TNA)",
                        "affaire": "Temps Non Attribué (TNA)",
                        "hours": 4.5,
                        "confidence": "high",
                        "reasoning": "TNA automatique calcule"
                    }
                ],
                "total_day_hours": 8.0
            },
            "2024-12-17": {
                "date": "2024-12-17",
                "day_name": "Tuesday",
                "events": [
                    {
                        "event_name": "Formation Docker",
                        "affaire": "Formation Interne",
                        "hours": 3.0,
                        "confidence": "high",
                        "reasoning": "Mapping partiel via pattern 'formation'"
                    },
                    {
                        "event_name": "Dev feature X",
                        "affaire": "Données fictives",
                        "hours": 4.0,
                        "confidence": "medium",
                        "reasoning": "Mapping partiel via pattern 'sdv'"
                    },
                    {
                        "event_name": "Temps Non Attribué (TNA)",
                        "affaire": "Temps Non Attribué (TNA)",
                        "hours": 1.0,
                        "confidence": "high",
                        "reasoning": "TNA automatique calcule"
                    }
                ],
                "total_day_hours": 8.0
            }
        },
        "regles_mapping": [
            "Si incertain -> utiliser 'Temps Non Attribué (TNA)'",
            "Réunions staff -> 'Epiconcept'",
            "Neha/NEHA/SDV/Synthetic Data/Données fictives -> 'Données fictives'",
            "Formations/Ateliers -> 'Formation Interne'",
            "Déplacements/Trajets -> 'Temps de déplacement'",
            "Tâches admin -> 'Temps Non Attribué (TNA)'"
        ],
        "niveaux_confidence": {
            "high": "Mapping certain basé sur règle exacte",
            "medium": "Mapping probable basé sur pattern partiel",
            "low": "Mapping incertain, nécessite validation",
            "unknown": "Aucune règle trouvée, nécessite IA ou correction manuelle"
        }
    }
    
    return json.dumps(schema, indent=2, ensure_ascii=False)

# RESOURCE : Guide d'utilisation
@mcp.resource("fitnet://docs/guide")
async def get_fitnet_guide() -> str:
    """Guide complet d'utilisation du système de mapping Fitnet."""
    guide = """
GUIDE D'UTILISATION - SYSTEME DE MAPPING FITNET

[RESOURCES DISPONIBLES]
- fitnet://memory/mappings : Mémoire des règles de mapping
- fitnet://schema/mapping-output : Format JSON attendu pour les mappings
- fitnet://docs/guide : Ce guide

[TOOLS DISPONIBLES]
- simplify_calendar_fitnet : Point d'entrée principal
- map_calendar_to_projects : Mapping intelligent (mémoire + IA)
- add_mapping_rule : Ajouter une nouvelle règle
- correct_mapping : Corriger un mapping existant
- reset_mapping_memory : Réinitialiser avec règles par défaut
- validate_mapping_json : Valider un JSON de mapping

[WORKFLOW RECOMMANDE]
1. Appeler simplify_calendar_fitnet avec le fichier XLS
2. Récupérer le JSON de mapping (complet ou partiel)
3. Si événements inconnus : Claude analyse avec l'IA
4. Valider avec validate_mapping_json si besoin
5. Corriger avec correct_mapping ou add_mapping_rule

[FORMAT DES HEURES]
Format décimal Fitnet :
- 0.25 = 15 minutes
- 0.5 = 30 minutes
- 0.75 = 45 minutes
- 1.0 = 1 heure
- 1.5 = 1h30
- 7.5 = journée standard mercredi/vendredi
- 8.0 = journée standard lundi/mardi/jeudi

[REGLES PAR DEFAUT]
- Neha/SDV/Synthetic Data -> Données fictives
- Staff/Réunion staff -> Epiconcept
- Formation -> Formation Interne
- Déplacement/Trajet -> Temps de déplacement
- Admin/Tâches -> Temps Non Attribué (TNA)
"""
    return guide

# ============================================================================
# TOOLS
# ============================================================================

# TOOL : Ajouter une règle de mapping
@mcp.tool()
async def add_mapping_rule(
    event_pattern: str,
    affaire: str,
    notes: str = ""
) -> str:
    """Enregistre une règle de mapping pour les événements futurs.
    
    Args:
        event_pattern: Pattern de l'événement (ex: "réunion sprint", "dev feature X")
        affaire: Affaire Fitnet (ex: "Données fictives", "Epiconcept")
        notes: Notes additionnelles sur ce mapping
    
    Returns:
        Message de confirmation
    """
    memory = load_mapping_memory()
    
    pattern_key = event_pattern.lower().strip()
    
    memory["event_patterns"][pattern_key] = {
        "project": affaire.split()[0] if affaire else "TNA",
        "affaire": affaire,
        "notes": notes,
        "added_at": datetime.now().isoformat(),
        "usage_count": 0
    }
    
    # Extraire les mots-clés
    keywords = pattern_key.split()
    for kw in keywords:
        if len(kw) > 3:
            if kw not in memory["keywords"]:
                memory["keywords"][kw] = []
            if affaire not in memory["keywords"][kw]:
                memory["keywords"][kw].append(affaire)
    
    memory["history"].append({
        "action": "add_rule",
        "pattern": event_pattern,
        "affaire": affaire,
        "timestamp": datetime.now().isoformat()
    })
    
    save_mapping_memory(memory)
    
    return f"[OK] Regle ajoutee : '{event_pattern}' -> {affaire}"

# TOOL : Corriger un mapping
@mcp.tool()
async def correct_mapping(
    event_name: str,
    correct_affaire: str,
    reason: str = ""
) -> str:
    """Corrige un mapping incorrect et l'enregistre pour l'avenir.
    
    Args:
        event_name: Nom de l'événement mal mappé
        correct_affaire: Bonne affaire Fitnet
        reason: Raison de la correction
    
    Returns:
        Message de confirmation
    """
    memory = load_mapping_memory()
    
    pattern_key = event_name.lower().strip()
    
    memory["event_patterns"][pattern_key] = {
        "project": correct_affaire.split()[0] if correct_affaire else "TNA",
        "affaire": correct_affaire,
        "notes": f"Correction: {reason}" if reason else "Correction utilisateur",
        "corrected_at": datetime.now().isoformat(),
        "usage_count": 0
    }
    
    memory["history"].append({
        "action": "correction",
        "event": event_name,
        "affaire": correct_affaire,
        "reason": reason,
        "timestamp": datetime.now().isoformat()
    })
    
    save_mapping_memory(memory)
    
    return f"[OK] Correction enregistree : '{event_name}' -> {correct_affaire}"

# TOOL : Réinitialiser la mémoire
@mcp.tool()
async def reset_mapping_memory() -> str:
    """Réinitialise la mémoire avec les règles par défaut.
    
    ATTENTION : Cela supprime toutes les règles personnalisées.
    """
    memory = DEFAULT_MAPPINGS.copy()
    memory["history"] = [{
        "action": "reset",
        "message": "Réinitialisation complète",
        "timestamp": datetime.now().isoformat()
    }]
    save_mapping_memory(memory)
    
    return f"""[OK] Memoire reinitialisee avec {len(DEFAULT_MAPPINGS['event_patterns'])} regles par defaut :

{chr(10).join(f"  - {pattern} -> {data['affaire']}" 
              for pattern, data in DEFAULT_MAPPINGS['event_patterns'].items())}
"""

# TOOL : Mapping HYBRIDE (Mémoire + IA) - VERSION PAR JOUR
@mcp.tool()
async def map_calendar_to_projects(
    input_calendar: dict,  # Structure: {day_key: {day_name, events, total_day_hours, TNA}}
    input_project_list: list
) -> str:
    """Mappe intelligemment les événements avec MEMOIRE + IA Claude.
    
    Les heures sont au format décimal Fitnet (0.25=15min, 0.5=30min, etc.)
    
    Stratégie hybride:
    1. Utilise d'abord la mémoire des règles connues (rapide, fiable)
    2. Pour les événements inconnus, génère un prompt pour l'IA
    3. Apprend des corrections utilisateur
    
    Args:
        input_calendar: Dict de la structure week_data avec jours et événements
        input_project_list: Liste des affaires Fitnet disponibles
    
    Returns:
        Mapping détaillé par jour avec suggestions IA pour les cas inconnus
    """
    memory = load_mapping_memory()
    
    # Structure finale par jour
    daily_mappings = {}
    all_unknown_events = {}
    total_week_hours = 0.0
    
    # Traiter chaque jour
    for day_key, day_info in sorted(input_calendar.items()):
        day_name = day_info.get("day_name", day_key)
        total_day = day_info.get("total_day_hours", 0)
        total_week_hours += total_day
        
        daily_mappings[day_key] = {
            "date": day_key,
            "day_name": day_name,
            "events": [],
            "total_day_hours": total_day
        }
        
        # Mapper les événements du jour
        if "events" in day_info:
            for event_name, hours in day_info["events"].items():
                hours_decimal = float(hours)
                event_lower = event_name.lower().strip()
                
                # Recherche exacte
                if event_lower in memory["event_patterns"]:
                    mapping = memory["event_patterns"][event_lower]
                    mapping["usage_count"] = mapping.get("usage_count", 0) + 1
                    daily_mappings[day_key]["events"].append({
                        "event_name": event_name,
                        "affaire": mapping["affaire"],
                        "hours": hours_decimal,
                        "confidence": "high",
                        "reasoning": f"Mapping exact depuis memoire"
                    })
                    continue
                
                # Recherche partielle
                found = False
                for pattern, mapping in memory["event_patterns"].items():
                    if pattern in event_lower or event_lower in pattern:
                        mapping["usage_count"] = mapping.get("usage_count", 0) + 1
                        daily_mappings[day_key]["events"].append({
                            "event_name": event_name,
                            "affaire": mapping["affaire"],
                            "hours": hours_decimal,
                            "confidence": "medium",
                            "reasoning": f"Mapping partiel via pattern '{pattern}'"
                        })
                        found = True
                        break
                
                if not found:
                    # Événement inconnu
                    daily_mappings[day_key]["events"].append({
                        "event_name": event_name,
                        "affaire": "INCONNU",
                        "hours": hours_decimal,
                        "confidence": "unknown",
                        "reasoning": "Aucune regle trouvee"
                    })
                    all_unknown_events[f"{day_key}:{event_name}"] = hours_decimal
        
        # Ajouter le TNA si présent
        if "TNA" in day_info and day_info["TNA"]:
            tna_value = day_info["TNA"]
            
            if isinstance(tna_value, str) and "/" in tna_value:
                try:
                    tna_hours = float(tna_value.split("/")[0])
                    
                    if tna_hours > 0:
                        daily_mappings[day_key]["events"].append({
                            "event_name": "Temps Non Attribué (TNA)",
                            "affaire": "Temps Non Attribué (TNA)",
                            "hours": tna_hours,
                            "confidence": "high",
                            "reasoning": "TNA automatique calcule"
                        })
                except (ValueError, IndexError) as e:
                    print(f"[WARNING] Impossible de parser TNA : {tna_value} - {e}")
    
    save_mapping_memory(memory)
    
    # Compter les stats
    total_known = sum(
        len([e for e in day["events"] if e["confidence"] in ["high", "medium"]])
        for day in daily_mappings.values()
    )
    total_unknown = len(all_unknown_events)
    total_events = total_known + total_unknown
    
    # Phase 2 : Prompt IA pour événements inconnus
    if all_unknown_events:
        known_patterns = "\n".join([
            f"  - '{pattern}' -> {data['affaire']}"
            for pattern, data in list(memory["event_patterns"].items())[:15]
        ])
        
        # Extraire juste les noms d'événements sans le préfixe jour
        unknown_events_simple = {
            k.split(":", 1)[1]: v for k, v in all_unknown_events.items()
        }
        
        ai_prompt = f"""Tu es un assistant qui mappe des événements de calendrier vers des affaires Fitnet.

[RESOURCE DISPONIBLE]
Consulte la resource 'fitnet://schema/mapping-output' pour le format de sortie exact attendu.

[AFFAIRES FITNET DISPONIBLES]
{json.dumps(input_project_list, indent=2, ensure_ascii=False)}

[REGLES DEJA APPRISES]
{known_patterns}

[EVENEMENTS A MAPPER] (format: 0.25=15min, 0.5=30min, 0.75=45min, 1.0=1h)
{json.dumps(unknown_events_simple, indent=2, ensure_ascii=False)}

[REGLES IMPORTANTES]
1. Si tu ne sais pas -> utilise "Temps Non Attribué (TNA)"
2. Réunions staff -> "Epiconcept"
3. Tout ce qui concerne Neha/NEHA/SDV/Données fictives/Synthetic Data -> "Données fictives"
4. Formations -> "Formation Interne"
5. Déplacements/Trajets -> "Temps de déplacement"
6. Tâches administratives -> "Temps Non Attribué (TNA)"

[FORMAT DE SORTIE REQUIS]
Réponds UNIQUEMENT avec un JSON valide (sans markdown, sans préambule, sans ```json) :
{{
  "event_name_exact": {{
    "affaire": "affaire_fitnet_exacte",
    "hours": nombre_decimal,
    "confidence": "high|medium|low",
    "reasoning": "courte explication"
  }}
}}
"""
        
        result = f"""[MAPPING PARTIEL] {total_known}/{total_events} evenements mappes (Total semaine: {total_week_hours:.2f}h)

[JSON MAPPING PAR JOUR]
{json.dumps(daily_mappings, indent=2, ensure_ascii=False)}

[EVENEMENTS INCONNUS] {total_unknown} evenements a mapper par IA
{json.dumps(all_unknown_events, indent=2, ensure_ascii=False)}

[PROMPT POUR L'IA]
{'='*60}
{ai_prompt}
{'='*60}

[INSTRUCTIONS]
Claude va automatiquement consulter la resource 'fitnet://schema/mapping-output'
pour connaitre le format exact attendu et repondre avec le JSON correct.
"""
    else:
        # Tout est mappé
        # Calculer résumé par affaire
        affaire_summary = {}
        for day_data in daily_mappings.values():
            for event in day_data["events"]:
                affaire = event["affaire"]
                if affaire not in affaire_summary:
                    affaire_summary[affaire] = 0.0
                affaire_summary[affaire] += event["hours"]
        
        result = f"""[MAPPING COMPLET] {total_events} evenements mappes (Total semaine: {total_week_hours:.2f}h)

[JSON MAPPING PAR JOUR]
{json.dumps(daily_mappings, indent=2, ensure_ascii=False)}

[RESUME PAR AFFAIRE]
{json.dumps(affaire_summary, indent=2, ensure_ascii=False)}

[OK] Tous les evenements ont ete mappes automatiquement grace a la memoire !
"""
    
    return result

# TOOL : Fonction principale - VERSION SIMPLIFIEE
@mcp.tool()
async def simplify_calendar_fitnet(
    input_path: str,
) -> str:
    """Récupère et mappe les heures de la semaine avec mémoire + IA.
    
    Va chercher les actions, réunions et événements de la semaine dernière,
    calcule les heures au format décimal Fitnet (0.25, 0.5, 0.75, etc.),
    et les mappe intelligemment aux affaires grâce à la mémoire.

    Args:
        input_path: Chemin vers le fichier XLS téléchargé de Fitnet

    Returns:
        Mapping par jour (mémoire + suggestions IA si besoin) avec résumé par affaire
    """
    if not os.path.exists(input_path):
        return f"[ERREUR] Le fichier '{input_path}' n'existe pas"
    
    try:
        # retrieve_data() retourne la structure par jour directement
        week_data = retrieve_data()
        
        if not week_data:
            return "[INFO] Aucun evenement trouve dans le calendrier cette semaine."
        
        # Récupérer les projets Fitnet
        list_of_projects = get_projects(input_path)
        
        # Mapper les événements (week_data est passé tel quel)
        mapping_result = await map_calendar_to_projects(
            week_data,
            list_of_projects
        )
        
        return f"""[OK] Recuperation des heures de la semaine derniere reussie

{mapping_result}
"""
        
    except Exception as e:
        import traceback
        return f"""[ERREUR] Erreur lors de la recuperation

Erreur: {str(e)}

Traceback:
{traceback.format_exc()}
"""

def main():
    """Point d'entrée du serveur MCP"""
    mcp.run(transport='stdio')

if __name__ == "__main__":
    main()