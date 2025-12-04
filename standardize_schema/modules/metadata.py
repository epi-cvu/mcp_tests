import re
import xml.etree.ElementTree as ET
from sdv.io.local import CSVHandler
from sdv.metadata import Metadata

def csv_to_metadata(folder_path):
    connector = CSVHandler()
    data = connector.read(folder_name=folder_path)
    metadata = Metadata.detect_from_dataframes(
        data=data
    )
    return metadata

def xml_to_metadata(file_path):
    tree = ET.parse(file_path)

    root = tree.getroot()
    mapping = {
        "varchar": object,
        "bigint": "Int64",
        "int": "Int64",
        "tinyint": "Int64",
        "smallint": "Int64",
        "date": 'datetime',
        "datetime": 'datetime',
        "longtext": object,
        "text": object,
        "double": float,
        "longblob": object,
        "char": object,
        "decimal": float,
        "float": float,
        "mediumblob": object,
        "timestamp": 'datetime',
        "mediumtext": object,
        "binary": object
    } 

    pandas_premap = {}
    date_dict = {}

    for table in root.findall("./TABLES/TABLE"):
        table_name = table.get('NAME')
        column_var = {}
        date_list = []
        
        fields_block = table.find("FIELDS")
        if fields_block is not None:
            for field in fields_block.findall("./FIELD"):
                column_name = field.get('NAME')
                column_type = field.get("TYPE").strip()
                
                type_raw = field.get("TYPE", "text").strip()

                type_clean = re.match(r"^\w+", type_raw)
                column_type_clean = type_clean.group(0) if type_clean else type_raw
                column_type = mapping.get(column_type_clean.lower(), column_type_clean)
                
                if column_name: 
                    column_var[column_name] = {}
                    if column_type == "datatime":
                        column_var[column_name]["sdtype"] = column_type
                        column_var[column_name]["datetime_format"] = "%Y-%m-%d"
                    elif column_type == float:
                        column_var[column_name]["sdtype"] = "numerical"
                        column_var[column_name]["computer_representation"] = "Float"
                    elif column_type == object:
                        column_var[column_name]["sdtype"] = "text"
                    elif column_type == "Int64":
                        column_var[column_name]["sdtype"] = "numerical"
                        column_var[column_name]["computer_representation"] = "Int64"
                    else: 
                        column_var[column_name]["sdtype"] = "id"

        pandas_premap[table_name] = column_var
        
    sdv_final = {
        "tables": pandas_premap,
        "relationships": [],
        "METADATA_SPEC_VERSION": "V1",
    }  
    return sdv_final

