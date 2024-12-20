import numpy as np
import itertools

FRAGMENTS = ["ACT", "CTC", "CTG", "TGG", "TCT"]

class FragmentAssembler:
    def __init__(self, fragments = FRAGMENTS):
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
    
    def hamiltonian_path(self):
        """
        Build and return a possible Hamiltonian path as a dictionary.
        Each node maps to its next neighbor in the path.

        Returns:
            dict: A dictionary representing the Hamiltonian path.
        """
        max_path = None
        max_overlap = -1

        for perm in itertools.permutations(range(self.n)):
            total_overlap = 0
            path = []

            for i in range(1, self.n):
                prev = perm[i - 1]
                curr = perm[i]
                total_overlap += self.overlap_matrix[prev][curr]
                path.append(self.fragments[prev])

            path.append(self.fragments[perm[-1]])

            if total_overlap > max_overlap:
                max_overlap = total_overlap
                max_path = path

        if max_path:
            hamiltonian_path = {
                max_path[i]: max_path[i + 1] if i + 1 < len(max_path) else None
                for i in range(len(max_path))
            }
            return hamiltonian_path
        else:
            return {}
        
    def find_shortest_superstring(self):
        """
        Find the shortest superstring that contains all fragments as substrings.

        Returns:
            str: The shortest superstring.
        """
        best_superstring = None
        max_overlap = -1

        for perm in itertools.permutations(range(self.n)):
            current_string = self.fragments[perm[0]]
            total_overlap = 0

            for i in range(1, self.n):
                prev = perm[i - 1]
                curr = perm[i]
                overlap = self.overlap_matrix[prev][curr]
                total_overlap += overlap
                current_string += self.fragments[curr][overlap:]

            if total_overlap > max_overlap:
                max_overlap = total_overlap
                best_superstring = current_string

        return best_superstring
    
# # Example usage
# # Create class instance
# assembler = FragmentAssembler()

# # Graph
# graph = assembler.graph()
# print(graph)

# # Hamiltonian path
# hamiltonian_path = assembler.hamiltonian_path()
# print(hamiltonian_path)

# # Find and print the shortest superstring
# shortest_superstring = assembler.find_shortest_superstring()
# print(shortest_superstring)