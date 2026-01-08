"""
PubMed Central Full-Text Access Module.

This module provides functions to:
1. Fetch full-text articles from PubMed Central (PMC)
2. Generate formatted literature reviews from PubMed searches
3. Get URLs for PMC articles and DOIs

Rate Limiting
-------------
PMC access should respect NCBI rate limits (same as Entrez):
- 3 requests/second without API key
- 10 requests/second with API key
"""

import time
from datetime import datetime
from pathlib import Path
from typing import Any, TypedDict

import httpx


class ReviewStats(TypedDict):
    """Statistics tracking for pubmed_review."""

    pmc_count: int
    doi_count: int
    years: list[int]
    journals: dict[str, int]


def pubmed_fetch(pmc_id: str, format: str = "xml", timeout: int = 30) -> dict[str, Any]:
    """
    Fetch full-text article from PubMed Central (PMC).

    This function retrieves open access full-text articles from PMC using the
    PMC OAI service. Only works for open access articles that have a PMC ID.

    Args:
        pmc_id: PMC identifier (with or without 'PMC' prefix, e.g., "PMC123456" or "123456")
        format: Output format - "xml" for structured XML or "text" for plain text (default: "xml")
        timeout: Request timeout in seconds (default: 30)

    Returns:
        Dictionary containing the full-text article and metadata:
        - success (bool): Whether fetch was successful
        - pmc_id (str): The PMC identifier
        - format (str): Format of returned content
        - content (str): Full-text article content
        - content_length (int): Length of content in characters
        - error (str): Error message if unsuccessful

    Examples:
        >>> result = pubmed_fetch("PMC3539452")
        >>> if result["success"]:
        ...     print(result["content"][:100])

        >>> result = pubmed_fetch("3539452", format="text")
        >>> print(result["content"])

    Note:
        - Only works for open access articles
        - Articles without PMC IDs cannot be fetched
        - Rate limiting applies (use with entrez_rate_limit context manager)
        - XML format preserves structure (sections, figures, tables, references)
        - Text format provides simplified plain text extraction
    """
    try:
        # Normalize PMC ID (ensure it starts with PMC)
        if not pmc_id.startswith("PMC"):
            pmc_id = f"PMC{pmc_id}"

        # PMC OAI service URL
        # This service provides full-text XML for open access articles
        base_url = "https://www.ncbi.nlm.nih.gov/pmc/oai/oai.cgi"

        # Request parameters for OAI GetRecord
        params = {
            "verb": "GetRecord",
            "identifier": f"oai:pubmedcentral.nih.gov:{pmc_id[3:]}",  # Remove PMC prefix
            "metadataPrefix": "pmc",  # PMC XML format
        }

        # Make HTTP request
        with httpx.Client(timeout=timeout) as client:
            response = client.get(base_url, params=params)
            response.raise_for_status()

        content = response.text

        # Check for errors in OAI response
        if "error" in content.lower() and "idDoesNotExist" in content:
            return {
                "success": False,
                "error": f"PMC ID {pmc_id} not found or not available in open access",
                "pmc_id": pmc_id,
            }

        # For text format, extract plain text from XML
        if format == "text":
            # Simple text extraction (remove XML tags)
            import re

            text_content = re.sub(r"<[^>]+>", " ", content)
            text_content = re.sub(r"\s+", " ", text_content).strip()
            content = text_content

        return {
            "success": True,
            "pmc_id": pmc_id,
            "format": format,
            "content": content,
            "content_length": len(content),
        }

    except httpx.TimeoutException as e:
        return {
            "success": False,
            "error": f"Request timeout after {timeout} seconds: {str(e)}",
            "pmc_id": pmc_id,
        }
    except httpx.HTTPStatusError as e:
        return {
            "success": False,
            "error": f"HTTP error: {e.response.status_code} - {e.response.reason_phrase}",
            "pmc_id": pmc_id,
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to fetch PMC article: {str(e)}",
            "pmc_id": pmc_id,
        }


def get_pmc_url(pmc_id: str) -> str:
    """
    Get the URL for a PubMed Central article.

    Args:
        pmc_id: PMC identifier (with or without 'PMC' prefix)

    Returns:
        Full URL to PMC article page

    Examples:
        >>> get_pmc_url("PMC3539452")
        'https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3539452/'

        >>> get_pmc_url("3539452")
        'https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3539452/'
    """
    if not pmc_id.startswith("PMC"):
        pmc_id = f"PMC{pmc_id}"
    return f"https://www.ncbi.nlm.nih.gov/pmc/articles/{pmc_id}/"


def get_doi_url(doi: str) -> str:
    """
    Get the URL for a DOI.

    Args:
        doi: Digital Object Identifier

    Returns:
        Full URL to DOI resolver

    Examples:
        >>> get_doi_url("10.1371/journal.pone.0012345")
        'https://doi.org/10.1371/journal.pone.0012345'
    """
    return f"https://doi.org/{doi}"