def sql_to_metadata(file_path):
    mapping = {
        "varchar": "str",
        "bigint": "Int64",
        "int": "Int32",
        "tinyint": "Int8",
        "smallint": "Int16",
        "date": "datetime",
        "datetime": "datetime",
        "longtext": "str",
        "text": "str",
        "double": "Float",
        "longblob": "str"
    }

    # Final outputs
    table_dict = {}
    constraints_dict = {}  # optional
    foreign_keys = []      # ← ta structure spéciale ici

    # Regex
    create_table_regex = r"CREATE TABLE `(\w+)` \((.*?)\) ENGINE"
    column_regex = r"^\s*`(\w+)`\s+([^\n,]+),?"

    constraint_keywords = ("PRIMARY KEY", "UNIQUE KEY", "KEY", "CONSTRAINT")

    # Lecture du fichier SQL
    with open(file_path, 'r') as file:
        sql = file.read()

    sql = re.sub(r"/\*!50001\s+CREATE TABLE .*?ENGINE=.*?\*/;", "", sql, flags=re.DOTALL)

    for match in re.finditer(create_table_regex, sql, re.DOTALL):
        table_name = match.group(1)
        columns_block = match.group(2)

        columns = {}
        constraints = []

        lines = columns_block.strip().split("\n")
        for line in lines:
            line = line.strip().rstrip(",")
            if not line or line.startswith("--"):
                continue

            if any(line.upper().startswith(k) for k in constraint_keywords):
                constraints.append(line)

                # 👇 Traitement spécifique FOREIGN KEY
                fk_match = re.search(
                    r"FOREIGN KEY\s*\(`(\w+)`\)\s+REFERENCES\s+`(\w+)`\s+\(`(\w+)`\)", line, re.IGNORECASE)
                if fk_match:
                    child_fk = fk_match.group(1)
                    parent_table = fk_match.group(2)
                    parent_pk = fk_match.group(3)

                    foreign_keys.append({
                        "parent_table_name": parent_table,
                        "child_table_name": table_name,
                        "parent_primary_key": parent_pk,
                        "child_foreign_key": child_fk
                    })

                continue

            # Sinon, on traite la colonne normalement
            column_match = re.match(column_regex, line)
            if column_match:
                column_name = column_match.group(1)
                raw_type = column_match.group(2).split()[0].split("(")[0]
                column_type = mapping.get(raw_type.lower(), raw_type)
                columns[column_name] = column_type

        table_dict[table_name] = columns
        if constraints:
            constraints_dict[table_name] = constraints
            
    temp_format = {"tables": {}}
    for table in table_dict:
        # Initialize the table structure in sdv_format
        temp_format["tables"][table] = {"columns": {}}
        
        for col in table_dict[table]:
            # Initialize the column structure in sdv_format
            temp_format["tables"][table]["columns"][col] = {}
            
            if table_dict[table][col] in ["Int64", "Int8", "Int16", "Int32"]:
                temp_format["tables"][table]["columns"][col]["sdtype"] = "numerical"
                temp_format["tables"][table]["columns"][col]["computer_representation"] = "Int64"
            elif table_dict[table][col] == "Float":
                temp_format["tables"][table]["columns"][col]["sdtype"] = "numerical"
                temp_format["tables"][table]["columns"][col]["computer_representation"] = "Float"
            elif table_dict[table][col] == "str":
                temp_format["tables"][table]["columns"][col]["sdtype"] = "text"
            elif table_dict[table][col] == "datetime":
                temp_format["tables"][table]["columns"][col]["sdtype"] = "datetime"
                temp_format["tables"][table]["columns"][col]["datetime_format"] = "%Y-%m-%d"
    
    for table, constraints in constraints_dict.items():
        # Find the primary key in the constraints
        primary_key = None
        for constraint in constraints:
            if "PRIMARY KEY" in constraint:
                match = re.search(r'`(\w+)`', constraint)
                if match:
                    primary_key = match.group(1)
                    break

        # If a primary key is found, update the sdv_format
        if primary_key and table in temp_format["tables"]:
            if primary_key in temp_format["tables"][table]["columns"]:
                temp_format["tables"][table]["columns"][primary_key]["sdtype"] = "id"
                # Remove other keys except "sdtype"
                keys_to_remove = list(temp_format["tables"][table]["columns"][primary_key].keys())
                for key in keys_to_remove:
                    if key != "sdtype":
                        del temp_format["tables"][table]["columns"][primary_key][key]
                # Add the primary key to the table structure
                temp_format["tables"][table]["primary_key"] = primary_key
    
    for fk in foreign_keys:
        parent_table = fk["parent_table_name"]
        child_table = fk["child_table_name"]
        parent_pk = fk["parent_primary_key"]
        child_fk = fk["child_foreign_key"]

        # Update parent table
        if parent_table in temp_format["tables"]:
            if parent_pk in temp_format["tables"][parent_table]["columns"]:
                temp_format["tables"][parent_table]["columns"][parent_pk]["sdtype"] = "id"
                temp_format["tables"][parent_table]["columns"][parent_pk].pop("computer_representation", None)
            temp_format["tables"][parent_table]["primary_key"] = parent_pk

        # Update child table
        if child_table in temp_format["tables"]:
            if child_fk in temp_format["tables"][child_table]["columns"]:
                temp_format["tables"][child_table]["columns"][child_fk]["sdtype"] = "id"
                temp_format["tables"][child_table]["columns"][child_fk].pop("computer_representation", None)
            
    sdv_final = {
        "tables": temp_format["tables"],
        "relationships": foreign_keys,
        "METADATA_SPEC_VERSION": "V1",
    }          
    
    return sdv_final
