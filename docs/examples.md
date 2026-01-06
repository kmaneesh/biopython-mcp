# Examples

Common workflows and use cases for BioPython MCP.

## Basic Sequence Analysis

### Analyze a DNA Sequence

```
1. Calculate GC content
   Tool: calculate_gc_content
   Input: {"sequence": "ATGGCCATTGTAATGGGCCGC"}

2. Find start codons
   Tool: find_motif
   Input: {"sequence": "ATGGCCATTGTAATGGGCCGC", "motif": "ATG"}

3. Translate to protein
   Tool: translate_sequence
   Input: {"sequence": "ATGGCCATTGTAATGGGCCGC"}
```

## Working with Public Databases

### Fetch and Analyze a Gene

```
1. Fetch from GenBank
   Tool: fetch_genbank
   Input: {
     "accession": "NM_000207",
     "email": "your@email.com"
   }

2. Extract sequence from the result and translate
   Tool: translate_sequence
   Input: {"sequence": "<sequence from step 1>"}
```

### Search PubMed for Research

```
Tool: search_pubmed
Input: {
  "query": "BRCA1 mutation cancer",
  "max_results": 5,
  "email": "your@email.com"
}
```

## Sequence Alignment Workflows

### Compare Two Sequences

```
1. Global alignment
   Tool: pairwise_align
   Input: {
     "seq1": "ATGGCCATTGTAATGGGCCGC",
     "seq2": "ATGGCCATTGTTATGGGCCGC",
     "mode": "global"
   }

2. Local alignment for finding similar regions
   Tool: pairwise_align
   Input: {
     "seq1": "ATGGCCATTGTAATGGGCCGC",
     "seq2": "ATGGCCATTGTTATGGGCCGC",
     "mode": "local"
   }
```

## Protein Structure Analysis

### Analyze PDB Structure

```
1. Fetch structure
   Tool: fetch_pdb_structure
   Input: {
     "pdb_id": "1ABC",
     "file_format": "pdb"
   }

2. Calculate statistics
   Tool: calculate_structure_stats
   Input: {"pdb_file": "<path from step 1>"}

3. Analyze active site
   Tool: find_active_site
   Input: {
     "pdb_file": "<path from step 1>",
     "residue_numbers": [25, 50, 75],
     "chain_id": "A"
   }
```

## Phylogenetic Analysis

### Build Phylogenetic Tree

```
1. Prepare aligned sequences
   sequences = [
     "ATGGCCATTGTAATGGGCCGC",
     "ATGGCCATTGTTATGGGCCGC",
     "ATGGCCATTGTTAAGGGCCGC"
   ]

2. Build tree
   Tool: build_phylogenetic_tree
   Input: {
     "sequences": sequences,
     "method": "nj",
     "labels": ["Species_A", "Species_B", "Species_C"]
   }

3. Visualize tree
   Tool: draw_tree
   Input: {
     "tree_newick": "<newick from step 2>",
     "output_format": "ascii"
   }
```

### Calculate Evolutionary Distances

```
Tool: calculate_distance_matrix
Input: {
  "sequences": [
    "ATGGCCATTGTAATGGGCCGC",
    "ATGGCCATTGTTATGGGCCGC",
    "ATGGCCATTGTTAAGGGCCGC"
  ],
  "model": "identity",
  "labels": ["Seq1", "Seq2", "Seq3"]
}
```

## Clinical Workflow Example

### Analyze Patient Sample

```
1. Search for gene information
   Tool: search_pubmed
   Input: {
     "query": "TP53 mutation clinical significance",
     "max_results": 10
   }

2. Fetch reference sequence
   Tool: fetch_genbank
   Input: {
     "accession": "NM_000546",
     "email": "clinician@hospital.com"
   }

3. Compare patient sequence to reference
   Tool: pairwise_align
   Input: {
     "seq1": "<reference from step 2>",
     "seq2": "<patient sequence>",
     "mode": "global"
   }

4. Translate both sequences
   Tool: translate_sequence
   Input: {"sequence": "<reference sequence>"}
   
   Tool: translate_sequence
   Input: {"sequence": "<patient sequence>"}

5. Identify mutations by comparing protein sequences
```

## Motif Analysis

### Find All Restriction Sites

```
# Find EcoRI sites (GAATTC)
Tool: find_motif
Input: {
  "sequence": "ATGGAATTCGCCGAATTCTTA",
  "motif": "GAATTC",
  "overlapping": false
}
```

### Find Promoter Elements

```
# Find TATA box
Tool: find_motif
Input: {
  "sequence": "<promoter sequence>",
  "motif": "TATAAA",
  "overlapping": true
}
```

## Working with UniProt

### Fetch and Analyze Protein

```
1. Fetch protein sequence
   Tool: fetch_uniprot
   Input: {
     "uniprot_id": "P04637",
     "format": "fasta"
   }

2. Calculate properties
   Tool: calculate_gc_content
   Input: {"sequence": "<extracted sequence>"}
```

## Batch Processing

### Analyze Multiple Sequences

```
For each sequence in batch:
  1. Calculate GC content
  2. Find motifs
  3. Translate to protein
  4. Compare to reference

Use the tools in sequence for each sample.
```

## Tips

- Always validate sequences before complex operations
- Use appropriate email addresses for NCBI queries
- Cache PDB structures locally to avoid repeated downloads
- Consider rate limits when making multiple database queries
- Use local alignment for finding conserved regions
- Use global alignment for full sequence comparison
