# Let's write the Python program to process the files and generate relationships based on the rules provided.

import os

# Function to parse the file and extract relevant information
def parse_file(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()
    
    entity = lines[0].split(':')[1].strip() if len(lines) > 0 and ':' in lines[0] else None
    attributes = lines[1].split(':')[1].strip().split(', ') if len(lines) > 1 and ':' in lines[1] else []
    primary_key = lines[2].split(':')[1].strip().split(', ') if len(lines) > 2 and ':' in lines[2] else []
    foreign_keys = {}
    
    if len(lines) > 3 and lines[3].startswith('foreign key:') and lines[3].split(':')[1].strip() != 'None':
        fk_lines = lines[3].split(':')[1].strip().split(';')
        for fk in fk_lines:
            if fk.strip():
                fk_attr, ref = fk.split(', ')
                ref_table, ref_key = ref.split('->')
                foreign_keys[fk_attr.strip()] = (ref_table.strip(), ref_key.strip())
    
    return {
        'entity': entity,
        'attributes': attributes,
        'primary_key': primary_key,
        'foreign_keys': foreign_keys
    }

# Updated function to handle 1:n relationships where a table has a primary key and also has a foreign key (even if not in the primary key).

def determine_relationships(parsed_data):
    relationships = []
    entities_with_relationships = set()  # Track entities that have already established relationships
    
    for data in parsed_data:
        entity = data['entity']
        primary_key = data['primary_key']
        foreign_keys = data['foreign_keys']
        attributes = data['attributes']
        
        if entity in entities_with_relationships:
            continue  # Skip entities that have already established relationships
        
        if len(primary_key) > 1:
            # Rule 1 and Rule 2 apply here
            fk_in_pk = [key for key in primary_key if key in foreign_keys]
            
            if len(fk_in_pk) == len(primary_key):
                # Rule 1: m:n relationship
                referenced_tables = [foreign_keys[key][0] for key in primary_key]
                attr_except_keys = [attr for attr in attributes if attr not in primary_key]
                if attr_except_keys:
                    relationships.append(f"m:n relationship between {', '.join(referenced_tables)} with attributes {', '.join(attr_except_keys)}")
                else:
                    relationships.append(f"m:n relationship between {', '.join(referenced_tables)}")
                entities_with_relationships.update(referenced_tables + [entity])
                continue  # Skip to the next entity since Rule 1 was applied
            
            elif len(fk_in_pk) == 1:
                # Check for the new multivalued attribute rule
                if len(primary_key) == 2 and len(attributes) == 2:
                    non_fk_column = [key for key in primary_key if key not in fk_in_pk][0]
                    relationships.append(f"Multivalued attribute {non_fk_column} for entity {foreign_keys[fk_in_pk[0]][0]}")
                    entities_with_relationships.add(entity)
                    entities_with_relationships.add(foreign_keys[fk_in_pk[0]][0])
                    continue  # Skip to the next entity since the multivalued attribute rule was applied
                
                # Rule 2: 1:n weak relationship
                referenced_table = foreign_keys[fk_in_pk[0]][0]
                relationships.append(f"1:n weak relationship between {entity} and {referenced_table}")
                entities_with_relationships.add(entity)
                entities_with_relationships.add(referenced_table)
                continue  # Skip to the next entity since Rule 2 was applied
        
        # Apply Rule 3 only if neither Rule 1 nor Rule 2 was applied
        for fk in foreign_keys:
            if fk not in primary_key:  # Check only if the foreign key is not part of the primary key
                referenced_table = foreign_keys[fk][0]
                relationships.append(f"1:n relationship between {entity} and {referenced_table}")
                entities_with_relationships.add(entity)
                entities_with_relationships.add(referenced_table)
    
    return relationships






# Function to read all files and determine relationships
def generate_relationship_file(directory_path, output_file):
    parsed_data = []
    
    # Parse all files in the directory
    for filename in os.listdir(directory_path):
        if filename.endswith(".txt"):
            file_path = os.path.join(directory_path, filename)
            parsed_data.append(parse_file(file_path))
    
    # Determine relationships based on parsed data
    relationships = determine_relationships(parsed_data)
    
    # Write the relationships to an output file
    with open(output_file, 'w') as file:
        for relationship in relationships:
            file.write(relationship + '\n')


# Since the program will be in the same folder as the .txt files, we can set the directory path to the current working directory.
# We will use os.getcwd() to get the current directory.

# Adjust the paths for local execution
directory_path = os.getcwd()  # Current working directory
output_file = os.path.join(directory_path, "relationships.txt")

# Generate the relationships file
generate_relationship_file(directory_path, output_file)

# Let's check the content of the generated file
with open(output_file, 'r') as file:
    relationships_content = file.read()

relationships_content
