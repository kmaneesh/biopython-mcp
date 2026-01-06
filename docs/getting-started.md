# Getting Started with BioPython MCP

This guide will help you get started with the BioPython MCP server.

## Installation

### Prerequisites

- Python 3.10 or higher
- pip package manager

### Install from PyPI

```bash
pip install biopython-mcp
```

### Install from Source

```bash
git clone https://github.com/kmaneesh/biopython-mcp.git
cd biopython-mcp
pip install -e ".[dev]"
```

## Running the Server

Start the MCP server:

```bash
biopython-mcp
```

The server will start and listen for MCP protocol connections.

## Configuration

### Setting Your Email for NCBI

NCBI requires an email address for API access. You can set this as an environment variable:

```bash
export NCBI_EMAIL="your.email@example.com"
```

Or pass it as a parameter when calling database tools.

### MCP Client Configuration

Configure your MCP client (e.g., Claude Desktop) to connect to the BioPython MCP server:

```json
{
  "mcpServers": {
    "biopython": {
      "command": "biopython-mcp"
    }
  }
}
```

## Quick Example

Once connected, you can use the tools through your MCP client:

```
# Translate a DNA sequence
Tool: translate_sequence
Input: {"sequence": "ATGGCCATTGTAATGGGCCGC"}

# Calculate GC content
Tool: calculate_gc_content
Input: {"sequence": "ATGGCCATTGTAATGGGCCGC"}

# Fetch a GenBank record
Tool: fetch_genbank
Input: {"accession": "NM_000207", "email": "your@email.com"}
```

## Available Tool Categories

- **Sequence Operations**: Translation, transcription, reverse complement, GC content, motif finding
- **Alignment**: Pairwise alignment, multiple sequence alignment, scoring
- **Database Access**: GenBank, UniProt, PubMed searches
- **Structure Analysis**: PDB structure fetching and analysis
- **Phylogenetics**: Tree building, distance matrices, visualization

## Next Steps

- Read the [Tools Reference](tools-reference.md) for detailed information on each tool
- Check out the [Examples](examples.md) for common workflows
- See the main [README](../README.md) for contributing guidelines

## Troubleshooting

### Import Errors

If you encounter import errors, ensure all dependencies are installed:

```bash
pip install -r requirements.txt
```

### NCBI Connection Issues

NCBI may rate-limit requests. Ensure you:
- Provide a valid email address
- Don't make too many requests in quick succession
- Consider using NCBI API keys for higher rate limits

### Type Checking Errors

Run mypy to check for type issues:

```bash
mypy biopython_mcp/
```
