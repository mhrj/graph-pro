import numpy as np

class FragmentAssembler:
    def __init__(self, fragments):
        """
        Initialize the FragmentAssembler with a list of fragments.

        Args:
            fragments (list of str): List of DNA/RNA fragments to assemble.
        """
        self.fragments = fragments
        self.n = len(fragments)
        self.overlap_matrix = self._build_overlap_matrix()

    def _calculate_overlap(self, fragment1, fragment2):
        """
        Calculate the length of the longest suffix of fragment1
        that matches a prefix of fragment2.

        Args:
            fragment1 (str): The first fragment.
            fragment2 (str): The second fragment.

        Returns:
            int: The length of the overlap.
        """
        max_overlap = 0
        len1, len2 = len(fragment1), len(fragment2)
        for i in range(1, min(len1, len2) + 1):
            if fragment1[-i:] == fragment2[:i]:
                max_overlap = i
        return max_overlap
    
    def _build_overlap_matrix(self):
            """
            Build the overlap matrix for the fragments.

            Returns:
                numpy.ndarray: A 2D matrix where element (i, j) represents
                            the overlap length between fragments[i] and fragments[j].
            """
            overlap_matrix = np.zeros((self.n, self.n), dtype=int)

            for i, fragment1 in enumerate(self.fragments):
                for j, fragment2 in enumerate(self.fragments):
                    if i != j:
                        overlap_matrix[i][j] = self._calculate_overlap(fragment1, fragment2)

            return overlap_matrix
    
    def graph(self):
        """
        Build and return the directed graph representation as a dictionary.
        Each node has its neighbors as keys and overlap lengths as values.

        Returns:
            dict: A dictionary where each key is a fragment, and the value is a dictionary
                  of neighboring fragments with their overlap lengths.
        """
        graph = {}
        for i, fragment1 in enumerate(self.fragments):
            neighbors = {}
            for j, fragment2 in enumerate(self.fragments):
                if self.overlap_matrix[i][j] > 0:
                    neighbors[fragment2] = self.overlap_matrix[i][j]
            graph[fragment1] = neighbors
        return graph