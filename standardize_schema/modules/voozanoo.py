import os
import glob
import json
import pandas as pd
import unicodedata
import re

conversion_map = {
    'textfield': 'id',
    'text': 'id',
    'integer': ('numerical', 'Int64'),
    'decimal': ('numerical', 'Float'),
    'date': {'sdtype': 'datetime', 'datetime_format': '%Y-%m-%d'},
    'single': 'categorical',
    'radio': 'categorical',
    'text_multiline': 'id',
    'list': 'id',
    'checkbox': 'categorical',
    'textmultiline': 'id',
    'multiples': 'categorical',
    'multiple' : 'categorical',
    'time': {'sdtype': 'datetime', 'datetime_format': '%H:%M:%S'},
    'choice': 'categorical',
    'calculated': 'categorical',
    None: 'categorical'
}

conversion_schema = {
            'textfield': 'str',
            'text': 'str',
            'integer': 'Int64',
            'decimal': 'Float',
            'date': 'object',
            'single': 'str',
            'radio': 'str',
            'text_multiline': 'str',
            'list': 'str',
            'checkbox': 'object',
            'textmultiline': 'str',
            'multiples': 'str',
            'multiple' : 'str',
            'time': 'object',
            'choice': 'str',
            'calculated': 'str',
            None: 'str'
        }

def import_csv_folder(folder_path, method=None):
    """Looks for the right folders to go fetch all the informations of a Voo3 project

    Args:
        folder_path (str): Folder path

    Returns:
        metadata (dict): The metadata in dictionnary format
        dicos (list): List of dictionnaries values
    """
    if folder_path:
        structure_folder_path = os.path.join(folder_path, '1_structure')
        link_folder_path = os.path.join(folder_path, '2_link/link.csv')
        dico_folder_path = os.path.join(folder_path, '4_dico/dico.csv')
        if os.path.exists(structure_folder_path) and \
        os.path.isdir(structure_folder_path):
            all_files = glob.glob(os.path.join(structure_folder_path, '*.csv'))
            fichier = pd.read_csv(link_folder_path, sep=';')
            dicos = pd.read_csv(dico_folder_path, sep = ';')
            return convert_to_metadata(all_files, fichier, dicos, method)
        else:
            print("'1_structure' folder not found in the selected folder.")


def import_json_file(json_file_path, calc="false", method=None):
    """Reads the JSON file of a Voo 4 project

    Args:
        json_file_path (str): The path to JSON file
        calc (bool): Whether or not we include calculated data
        method (str): By default "" will give the metadata and the dictionnaries
        but adding the "schema" will get the schema ready for Data Migration

    Returns:
        metadata (dict): Either the Metadata or with "schema" the Schema for Data Migration
        dictionnary (list): The list of all dictionnaries of the project
    """
    if json_file_path:
        json_code = read_json_file(json_file_path)
        return convert_json_to_metadata(json_code, calc, method)


def read_json_file(json_file_path):
    """Reads the JSON File

    Args:
        json_file_path (str): Path to JSON file

    Returns:
        json_file (dict): The read JSON file dict format
    """
    if json_file_path.split(".")[-1] == "json":
        json_file_path_js = json_file_path 
    else:
        json_file_path_js = json_file_path + ".json" # On autorise l'oubli de l'ajout de l'extension
    with open(json_file_path_js, 'r', encoding='utf-8') as json_file:
        return json.load(json_file)


