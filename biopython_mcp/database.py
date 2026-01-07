"""Database access tools for NCBI, UniProt, and other biological databases.

NCBI Entrez System
------------------
The Entrez system provides programmatic access to NCBI databases including:

- **pubmed**: PubMed citations and abstracts
- **nucleotide**: GenBank nucleotide sequences
- **protein**: Protein sequences
- **gene**: Gene records with genomic information
- **clinvar**: ClinVar variant-phenotype relationships
- **snp**: dbSNP genetic variations
- **structure**: 3D molecular structures (PDB)
- **taxonomy**: Taxonomic information

Query Syntax Examples
---------------------
Basic searches:
    "BRCA1[Gene]" - Search by gene symbol
    "breast cancer" - Free text search
    "2024/01/01:2024/12/31[PDAT]" - Publication date range

Boolean operators:
    "BRCA1 AND breast cancer" - Both terms required
    "diabetes OR obesity" - Either term matches
    "cancer NOT lung" - Exclude lung cancer

Field searches:
    "Smith J[Author]" - Search by author
    "Nature[Journal]" - Search by journal name
    "review[Publication Type]" - Filter by publication type

Rate Limiting
-------------
NCBI enforces rate limits on API requests:
- **Default**: 3 requests/second (no API key)
- **With API key**: 10 requests/second
- Set `NCBI_API_KEY` environment variable for higher limits
- API keys available at: https://www.ncbi.nlm.nih.gov/account/settings/

Environment Variables
---------------------
- **NCBI_EMAIL**: Your email address (required by NCBI)
- **NCBI_API_KEY**: Your API key (optional, for higher rate limits)

Example:
    export NCBI_EMAIL="your.email@example.com"
    export NCBI_API_KEY="your_api_key_here"
"""

from typing import Any

from Bio import Entrez, SeqIO

from biopython_mcp.utils import entrez_rate_limit, format_entrez_error, parse_ids


def fetch_genbank(
    accession: str, email: str = "user@example.com", rettype: str = "gb"
) -> dict[str, Any]:
    """
    Fetch a sequence from GenBank by accession number.

    Args:
        accession: GenBank accession number
        email: Email address for Entrez (required by NCBI)
        rettype: Return type - 'gb' for GenBank, 'fasta' for FASTA (default: 'gb')

    Returns:
        Dictionary containing the sequence record and metadata
    """
    try:
        Entrez.email = email  # type: ignore[assignment]

        handle = Entrez.efetch(db="nucleotide", id=accession, rettype=rettype, retmode="text")
        record_text = handle.read()
        handle.close()

        normalized = "".join(record_text.split()).lower()
        if normalized.startswith("error:") or "failedtounderstandid" in normalized:
            return {
                "success": False,
                "error": record_text.strip() or "NCBI returned an error response",
                "accession": accession,
                "format": rettype,
            }

        return {
            "success": True,
            "accession": accession,
            "format": rettype,
            "data": record_text,
            "length": len(record_text),
        }
    except Exception as e:
        return {"success": False, "error": str(e), "accession": accession}


def fetch_uniprot(uniprot_id: str, format: str = "fasta") -> dict[str, Any]:
    """
    Fetch a protein sequence from UniProt.

    Args:
        uniprot_id: UniProt accession or ID
        format: Output format - 'fasta', 'txt', 'xml' (default: 'fasta')

    Returns:
        Dictionary containing the UniProt record
    """
    try:
        import httpx

        url = f"https://rest.uniprot.org/uniprotkb/{uniprot_id}.{format}"

        response = httpx.get(url, timeout=30.0)
        response.raise_for_status()

        return {
            "success": True,
            "uniprot_id": uniprot_id,
            "format": format,
            "data": response.text,
            "length": len(response.text),
        }
    except Exception as e:
        return {"success": False, "error": str(e), "uniprot_id": uniprot_id}


