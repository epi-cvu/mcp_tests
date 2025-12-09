from mcp.server.fastmcp import FastMCP
import os
import json

from modules.voozanoo import import_csv_folder, import_json_file
from modules.metadata import xml_to_metadata, sql_to_metadata, csv_to_metadata

mcp = FastMCP("sdv-converter")

@mcp.tool()
async def convert_to_sdv(
    input_path: str,
    input_type: str,
    output_path: str = None
) -> str:
    """Convertit des fichiers sources vers le format SDV (Synthetic Data Vault) 
    metadata.json
    Support plusieurs formats d'entrée : Voozanoo4 (JSON), Voozanoo3 (dossiers),
    XML, SQL ou CSV.

    Args:
        input_path (str): Chemin vers le fichier ou dossier source à convertir
        input_type (str): Type de source : voozanoo4 (JSON), voozanoo3 (dossiers),
        xml, sql ou csv
        output_path (str, optional): Chemin où sauvegarder le fichier metadata.json 
        généré optionnel. Defaults to None.

    Returns:
        str: Message qui indique que le fichier à été généré
    """
    if not os.path.exists(input_path):
        return f"❌ Le chemin '{input_path}' n'existe pas."
    
    if not output_path:
        if os.path.isdir(input_path):
            output_path = os.path.join(input_path, "metadata.json")
        else:
            output_path = os.path.join(os.path.dirname(input_path), "metadata.json")
        
    try:
        if input_type == "voozanoo4":
            metadata, dico = import_json_file(input_path)
        
        elif input_type == "voozanoo3":
            metadata, dico = import_csv_folder(input_path)
        
        elif input_type == "xml":
            metadata = xml_to_metadata(input_path)
        
        elif input_type == "sql":
            metadata = sql_to_metadata(input_path)
        
        elif input_type == "csv":
            metadata = csv_to_metadata(input_path)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        
        return  f"✅ Conversion réussie !\n\n\
            📁 Source : {input_path}\n\
            📄 Type : {input_type}\n\
            💾 Sortie : {output_path}\n\n\
            Le fichier metadata.json a été généré avec succès."
    
    except Exception as e:
        return f"❌ Erreur lors de la conversion : {str(e)}"
    
@mcp.tool()
async def detect_input_type(
    input_path: str
    ) -> str:
    """Détecte automatiquement le typ de fichier/dossier source

    Args:
        input_path (str): Chemin vers le fichier ou dossier à analyser

    Returns:
        str: Message qui indique le type de fichier.
    """
    if not os.path.exists(input_path):
        return f"❌ Le chemin '{input_path}' n'existe pas."
    
    detected_type = None
    confidence = "faible"
    details = []
    
    # Logique de détection (à adapter selon vos besoins)
    if os.path.isfile(input_path):
        ext = os.path.splitext(input_path)[1].lower()
        
        if ext == ".json":
            # Vérifier si c'est du Voozanoo4
            try:
                with open(input_path, 'r') as f:
                    data = json.load(f)
                    # Adaptez cette logique selon votre structure Voozanoo4
                    if "voozanoo_version" in data or "structure" in data:
                        detected_type = "voozanoo4"
                        confidence = "élevée"
                        details.append("Structure JSON Voozanoo4 détectée")
                    else:
                        detected_type = "voozanoo4"
                        confidence = "moyenne"
                        details.append("Fichier JSON, probablement Voozanoo4")
            except:
                pass
        
        elif ext == ".xml":
            detected_type = "xml"
            confidence = "élevée"
            details.append("Fichier XML détecté")
        
        elif ext == ".sql":
            detected_type = "sql"
            confidence = "élevée"
            details.append("Fichier SQL détecté")
    
    elif os.path.isdir(input_path):
        # Vérifier si c'est du Voozanoo3 ou un dossier CSV
        files = os.listdir(input_path)
        
        has_csv = any(f.endswith('.csv') for f in files)
        has_subdirs = any(os.path.isdir(os.path.join(input_path, f)) for f in files)
        
        if has_csv and not has_subdirs:
            detected_type = "csv"
            confidence = "élevée"
            details.append(f"Dossier contenant {sum(1 for f in files if f.endswith('.csv'))} fichiers CSV")
        
        elif has_subdirs:
            detected_type = "voozanoo3"
            confidence = "moyenne"
            details.append("Structure de dossiers, probablement Voozanoo3")
    
    if detected_type:
        result = (
            f"🔍 Détection automatique\n\n"
            f"📁 Chemin : {input_path}\n"
            f"📊 Type détecté : {detected_type}\n"
            f"🎯 Confiance : {confidence}\n\n"
            f"Détails :\n" + "\n".join(f"  • {d}" for d in details)
        )
    else:
        result = (
            f"❓ Type non détecté pour '{input_path}'.\n\n"
            f"Veuillez spécifier manuellement le type parmi : "
            f"voozanoo4, voozanoo3, xml, sql, csv"
        )
    
    return result

def main():
    """Point d'entrée du serveur MCP"""
    mcp.run(transport='stdio')

    
if __name__ == "__main__":
    main()