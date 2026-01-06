"""Main MCP server for BioPython tools."""

from fastmcp import FastMCP

# Import all tool modules
from biopython_mcp import alignment, database, phylo, sequence, structure

# Initialize FastMCP server
mcp = FastMCP("biopython-mcp")

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