def search_pubmed(
    query: str, max_results: int = 10, email: str = "user@example.com"
) -> dict[str, Any]:
    """
    Search PubMed for scientific articles.

    Args:
        query: Search query string
        max_results: Maximum number of results to return (default: 10)
        email: Email address for Entrez (required by NCBI)

    Returns:
        Dictionary containing search results with PMIDs and article information
    """
    try:
        Entrez.email = email  # type: ignore[assignment]

        search_handle = Entrez.esearch(db="pubmed", term=query, retmax=max_results)
        search_results = Entrez.read(search_handle)
        search_handle.close()

        pmids = search_results["IdList"]

        if not pmids:
            return {
                "success": True,
                "query": query,
                "count": 0,
                "results": [],
            }

        fetch_handle = Entrez.efetch(db="pubmed", id=pmids, rettype="abstract", retmode="xml")
        articles = Entrez.read(fetch_handle)
        fetch_handle.close()

        results = []
        for article in articles["PubmedArticle"]:
            medline = article["MedlineCitation"]
            pmid = str(medline["PMID"])
            article_data = medline["Article"]

            title = article_data.get("ArticleTitle", "No title")
            abstract = article_data.get("Abstract", {}).get("AbstractText", ["No abstract"])[0]

            results.append({"pmid": pmid, "title": str(title), "abstract": str(abstract)[:500]})

        return {
            "success": True,
            "query": query,
            "count": len(results),
            "total_found": int(search_results["Count"]),
            "results": results,
        }
    except Exception as e:
        return {"success": False, "error": str(e), "query": query}


def fetch_sequence_by_id(db: str, seq_id: str, email: str = "user@example.com") -> dict[str, Any]:
    """
    Fetch a sequence from NCBI database by ID.

    Args:
        db: Database name ('nucleotide', 'protein', etc.)
        seq_id: Sequence identifier
        email: Email address for Entrez (required by NCBI)

    Returns:
        Dictionary containing sequence information
    """
    try:
        Entrez.email = email  # type: ignore[assignment]

        handle = Entrez.efetch(db=db, id=seq_id, rettype="fasta", retmode="text")
        record = SeqIO.read(handle, "fasta")
        handle.close()

        return {
            "success": True,
            "database": db,
            "id": seq_id,
            "description": record.description,
            "sequence": str(record.seq),
            "length": len(record.seq),
        }
    except Exception as e:
        return {"success": False, "error": str(e), "database": db, "id": seq_id}


# Core Entrez tools
def entrez_info(database: str = "") -> dict[str, Any]:
    """
    Get information about NCBI Entrez databases.

    Args:
        database: Specific database name (empty string for list of all databases)

    Returns:
        Dictionary containing database information:
        - If database="": List of all available databases with count
        - If database specified: Detailed info including description, record count,
          searchable fields, and available links

    Examples:
        >>> entrez_info()  # List all databases
        >>> entrez_info("pubmed")  # Get PubMed database details
        >>> entrez_info("gene")  # Get Gene database details
    """
    try:
        with entrez_rate_limit():
            handle = Entrez.einfo(db=database if database else None)
            result = Entrez.read(handle)
            handle.close()

        if not database:
            # Return list of all databases
            return {
                "success": True,
                "databases": result["DbList"],
                "count": len(result["DbList"]),
            }
        else:
            # Return detailed info about specific database
            db_info = result["DbInfo"]
            return {
                "success": True,
                "database": database,
                "description": db_info.get("Description", ""),
                "record_count": int(db_info.get("Count", 0)),
                "last_update": db_info.get("LastUpdate", ""),
                "fields": [f["Name"] for f in db_info.get("FieldList", [])],
                "links": [link["Name"] for link in db_info.get("LinkList", [])],
            }
    except Exception as e:
        return format_entrez_error(e, {"database": database})


def entrez_search(
    database: str,
    query: str,
    max_results: int = 20,
    sort: str = "relevance",
    use_cache: bool = True,
) -> dict[str, Any]:
    """
    Search any NCBI Entrez database using query syntax.

    Args:
        database: Database to search (e.g., 'pubmed', 'nucleotide', 'gene', 'clinvar')
        query: Search query using Entrez syntax (see module docstring for examples)
        max_results: Maximum number of results to return (default: 20, max: 10000)
        sort: Sort order - 'relevance', 'pub_date', 'Author', etc. (default: 'relevance')
        use_cache: Whether to use cached results (default: True, TTL: 1 hour)

    Returns:
        Dictionary containing:
        - ids: List of matching record IDs
        - count: Number of IDs returned
        - total_found: Total number of matches in database
        - query: Original query string
        - database: Database searched
        - cached: Whether result was from cache (if use_cache=True)

    Examples:
        >>> entrez_search("pubmed", "BRCA1 AND breast cancer", max_results=10)
        >>> entrez_search("gene", "BRCA1[Gene Name] AND Homo sapiens[Organism]")
        >>> entrez_search("nucleotide", "Homo sapiens[Organism]", max_results=5)
        >>> entrez_search("clinvar", "BRCA1[Gene] AND Pathogenic[Clinical Significance]")

    Notes:
        - Uses NCBI Entrez query syntax with field tags and Boolean operators
        - Rate limited to 3 req/sec (or 10 req/sec with API key)
        - See module docstring for comprehensive query syntax examples
        - Cached results have 1 hour TTL to balance freshness and API usage
    """
    try:
        from biopython_mcp.utils import get_cached_result, set_cached_result

        # Check cache if enabled
        cache_params = {
            "query": query,
            "max_results": max_results,
            "sort": sort,
        }

        if use_cache:
            cached = get_cached_result(database, "search", cache_params, ttl=3600)
            if cached:
                cached["cached"] = True
                return cached

        # Perform search
        with entrez_rate_limit():
            handle = Entrez.esearch(
                db=database, term=query, retmax=min(max_results, 10000), sort=sort
            )
            result = Entrez.read(handle)
            handle.close()

        response = {
            "success": True,
            "database": database,
            "query": query,
            "ids": result["IdList"],
            "count": len(result["IdList"]),
            "total_found": int(result["Count"]),
            "sort": sort,
            "cached": False,
        }

        # Cache successful result
        if use_cache:
            set_cached_result(database, "search", cache_params, response)

        return response
    except Exception as e:
        return format_entrez_error(e, {"database": database, "query": query})


