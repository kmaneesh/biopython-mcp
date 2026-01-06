"""Phylogenetics analysis tools using BioPython."""

from io import StringIO
from typing import Any

from Bio import AlignIO, Phylo
from Bio.Phylo.TreeConstruction import DistanceCalculator, DistanceTreeConstructor


def build_phylogenetic_tree(
    sequences: list[str], method: str = "nj", labels: list[str] | None = None
) -> dict[str, Any]:
    """
    Build a phylogenetic tree from sequences.

    Args:
        sequences: List of aligned sequences
        method: Tree building method - 'nj' (neighbor-joining) or 'upgma' (default: 'nj')
        labels: Optional labels for sequences

    Returns:
        Dictionary containing tree information
    """
    try:
        if len(sequences) < 3:
            return {
                "success": False,
                "error": "At least 3 sequences required for tree construction",
                "num_sequences": len(sequences),
            }

        if labels is None:
            labels = [f"Seq{i+1}" for i in range(len(sequences))]

        if len(labels) != len(sequences):
            return {
                "success": False,
                "error": "Number of labels must match number of sequences",
                "num_sequences": len(sequences),
                "num_labels": len(labels),
            }

        alignment_str = "\n".join(
            [f">{label}\n{seq}" for label, seq in zip(labels, sequences, strict=True)]
        )
        alignment = AlignIO.read(StringIO(alignment_str), "fasta")

        calculator = DistanceCalculator("identity")

        if method == "nj":
            constructor = DistanceTreeConstructor(calculator, "nj")
        elif method == "upgma":
            constructor = DistanceTreeConstructor(calculator, "upgma")
        else:
            return {
                "success": False,
                "error": f"Unknown method: {method}. Use 'nj' or 'upgma'",
            }

        tree = constructor.build_tree(alignment)

        tree_str = StringIO()
        Phylo.write(tree, tree_str, "newick")
        newick_tree = tree_str.getvalue()

        return {
            "success": True,
            "method": method,
            "num_sequences": len(sequences),
            "tree_newick": newick_tree.strip(),
            "message": f"Phylogenetic tree built using {method.upper()} method",
        }
    except Exception as e:
        return {"success": False, "error": str(e), "method": method}


def calculate_distance_matrix(
    sequences: list[str], model: str = "identity", labels: list[str] | None = None
) -> dict[str, Any]:
    """
    Calculate pairwise distance matrix for sequences.

    Args:
        sequences: List of aligned sequences
        model: Distance model to use (default: 'identity')
        labels: Optional labels for sequences

    Returns:
        Dictionary containing distance matrix
    """
    try:
        if len(sequences) < 2:
            return {
                "success": False,
                "error": "At least 2 sequences required",
                "num_sequences": len(sequences),
            }

        if labels is None:
            labels = [f"Seq{i+1}" for i in range(len(sequences))]

        if len(labels) != len(sequences):
            return {
                "success": False,
                "error": "Number of labels must match number of sequences",
                "num_sequences": len(sequences),
                "num_labels": len(labels),
            }

        alignment_str = "\n".join(
            [f">{label}\n{seq}" for label, seq in zip(labels, sequences, strict=True)]
        )
        alignment = AlignIO.read(StringIO(alignment_str), "fasta")

        calculator = DistanceCalculator(model)
        distance_matrix = calculator.get_distance(alignment)

        matrix_dict: dict[str, dict[str, float]] = {}
        for i, name1 in enumerate(distance_matrix.names):
            matrix_dict[name1] = {}
            for j, name2 in enumerate(distance_matrix.names):
                matrix_dict[name1][name2] = distance_matrix[i, j]

        return {
            "success": True,
            "model": model,
            "num_sequences": len(sequences),
            "labels": distance_matrix.names,
            "distance_matrix": matrix_dict,
        }
    except Exception as e:
        return {"success": False, "error": str(e), "model": model}


def draw_tree(tree_newick: str, output_format: str = "ascii") -> dict[str, Any]:
    """
    Draw a phylogenetic tree from Newick format.

    Args:
        tree_newick: Tree in Newick format
        output_format: Output format - 'ascii' for text representation (default: 'ascii')

    Returns:
        Dictionary containing tree visualization
    """
    try:
        tree = Phylo.read(StringIO(tree_newick), "newick")

        if output_format == "ascii":
            tree_str = StringIO()
            Phylo.draw_ascii(tree, file=tree_str)
            visualization = tree_str.getvalue()

            return {
                "success": True,
                "format": output_format,
                "visualization": visualization,
                "num_terminals": tree.count_terminals(),
            }
        else:
            return {
                "success": False,
                "error": f"Unsupported format: {output_format}. Use 'ascii'",
            }
    except Exception as e:
        return {"success": False, "error": str(e), "format": output_format}
