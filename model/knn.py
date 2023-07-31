import numpy as np
from sklearn.metrics import accuracy_score, precision_recall_fscore_support


class Knn:
    def __init__(self, participants, k):
        self.participants = participants
        self.k = k

    @staticmethod
    def _calculate_distance(participant1, participant2):
        # Calculate distance between two participants using diversity indices and gene data
        diversity_dist = 0
        for functionality in ['productive', 'unproductive']:
            for metric in participant1.diversity_indices[functionality]:
                diff = participant1.diversity_indices[functionality][metric] - participant2.diversity_indices[functionality][metric]
                diversity_dist += diff ** 2

            for col in participant1.cols:
                for gene_type in ['productive', 'unproductive']:
                    for gene in participant1.genes[gene_type][col].values:
                        match = participant2.genes[gene_type][col].query(f"{col}=='{gene[0]}'")
                        if not match.empty:
                            # unique
                            diff = gene[1] - match['unique'].values[0]
                            diversity_dist += diff ** 2
                            # total
                            diff = gene[2] - match['total'].values[0]
                            diversity_dist += diff ** 2

        return np.sqrt(diversity_dist)

    def find_k_nearest_neighbors(self, target_participant):
        # Calculate distances from the target participant to all other participants
        distances = []
        for participant in self.participants:
            if participant != target_participant:
                distance = self._calculate_distance(target_participant, participant)
                distances.append((participant, distance))

        # Sort the distances in ascending order
        distances.sort(key=lambda x: x[1])

        # Get the k-nearest neighbors
        k_nearest_neighbors = [participant for participant, _ in distances[:self.k]]

        return k_nearest_neighbors

    @staticmethod
    def calculate_metrics(true_labels, predicted_labels):
        # Calculate validation metrics (accuracy, precision, recall, F1 score)
        accuracy = accuracy_score(true_labels, predicted_labels)
        precision, recall, f1, _ = precision_recall_fscore_support(true_labels, predicted_labels, average='weighted')
        return accuracy, precision, recall, f1