def entrez_fetch(
    database: str,
    ids: str | list[str],
    rettype: str = "xml",
    retmode: str = "xml",
    use_cache: bool = True,
) -> dict[str, Any]:
    """
    Fetch full records from NCBI Entrez by UID.

    Args:
        database: Database name (e.g., 'pubmed', 'nucleotide', 'gene', 'protein')
        ids: Single ID, comma-separated string, or list of IDs
        rettype: Return type - 'xml', 'gb', 'fasta', 'abstract', etc. (default: 'xml')
        retmode: Return mode - 'xml', 'text', 'json' (default: 'xml')
        use_cache: Whether to use cached results (default: True, TTL: 7 days)

    Returns:
        Dictionary containing:
        - data: Raw data in requested format (parsed if XML, raw text otherwise)
        - ids: List of IDs fetched
        - count: Number of records retrieved
        - format: Return type/mode used
        - database: Database queried
        - cached: Whether result was from cache (if use_cache=True)

    Examples:
        >>> entrez_fetch("pubmed", "12345678", rettype="abstract", retmode="xml")
        >>> entrez_fetch("nucleotide", ["NM_000207", "NM_001127"], rettype="fasta", retmode="text")
        >>> entrez_fetch("gene", "672", rettype="xml")
        >>> entrez_fetch("protein", "NP_000198.1", rettype="fasta", retmode="text")

    Notes:
        - For >100 IDs, consider batching to avoid timeouts
        - Valid rettype/retmode combinations depend on database
        - XML mode returns parsed Python dict/list structure
        - Text mode returns raw string data
        - Rate limited to 3 req/sec (or 10 req/sec with API key)
        - Cached results have 7 day TTL since record data is relatively static
    """
    try:
        from biopython_mcp.utils import get_cached_result, set_cached_result

        id_list = parse_ids(ids)

        if not id_list:
            return format_entrez_error(
                ValueError("No valid IDs provided"), {"database": database, "ids": ids}
            )

        # Check cache if enabled
        cache_params = {
            "ids": sorted(id_list),  # Sort for consistent cache keys
            "rettype": rettype,
            "retmode": retmode,
        }

        if use_cache:
            cached = get_cached_result(database, "fetch", cache_params, ttl=604800)  # 7 days
            if cached:
                cached["cached"] = True
                return cached

        # Perform fetch
        with entrez_rate_limit():
            handle = Entrez.efetch(db=database, id=id_list, rettype=rettype, retmode=retmode)

            # Read based on mode
            data = Entrez.read(handle) if retmode == "xml" else handle.read()

            handle.close()

        response = {
            "success": True,
            "database": database,
            "ids": id_list,
            "count": len(id_list),
            "format": f"{rettype}/{retmode}",
            "data": data,
            "cached": False,
        }

        # Cache successful result
        if use_cache:
            set_cached_result(database, "fetch", cache_params, response)

        return response
    except Exception as e:
        return format_entrez_error(e, {"database": database, "ids": str(ids)[:100]})


