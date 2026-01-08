"""Basic usage examples for BioPython MCP server."""

from biopython_mcp.alignment import pairwise_align
from biopython_mcp.phylo import build_phylogenetic_tree, draw_tree
from biopython_mcp.sequence import (
    calculate_gc_content,
    find_motif,
    reverse_complement,
    transcribe_dna,
    translate_sequence,
)


def example_sequence_analysis() -> None:
    """Demonstrate basic sequence analysis."""
    print("=== Sequence Analysis Example ===\n")

    dna_seq = "ATGGCCATTGTAATGGGCCGC"
    print(f"DNA Sequence: {dna_seq}\n")

    print("1. Translation:")
    result = translate_sequence(dna_seq)
    if result["success"]:
        print(f"   Protein: {result['protein_sequence']}")
        print(f"   Length: {result['protein_length']} amino acids\n")

    print("2. GC Content:")
    result = calculate_gc_content(dna_seq)
    if result["success"]:
        print(f"   GC%: {result['gc_content_percent']}%")
        print(f"   Nucleotide counts: {result['nucleotide_counts']}\n")

    print("3. Reverse Complement:")
    result = reverse_complement(dna_seq)
    if result["success"]:
        print(f"   Rev Comp: {result['reverse_complement']}\n")

    print("4. Transcription:")
    result = transcribe_dna(dna_seq)
    if result["success"]:
        print(f"   mRNA: {result['output_sequence']}\n")

    print("5. Find Start Codons (ATG):")
    result = find_motif(dna_seq, "ATG")
    if result["success"]:
        print(f"   Found {result['occurrences']} occurrences")
        print(f"   Positions: {result['positions']}\n")


def example_alignment() -> None:
    """Demonstrate sequence alignment."""
    print("=== Sequence Alignment Example ===\n")

    seq1 = "ATGGCCATTGTAATGGGCCGC"
    seq2 = "ATGGCCATTGTTATGGGCCGC"

    print(f"Sequence 1: {seq1}")
    print(f"Sequence 2: {seq2}\n")

    print("Global Alignment:")
    result = pairwise_align(seq1, seq2, mode="global")
    if result["success"]:
        print(f"Score: {result['score']}")
        print(f"Alignment:\n{result['alignment']}\n")

    print("Local Alignment:")
    result = pairwise_align(seq1, seq2, mode="local")
    if result["success"]:
        print(f"Score: {result['score']}\n")


def example_phylogenetics() -> None:
    """Demonstrate phylogenetic analysis."""
    print("=== Phylogenetic Analysis Example ===\n")

    sequences = [
        "ATGGCCATTGTAATGGGCCGC",
        "ATGGCCATTGTTATGGGCCGC",
        "ATGGCCATTGTTAAGGGCCGC",
        "ATGGCCATTGTTTTGGGCCGC",
    ]

    labels = ["Species_A", "Species_B", "Species_C", "Species_D"]

    print("Building phylogenetic tree (Neighbor-Joining)...")
    result = build_phylogenetic_tree(sequences, method="nj", labels=labels)

    if result["success"]:
        print(f"Tree (Newick format):\n{result['tree_newick']}\n")

        print("Drawing tree:")
        tree_result = draw_tree(result["tree_newick"])
        if tree_result["success"]:
            print(tree_result["visualization"])


def example_motif_search() -> None:
    """Demonstrate motif searching."""
    print("=== Motif Search Example ===\n")

    sequence = "ATGGAATTCGCCGAATTCTTAATGGCC"
    print(f"Sequence: {sequence}\n")

    motifs = {
        "Start Codon (ATG)": "ATG",
        "EcoRI Site (GAATTC)": "GAATTC",
        "Stop Codon (TTA)": "TTA",
    }

    for name, motif in motifs.items():
        result = find_motif(sequence, motif, overlapping=True)
        if result["success"]:
            print(f"{name}:")
            print(f"  Pattern: {motif}")
            print(f"  Occurrences: {result['occurrences']}")
            print(f"  Positions: {result['positions']}\n")


def main() -> None:
    """Run all examples."""
    print("\n" + "=" * 60)
    print("BioPython MCP - Basic Usage Examples")
    print("=" * 60 + "\n")

    example_sequence_analysis()
    print("\n" + "-" * 60 + "\n")

    example_alignment()
    print("\n" + "-" * 60 + "\n")

    example_phylogenetics()
    print("\n" + "-" * 60 + "\n")

    example_motif_search()

    print("=" * 60)
    print("Examples completed!")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
