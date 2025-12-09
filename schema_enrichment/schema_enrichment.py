"""
Serveur MCP pour l'ajout des commentaires des metadata en fonction du contexte
"""
from mcp.server.fastmcp import FastMCP
import os 
import json

mcp = FastMCP("schema-enrichment")


@mcp.tool()
async def add_column_description(
    input_path: str,
    context: str,
    output_path: str = None,
    language: str = "fr"
) -> str:
    """
    Utilise l'IA pour ajouter des commentaires aux metadata.
    
    Args:
        input_path: Chemin vers le fichier metadata.json
        context: Le contexte de la base de données
        output_path: Chemin vers où sauvegarder le nouveau fichier annoté (optionnel)
        language: La langue dans laquelle la description doit être (fr ou en)
    
    Returns:
        Message décrivant l'analyse et le prompt pour générer les descriptions
    """
    if not os.path.exists(input_path):
        return f"❌ Le chemin '{input_path}' n'existe pas."
    
    # Définir le chemin de sortie par défaut
    if not output_path:
        if os.path.isdir(input_path):
            output_path = os.path.join(input_path, "commented_metadata.json")
        else:
            output_path = os.path.join(os.path.dirname(input_path), "commented_metadata.json")
    
    try:
        # Lire le metadata.json
        with open(input_path, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
        
        # Extraire la structure des colonnes
        tables_info = []
        for table_name, table_data in metadata.get("tables", {}).items():
            columns = table_data.get("columns", {})
            
            table_info = {
                "table_name": table_name,
                "columns": []
            }
            
            for col_name, col_data in columns.items():
                table_info["columns"].append({
                    "name": col_name,
                    "sdtype": col_data.get("sdtype", "unknown"),
                    "current_description": col_data.get("description", "")
                })
            tables_info.append(table_info)
        
        # Créer un résumé de la structure
        structure_summary = "Structure de la base de données :\n\n"
        for table in tables_info:
            structure_summary += f"📊 Table: {table['table_name']}\n"
            for col in table["columns"]:
                current_desc = col["current_description"] or "(pas de description)"
                structure_summary += f"  - {col['name']} ({col['sdtype']}) : {current_desc}\n"
            structure_summary += "\n"
        
        # Créer le prompt pour Claude
        prompt = (
            f"Je dois enrichir ce fichier metadata.json SDV avec des descriptions.\n\n"
            f"**Contexte métier** : {context}\n\n"
            f"{structure_summary}\n"
            f"**Langue des descriptions** : {language}\n\n"
            f"Pour chaque colonne, propose une description détaillée et pertinente basée sur :\n"
            f"1. Le nom de la colonne\n"
            f"2. Le type de données\n"
            f"3. Le contexte métier fourni\n\n"
            f"Retourne un JSON avec cette structure :\n"
            f'{{\n'
            f'  "table_name": {{\n'
            f'    "column_name": "description ici"\n'
            f'  }}\n'
            f'}}\n\n'
            f"Génère maintenant les descriptions, puis utilise l'outil 'save_commentary' pour les sauvegarder."
        )
        
        # Retourner le résultat
        return (
            f"📝 Analyse de la structure pour génération des descriptions\n\n"
            f"📁 Fichier : {input_path}\n"
            f"💾 Sortie prévue : {output_path}\n"
            f"🎯 Contexte : {context}\n"
            f"🌍 Langue : {language}\n\n"
            f"J'ai identifié {len(tables_info)} table(s) avec "
            f"{sum(len(t['columns']) for t in tables_info)} colonne(s) au total.\n\n"
            f"{prompt}"
        )
    
    except json.JSONDecodeError as e:
        return f"❌ Erreur de parsing JSON : {str(e)}"
    except Exception as e:
        return f"❌ Erreur lors de l'analyse : {str(e)}"


@mcp.tool()
async def save_commentary(
    metadata_path: str,
    descriptions: dict,
    backup: bool = True
) -> str:
    """
    Sauvegarde les descriptions générées dans le metadata.json.
    
    Args:
        metadata_path: Chemin vers le fichier metadata.json à mettre à jour
        descriptions: Dictionnaire hiérarchique {table_name: {column_name: description}}
        backup: Créer une sauvegarde avant modification (par défaut: True)
    
    Returns:
        Message de confirmation avec statistiques
    """
    if not os.path.exists(metadata_path):
        return f"❌ Le fichier '{metadata_path}' n'existe pas."
    
    try:
        # Créer une sauvegarde
        if backup:
            backup_path = metadata_path.replace(".json", "_backup.json")
            import shutil
            shutil.copy2(metadata_path, backup_path)
        
        # Lire le metadata actuel
        with open(metadata_path, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
        
        # Mettre à jour les descriptions
        updated_count = 0
        skipped = []
        
        for table_name, columns_desc in descriptions.items():
            if table_name not in metadata.get("tables", {}):
                skipped.append(f"Table '{table_name}' introuvable")
                continue
                
            for col_name, description in columns_desc.items():
                if col_name in metadata["tables"][table_name].get("columns", {}):
                    metadata["tables"][table_name]["columns"][col_name]["description"] = description
                    updated_count += 1
                else:
                    skipped.append(f"Colonne '{table_name}.{col_name}' introuvable")
        
        # Sauvegarder le fichier mis à jour
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        
        result = (
            f"✅ Descriptions sauvegardées avec succès !\n\n"
            f"📁 Fichier : {metadata_path}\n"
            f"📝 Colonnes mises à jour : {updated_count}\n"
        )
        
        if backup:
            result += f"💾 Backup créé : {backup_path}\n"
        
        if skipped:
            result += f"\n⚠️ Éléments ignorés :\n" + "\n".join(f"  - {s}" for s in skipped)
        
        return result
    
    except Exception as e:
        return f"❌ Erreur lors de la sauvegarde : {str(e)}"


@mcp.tool()
async def validate_commentary(
    metadata_path: str,
    show_empty_only: bool = False
) -> str:
    """
    Affiche les commentaires du metadata.json pour validation humaine.
    
    Args:
        metadata_path: Chemin vers le fichier metadata.json à valider
        show_empty_only: Afficher uniquement les colonnes sans description (par défaut: False)
    
    Returns:
        Liste formatée des descriptions pour validation
    """
    if not os.path.exists(metadata_path):
        return f"❌ Le fichier '{metadata_path}' n'existe pas."
    
    try:
        with open(metadata_path, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
        
        result = "📋 Validation des descriptions\n\n"
        
        for table_name, table_data in metadata.get("tables", {}).items():
            columns = table_data.get("columns", {})
            
            # Filtrer les colonnes si nécessaire
            if show_empty_only:
                columns = {k: v for k, v in columns.items() if not v.get("description")}
            
            if not columns:
                continue
            
            result += f"📊 Table: {table_name}\n"
            result += f"{'─' * 60}\n"
            
            for col_name, col_data in columns.items():
                desc = col_data.get("description", "(pas de description)")
                sdtype = col_data.get("sdtype", "unknown")
                
                result += f"  • {col_name} ({sdtype})\n"
                result += f"    └─ {desc}\n\n"
            
            result += "\n"
        
        return result
    
    except Exception as e:
        return f"❌ Erreur lors de la validation : {str(e)}"


def main():
    """Point d'entrée du serveur MCP"""
    mcp.run(transport='stdio')

    
if __name__ == "__main__":
    main()