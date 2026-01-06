# Tools Reference

Complete reference for all BioPython MCP tools.

## Sequence Operations

### translate_sequence

Translate a DNA or RNA sequence to protein.

**Parameters:**
- `sequence` (string, required): DNA or RNA sequence
- `table` (integer, optional): Genetic code table (default: 1)
- `to_stop` (boolean, optional): Stop at first stop codon (default: false)

**Returns:**
- `success`: Operation status
- `protein_sequence`: Translated protein sequence
- `protein_length`: Length of protein
- `input_sequence`: Original input
- `input_length`: Length of input

**Example:**
```json
{
  "sequence": "ATGGCCATTGTAATGGGCCGC",
  "table": 1,
  "to_stop": false
}
```

### reverse_complement

Get the reverse complement of a DNA sequence.

**Parameters:**
- `sequence` (string, required): DNA sequence

**Returns:**
- `success`: Operation status
- `reverse_complement`: Reverse complement sequence
- `input_sequence`: Original input
- `length`: Sequence length

### transcribe_dna

Transcribe DNA to RNA or reverse transcribe RNA to DNA.

**Parameters:**
- `sequence` (string, required): DNA or RNA sequence
- `reverse` (boolean, optional): Reverse transcribe (default: false)

**Returns:**
- `success`: Operation status
- `output_sequence`: Transcribed sequence
- `operation`: Type of operation performed
- `input_sequence`: Original input

### calculate_gc_content

Calculate GC content percentage of a sequence.

**Parameters:**
- `sequence` (string, required): DNA or RNA sequence

**Returns:**
- `success`: Operation status
- `gc_content_percent`: GC percentage
- `nucleotide_counts`: Individual nucleotide counts
- `gc_count`: Total G+C count
- `at_count`: Total A+T count

### find_motif

Find all occurrences of a motif in a sequence.

**Parameters:**
- `sequence` (string, required): Sequence to search
- `motif` (string, required): Motif pattern
- `overlapping` (boolean, optional): Allow overlaps (default: true)

**Returns:**
- `success`: Operation status
- `occurrences`: Number of matches
- `positions`: List of match positions
- `motif_length`: Length of motif

## Alignment Tools

### pairwise_align

Perform pairwise sequence alignment.

**Parameters:**
- `seq1` (string, required): First sequence
- `seq2` (string, required): Second sequence
- `mode` (string, optional): 'global' or 'local' (default: 'global')
- `match_score` (float, optional): Match score (default: 2.0)
- `mismatch_score` (float, optional): Mismatch score (default: -1.0)
- `gap_open` (float, optional): Gap opening penalty (default: -2.0)
- `gap_extend` (float, optional): Gap extension penalty (default: -0.5)

**Returns:**
- `success`: Operation status
- `score`: Alignment score
- `alignment`: Formatted alignment
- `num_alignments`: Total alignments found
- `parameters`: Scoring parameters used

### multiple_sequence_alignment

Perform multiple sequence alignment.

**Parameters:**
- `sequences` (list, required): List of sequences to align
- `algorithm` (string, optional): Algorithm to use (default: 'clustalw')

**Returns:**
- `success`: Operation status
- `num_sequences`: Number of sequences
- `algorithm`: Algorithm used
- `note`: Implementation notes

### calculate_alignment_score

Calculate alignment score using substitution matrix.

**Parameters:**
- `alignment_str` (string, required): Aligned sequences
- `matrix_name` (string, optional): Matrix name (default: 'BLOSUM62')

**Returns:**
- `success`: Operation status
- `matrix_used`: Substitution matrix
- `statistics`: Match/mismatch/gap counts
- `alignment_length`: Length of alignment

## Database Access

### fetch_genbank

Fetch sequence from GenBank.

**Parameters:**
- `accession` (string, required): GenBank accession
- `email` (string, optional): Email for NCBI
- `rettype` (string, optional): Return type (default: 'gb')

**Returns:**
- `success`: Operation status
- `data`: GenBank record
- `accession`: Accession number
- `format`: Data format

### fetch_uniprot

Fetch protein from UniProt.

**Parameters:**
- `uniprot_id` (string, required): UniProt ID
- `format` (string, optional): Output format (default: 'fasta')

**Returns:**
- `success`: Operation status
- `data`: UniProt record
- `uniprot_id`: ID queried
- `format`: Data format

### search_pubmed

Search PubMed for articles.

**Parameters:**
- `query` (string, required): Search query
- `max_results` (integer, optional): Max results (default: 10)
- `email` (string, optional): Email for NCBI

**Returns:**
- `success`: Operation status
- `results`: List of articles with PMID, title, abstract
- `count`: Number of results returned
- `total_found`: Total matches

### fetch_sequence_by_id

Fetch sequence from NCBI database.

**Parameters:**
- `db` (string, required): Database name
- `seq_id` (string, required): Sequence ID
- `email` (string, optional): Email for NCBI

**Returns:**
- `success`: Operation status
- `sequence`: Sequence data
- `description`: Sequence description
- `length`: Sequence length

## Structure Analysis

### fetch_pdb_structure

Fetch protein structure from PDB.

**Parameters:**
- `pdb_id` (string, required): PDB ID
- `file_format` (string, optional): Format (default: 'pdb')

**Returns:**
- `success`: Operation status
- `file_path`: Path to downloaded file
- `pdb_id`: PDB ID
- `format`: File format

### calculate_structure_stats

Calculate statistics for PDB structure.

**Parameters:**
- `pdb_file` (string, required): Path to PDB file

**Returns:**
- `success`: Operation status
- `num_models`: Number of models
- `num_chains`: Number of chains
- `num_residues`: Total residues
- `num_atoms`: Total atoms
- `chains`: Chain information

### find_active_site

Extract active site residue information.

**Parameters:**
- `pdb_file` (string, required): Path to PDB file
- `residue_numbers` (list, required): Residue numbers
- `chain_id` (string, optional): Chain ID (default: 'A')

**Returns:**
- `success`: Operation status
- `active_site`: List of residue information
- `chain_id`: Chain analyzed

## Phylogenetics

### build_phylogenetic_tree

Build phylogenetic tree from sequences.

**Parameters:**
- `sequences` (list, required): List of aligned sequences
- `method` (string, optional): 'nj' or 'upgma' (default: 'nj')
- `labels` (list, optional): Sequence labels

**Returns:**
- `success`: Operation status
- `tree_newick`: Tree in Newick format
- `method`: Method used
- `num_sequences`: Number of sequences

### calculate_distance_matrix

Calculate pairwise distance matrix.

**Parameters:**
- `sequences` (list, required): List of aligned sequences
- `model` (string, optional): Distance model (default: 'identity')
- `labels` (list, optional): Sequence labels

**Returns:**
- `success`: Operation status
- `distance_matrix`: Distance matrix
- `model`: Model used
- `labels`: Sequence labels

### draw_tree

Visualize phylogenetic tree.

**Parameters:**
- `tree_newick` (string, required): Tree in Newick format
- `output_format` (string, optional): Format (default: 'ascii')

**Returns:**
- `success`: Operation status
- `visualization`: Tree visualization
- `num_terminals`: Number of leaf nodes
