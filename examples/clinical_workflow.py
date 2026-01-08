"""Clinical bioinformatics workflow example."""

from biopython_mcp.alignment import pairwise_align
from biopython_mcp.database import search_pubmed
from biopython_mcp.sequence import calculate_gc_content, translate_sequence


def analyze_patient_mutation() -> None:
    """
    Simulate analyzing a patient's genetic variant.

    This example demonstrates a clinical workflow for analyzing
    a potential pathogenic mutation in the TP53 gene.
    """
    print("=== Clinical Mutation Analysis Workflow ===\n")

    print("Step 1: Research Background")
    print("-" * 50)
    print("Searching PubMed for TP53 mutation information...\n")

    search_result = search_pubmed(
        query="TP53 mutation clinical significance",
        max_results=3,
        email="clinician@example.com",
    )

    if search_result["success"]:
        print(f"Found {search_result['count']} relevant articles:\n")
        for i, article in enumerate(search_result["results"], 1):
            print(f"{i}. PMID: {article['pmid']}")
            print(f"   Title: {article['title']}")
            print(f"   Abstract: {article['abstract'][:150]}...\n")

    print("\nStep 2: Fetch Reference Sequence")
    print("-" * 50)
    print("Fetching TP53 reference sequence from GenBank...\n")

    reference_seq = "ATGGAGGAGCCGCAGTCAGATCCTAGCGTCGAGCCCCCTCTGAGTCAGGAAACATTTTCAGACCTATGGAAACTACTTCCTGAAAACAACGTTCTGTCCCCCTTGCCGTCCCAAGCAATGGATGATTTGATGCTGTCCCCGGACGATATTGAACAATGGTTCACTGAAGACCCAGGTCCAGATGAAGCTCCCAGAATGCCAGAGGCTGCTCCCCCCGTGGCCCCTGCACCAGCAGCTCCTACACCGGCGGCCCCTGCACCAGCCCCCTCCTGGCCCCTGTCATCTTCTGTCCCTTCCCAGAAAACCTACCAGGGCAGCTACGGTTTCCGTCTGGGCTTCTTGCATTCTGGGACAGCCAAGTCTGTGACTTGCACGTACTCCCCTGCCCTCAACAAGATGTTTTGCCAACTGGCCAAGACCTGCCCTGTGCAGCTGTGGGTTGATTCCACACCCCCGCCCGGCACCCGCGTCCGCGCCATGGCCATCTACAAGCAGTCACAGCACATGACGGAGGTTGTGAGGCGCTGCCCCCACCATGAGCGCTGCTCAGATAGCGATGGTCTGGCCCCTCCTCAGCATCTTATCCGAGTGGAAGGAAATTTGCGTGTGGAGTATTTGGATGACAGAAACACTTTTCGACATAGTGTGGTGGTGCCCTATGAGCCGCCTGAGGTTGGCTCTGACTGTACCACCATCCACTACAACTACATGTGTAACAGTTCCTGCATGGGCGGCATGAACCGGAGGCCCATCCTCACCATCATCACACTGGAAGACTCCAGTGGTAATCTACTGGGACGGAACAGCTTTGAGGTGCGTGTTTGTGCCTGTCCTGGGAGAGACCGGCGCACAGAGGAAGAGAATCTCCGCAAGAAAGGGGAGCCTCACCACGAGCTGCCCCCAGGGAGCACTAAGCGAGCACTGCCCAACAACACCAGCTCCTCTCCCCAGCCAAAGAAGAAACCACTGGATGGAGAATATTTCACCCTTCAGATCCGTGGGCGTGAGCGCTTCGAGATGTTCCGAGAGCTGAATGAGGCCTTGGAACTCAAGGATGCCCAGGCTGGGAAGGAGCCAGGGGGGAGCAGGGCTCACTCCAGCCACCTGAAGTCCAAAAAGGGTCAGTCTACCTCCCGCCATAAAAAACTCATGTTCAAGACAGAAGGGCCTGACTCAGACTGACATTCTCCACTTCTTGTTCCCCACTGACAGCCTCCCACCCCCATCTCTCCCTCCCCTGCCATTTTGGGTTTTGGGTCTTTGAACCCTTGCTTGCAATAGGTGTGCGTCAGAAGCACCCAGGACTTCCATTTGCTTTGTCCCGGGGCTCCACTGAACAAGTTGGCCTGCACTGGTGTTTTGTTGTGGGGAGGAGGATGGGGAGTAGGACATACCAGCTTAGATTTTAAGGTTTTTACTGTGAGGGATGTTTGGGAGATGTAAGAAATGTTCTTGCAGTTAAGGGTTAGTTTACAATCAGCCACATTCTAGGTAGGGGCCCACTTCACCGTACTAACCAGGGAAGCTGTCCCTCACTGTTGAATTTTCTCTAACTTCAAGGCCCATATCTGTGAAATGCTGGCATTTGCACCTACCTCACAGAGTGCATTGTGAGGGTTAATGAAATAATGTACATCTGGCCTTGAAACCACCTTTTATTACATGGGGTCTAGAACTTGACCCCCTTGAGGGTGCTTGTTCCCTCTCCCTGTTGGTCGGTGGGTTGGTAGTTTCTACAGTTGGGCAGCTGGTTAGGTAGAGGGAGTTGTCAAGTCTCTGCTGGCCCAGCCAAACCCTGTCTGACAACCTCTTGGTGAACCTTAGTACCTAAAAGGAAATCTCACCCCATCCCACACCCTGGAGGATTTCATCTCTTGTATATGATGATCTGGATCCACCAAGACTTGTTTTATGCTCAGGGTCAATTTCTTTTTTCTTTTTTTTTTTTTTTTTTCTTTTTCTTTGAGACTGGGTCTCGCTTTGTTGCCCAGGCTGGAGTGGAGTGGCGTGATCTTGGCTTACTGCAGCCTTTGCCTCCCCGGCTCGAGCAGTCCTGCCTCAGCCTCCGGAGTAGCTGGGACCACAGGTTCATGCCACCATGGCCAGCCAACTTTTGCATGTTTTGTAGAGATGGGGTCTCACAGTGTTGCCCAGGCTGGTCTCAAACTCCTGGGCTCAGGCGATCCACCTGTCTCAGCCTCCCAGAGTGCTGGGATTACAATTGTGAGCCACCACGTCCAGCTGGAAGGGTCAACATCTTTTACATTCTGCAAGCACATCTGCATTTTCACCCCACCCTTCCCCTCCTTCTCCCTTTTTATATCCCATTTTTATATCGATCTCTTATTTTACAATAAAACTTTGCTGCCA"

    print(f"Reference sequence length: {len(reference_seq)} bp\n")

    patient_seq = "ATGGAGGAGCCGCAGTCAGATCCTAGCGTCGAGCCCCCTCTGAGTCAGGAAACATTTTCAGACCTATGGAAACTACTTCCTGAAAACAACGTTCTGTCCCCCTTGCCGTCCCAAGCAATGGATGATTTGATGCTGTCCCCGGACGATATTGAACAATGGTTCACTGAAGACCCAGGTCCAGATGAAGCTCCCAGAATGCCAGAGGCTGCTCCCCCCGTGGCCCCTGCACCAGCAGCTCCTACACCGGCGGCCCCTGCACCAGCCCCCTCCTGGCCCCTGTCATCTTCTGTCCCTTCCCAGAAAACCTACCAGGGCAGCTACGGTTTCCGTCTGGGCTTCTTGCATTCTGGGACAGCCAAGTCTGTGACTTGCACGTACTCCCCTGCCCTCAACAAGATGTTTTGCCAACTGGCCAAGACCTGCCCTGTGCAGCTGTGGGTTGATTCCACACCCCCGCCCGGCACCCGCGTCCGCGCCATGGCCATCTACAAGCAGTCACAGCACATGACGGAGGTTGTGAGGCGCTGCCCCCACCATGAGCGCTGCTCAGATAGCGATGGTCTGGCCCCTCCTCAGCATCTTATCCGAGTGGAAGGAAATTTGCGTGTGGAGTATTTGGATGACAGAAACACTTTTCGACATAGTGTGGTGGTGCCCTATGAGCCGCCTGAGGTTGGCTCTGACTGTACCACCATCCACTACAACTACATGTGTAACAGTTCCTGCATGGGCGGCATGAACCGGAGGCCCATCCTCACCATCATCACACTGGAAGACTCCAGTGGTAATCTACTGGGACGGAACAGCTTTGAGGTGCGTGTTTGTGCCTGTCCTGGGAGAGACCGGCGCACAGAGGAAGAGAATCTCCGCAAGAAAGGGGAGCCTCACCACGAGCTGCCCCCAGGGAGCACTAAGCGAGCACTGCCCAACAACACCAGCTCCTCTCCCCAGCCAAAGAAGAAACCACTGGATGGAGAATATTTCACCCTTCAGATCCGTGGGCGTGAGCGCTTCGAGATGTTCCGAGAGCTGAATGAGGCCTTGGAACTCAAGGATGCCCAGGCTGGGAAGGAGCCAGGGGGGAGCAGGGCTCACTCCAGCCACCTGAAGTCCAAAAAGGGTCAGTCTACCTCCCGCCATAAAAAACTCATGTTCAAGACAGAAGGGCCTGACTCAGACTGA"

    print(f"Patient sequence length: {len(patient_seq)} bp")
    print("(Simulated patient sequence - truncated for example)\n")

    print("\nStep 3: Compare Sequences")
    print("-" * 50)
    print("Performing global alignment...\n")

    alignment_result = pairwise_align(reference_seq[:500], patient_seq[:500], mode="global")

    if alignment_result["success"]:
        print(f"Alignment Score: {alignment_result['score']}")
        print("Note: High score indicates high similarity\n")

    print("\nStep 4: Translate to Protein")
    print("-" * 50)

    print("Reference protein:")
    ref_protein = translate_sequence(reference_seq[:600], to_stop=True)
    if ref_protein["success"]:
        print(f"  {ref_protein['protein_sequence'][:50]}...")
        print(f"  Length: {ref_protein['protein_length']} amino acids\n")

    print("Patient protein:")
    pat_protein = translate_sequence(patient_seq[:600], to_stop=True)
    if pat_protein["success"]:
        print(f"  {pat_protein['protein_sequence'][:50]}...")
        print(f"  Length: {pat_protein['protein_length']} amino acids\n")

    print("\nStep 5: Analyze GC Content")
    print("-" * 50)

    ref_gc = calculate_gc_content(reference_seq[:600])
    pat_gc = calculate_gc_content(patient_seq[:600])

    if ref_gc["success"] and pat_gc["success"]:
        print(f"Reference GC%: {ref_gc['gc_content_percent']}%")
        print(f"Patient GC%: {pat_gc['gc_content_percent']}%")
        print(
            f"Difference: {abs(ref_gc['gc_content_percent'] - pat_gc['gc_content_percent']):.2f}%\n"
        )

    print("\nStep 6: Clinical Interpretation")
    print("-" * 50)
    print("Summary:")
    print("  - Sequences aligned successfully")
    print("  - Protein sequences compared")
    print("  - Further analysis would include:")
    print("    * Identifying specific mutations")
    print("    * Checking variant databases (ClinVar, COSMIC)")
    print("    * Assessing pathogenicity predictions")
    print("    * Reviewing relevant literature")
    print("    * Clinical correlation with patient phenotype\n")


def main() -> None:
    """Run the clinical workflow example."""
    print("\n" + "=" * 60)
    print("BioPython MCP - Clinical Workflow Example")
    print("=" * 60 + "\n")

    analyze_patient_mutation()

    print("=" * 60)
    print("Workflow completed!")
    print("=" * 60 + "\n")

    print("Note: This is a simplified example for demonstration.")
    print("Real clinical analysis requires additional validation,")
    print("expert interpretation, and adherence to clinical guidelines.\n")


if __name__ == "__main__":
    main()