def pubmed_review(
    query: str,
    obsidian_vault: str,
    storage_path: str,
    max_results: int = 25,
    sort: str = "pub_date",
) -> dict[str, Any]:
    """
    Create a formatted literature review from PubMed search results and write to MD file.

    This function searches PubMed, fetches article metadata, formats it as
    markdown with complete abstracts, and writes the content directly to a file.
    The filename is auto-generated with datetime and query indication.

    Args:
        query: PubMed search query (supports full Entrez syntax including year filters)
            Example: "BRCA1 AND breast cancer AND 2020:2024[PDAT]"
        obsidian_vault: Path to the Obsidian vault (e.g., "/Users/user/Documents/MyVault")
        storage_path: Relative path within the vault to store the file (e.g., "KB/pubmed")
        max_results: Maximum number of articles to include (default: 25, max: 1000)
        sort: Sort order - "pub_date", "relevance", etc. (default: "pub_date")

    Returns:
        Dictionary with review results and metadata:
            - status: "success" or "error"
            - filepath: Full path where file was written
            - articles_found: Total number of articles found
            - articles_written: Number of articles successfully processed
            - articles_with_pmc: Count of articles with PMC IDs
            - articles_with_doi: Count of articles with DOIs
            - query: Original search query
            - file_size_kb: File size in kilobytes
            - year_range: {"min": int, "max": int}
            - top_journals: List of top 5 journals by article count
            - execution_time_seconds: Time taken to generate review

    Examples:
        >>> result = pubmed_review(
        ...     query="COL4A3[Gene] AND Alport syndrome",
        ...     obsidian_vault="/Users/user/Documents/Obsidian",
        ...     storage_path="KB/pubmed"
        ... )
        >>> # File written to: /Users/user/Documents/Obsidian/KB/pubmed/20260108_143025_COL4A3_Gene_AND_Alport.md

        >>> # More results
        >>> result = pubmed_review(
        ...     query="BRCA1 AND breast cancer AND 2020:2024[PDAT]",
        ...     obsidian_vault="/Users/user/Vault",
        ...     storage_path="research/cancer",
        ...     max_results=50
        ... )

    Notes:
        - Writes markdown file directly to disk with complete abstracts
        - Fetches articles in batches of 20 (NCBI limit)
        - Respects NCBI rate limits (3/sec or 10/sec with API key)
        - For very large reviews (>500 articles), consider splitting into multiple calls
        - Includes Obsidian-compatible YAML frontmatter
        - Filename format: YYYYMMDD_HHMMSS_query_slug.md
    """
    start_time = time.time()
    articles_written = 0

    try:
        # Import here to avoid circular dependency
        from biopython_mcp import database

        # Generate filename with datetime + query slug
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        # Create query slug (first 30 chars, sanitize)
        query_slug = (
            query[:30].replace(" ", "_").replace("[", "").replace("]", "").replace("/", "_")
        )
        filename = f"{timestamp}_{query_slug}.md"

        # Join paths
        full_dir_path = Path(obsidian_vault) / storage_path
        output_path = full_dir_path / filename

        # Create directory if it doesn't exist
        full_dir_path.mkdir(parents=True, exist_ok=True)

        # Search PubMed for PMIDs
        search_result = database.entrez_search(
            "pubmed", query, max_results=min(max_results, 1000), sort=sort
        )

        if not search_result["success"]:
            return {
                "status": "error",
                "error_type": "query_error",
                "message": search_result.get("error", "Search failed"),
            }

        pmids = search_result["ids"]
        total_found = search_result["total_found"]

        if not pmids:
            return {
                "status": "error",
                "error_type": "query_error",
                "message": "No articles found for query",
            }

        # Statistics tracking
        stats: ReviewStats = {
            "pmc_count": 0,
            "doi_count": 0,
            "years": [],
            "journals": {},
        }

        # Build content in memory
        content_parts = []

        # Step 1: Generate frontmatter (Obsidian YAML)
        query_truncated = query[:50] + "..." if len(query) > 50 else query
        content_parts.append("---")
        content_parts.append(f"title: Literature Review - {query_truncated}")
        content_parts.append("tags: [literature-review, pubmed, biopython-mcp]")
        content_parts.append(f"date: {datetime.now().isoformat()}")
        content_parts.append(f'query: "{query}"')
        content_parts.append(f"total_articles: {len(pmids)}")
        content_parts.append("status: complete")
        content_parts.append("---\n")

        # Step 2: Write header
        content_parts.append(f"# Literature Review: {query}\n")
        content_parts.append("## Query Details\n")
        content_parts.append(f"- **Query:** `{query}`")
        content_parts.append(f"- **Total Found:** {total_found:,}")
        content_parts.append(f"- **Retrieved:** {len(pmids)}")
        content_parts.append(f"- **Sort:** {sort}")
        content_parts.append(f"- **Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        content_parts.append("---\n")

        # Step 3: Fetch and format articles in batches
        batch_size = 20
        for i in range(0, len(pmids), batch_size):
            batch = pmids[i : i + batch_size]

            # Fetch summaries for this batch
            summary_result = database.entrez_summary("pubmed", batch)

            if not summary_result["success"]:
                # Write error note but continue
                content_parts.append(f"\n**Error fetching batch {i//batch_size + 1}:** ")
                content_parts.append(f"{summary_result.get('error', 'Unknown error')}\n")
                continue

            # Process each article in the batch immediately
            for idx, summary in enumerate(summary_result["summaries"]):
                try:
                    article_num = i + idx + 1

                    # Extract metadata
                    pmid = summary.get("Id", "")
                    title = summary.get("Title", "Untitled")
                    authors = summary.get("AuthorList", [])
                    journal = summary.get("FullJournalName", summary.get("Source", "Unknown"))
                    year = summary.get("PubDate", "")[:4] if summary.get("PubDate") else "N/A"

                    # Extract IDs
                    article_ids = summary.get("ArticleIds", {})
                    pmc_id = article_ids.get("pmc", "")
                    doi = article_ids.get("doi", "")

                    # Track statistics
                    if pmc_id:
                        stats["pmc_count"] += 1
                    if doi:
                        stats["doi_count"] += 1
                    if year.isdigit():
                        stats["years"].append(int(year))
                    if journal:
                        stats["journals"][journal] = stats["journals"].get(journal, 0) + 1

                    # Full format: complete abstract
                    content_parts.append(f"## [{article_num}] {title}\n")
                    content_parts.append(
                        f"**PMID:** [{pmid}](https://pubmed.ncbi.nlm.nih.gov/{pmid}/)"
                    )
                    content_parts.append(f" | **Year:** {year} | **Journal:** {journal}\n")

                    if doi:
                        content_parts.append(f"**DOI:** [{doi}]({get_doi_url(doi)})")
                    if pmc_id:
                        content_parts.append(f" | **PMC:** [{pmc_id}]({get_pmc_url(pmc_id)})")
                    content_parts.append("\n")

                    # Authors
                    if authors:
                        author_names = [
                            f"{a.get('LastName', '')} {a.get('Initials', '')}".strip()
                            for a in authors[:10]
                        ]
                        content_parts.append(f"**Authors:** {', '.join(author_names)}")
                        if len(authors) > 10:
                            content_parts.append(f", et al. ({len(authors)} total)")
                        content_parts.append("\n")

                    # Fetch full abstract
                    fetch_result = database.entrez_fetch(
                        "pubmed", pmid, rettype="abstract", retmode="text"
                    )
                    if fetch_result["success"]:
                        abstract = fetch_result["data"]
                        content_parts.append("**Full Abstract:**\n")
                        content_parts.append(f"{abstract}\n")
                    else:
                        content_parts.append("**Abstract:** Not available\n")

                    content_parts.append("---\n")

                    articles_written += 1

                except Exception as e:
                    # Write error note for this article but continue
                    content_parts.append(
                        f"\n**Error processing article {article_num}:** {str(e)}\n"
                    )
                    continue

        # Step 4: Write summary statistics at end
        content_parts.append("\n## Summary Statistics\n")
        content_parts.append(f"- **Total Articles:** {articles_written}")
        content_parts.append(f"- **With PMC IDs:** {stats['pmc_count']}")
        content_parts.append(f"- **With DOIs:** {stats['doi_count']}")

        if stats["years"]:
            content_parts.append(f"- **Year Range:** {min(stats['years'])} - {max(stats['years'])}")

        if stats["journals"]:
            top_journals = sorted(stats["journals"].items(), key=lambda x: x[1], reverse=True)[:5]
            content_parts.append("\n**Top Journals:**")
            for journal, count in top_journals:
                content_parts.append(f"- {journal}: {count} articles")

        # Step 5: Combine all parts
        full_content = "\n".join(content_parts)

        # Step 6: Write to file
        output_path.write_text(full_content, encoding="utf-8")
        file_size_kb = round(len(full_content.encode("utf-8")) / 1024, 2)

        # Calculate execution time
        execution_time = round(time.time() - start_time, 2)

        # Build top journals list
        top_journals_list = [
            {"name": name, "count": count}
            for name, count in sorted(stats["journals"].items(), key=lambda x: x[1], reverse=True)[
                :5
            ]
        ]

        # Step 7: Return results
        return {
            "status": "success",
            "filepath": str(output_path),
            "articles_found": total_found,
            "articles_written": articles_written,
            "articles_with_pmc": stats["pmc_count"],
            "articles_with_doi": stats["doi_count"],
            "query": query,
            "file_size_kb": file_size_kb,
            "year_range": (
                {"min": min(stats["years"]), "max": max(stats["years"])}
                if stats["years"]
                else {"min": 0, "max": 0}
            ),
            "top_journals": top_journals_list,
            "execution_time_seconds": execution_time,
        }

    except Exception as e:
        return {
            "status": "error",
            "error_type": "unknown",
            "message": f"Error creating literature review: {str(e)}",
        }
