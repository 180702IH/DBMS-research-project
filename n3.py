from sentence_transformers import SentenceTransformer
from sklearn.cluster import DBSCAN
import os
import numpy as np

# Load BERT model for embeddings
model = SentenceTransformer('all-MiniLM-L6-v2')

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

def cluster_attributes(embeddings, attributes):
    # Using DBSCAN to handle varying number of clusters
    clustering = DBSCAN(eps=0.5, min_samples=2, metric='cosine')
    labels = clustering.fit_predict(embeddings)
    
    clusters = {}
    for label, attr in zip(labels, attributes):
        if label not in clusters:
            clusters[label] = []
        clusters[label].append(attr)
    
    return clusters

def write_clusters_to_file(file_path, clusters):
    if clusters:
        with open(file_path, 'a') as file:
            file.write("\nComposite Attributes:")
            for cluster_id, attrs in clusters.items():
                if cluster_id != -1:  # Exclude noise points
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
