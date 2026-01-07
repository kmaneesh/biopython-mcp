# BioPython MCP Server

[![CI](https://github.com/kmaneesh/biopython-mcp/actions/workflows/ci.yml/badge.svg)](https://github.com/kmaneesh/biopython-mcp/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/kmaneesh/biopython-mcp/branch/main/graph/badge.svg)](https://codecov.io/gh/kmaneesh/biopython-mcp)
[![PyPI version](https://img.shields.io/pypi/v/biopython-mcp.svg)](https://pypi.org/project/biopython-mcp/)
[![PyPI downloads](https://img.shields.io/pypi/dm/biopython-mcp.svg)](https://pypi.org/project/biopython-mcp/)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

A Model Context Protocol (MCP) server that provides comprehensive BioPython capabilities for biological sequence analysis, alignment, database access, and structural bioinformatics.

## Overview

BioPython MCP bridges the powerful BioPython library with MCP-enabled applications like Claude Desktop, allowing seamless integration of bioinformatics tools into AI-assisted workflows. This enables researchers, clinicians, and developers to perform complex biological analyses through natural language interfaces.

## Motivation

Bioinformatics workflows often require switching between multiple tools and writing custom scripts. BioPython MCP simplifies this by:

- **Unified Interface**: Access BioPython's capabilities through a standardized MCP protocol
- **AI Integration**: Combine computational biology with AI-powered analysis and interpretation
- **Workflow Automation**: Chain complex bioinformatics tasks through conversational interfaces
- **Accessibility**: Make advanced bioinformatics tools available to non-programmers

## Features

- **Sequence Operations**
  - DNA/RNA translation and transcription
  - Reverse complement calculation
  - GC content analysis
  - Motif finding and pattern matching

- **Sequence Alignment**
  - Pairwise global and local alignment
  - Multiple sequence alignment support
  - Alignment scoring with substitution matrices

- **Database Access**
  - GenBank sequence retrieval
  - UniProt protein data access
  - PubMed literature search
  - NCBI database queries

- **Protein Structure Analysis**
  - PDB structure fetching and parsing
  - Structure statistics calculation
  - Active site residue analysis

- **Phylogenetics**
  - Phylogenetic tree construction (NJ, UPGMA)
  - Distance matrix calculation
  - Tree visualization

## Installation

### Requirements

- Python 3.10 or higher
- pip or [uv](https://docs.astral.sh/uv/) package manager

### Quick Install with uvx (Recommended)

The fastest way to run BioPython MCP without installation:

```bash
uvx biopython-mcp
```

Or run from source:

```bash
git clone https://github.com/kmaneesh/biopython-mcp.git
cd biopython-mcp
uvx --from . biopython-mcp
```

### Install from PyPI

```bash
pip install biopython-mcp
```

### Install from Source with uv

```bash
git clone https://github.com/kmaneesh/biopython-mcp.git
cd biopython-mcp
uv venv --python 3.10
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -e ".[dev]"
```

### Install from Source with pip

```bash
git clone https://github.com/kmaneesh/biopython-mcp.git
cd biopython-mcp
pip install -e ".[dev]"
```

### Development Installation

For contributing or development:

```bash
git clone https://github.com/kmaneesh/biopython-mcp.git
cd biopython-mcp
uv venv --python 3.10
source .venv/bin/activate
uv pip install -e ".[dev]"
pre-commit install
```

## Quick Start

### Running the Server

Start the MCP server:

```bash
# With uvx (no installation needed)
uvx biopython-mcp

# Or if installed
biopython-mcp
```

### Configuration for Claude Desktop

Add to your Claude Desktop configuration file:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

**Using uvx (recommended):**
```json
{
  "mcpServers": {
    "biopython": {
      "command": "uvx",
      "args": ["biopython-mcp"],
      "env": {
        "NCBI_EMAIL": "you@example.com",
        "NCBI_API_KEY": "your_ncbi_api_key"
      }
    }
  }
}
```

**Using installed package:**
```json
{
  "mcpServers": {
    "biopython": {
      "command": "biopython-mcp",
      "env": {
        "NCBI_EMAIL": "you@example.com",
        "NCBI_API_KEY": "your_ncbi_api_key"
      }
    }
  }
}
```

**Using local development version:**
```json
{
  "mcpServers": {
    "biopython": {
      "command": "uvx",
      "args": ["--from", "/path/to/biopython-mcp", "biopython-mcp"],
      "env": {
        "NCBI_EMAIL": "you@example.com",
        "NCBI_API_KEY": "your_ncbi_api_key"
      }
    }
  }
}
```

### Basic Usage Example

Once configured, you can use BioPython tools through Claude Desktop:

```
User: Translate the DNA sequence ATGGCCATTGTAATGGGCCGC to protein

Claude: [Uses translate_sequence tool]
Result: MAIVMGR (7 amino acids)

User: What's the GC content of this sequence?

Claude: [Uses calculate_gc_content tool]
Result: 57.14% GC content
```

## Available Tools

### Sequence Operations

| Tool | Description |
|------|-------------|
| `translate_sequence` | Translate DNA/RNA to protein |
| `reverse_complement` | Get reverse complement of DNA |
| `transcribe_dna` | Transcribe DNA to RNA |
| `calculate_gc_content` | Calculate GC percentage |
| `find_motif` | Find sequence motifs |

### Alignment

| Tool | Description |
|------|-------------|
| `pairwise_align` | Align two sequences |
| `multiple_sequence_alignment` | Align multiple sequences |
| `calculate_alignment_score` | Score alignments |

### Database Access

| Tool | Description |
|------|-------------|
| `fetch_genbank` | Retrieve GenBank records |
| `fetch_uniprot` | Retrieve UniProt entries |
| `search_pubmed` | Search PubMed literature |
| `fetch_sequence_by_id` | Get sequences by ID |

### Structure Analysis

| Tool | Description |
|------|-------------|
| `fetch_pdb_structure` | Download PDB structures |
| `calculate_structure_stats` | Analyze structure statistics |
| `find_active_site` | Extract active site info |

### Phylogenetics

| Tool | Description |
|------|-------------|
| `build_phylogenetic_tree` | Build phylogenetic trees |
| `calculate_distance_matrix` | Compute distance matrices |
| `draw_tree` | Visualize trees |

See the [Tools Reference](docs/tools-reference.md) for detailed documentation.

## Configuration Options

### Environment Variables

- `NCBI_EMAIL`: Email address for NCBI Entrez queries (recommended)
- `NCBI_API_KEY`: API key for higher NCBI rate limits (optional)

### Setting Environment Variables

```bash
export NCBI_EMAIL="your.email@example.com"
export NCBI_API_KEY="your_api_key_here"
```

## Examples

### Analyze a Gene Sequence

```python
# 1. Fetch from GenBank
fetch_genbank(accession="NM_000207", email="user@example.com")

# 2. Calculate GC content
calculate_gc_content(sequence="ATGGCC...")

# 3. Translate to protein
translate_sequence(sequence="ATGGCC...")

# 4. Find start codons
find_motif(sequence="ATGGCC...", motif="ATG")
```

### Compare Sequences

```python
# Perform global alignment
pairwise_align(
    seq1="ATGGCCATTGTAATGGGCCGC",
    seq2="ATGGCCATTGTTATGGGCCGC",
    mode="global"
)
```

### Build Phylogenetic Tree

```python
# Build tree from aligned sequences
build_phylogenetic_tree(
    sequences=["ATGGCC...", "ATGGCT...", "ATGGCA..."],
    method="nj",
    labels=["Species_A", "Species_B", "Species_C"]
)
```

See [examples/](examples/) for complete workflow examples.

## Documentation

- [Getting Started Guide](docs/getting-started.md)
- [Tools Reference](docs/tools-reference.md)
- [Usage Examples](docs/examples.md)
- [API Documentation](docs/)

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Development Setup

1. Fork the repository
2. Clone your fork: `git clone https://github.com/yourusername/biopython-mcp.git`
3. Install development dependencies: `pip install -e ".[dev]"`
4. Install pre-commit hooks: `pre-commit install`
5. Create a feature branch: `git checkout -b feature-name`
6. Make your changes and commit
7. Run tests: `pytest`
8. Push and create a pull request

### Code Quality

We use:
- **Black** for code formatting
- **Ruff** for linting
- **mypy** for type checking
- **pytest** for testing
- **pre-commit** for automated checks

## Testing

Run tests:

```bash
pytest
```

Run tests with coverage:

```bash
pytest --cov=biopython_mcp --cov-report=term-missing
```

Generate coverage reports (HTML and XML):

```bash
pytest --cov=biopython_mcp --cov-report=html --cov-report=xml --cov-report=term-missing
```

View HTML coverage report:

```bash
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
start htmlcov/index.html  # Windows
```

Run type checking:

```bash
mypy biopython_mcp/
```

### CI/CD Coverage

The project uses GitHub Actions for continuous integration with automatic coverage reporting to [Codecov](https://codecov.io/gh/kmaneesh/biopython-mcp).

Coverage is automatically uploaded when:
- Tests run on Ubuntu with Python 3.11
- Pull requests are created or updated
- Commits are pushed to `main` or `develop` branches

**Note for Contributors**: Coverage reports are publicly available. The CI workflow uses the `CODECOV_TOKEN` secret for authenticated uploads. Repository maintainers should configure this secret in GitHub repository settings.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Citation

If you use BioPython MCP in your research, please cite:

```bibtex
@software{biopython_mcp,
  title = {BioPython MCP: Model Context Protocol Server for BioPython},
  author = {BioPython MCP Contributors},
  year = {2026},
  url = {https://github.com/kmaneesh/biopython-mcp}
}
```

## Acknowledgments

- Built on the excellent [BioPython](https://biopython.org/) library
- Uses [FastMCP](https://github.com/jlowin/fastmcp) for MCP implementation
- Inspired by the [Model Context Protocol](https://modelcontextprotocol.io/)

## Support

- **Issues**: [GitHub Issues](https://github.com/kmaneesh/biopython-mcp/issues)
- **Discussions**: [GitHub Discussions](https://github.com/kmaneesh/biopython-mcp/discussions)
- **Email**: [Contact maintainers](mailto:maintainers@example.com)

## Roadmap

- [ ] Add support for protein secondary structure prediction
- [ ] Implement BLAST search integration
- [ ] Add sequence feature annotation tools
- [ ] Support for custom HMM profiles
- [ ] Interactive structure visualization
- [ ] Batch processing capabilities
- [ ] REST API wrapper

## Related Projects

- [BioPython](https://biopython.org/) - The core library
- [Model Context Protocol](https://modelcontextprotocol.io/) - The MCP specification
- [FastMCP](https://github.com/jlowin/fastmcp) - MCP framework for Python

---

**Made with BioPython and MCP**