def entrez_summary(database: str, ids: str | list[str], use_cache: bool = True) -> dict[str, Any]:
    """
    Get document summaries (DocSums) from NCBI Entrez.

    Document summaries are lightweight alternatives to full records, containing
    key metadata without the full content. Much faster for metadata-only queries.

    Args:
        database: Database name (e.g., 'pubmed', 'gene', 'clinvar', 'nucleotide')
        ids: Single ID, comma-separated string, or list of IDs
        use_cache: Whether to use cached results (default: True, TTL: 7 days)

    Returns:
        Dictionary containing:
        - summaries: List of document summary dictionaries
        - ids: List of IDs requested
        - count: Number of summaries returned
        - database: Database queried
        - cached: Whether result was from cache (if use_cache=True)

    Examples:
        >>> entrez_summary("pubmed", "12345678")
        >>> entrez_summary("gene", ["672", "7157"])  # BRCA1, TP53
        >>> entrez_summary("clinvar", "12345")
        >>> entrez_summary("nucleotide", "NM_000207,NM_001127")

    Notes:
        - Much faster than entrez_fetch for metadata-only queries
        - Fields returned vary by database type
        - Rate limited to 3 req/sec (or 10 req/sec with API key)
        - Use this instead of fetch when you don't need full sequence/text
        - Cached results have 7 day TTL since summary data is relatively static
    """
    try:
        from biopython_mcp.utils import get_cached_result, set_cached_result

        id_list = parse_ids(ids)

        if not id_list:
            return format_entrez_error(
                ValueError("No valid IDs provided"), {"database": database, "ids": ids}
            )

        # Check cache if enabled
        cache_params = {
            "ids": sorted(id_list),  # Sort for consistent cache keys
        }

        if use_cache:
            cached = get_cached_result(database, "summary", cache_params, ttl=604800)  # 7 days
            if cached:
                cached["cached"] = True
                return cached

        # Perform summary fetch
        with entrez_rate_limit():
            handle = Entrez.esummary(db=database, id=id_list)
            result = Entrez.read(handle)
            handle.close()

        # esummary returns different formats depending on single vs multiple IDs
        # Normalize to always return a list
        summaries = result if isinstance(result, list) else [result]

        response = {
            "success": True,
            "database": database,
            "ids": id_list,
            "count": len(summaries),
            "summaries": summaries,
            "cached": False,
        }

        # Cache successful result
        if use_cache:
            set_cached_result(database, "summary", cache_params, response)

        return response
    except Exception as e:
        return format_entrez_error(e, {"database": database, "ids": str(ids)[:100]})


# Clinical Genomics Specialized Tools
def clinvar_variant_lookup(
    variant: str = "",
    gene: str = "",
    condition: str = "",
    significance: str = "",
    max_results: int = 20,
    use_cache: bool = True,
) -> dict[str, Any]:
    """
    Search ClinVar for genetic variants and their clinical interpretations.

    This specialized wrapper combines entrez_search and entrez_summary for
    convenient ClinVar queries.

    Args:
        variant: Variant notation (e.g., "rs80357906", "NM_000059.3:c.1521_1523del")
        gene: Gene symbol (e.g., "BRCA1", "TP53")
        condition: Condition/phenotype (e.g., "breast cancer", "Lynch syndrome")
        significance: Clinical significance filter:
            - "pathogenic"
            - "likely_pathogenic"
            - "benign"
            - "likely_benign"
            - "uncertain"
        max_results: Maximum results to return (default: 20)
        use_cache: Whether to use cached results (default: True)

    Returns:
        Dictionary containing:
        - variants: List of variant dictionaries with clinical information
        - count: Number of variants returned
        - total_found: Total matches in ClinVar
        - query_terms: Dictionary of search terms used
        - cached: Whether result was from cache (if use_cache=True)

    Examples:
        >>> clinvar_variant_lookup(gene="BRCA1", significance="pathogenic", max_results=5)
        >>> clinvar_variant_lookup(variant="rs80357906")
        >>> clinvar_variant_lookup(gene="TP53", condition="cancer", max_results=10)

    Notes:
        - At least one search parameter must be provided
        - Multiple parameters are combined with AND logic
        - Rate limited (3 req/sec or 10 req/sec with API key)
        - Cached results inherit TTL from underlying entrez_search and entrez_summary calls
    """
    try:
        # Build query from parameters
        query_parts = []
        if variant:
            query_parts.append(f'"{variant}"[Variant Name]')
        if gene:
            query_parts.append(f"{gene}[Gene Name]")
        if condition:
            query_parts.append(f"{condition}[Disease/Phenotype]")
        if significance:
            # Map to ClinVar terminology
            sig_map = {
                "pathogenic": "Pathogenic",
                "likely_pathogenic": "Likely pathogenic",
                "benign": "Benign",
                "likely_benign": "Likely benign",
                "uncertain": "Uncertain significance",
            }
            sig_term = sig_map.get(significance.lower(), significance)
            query_parts.append(f'"{sig_term}"[Clinical Significance]')

        if not query_parts:
            return {
                "success": False,
                "error": "At least one search parameter required (variant, gene, condition, or significance)",
                "query_terms": {},
            }

        query = " AND ".join(query_parts)

        # Search ClinVar using generic tool
        search_result = entrez_search(
            "clinvar", query, max_results=max_results, use_cache=use_cache
        )

        if not search_result["success"]:
            return search_result

        if not search_result["ids"]:
            return {
                "success": True,
                "variants": [],
                "count": 0,
                "total_found": 0,
                "query_terms": {
                    "variant": variant,
                    "gene": gene,
                    "condition": condition,
                    "significance": significance,
                },
                "query": query,
                "cached": search_result.get("cached", False),
            }

        # Get summaries using generic tool
        summary_result = entrez_summary("clinvar", search_result["ids"], use_cache=use_cache)

        if not summary_result["success"]:
            return summary_result

        # Format variants for clinical use
        variants = []
        for summary in summary_result["summaries"]:
            # Extract key clinical information
            variant_info = {
                "clinvar_id": str(summary.get("uid", "")),
                "title": str(summary.get("title", "")),
                "accession": str(summary.get("accession", "")),
                "gene_symbol": (
                    str(summary.get("genes", [{}])[0].get("symbol", ""))
                    if summary.get("genes")
                    else ""
                ),
                "variation_type": str(summary.get("obj_type", "")),
                "clinical_significance": (
                    str(summary.get("clinical_significance", {}).get("description", ""))
                    if isinstance(summary.get("clinical_significance"), dict)
                    else str(summary.get("clinical_significance", ""))
                ),
            }
            variants.append(variant_info)

        return {
            "success": True,
            "variants": variants,
            "count": len(variants),
            "total_found": search_result["total_found"],
            "query_terms": {
                "variant": variant,
                "gene": gene,
                "condition": condition,
                "significance": significance,
            },
            "query": query,
            "cached": search_result.get("cached", False) or summary_result.get("cached", False),
        }

    except Exception as e:
        return format_entrez_error(e, {"gene": gene, "variant": variant, "condition": condition})


