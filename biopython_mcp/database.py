"""Database access tools for NCBI, UniProt, and other biological databases."""

from typing import Any

from Bio import Entrez, SeqIO


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
        Entrez.email = email

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


def search_pubmed(query: str, max_results: int = 10, email: str = "user@example.com") -> dict[str, Any]:
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
        Entrez.email = email

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

            results.append(
                {"pmid": pmid, "title": str(title), "abstract": str(abstract)[:500]}
            )

        return {
            "success": True,
            "query": query,
            "count": len(results),
            "total_found": int(search_results["Count"]),
            "results": results,
        }
    except Exception as e:
        return {"success": False, "error": str(e), "query": query}


def fetch_sequence_by_id(
    db: str, seq_id: str, email: str = "user@example.com"
) -> dict[str, Any]:
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
        Entrez.email = email

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
