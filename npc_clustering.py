import numpy as np
import random

def kmeans_clustering(npc_positions, k=3, max_iterations=100):
    if len(npc_positions) < k:
        return list(range(len(npc_positions))), npc_positions

    centroids = random.sample(npc_positions, k)
    for _ in range(max_iterations):
        clusters = {i: [] for i in range(k)}
        labels = []

        for npc in npc_positions:
            distances = [np.linalg.norm(np.array(npc) - np.array(centroid)) for centroid in centroids]
            closest_cluster = distances.index(min(distances))
            clusters[closest_cluster].append(npc)
            labels.append(closest_cluster)

        new_centroids = []
        for i in range(k):
            if clusters[i]: 
                cluster_points = np.array(clusters[i])
                new_centroids.append(tuple(np.mean(cluster_points, axis=0).astype(int)))
            else:
                new_centroids.append(centroids[i])

        if new_centroids == centroids:
            break
        centroids = new_centroids

    return labels, centroids

def cluster_npc_groups(player_pos, npc_positions):
    
    labels, centroids = kmeans_clustering(npc_positions, k=3)

    distances = [np.linalg.norm(np.array(centroid) - np.array(player_pos)) for centroid in centroids]
    sorted_groups = np.argsort(distances)

    clustered_npcs = {"chaser": [], "helper": [], "blocker": []}
    for npc, label in zip(npc_positions, labels):
        if label == sorted_groups[0]:
            clustered_npcs["chaser"].append(npc)
        elif label == sorted_groups[1]:
            clustered_npcs["helper"].append(npc)
        else:
            clustered_npcs["blocker"].append(npc)

    return clustered_npcs