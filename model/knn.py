import numpy as np
from sklearn.metrics import accuracy_score, precision_recall_fscore_support
import pandas as pd


class Knn:
    def __init__(self, participants, k):
        self.participants = participants
        self.k = k

    @staticmethod
    def _calculate_distance(participant1, participant2):
        # Calculate diversity distances (x)
        diversity_dist = 0
        for functionality in ['productive', 'unproductive']:
            for metric in participant1.diversity_indices[functionality]:
                diff = participant1.diversity_indices[functionality][metric] - participant2.diversity_indices[functionality][metric]
                diversity_dist += diff ** 2

        # Calculate gene distances (y)
        gene_dist = 0
        for col in participant1.cols:
            for gene_type in ['productive', 'unproductive']:
                for gene in participant1.genes[gene_type][col].values:
                    match = participant2.genes[gene_type][col].query(f"{col}=='{gene[0]}'")
                    if not match.empty:
                        # unique
                        diff = gene[1] - match['unique'].values[0]
                        gene_dist += diff ** 2
                        # total
                        diff = gene[2] - match['total'].values[0]
                        gene_dist += diff ** 2

        # Weighted combination of diversity_dist and gene_dist
        overall_dist = np.sqrt(diversity_dist) + np.sqrt(gene_dist)

        return diversity_dist, gene_dist, overall_dist

    def find_k_nearest_neighbors(self, target_participant):
        # Calculate distances from the target participant to all other participants
        distances = []
        for participant in self.participants:
            if participant != target_participant:
                diversity_dist, gene_dist, overall_dist = self._calculate_distance(target_participant, participant)
                distances.append((participant.individual, diversity_dist, gene_dist, overall_dist))

        # Sort the distances based on overall_dist in ascending order
        distances.sort(key=lambda x: x[3])

        # Get the k-nearest neighbors as a list of participant objects
        k_nearest_neighbors = [participant for participant, _, _, _ in distances[:self.k]]

        # Convert distances list to DataFrame
        df = pd.DataFrame(distances, columns=['participant', 'diversity_dist', 'gene_dist', 'overall_dist'])

        return k_nearest_neighbors, df

    @staticmethod
    def calculate_metrics(true_labels, predicted_labels):
        # Calculate validation metrics (accuracy, precision, recall, F1 score)
        accuracy = accuracy_score(true_labels, predicted_labels)
        precision, recall, f1, _ = precision_recall_fscore_support(true_labels, predicted_labels, average='weighted')
        return accuracy, precision, recall, f1