def convert_to_metadata(all_files, link, dico, method=None):
    """Converts all the CSVs to SDV Metadata

    Args:
        all_files (list): A list of all tables
        link (list): A list of relationships
        dico (dict): A dictionnary

    Returns:
        metadata (dict) : Metadata in dict format 
        dictionnaries (list) : List of dictionnaries
    """
    metadata_json = {
        "METADATA_SPEC_VERSION": "MULTI_TABLE_V1",
        "tables": {},
        "relationships": [],
    }
    
    listo = []

    for filename in all_files:

        df = pd.read_csv(filename, sep=";")
        table_name = df.loc[df["type"] == "P", "varset"].to_string(index=False)
        specs = df.loc[df["type"] == "V"]
        table_specs = {
            "primary_key": "",
            "columns": {},
            "column_relationships": [],
        }

        for line in specs.iterrows():
            big_dico = {'table_name':"",
            'col': "",
            'type': "",
            'values':[]}
            column_id = line[1]["field_name"]
            sdtype = line[1]["field_type"]

            if sdtype == 'radio':
                big_dico['table_name'] = table_name
                
                big_dico['col'] = column_id
                type = line[1]['dico']
                big_dico['type'] = type
                values = dico[dico['dico_name'] == type]
                for value in values.iterrows():
                    big_dico['values'].append(value[1]['code'])
                listo.append(big_dico)
            if method == "schema":
                sdtype = conversion_schema.get(sdtype, sdtype)
            else:
                sdtype = conversion_map.get(sdtype, sdtype)
            if isinstance(sdtype, tuple):
                table_specs["columns"][column_id] \
                = {"sdtype": sdtype[0], "computer_representation": sdtype[1]}
            elif isinstance(sdtype, dict): 
                table_specs["columns"][column_id] = sdtype
            else:
                table_specs["columns"][column_id] = {"sdtype": sdtype}

        metadata_json["tables"][table_name] = table_specs
    for index, all in link.iterrows():
        parent = all['varset_1']
        child = all['varset_2']
        nom_id = parent + '.id_data'
        relation = {
            'parent_table_name': parent,
            'child_table_name': child,
            'parent_primary_key': 'id_data',
            'child_foreign_key': nom_id
        }
        if method == "schema":
            sd = {"sdtype": "object"}
        else:
            sd = {"sdtype": "id"}
        metadata_json['tables'][parent]['columns']['id_data'] \
        = sd
        metadata_json['tables'][child]['columns']['id_data'] = sd
        metadata_json['tables'][child]['columns'][nom_id] = sd
        metadata_json['tables'][parent]['primary_key'] = 'id_data'
        metadata_json['tables'][child]['primary_key'] = 'id_data'
        # metadata_json['tables'][child]['foreign_key'] = nom_id
        metadata_json['relationships'].append(relation)
        
    if method == "schema":
        temp_schema = {}
        for tab in metadata_json["tables"]:
            temp_schema[tab] = metadata_json["tables"][tab]["columns"]
        return temp_schema 
    else:
        return metadata_json, listo


