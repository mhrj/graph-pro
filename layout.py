import sys
import numpy as np
import plotly.graph_objects as go
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
                             QWidget, QLabel, QGroupBox, QPushButton)
from PyQt5.QtWebEngineWidgets import QWebEngineView
from fragment_assembler import FragmentAssembler  # Assuming FragmentAssembler is in fragment_assembler.py

# Plotly Widget Class
class PlotlyWidget(QWebEngineView):
    def __init__(self, fig):
        super().__init__()
        self.setHtml(fig.to_html(include_plotlyjs='cdn'))

# Graph Visualization Window
class GraphWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Fragment Assembler Visualization")
        self.setGeometry(100, 100, 1200, 800)

        # Initialize the FragmentAssembler
        self.assembler = FragmentAssembler()

        # Generate graphs
        self.full_graph_fig = self.create_graph_figure(self.assembler.graph(), show_hamiltonian=False)
        self.hamiltonian_graph_fig = self.create_graph_figure(self.assembler.graph(), show_hamiltonian=True)
        self.superstring = self.assembler.find_shortest_superstring()

        # Initialize UI layout
        self.init_ui()

    def get_layout(self, nodes):
        """
        Generate a circular layout for graph nodes.

        Args:
            nodes (list of str): List of node names.

        Returns:
            tuple: Two lists containing the x and y coordinates of the nodes.
        """
        node_count = len(nodes)
        angle_step = 2 * np.pi / node_count
        node_x = [0.5 + 0.4 * np.cos(i * angle_step) for i in range(node_count)]
        node_y = [0.5 + 0.4 * np.sin(i * angle_step) for i in range(node_count)]
        return node_x, node_y

    def get_hamiltonian_edges(self):
        """
        Extract edges from the Hamiltonian path.

        Returns:
            list of tuple: List of edges in the Hamiltonian path.
        """
        hamiltonian_path = self.assembler.hamiltonian_path()
        hamiltonian_edges = []

        for node1, node2 in zip(list(hamiltonian_path.keys()), list(hamiltonian_path.values())):
            if node2 is not None:
                hamiltonian_edges.append((node1, node2))

        return hamiltonian_edges

    def create_graph_figure(self, graph, show_hamiltonian=False):
        nodes = list(graph.keys())
        edges = []
        edge_weights = []

        for node, neighbors in graph.items():
            for neighbor, weight in neighbors.items():
                edges.append((node, neighbor))
                edge_weights.append(weight)

        hamiltonian_edges = self.get_hamiltonian_edges() if show_hamiltonian else []

        node_x, node_y = self.get_layout(nodes)

        fig = go.Figure()

        # First, add Hamiltonian path edges in red with arrows and weights in the middle of the edges
        for node1, node2 in hamiltonian_edges:
            x0, y0 = node_x[nodes.index(node1)], node_y[nodes.index(node1)]
            x1, y1 = node_x[nodes.index(node2)], node_y[nodes.index(node2)]

            # Find the weight for the edge
            edge_weight = graph[node1].get(node2, 0)

            # Add edge as a line with an arrow at the end
            fig.add_trace(go.Scatter(
                x=[x0, x1], y=[y0, y1],
                mode='lines+text',
                line=dict(width=2, color='red'),
                hoverinfo='text',
                showlegend=False,
                line_shape='linear'
            ))

            # Add arrowhead by using an annotation
            fig.add_annotation(
                x=x1, y=y1,
                ax=x0, ay=y0,
                xref="x", yref="y",
                axref="x", ayref="y",
                showarrow=True,
                arrowhead=2,
                arrowsize=2,
                arrowwidth=1,
                arrowcolor='red',
                standoff=40  # Adjust space for arrow
            )

            # Add edge weight text at the midpoint of the edge
            mid_x = (x0 + x1) / 2
            mid_y = (y0 + y1) / 2
            fig.add_trace(go.Scatter(
                x=[mid_x], y=[mid_y],
                mode='text',
                text=[f'{edge_weight}'],
                textposition='middle center',  # Position the weight in the middle of the edge
                textfont=dict(size=12, color="black"),
                hoverinfo='none',
                showlegend=False
            ))

        # Now, add the remaining edges in gray with arrows and weights in the middle of the edges
        for node, neighbors in graph.items():
            for neighbor, weight in neighbors.items():
                if (node, neighbor) not in hamiltonian_edges and (neighbor, node) not in hamiltonian_edges:
                    x0, y0 = node_x[nodes.index(node)], node_y[nodes.index(node)]
                    x1, y1 = node_x[nodes.index(neighbor)], node_y[nodes.index(neighbor)]

                    # Find the weight for the edge
                    edge_weight = graph[node].get(neighbor, 0)

                    # Add edge as a line with an arrow at the end
                    fig.add_trace(go.Scatter(
                        x=[x0, x1], y=[y0, y1],
                        mode='lines+text',
                        line=dict(width=2, color='gray'),
                        hoverinfo='text',
                        showlegend=False,
                        line_shape='linear'
                    ))

                    # Add arrowhead by using an annotation
                    fig.add_annotation(
                        x=x1, y=y1,
                        ax=x0, ay=y0,
                        xref="x", yref="y",
                        axref="x", ayref="y",
                        showarrow=True,
                        arrowhead=2,
                        arrowsize=2,
                        arrowwidth=1,
                        arrowcolor='gray',
                        standoff=40  # Adjust space for arrow
                    )

                    # Add edge weight text at the midpoint of the edge
                    mid_x = (x0 + x1) / 2
                    mid_y = (y0 + y1) / 2
                    fig.add_trace(go.Scatter(
                        x=[mid_x], y=[mid_y],
                        mode='text',
                        text=[f'{edge_weight}'],
                        textposition='top center',  # Position the weight in the middle of the edge
                        textfont=dict(size=12, color="black"),
                        hoverinfo='none',
                        showlegend=False
                    ))

        # Add the node markers and labels
        fig.add_trace(go.Scatter(
            x=node_x, y=node_y, mode='markers+text',  # Keep the node positions as is
            text=nodes,
            marker=dict(size=15, color='blue'),
            textposition='top center',  # Shift the label text above the node
            hoverinfo='text',
            showlegend=False
        ))

        # Update layout to make the plot more visually appealing
        fig.update_layout(
            title="Hamiltonian Path" if show_hamiltonian else "Graph Visualization",
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            plot_bgcolor='white'
        )

        return fig





    def init_ui(self):
        central_widget = QWidget(self)
        main_layout = QVBoxLayout(central_widget)
        graph_layout = QHBoxLayout()

        # Group Boxes
        full_graph_group = QGroupBox("Full Graph (No Hamiltonian Highlight)")
        hamiltonian_graph_group = QGroupBox("Graph with Hamiltonian Path Highlighted")

        full_graph_widget = PlotlyWidget(self.full_graph_fig)
        hamiltonian_graph_widget = PlotlyWidget(self.hamiltonian_graph_fig)

        full_graph_layout = QVBoxLayout()
        full_graph_layout.addWidget(full_graph_widget)
        full_graph_group.setLayout(full_graph_layout)

        hamiltonian_graph_layout = QVBoxLayout()
        hamiltonian_graph_layout.addWidget(hamiltonian_graph_widget)
        hamiltonian_graph_group.setLayout(hamiltonian_graph_layout)

        graph_layout.addWidget(full_graph_group)
        graph_layout.addWidget(hamiltonian_graph_group)

        main_layout.addLayout(graph_layout)

        superstring_label = QLabel(f"Shortest Superstring: {self.superstring if self.superstring else 'No valid superstring found.'}")
        superstring_label.setAlignment(Qt.AlignCenter)
        superstring_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #D4AF37;")

        main_layout.addWidget(superstring_label)

        self.setCentralWidget(central_widget)

# Run Application
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = GraphWindow()
    window.show()
    sys.exit(app.exec_())