def gene_info_fetch(
    gene_symbol: str = "",
    gene_id: str = "",
    organism: str = "Homo sapiens",
    use_cache: bool = True,
) -> dict[str, Any]:
    """
    Fetch comprehensive gene information from NCBI Gene database.

    This specialized wrapper provides easy access to gene records with
    structured output.

    Args:
        gene_symbol: Gene symbol (e.g., "BRCA1", "TP53")
        gene_id: NCBI Gene ID (e.g., "672" for BRCA1)
        organism: Organism name (default: "Homo sapiens")
        use_cache: Whether to use cached results (default: True)

    Returns:
        Dictionary containing:
        - gene_id: NCBI Gene ID
        - symbol: Official gene symbol
        - name: Full gene name
        - summary: Gene summary/description
        - organism: Organism name
        - chromosome: Chromosomal location
        - aliases: List of gene aliases
        - type: Gene type (protein-coding, ncRNA, etc.)
        - cached: Whether result was from cache (if use_cache=True)

    Examples:
        >>> gene_info_fetch(gene_symbol="BRCA1")
        >>> gene_info_fetch(gene_id="672")
        >>> gene_info_fetch(gene_symbol="Brca1", organism="Mus musculus")

    Notes:
        - Provide either gene_symbol or gene_id (gene_id takes precedence)
        - Organism filter helps disambiguate gene symbols
        - Rate limited (3 req/sec or 10 req/sec with API key)
        - Cached results inherit TTL from underlying entrez_search and entrez_summary calls
    """
    try:
        if not gene_symbol and not gene_id:
            return {
                "success": False,
                "error": "Either gene_symbol or gene_id required",
            }

        # If gene_id provided, fetch directly
        if gene_id:
            summary_result = entrez_summary("gene", gene_id, use_cache=use_cache)
            if not summary_result["success"]:
                return summary_result

            if not summary_result["summaries"]:
                return {
                    "success": False,
                    "error": f"Gene ID '{gene_id}' not found",
                    "gene_id": gene_id,
                }

            gene_summary = summary_result["summaries"][0]
            cached = summary_result.get("cached", False)
        else:
            # Search by symbol + organism
            query = f"{gene_symbol}[Gene Name] AND {organism}[Organism]"
            search_result = entrez_search("gene", query, max_results=1, use_cache=use_cache)

            if not search_result["success"] or not search_result["ids"]:
                return {
                    "success": False,
                    "error": f"Gene '{gene_symbol}' not found for {organism}",
                    "gene_symbol": gene_symbol,
                    "organism": organism,
                }

            # Get summary of first result
            summary_result = entrez_summary("gene", search_result["ids"][0], use_cache=use_cache)
            if not summary_result["success"]:
                return summary_result

            gene_summary = summary_result["summaries"][0]
            cached = search_result.get("cached", False) or summary_result.get("cached", False)

        # Extract and structure gene information
        gene_info = {
            "success": True,
            "gene_id": str(gene_summary.get("uid", "")),
            "symbol": str(gene_summary.get("name", "")),
            "name": str(gene_summary.get("description", "")),
            "summary": str(gene_summary.get("summary", "")),
            "organism": (
                str(gene_summary.get("organism", {}).get("scientificname", ""))
                if isinstance(gene_summary.get("organism"), dict)
                else str(gene_summary.get("organism", ""))
            ),
            "chromosome": str(gene_summary.get("chromosome", "")),
            "map_location": str(gene_summary.get("maplocation", "")),
            "gene_type": str(gene_summary.get("genetype", "")),
            "aliases": (
                gene_summary.get("otheraliases", "").split(", ")
                if gene_summary.get("otheraliases")
                else []
            ),
            "cached": cached,
        }

        return gene_info

    except Exception as e:
        return format_entrez_error(
            e, {"gene_symbol": gene_symbol, "gene_id": gene_id, "organism": organism}
        )


