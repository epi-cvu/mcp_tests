"""
Serveur MCP pour la conversion de fichiers vers le format SDV metadata.json
"""
import asyncio
import json
import os
from pathlib import Path
from typing import Any

from mcp.server import Server
from mcp.types import Tool, TextContent, ImageContent, EmbeddedResource

from modules.voozanoo import import_csv_folder, import_json_file

app = Server("sdv-converter")


@app.list_tools()
async def list_tools() -> list[Tool]:
    """Liste tous les outils disponibles pour la conversion SDV"""
    return [
        Tool(
            name="convert_to_sdv",
            description=(
                "Convertit des fichiers sources vers le format SDV (Synthetic Data Vault) metadata.json. "
                "Supporte plusieurs formats d'entrée : Voozanoo4 (JSON), Voozanoo3 (dossiers), XML, SQL, ou CSV."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "input_path": {
                        "type": "string",
                        "description": "Chemin vers le fichier ou dossier source à convertir"
                    },
                    "input_type": {
                        "type": "string",
                        "enum": ["voozanoo4", "voozanoo3", "xml", "sql", "csv"],
                        "description": "Type de source : voozanoo4 (JSON), voozanoo3 (dossiers), xml, sql, ou csv"
                    },
                    "output_path": {
                        "type": "string",
                        "description": "Chemin où sauvegarder le fichier metadata.json généré (optionnel, par défaut : même dossier que l'entrée)"
                    }
                },
                "required": ["input_path", "input_type"]
            }
        ),
        Tool(
            name="validate_sdv_metadata",
            description=(
                "Valide un fichier metadata.json SDV existant pour vérifier sa conformité au format."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "metadata_path": {
                        "type": "string",
                        "description": "Chemin vers le fichier metadata.json à valider"
                    }
                },
                "required": ["metadata_path"]
            }
        ),
        Tool(
            name="detect_input_type",
            description=(
                "Détecte automatiquement le type de fichier/dossier source "
                "(Voozanoo3, Voozanoo4, XML, SQL, CSV) pour faciliter la conversion."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "input_path": {
                        "type": "string",
                        "description": "Chemin vers le fichier ou dossier à analyser"
                    }
                },
                "required": ["input_path"]
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Gère les appels aux différents outils"""
    
    try:
        if name == "convert_to_sdv":
            return await convert_to_sdv(arguments)
        
        elif name == "validate_sdv_metadata":
            return await validate_sdv_metadata(arguments)
        
        elif name == "detect_input_type":
            return await detect_input_type(arguments)
        
        else:
            raise ValueError(f"Outil inconnu: {name}")
    
    except Exception as e:
        return [TextContent(
            type="text",
            text=f"❌ Erreur lors de l'exécution de {name}: {str(e)}"
        )]


async def convert_to_sdv(arguments: dict) -> list[TextContent]:
    """Convertit un fichier source vers le format SDV"""
    input_path = arguments["input_path"]
    input_type = arguments["input_type"]
    output_path = arguments.get("output_path")
    
    # Vérifier que le fichier/dossier existe
    if not os.path.exists(input_path):
        return [TextContent(
            type="text",
            text=f"❌ Le chemin '{input_path}' n'existe pas."
        )]
    
    # Définir le chemin de sortie par défaut
    if not output_path:
        if os.path.isdir(input_path):
            output_path = os.path.join(input_path, "metadata.json")
        else:
            output_path = os.path.join(
                os.path.dirname(input_path),
                "metadata.json"
            )
    
    try:
        
        # Appeler votre module de conversion approprié
        if input_type == "voozanoo4":
            # from votre_package import convertir_voozanoo4
            # metadata = convertir_voozanoo4(input_path)
            metadata, dico = import_json_file(input_path)
        
        elif input_type == "voozanoo3":
            # from votre_package import convertir_voozanoo3
            # metadata = convertir_voozanoo3(input_path)
            metadata, dico = import_csv_folder(input_path)
        
        # elif input_type == "xml":
        #     # from votre_package import convertir_xml
        #     # metadata = convertir_xml(input_path)
        #     metadata = {"example": "Remplacez par votre fonction"}
        
        # elif input_type == "sql":
        #     # from votre_package import convertir_sql
        #     # metadata = convertir_sql(input_path)
        #     metadata = {"example": "Remplacez par votre fonction"}
        
        # elif input_type == "csv":
        #     # from votre_package import convertir_csv
        #     # metadata = convertir_csv(input_path)
        #     metadata = {"example": "Remplacez par votre fonction"}
        
        # Sauvegarder le metadata.json
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        
        return [TextContent(
            type="text",
            text=(
                f"✅ Conversion réussie !\n\n"
                f"📁 Source : {input_path}\n"
                f"📄 Type : {input_type}\n"
                f"💾 Sortie : {output_path}\n\n"
                f"Le fichier metadata.json a été généré avec succès."
            )
        )]
    
    except Exception as e:
        return [TextContent(
            type="text",
            text=f"❌ Erreur lors de la conversion : {str(e)}"
        )]


async def validate_sdv_metadata(arguments: dict) -> list[TextContent]:
    """Valide un fichier metadata.json SDV"""
    metadata_path = arguments["metadata_path"]
    
    if not os.path.exists(metadata_path):
        return [TextContent(
            type="text",
            text=f"❌ Le fichier '{metadata_path}' n'existe pas."
        )]
    
    try:
        with open(metadata_path, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
        
        # Validations basiques du format SDV
        errors = []
        warnings = []
        
        # Vérifier les champs obligatoires
        if "tables" not in metadata:
            errors.append("❌ Champ 'tables' manquant")
        
        # Vérifier la structure des tables
        if "tables" in metadata:
            for table_name, table_info in metadata["tables"].items():
                if "columns" not in table_info:
                    errors.append(f"❌ Table '{table_name}': champ 'columns' manquant")
                
                if "primary_key" not in table_info:
                    warnings.append(f"⚠️ Table '{table_name}': pas de clé primaire définie")
        
        # Générer le rapport
        if errors:
            result = f"❌ Validation échouée :\n\n" + "\n".join(errors)
            if warnings:
                result += f"\n\n⚠️ Avertissements :\n" + "\n".join(warnings)
        elif warnings:
            result = f"✅ Validation réussie avec avertissements :\n\n" + "\n".join(warnings)
        else:
            result = "✅ Le fichier metadata.json est valide !"
        
        return [TextContent(type="text", text=result)]
    
    except json.JSONDecodeError as e:
        return [TextContent(
            type="text",
            text=f"❌ Erreur de parsing JSON : {str(e)}"
        )]
    except Exception as e:
        return [TextContent(
            type="text",
            text=f"❌ Erreur lors de la validation : {str(e)}"
        )]


async def detect_input_type(arguments: dict) -> list[TextContent]:
    """Détecte automatiquement le type de fichier source"""
    input_path = arguments["input_path"]
    
    if not os.path.exists(input_path):
        return [TextContent(
            type="text",
            text=f"❌ Le chemin '{input_path}' n'existe pas."
        )]
    
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
    
    return [TextContent(type="text", text=result)]


async def main():
    """Point d'entrée du serveur MCP"""
    from mcp.server.stdio import stdio_server
    
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())