def convert_json_to_metadata(root, calc="false", method=None):
    """Takes in the JSON file and converts it to the metadata using imbeded 
    functions

    Args:
        root (dict): The raw JSON imported file
        calc (bool): The setting to take account the calculted values
    """


    def convert_to_metadata_json(liste, liens, dicos, rep):
        """Convert the JSON file to the right SDV Metadata format

        Args:
            liste (list): Tables descriptions
            liens (list): Tables relationships
            dicos (dict): A list that contains all the datasets dictionnary
            rep (bool): The setting to take account the calculted values

        Returns:
            Metadata (dict) : Metadata in dict format
            Dicos (list) : List of dictionnaries containing the values of categorical values
        """
        metadata_json = {
            "METADATA_SPEC_VERSION": "MULTI_TABLE_V1",
            "tables":{},
            "relationships": []
        }

        listo = []
        linked_tables = []

        for m in range(len(liens)):
            parent = liens[m][0]['name']
            child = liens[m][1]['name']
            linked_tables.append(parent)
            linked_tables.append(child)

        for i in range(len(liste)):
            if liste[i]['nom'] in list(set(linked_tables)) or len(liste) == 1:
                table_names = liste[i]['nom']
                tables_specs =  {
                    "primary_key": "",
                    "columns": {},
                    "column_relationships": []
                }
                for j in range(len(liste[i]['valeur'])):
                    big_dico = {'table_name':"",
                        'col': "",
                        'type': "",
                        'values':[]}
                    colonne = liste[i]['valeur'][j]['nom']
                    sdtype = liste[i]['valeur'][j]['type']
                    if sdtype == 'radio' or sdtype == 'single':
                        dico_id = liste[i]['valeur'][j]['dico']
                        for k in range(len(dicos)):
                            if dicos[k]['id'] == dico_id:
                                big_dico['table_name'] = table_names
                                big_dico['col'] = colonne
                                big_dico['type'] = sdtype
                                for l in range(len(dicos[k]\
                                                   ['attrs']['value'])):
                                    if "archived" in dicos[k]['attrs']\
                                        ['value'][l].keys():
                                                    if dicos[k]['attrs']\
                                                        ['value'][l]['archived']:
                                                            continue
                                                    else:
                                                        big_dico['values']\
                                                            .append(dicos[k]\
                                                                ['attrs']['value']\
                                                                    [l]['code'])
                                    else:
                                        big_dico['values'].append(dicos[k]\
                                            ['attrs']['value'][l]['code'])
                        listo.append(big_dico)


                    
                    sdtype = conversion_map.get(sdtype, sdtype)
                    if isinstance(sdtype, tuple):
                        tables_specs["columns"][colonne] \
                            = {"sdtype": sdtype[0], 
                               "computer_representation": sdtype[1]}
                    elif isinstance(sdtype, dict): 
                        tables_specs["columns"][colonne] = sdtype
                    elif sdtype == 'calculated' and rep == "true":
                        tables_specs["columns"][colonne] = {"sdtype": 'text'}
                    elif sdtype == 'calculated' and rep == "false":
                        tables_specs["columns"][colonne] = {"sdtype": 'categorical'}
                    else:
                        tables_specs["columns"][colonne] = {"sdtype": sdtype}

                tables_specs["columns"]['sys_id'] = {"sdtype" : "id" }
                tables_specs['primary_key'] = 'sys_id'
                metadata_json['tables'][table_names] = tables_specs
            else:
                print(f"The table {liste[i]['nom']} is not explicitly linked.")
                continue

        for s in range(len(liens)):
            relat = {
                "parent_table_name": "",
                "child_table_name": "",
                "parent_primary_key": "",
                "child_foreign_key": ""
            }
            parent = liens[s][0]['name']
            child = liens[s][1]['name']

            relat['parent_table_name'] = parent
            relat['child_table_name'] = child
            relat['parent_primary_key'] \
                = metadata_json['tables'][parent]['primary_key']
            parent_key = parent + '.sys_id'
            metadata_json['tables'][child]['columns'][parent_key] \
                = {'sdtype' : 'id'}
            relat['child_foreign_key'] = parent_key

            metadata_json['relationships'].append(relat)

        return metadata_json, listo


    def extract_component_info(data, nam):
        """Recursive function to find all variables within the pages of a 
        Voozanoo 4 project

        Args:
            data (dict): the JSON file converted to understandable python
            nam (string): The name of the page/table/varset

        Returns:
            metadate (dict) : Specific format dictionnary that will allow 
            the convert function to work
        
        Raises:
            KeyError: 
                pass
        """
        metadate = {'nom': nam, 'valeur': []}
        if isinstance(data, dict):
            attrs = data.get('attrs', {})
            try:
                name = attrs['name']
                render_type = attrs.get('render-type')
                subtype = attrs.get('subtype')
                label_position = attrs.get('labelPosition')
                
                if attrs.get('type') == 'component' and render_type != 'form':
                    if render_type == 'single' or render_type == 'multiples':
                        dico = attrs.get('dico')
                        metadate['valeur'].append({'nom': name, 
                                                   'type': render_type, 
                                                   'dico': dico})
                    elif subtype == 'boolean' and label_position:
                        metadate['valeur'].append({'nom': name, 
                                                   'type': 'boolean'})
                    elif subtype == "tableColumn":
                        pass
                    else:
                        metadate['valeur'].append({'nom': name, 
                                                   'type': render_type})
                elif attrs.get('type') == 'datasource' and \
                    attrs.get('subtype') == 'custom' and \
                        attrs.get('mode') == 'xml':
                            pass
                elif attrs.get('type') == 'datasource' and \
                    attrs.get('subtype') == 'custom':
                    label = attrs.get('label', '').lower()
                    label = unicodedata.normalize('NFKD', 
                                                  label)\
                                                    .encode('ascii', 'ignore')\
                                                        .decode('utf-8')
                    label = re.sub(r'[^a-zA-Z0-9_]', '_', label)
                    metadate['valeur'].append({'nom': label, 
                                               'type': 'calculated'})

            except KeyError:
                pass
            for child in data.get('child', []):
                child_metadate = extract_component_info(child, nam)
                metadate['valeur'].extend(child_metadate['valeur'])
        elif isinstance(data, list):
            for item in data:
                child_metadate = extract_component_info(item, nam)
                metadate['valeur'].extend(child_metadate['valeur'])
        return metadate
    

    def parse_pages(data):
        """Parse pages using a recursive function to look for the right ones
        and use the extract_component function to extract all the variables to
        create the right format for the final converter

        Args:
            data (dict): JSON portion that contains all the pages 
            of the project

        Returns:
            metadates (list): A list of all the tables
            that the project contains under the right input format for the 
            final converter
        """
        metadates = []
        if isinstance(data, dict):
            attrs = data.get('attrs', {})
            component_type = attrs.get('type', '')
            component_subtype = attrs.get('subtype', '')
            if component_type == 'component' and component_subtype == 'page':
                if attrs.get('render-type', '') == 'form':
                    no = data['attrs']['varset']
                    metadate = extract_component_info(data, no)
                    metadates.append(metadate)
            for child in data.get('child', []):
                metadates.extend(parse_pages(child))
        elif isinstance(data, list):
            for item in data:
                metadates.extend(parse_pages(item))
        return metadates


    def parse_dicos(data):
        """Look for the dictionnaries informations and creates a list of these 
        informations for the converter to search into

        Args:
            data (dict): JSON portion that contains all the dictionnaries 
            of the project

        Returns:
            dicos (list): A list of all the dictionnaries 
            that the project contains under the right input format for the 
            final converter
        """
        dicos = []
        for item in data:
            dicos.append(item)
        return dicos


    def parse_relationship(data):
        """Look for the relationships informations and creates a list of these 
        informations for the converter to search into

        Args:
            data (dict): JSON portion that contains all the relationships 
            of the project

        Returns:
            liaisons (list): A list of all the relationships that the project 
            contains under the right input format for the final converter
        """
        liaisons = []
        for item in data:
            liaisons.append(item['attrs']['varsets'])
        return liaisons


    def treat_form_pages(data):
        """A JSON parser that will parse the JSON file and seperate it a uses 
        the right funciton to ease the process

        Args:
            data (dict): The read JSON file using the read function.

        Returns:
            metadates, dicos, liaisons (dicts and lists): Dictionnaries and 
            Lists to the right format so the convert_to_metadata_json function 
            can use them to create the right metadata format
        """
        metadates = []
        dicos = []
        liaisons = []
        if isinstance(data, dict):
            id = data.get('id')
            if id == 'pages':
                metadates = parse_pages(data)
            elif id == 'dicos':
                dicos = parse_dicos(data['child'])
            elif id == 'relations':
                liaisons = parse_relationship(data['child'])
            else:
                for child in data.get('child', []):
                    result = treat_form_pages(child)
                    metadates.extend(result[0])
                    dicos.extend(result[1])
                    liaisons.extend(result[2])
        elif isinstance(data, list):
            for item in data:
                result = treat_form_pages(item)
                metadates.extend(result[0])
                dicos.extend(result[1])
                liaisons.extend(result[2])
        return metadates, dicos, liaisons


    def merge_dicts_with_same_table_name(metadates):
        """If a same varset contains multiple pages, the function will merge
        them together in order to not create multiple same name tables

        Args:
            metadates (list): A list of the parsed pages of the the JSON file

        Returns:
            merged_tables (list): A list with the tables that had the same 
            names merged with their values merged (same name values will be
            merged too)
        """
        merged_metadates = {}
        for metadate in metadates:
            table_name = metadate['nom']
            if table_name not in merged_metadates:
                merged_metadates[table_name] = metadate['valeur']
            else:
                merged_metadates[table_name].extend(metadate['valeur'])
        return [{'nom': table_name, 'valeur': values} for table_name, 
                values in merged_metadates.items()]


    metadates, dicos, liaisons = treat_form_pages(root) 

    merged_metadates = merge_dicts_with_same_table_name(metadates)
    
    if method == "schema":
        
        table_specs = {}
        for i in range(len(merged_metadates)): 
            table_name = merged_metadates[i]["nom"]
            table_specs[table_name] = {}
            
            for val in merged_metadates[i]["valeur"]:
                col = val["nom"]
                dtype = conversion_schema.get(val["type"], val["type"])
                table_specs[table_name][col] = dtype
        
        return table_specs
    else:
        metadata, lista = convert_to_metadata_json(merged_metadates, 
                                                liaisons, 
                                                dicos, 
                                                calc)

        return metadata, lista