def pubmed_search(
    query: str,
    max_results: int = 10,
    sort: str = "relevance",
    year_start: int = 0,
    year_end: int = 0,
    use_cache: bool = True,
) -> dict[str, Any]:
    """
    Search PubMed with enhanced metadata extraction.

    This specialized wrapper provides enriched PubMed search results with
    structured article metadata.

    Args:
        query: PubMed search query (supports all Entrez query syntax)
        max_results: Maximum results to return (default: 10)
        sort: Sort order - "relevance", "pub_date", "first_author" (default: "relevance")
        year_start: Filter by publication year start (e.g., 2020)
        year_end: Filter by publication year end (e.g., 2024)
        use_cache: Whether to use cached results (default: True, TTL: 1 hour)

    Returns:
        Dictionary containing:
        - articles: List of article dictionaries with:
            - pmid: PubMed ID
            - title: Article title
            - abstract: Full abstract text
            - authors: List of author names
            - journal: Journal name
            - year: Publication year
            - date: Publication date
            - doi: DOI (if available)
            - pmc_id: PMC ID (if available)
        - count: Number of articles returned
        - total_found: Total matches in PubMed
        - cached: Whether result was from cache (if use_cache=True)

    Examples:
        >>> pubmed_search("BRCA1 AND breast cancer", max_results=5)
        >>> pubmed_search("Smith J[Author]", sort="pub_date")
        >>> pubmed_search("diabetes", year_start=2020, year_end=2024, max_results=20)

    Notes:
        - Uses comprehensive Entrez query syntax
        - Returns full abstracts when available
        - Rate limited (3 req/sec or 10 req/sec with API key)
        - Cached results have 1 hour TTL to balance freshness and API usage
    """
    try:
        # Add year filters to query if provided
        if year_start or year_end:
            start_year = year_start if year_start else "1900"
            end_year = year_end if year_end else "3000"
            year_query = f"{start_year}:{end_year}[PDAT]"
            query = f"({query}) AND {year_query}"

        # Search PubMed using generic tool
        search_result = entrez_search(
            "pubmed", query, max_results=max_results, sort=sort, use_cache=use_cache
        )

        if not search_result["success"]:
            return search_result

        if not search_result["ids"]:
            return {
                "success": True,
                "articles": [],
                "count": 0,
                "total_found": 0,
                "query": query,
                "cached": search_result.get("cached", False),
            }

        # Fetch article details using generic tool
        fetch_result = entrez_fetch(
            "pubmed", search_result["ids"], rettype="abstract", retmode="xml", use_cache=use_cache
        )

        if not fetch_result["success"]:
            return fetch_result

        # Extract rich metadata from articles
        articles = []
        for article_data in fetch_result["data"]["PubmedArticle"]:
            medline = article_data["MedlineCitation"]
            article_info = medline["Article"]

            # Extract authors
            author_list = article_info.get("AuthorList", [])
            authors = []
            for author in author_list:
                if "LastName" in author and "Initials" in author:
                    authors.append(f"{author['LastName']} {author['Initials']}")
                elif "CollectiveName" in author:
                    authors.append(str(author["CollectiveName"]))

            # Extract abstract
            abstract_sections = article_info.get("Abstract", {}).get("AbstractText", [])
            if abstract_sections:
                if isinstance(abstract_sections, list):
                    abstract = " ".join(str(section) for section in abstract_sections)
                else:
                    abstract = str(abstract_sections)
            else:
                abstract = "No abstract available"

            # Extract publication info
            pub_date = article_info.get("Journal", {}).get("JournalIssue", {}).get("PubDate", {})
            year = int(pub_date.get("Year", 0)) if pub_date.get("Year") else 0

            # Extract DOI and PMC ID from ArticleIdList
            doi = None
            pmc_id = None
            article_ids = article_data.get("PubmedData", {}).get("ArticleIdList", [])
            for article_id in article_ids:
                if article_id.attributes.get("IdType") == "doi":
                    doi = str(article_id)
                elif article_id.attributes.get("IdType") == "pmc":
                    pmc_id = str(article_id)

            article = {
                "pmid": str(medline["PMID"]),
                "title": str(article_info.get("ArticleTitle", "No title")),
                "abstract": abstract,
                "authors": authors,
                "journal": str(article_info.get("Journal", {}).get("Title", "")),
                "year": year,
                "date": f"{pub_date.get('Year', '')}-{pub_date.get('Month', '')}-{pub_date.get('Day', '')}".strip(
                    "-"
                ),
                "doi": doi,
                "pmc_id": pmc_id,
            }
            articles.append(article)

        return {
            "success": True,
            "articles": articles,
            "count": len(articles),
            "total_found": search_result["total_found"],
            "query": query,
            "sort": sort,
            "cached": search_result.get("cached", False) or fetch_result.get("cached", False),
        }

    except Exception as e:
        return format_entrez_error(e, {"query": query, "max_results": max_results})


