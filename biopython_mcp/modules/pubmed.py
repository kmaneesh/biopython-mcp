"""Utilities for accessing PubMed Central (PMC) full-text articles.

This module provides functions for fetching full-text articles from PMC,
which hosts open access biomedical and life sciences literature.

PMC Access
----------
PMC provides several access methods:
- OAI Service: For open access articles in XML format
- E-utilities: For metadata and full-text links
- FTP: For bulk downloads

Rate Limiting
-------------
PMC access should respect NCBI rate limits (same as Entrez):
- 3 requests/second without API key
- 10 requests/second with API key
"""

from typing import Any

import httpx


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
            "source": "PMC OAI Service",
        }

    except httpx.HTTPStatusError as e:
        return {
            "success": False,
            "error": f"HTTP error: {e.response.status_code} - {e.response.reason_phrase}",
            "pmc_id": pmc_id,
        }
    except httpx.TimeoutException:
        return {
            "success": False,
            "error": f"Request timeout after {timeout} seconds",
            "pmc_id": pmc_id,
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Error fetching PMC article: {str(e)}",
            "pmc_id": pmc_id,
        }


def get_pmc_url(pmc_id: str) -> str:
    """
    Generate PMC article URL from PMC ID.

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
    Generate DOI resolver URL from DOI.

    Args:
        doi: Digital Object Identifier

    Returns:
        Full URL to DOI resolver

    Examples:
        >>> get_doi_url("10.1371/journal.pone.0012345")
        'https://doi.org/10.1371/journal.pone.0012345'
    """
    return f"https://doi.org/{doi}"
