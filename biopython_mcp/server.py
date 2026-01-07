"""Main MCP server for BioPython tools."""

import os
import sys

from Bio import Entrez
from fastmcp import FastMCP

# Import all tool modules
from biopython_mcp import alignment, database, phylo, sequence, structure
from biopython_mcp.modules import pubmed

# Initialize FastMCP server
mcp = FastMCP("biopython-mcp")

# Configure Entrez with environment variables
_email = os.environ.get("NCBI_EMAIL", "user@example.com")
_api_key = os.environ.get("NCBI_API_KEY")

Entrez.email = _email  # type: ignore[assignment]
if _api_key:
    Entrez.api_key = _api_key  # type: ignore[assignment]

rate_limit_msg = "10 req/sec (with API key)" if _api_key else "3 req/sec (no API key)"
print(f"Entrez configured: {_email}, Rate limit: {rate_limit_msg}", file=sys.stderr)

# Register sequence tools
mcp.tool()(sequence.translate_sequence)
mcp.tool()(sequence.reverse_complement)
mcp.tool()(sequence.transcribe_dna)
mcp.tool()(sequence.calculate_gc_content)
mcp.tool()(sequence.find_motif)

# Register alignment tools
mcp.tool()(alignment.pairwise_align)
mcp.tool()(alignment.multiple_sequence_alignment)
mcp.tool()(alignment.calculate_alignment_score)

# Register database tools
mcp.tool()(database.fetch_genbank)
mcp.tool()(database.fetch_uniprot)
mcp.tool()(database.search_pubmed)
mcp.tool()(database.fetch_sequence_by_id)

# Register Entrez core tools
mcp.tool()(database.entrez_info)
mcp.tool()(database.entrez_search)
mcp.tool()(database.entrez_fetch)
mcp.tool()(database.entrez_summary)

# Register clinical genomics tools
mcp.tool()(database.clinvar_variant_lookup)
mcp.tool()(database.gene_info_fetch)
mcp.tool()(database.pubmed_search)
mcp.tool()(database.variant_literature_link)

# Register Phase 3 advanced tools
mcp.tool()(database.entrez_link)
mcp.tool()(database.clear_entrez_cache)

# Register PubMed Central full-text tools
mcp.tool()(pubmed.pubmed_fetch)
mcp.tool()(pubmed.get_pmc_url)
mcp.tool()(pubmed.get_doi_url)
mcp.tool()(pubmed.pubmed_review)

# Register structure tools
mcp.tool()(structure.fetch_pdb_structure)
mcp.tool()(structure.calculate_structure_stats)
mcp.tool()(structure.find_active_site)

# Register phylogenetics tools
mcp.tool()(phylo.build_phylogenetic_tree)
mcp.tool()(phylo.calculate_distance_matrix)
mcp.tool()(phylo.draw_tree)


def main() -> int:
    """Run the MCP server."""
    import sys

    try:
        mcp.run()
        return 0
    except KeyboardInterrupt:
        print("\nServer stopped by user")
        return 0
    except Exception as e:
        print(f"Error running server: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    import sys

    sys.exit(main())