def variant_literature_link(
    variant_id: str, source_db: str = "clinvar", max_results: int = 10
) -> dict[str, Any]:
    """
    Find literature (PubMed) articles linked to a specific variant.

    Uses Entrez ELink to find cross-database relationships between
    variant databases and PubMed.

    Args:
        variant_id: Variant ID (ClinVar ID or dbSNP rs number)
        source_db: Source database - "clinvar" or "snp" (default: "clinvar")
        max_results: Maximum articles to return (default: 10)

    Returns:
        Dictionary containing:
        - variant_id: Input variant ID
        - source_db: Source database used
        - linked_pmids: List of linked PubMed IDs
        - articles: List of article summaries
        - count: Number of articles found

    Examples:
        >>> variant_literature_link("12345", source_db="clinvar")
        >>> variant_literature_link("80357906", source_db="snp", max_results=5)

    Notes:
        - Not all variants have linked literature
        - Uses Entrez ELink for database cross-referencing
        - Rate limited (3 req/sec or 10 req/sec with API key)
    """
    try:
        # Validate source database
        if source_db not in ["clinvar", "snp"]:
            return {
                "success": False,
                "error": f"Invalid source_db '{source_db}'. Must be 'clinvar' or 'snp'",
                "variant_id": variant_id,
            }

        # Use Entrez.elink to find linked PubMed IDs
        with entrez_rate_limit():
            handle = Entrez.elink(dbfrom=source_db, db="pubmed", id=variant_id)
            result = Entrez.read(handle)
            handle.close()

        # Extract linked PMIDs
        linked_pmids = []
        if result and result[0].get("LinkSetDb"):
            for link_set in result[0]["LinkSetDb"]:
                if link_set.get("Link"):
                    linked_pmids = [link["Id"] for link in link_set["Link"]]
                    break

        if not linked_pmids:
            return {
                "success": True,
                "variant_id": variant_id,
                "source_db": source_db,
                "linked_pmids": [],
                "articles": [],
                "count": 0,
            }

        # Limit to max_results
        linked_pmids = linked_pmids[:max_results]

        # Get article summaries using generic tool
        summary_result = entrez_summary("pubmed", linked_pmids)

        if not summary_result["success"]:
            return summary_result

        # Format article info
        articles = []
        for summary in summary_result["summaries"]:
            article = {
                "pmid": str(summary.get("uid", "")),
                "title": str(summary.get("title", "")),
                "authors": (
                    summary.get("authors", [{}])[0].get("name", "")
                    if summary.get("authors")
                    else ""
                ),
                "journal": str(summary.get("fulljournalname", "")),
                "year": str(summary.get("pubdate", ""))[:4],
            }
            articles.append(article)

        return {
            "success": True,
            "variant_id": variant_id,
            "source_db": source_db,
            "linked_pmids": linked_pmids,
            "articles": articles,
            "count": len(articles),
        }

    except Exception as e:
        return format_entrez_error(e, {"variant_id": variant_id, "source_db": source_db})


