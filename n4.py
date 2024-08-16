from sentence_transformers import SentenceTransformer
from sklearn.cluster import DBSCAN
import os
import numpy as np

# Load BERT model for embeddings
model = SentenceTransformer('all-MiniLM-L6-v2')

# Define keywords for hardcoded categorization
address_keywords = ['street', 'avenue', 'road', 'lane', 'city', 'state', 'zipcode', 'postcode', 'pincode', 'address', 'houseno', 'hno','doorno','streetno']
name_keywords = ['firstname', 'lastname', 'middlename', 'surname', 'name','fname','mname','lname']
dob_keywords = ['dob', 'birthdate', 'birth', 'date']

def read_file(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()
        
    entity = lines[0].split(':')[1].strip()
    attributes = [attr.strip() for attr in lines[1].split(':')[1].split(',')]
    constraints = {}
    for line in lines[2:]:
        if ':' in line:
            key, value = line.split(':', 1)
            constraints[key.strip()] = value.strip()
        
    return entity, attributes, constraints

def get_embeddings(attributes):
    embeddings = model.encode(attributes)
    return embeddings

def categorize_hardcoded(attributes):
    clusters = {
        'address': [],
        'name': [],
        'dob': [],
        'others': []
    }
    
    for attr in attributes:
        lower_attr = attr.lower()
        if any(keyword in lower_attr for keyword in address_keywords):
            clusters['address'].append(attr)
        elif any(keyword in lower_attr for keyword in name_keywords):
            clusters['name'].append(attr)
        elif any(keyword in lower_attr for keyword in dob_keywords):
            clusters['dob'].append(attr)
        else:
            clusters['others'].append(attr)
    
    return clusters

def cluster_attributes(embeddings, attributes):
    # Perform hardcoded categorization first
    hardcoded_clusters = categorize_hardcoded(attributes)
    
    # Cluster remaining attributes using DBSCAN
    if hardcoded_clusters['others']:
        clustering = DBSCAN(eps=0.5, min_samples=2, metric='cosine')
        labels = clustering.fit_predict(embeddings)
        
        clusters = {}
        for label, attr in zip(labels, hardcoded_clusters['others']):
            if label not in clusters:
                clusters[label] = []
            clusters[label].append(attr)
        
        # Combine hardcoded clusters with DBSCAN results
        for category, attrs in hardcoded_clusters.items():
            if category != 'others' and attrs:
                clusters[category] = attrs
        
        return clusters
    else:
        return hardcoded_clusters

def write_clusters_to_file(file_path, clusters):
    if clusters:
        with open(file_path, 'a') as file:
            file.write("\nComposite Attributes:")
            for cluster_id, attrs in clusters.items():
                if cluster_id != -1 and len(attrs) > 1:  # Exclude noise points and single attributes
                    file.write(f" {', '.join(attrs)}\n")

def process_files(directory):
    for file_name in os.listdir(directory):
        if file_name.endswith('.txt') and file_name != 'relationships.txt':
            file_path = os.path.join(directory, file_name)
            
            entity, attributes, constraints = read_file(file_path)
            embeddings = get_embeddings(attributes)
            clusters = cluster_attributes(embeddings, attributes)
            write_clusters_to_file(file_path, clusters)

if __name__ == "__main__":
    directory = '.'  # Directory where the .txt files are located
    process_files(directory)
