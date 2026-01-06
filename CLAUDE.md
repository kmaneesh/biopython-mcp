# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Model Context Protocol (MCP) server that exposes BioPython library capabilities as tools for AI assistants. It allows AI models to perform bioinformatics operations like sequence analysis, alignment, database access, structural analysis, and phylogenetics.

## Development Commands

### Setup
```bash
pip install -e ".[dev]"
```

### Running the Server
```bash
biopython-mcp
# Or directly:
python -m src.server
```

### Testing
```bash
# Run all tests with coverage
pytest

# Run specific test file
pytest tests/test_sequence.py

# Run specific test class or function
pytest tests/test_sequence.py::TestTranslateSequence
pytest tests/test_sequence.py::TestTranslateSequence::test_translate_simple_dna
```

### Code Quality
```bash
# Format code
black src/ tests/

# Lint code
ruff src/ tests/

# Type checking
mypy src/
```

## Architecture

### Tool Registration Pattern

The server uses FastMCP to expose BioPython functions as MCP tools. All tool functions follow this pattern:

1. **Tool modules** (`src/sequence.py`, `src/alignment.py`, etc.) contain individual tool functions
2. **Each tool function** returns a dictionary with `{"success": bool, ...}` format
3. **Central registration** in `src/server.py` imports and registers all tools with `mcp.tool()`

To add a new tool:
1. Create the function in the appropriate module (or create a new module)
2. Ensure it returns a dict with `success` field
3. Import and register it in `src/server.py` using `mcp.tool()(your_function)`

### Error Handling Convention

All tool functions use try-except blocks and return error information in the response dict:

```python
try:
    # Tool logic here
    return {"success": True, "result": ...}
except Exception as e:
    return {"success": False, "error": str(e)}
```

### Validation Layer

Common validation functions in `src/utils.py` are used across modules:
- `validate_sequence()` - validates and cleans biological sequences
- `parse_fasta()` / `format_fasta()` - FASTA format handling
- `calculate_molecular_weight()` - molecular weight calculations

### Module Organization

- `src/sequence.py` - DNA/RNA/protein sequence operations (translate, transcribe, GC content, motif finding)
- `src/alignment.py` - Sequence alignment tools (pairwise, MSA, scoring)
- `src/database.py` - External database access (GenBank, UniProt, PubMed via Bio.Entrez)
- `src/structure.py` - Protein structure analysis (PDB fetching, structure stats, active sites)
- `src/phylo.py` - Phylogenetic analysis (tree building, distance matrices)
- `src/utils.py` - Shared utility functions

## Important Notes

### NCBI Database Access

Functions in `src/database.py` require an email address for NCBI Entrez. The default is `"user@example.com"` but users should provide their actual email. NCBI rate-limits apply.

### Multiple Sequence Alignment Limitation

The `multiple_sequence_alignment()` function in `src/alignment.py` is a placeholder. Full implementation requires external tools (MUSCLE, Clustal Omega) which are not currently integrated.

### PDB Structure Files

`fetch_pdb_structure()` downloads files to the current directory (`.`). Consider the file location when using structure tools.

### BioPython Version Compatibility

The project requires `biopython>=1.81`. Some APIs may differ in older versions.