# Phase 3: Advanced Tools
def entrez_link(
    source_db: str,
    target_db: str,
    ids: str | list[str],
    link_name: str = "",
) -> dict[str, Any]:
    """
    Find related records across NCBI databases using ELink.

    This tool discovers relationships between records in different databases,
    such as finding PubMed articles related to genes, or nucleotide sequences
    related to proteins.

    Args:
        source_db: Source database (e.g., 'gene', 'protein', 'clinvar')
        target_db: Target database to link to (e.g., 'pubmed', 'nucleotide')
        ids: Single ID, comma-separated string, or list of IDs from source_db
        link_name: Specific link type (optional, empty = all available links)

    Returns:
        Dictionary containing:
        - source_db: Source database name
        - target_db: Target database name
        - source_ids: List of source IDs queried
        - linked_ids: Dict mapping source IDs to lists of linked target IDs
        - total_links: Total number of links found
        - link_name: Link type used (if specified)

    Examples:
        >>> entrez_link("gene", "pubmed", "672")  # BRCA1 gene to PubMed
        >>> entrez_link("protein", "nucleotide", ["NP_000198.1", "NP_001121"])
        >>> entrez_link("clinvar", "pubmed", "12345", link_name="clinvar_pubmed")

    Notes:
        - Discovers cross-database relationships automatically
        - Use entrez_info() to see available link names for databases
        - Rate limited (3 req/sec or 10 req/sec with API key)
        - Different databases support different link types
    """
    try:
        from biopython_mcp.utils import parse_ids

        id_list = parse_ids(ids)

        if not id_list:
            return format_entrez_error(
                ValueError("No valid IDs provided"),
                {"source_db": source_db, "target_db": target_db},
            )

        linked_ids: dict[str, list[str]] = {}
        total_links = 0

        # Link each ID individually for better tracking
        for source_id in id_list:
            with entrez_rate_limit():
                if link_name:
                    handle = Entrez.elink(
                        dbfrom=source_db, db=target_db, id=source_id, linkname=link_name
                    )
                else:
                    handle = Entrez.elink(dbfrom=source_db, db=target_db, id=source_id)

                result = Entrez.read(handle)
                handle.close()

            # Extract linked IDs for this source ID
            source_links = []
            if result and result[0].get("LinkSetDb"):
                for link_set in result[0]["LinkSetDb"]:
                    if link_set.get("Link"):
                        source_links.extend([link["Id"] for link in link_set["Link"]])

            linked_ids[source_id] = source_links
            total_links += len(source_links)

        return {
            "success": True,
            "source_db": source_db,
            "target_db": target_db,
            "source_ids": id_list,
            "linked_ids": linked_ids,
            "total_links": total_links,
            "link_name": link_name if link_name else "all",
        }

    except Exception as e:
        return format_entrez_error(
            e, {"source_db": source_db, "target_db": target_db, "ids": str(ids)[:100]}
        )


def clear_entrez_cache(database: str = "") -> dict[str, Any]:
    """
    Clear cached Entrez results.

    The caching system stores Entrez query results to reduce API calls and
    improve response times. Use this tool to clear stale cache data.

    Args:
        database: Database name to clear (empty string clears all databases)

    Returns:
        Dictionary containing:
        - success: Whether operation succeeded
        - cleared: Number of cache files removed
        - database: Database cleared (or "all" if empty string)
        - cache_location: Path to cache directory

    Examples:
        >>> clear_entrez_cache()  # Clear all caches
        >>> clear_entrez_cache("pubmed")  # Clear only PubMed cache
        >>> clear_entrez_cache("gene")  # Clear only Gene cache

    Notes:
        - Caching is optional and controlled via use_cache parameter
        - Default TTL: 1 hour for searches, 7 days for fetches
        - Cache stored in ~/.biopython-mcp/cache/
        - Cached data includes search results and summaries
    """
    try:
        from biopython_mcp.utils import _get_cache_dir, clear_cache

        cache_dir = _get_cache_dir()
        count = clear_cache(database)

        return {
            "success": True,
            "cleared": count,
            "database": database if database else "all",
            "cache_location": str(cache_dir),
        }

    except Exception as e:
        return {"success": False, "error": str(e), "database": database}
