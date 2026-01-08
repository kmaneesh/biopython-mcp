"""Tests for PubMed module."""

import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

from biopython_mcp.modules import pubmed


class TestPubMedFetch:
    """Tests for pubmed_fetch function."""

    @patch("biopython_mcp.modules.pubmed.httpx.Client")
    def test_pubmed_fetch_success(self, mock_client_class: MagicMock) -> None:
        """Test successful PMC article fetch."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "<article>Test Article</article>"

        mock_client = MagicMock()
        mock_client.get.return_value = mock_response
        mock_client.__enter__.return_value = mock_client
        mock_client.__exit__.return_value = None
        mock_client_class.return_value = mock_client

        result = pubmed.pubmed_fetch("PMC123456", format="xml")

        assert result["success"] is True
        assert result["pmc_id"] == "PMC123456"
        assert result["format"] == "xml"
        assert "<article>" in result["content"]

    @patch("biopython_mcp.modules.pubmed.httpx.Client")
    def test_pubmed_fetch_not_found(self, mock_client_class: MagicMock) -> None:
        """Test PMC article not found."""
        import httpx

        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "404 Not Found", request=MagicMock(), response=MagicMock(status_code=404)
        )

        mock_client = MagicMock()
        mock_client.get.return_value = mock_response
        mock_client.__enter__.return_value = mock_client
        mock_client.__exit__.return_value = None
        mock_client_class.return_value = mock_client

        result = pubmed.pubmed_fetch("PMC999999", format="xml")

        assert result["success"] is False
        assert "error" in result

    @patch("biopython_mcp.modules.pubmed.httpx.Client")
    def test_pubmed_fetch_timeout(self, mock_client_class: MagicMock) -> None:
        """Test PMC fetch timeout."""
        import httpx

        mock_client = MagicMock()
        mock_client.get.side_effect = httpx.TimeoutException("Timeout")
        mock_client.__enter__.return_value = mock_client
        mock_client.__exit__.return_value = None
        mock_client_class.return_value = mock_client

        result = pubmed.pubmed_fetch("PMC123456", format="xml", timeout=1)

        assert result["success"] is False
        assert "timeout" in result["error"].lower()

    @patch("biopython_mcp.modules.pubmed.httpx.Client")
    def test_pubmed_fetch_invalid_format(self, mock_client_class: MagicMock) -> None:
        """Test that invalid format still returns content (no format validation)."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "<article>Test Article</article>"

        mock_client = MagicMock()
        mock_client.get.return_value = mock_response
        mock_client.__enter__.return_value = mock_client
        mock_client.__exit__.return_value = None
        mock_client_class.return_value = mock_client

        result = pubmed.pubmed_fetch("PMC123456", format="invalid")

        # Function doesn't validate format - it just returns XML content
        assert result["success"] is True
        assert result["format"] == "invalid"
        assert "<article>" in result["content"]


class TestGetPMCURL:
    """Tests for get_pmc_url function."""

    def test_get_pmc_url_with_prefix(self) -> None:
        """Test URL generation with PMC prefix."""
        url = pubmed.get_pmc_url("PMC123456")
        assert url == "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC123456/"

    def test_get_pmc_url_without_prefix(self) -> None:
        """Test URL generation without PMC prefix."""
        url = pubmed.get_pmc_url("123456")
        assert url == "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC123456/"


class TestGetDOIURL:
    """Tests for get_doi_url function."""

    def test_get_doi_url(self) -> None:
        """Test DOI URL generation."""
        url = pubmed.get_doi_url("10.1371/journal.pone.0012345")
        assert url == "https://doi.org/10.1371/journal.pone.0012345"


class TestPubMedReview:
    """Tests for pubmed_review function."""

    @patch("biopython_mcp.database")
    def test_pubmed_review_full_format(self, mock_database: MagicMock) -> None:
        """Test review generation with full format."""
        # Mock search result
        mock_database.entrez_search.return_value = {
            "success": True,
            "ids": ["12345", "67890"],
            "total_found": 2,
        }

        # Mock summary result
        mock_database.entrez_summary.return_value = {
            "success": True,
            "summaries": [
                {
                    "Id": "12345",
                    "Title": "Test Article 1",
                    "AuthorList": [{"LastName": "Smith", "Initials": "J"}],
                    "FullJournalName": "Test Journal",
                    "PubDate": "2024",
                    "ArticleIds": {"pmc": "PMC123", "doi": "10.1234/test"},
                }
            ],
        }

        # Mock fetch result for abstract
        mock_database.entrez_fetch.return_value = {
            "success": True,
            "data": "Test abstract content.",
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            result = pubmed.pubmed_review(
                query="test query",
                obsidian_vault=tmpdir,
                storage_path="test",
                max_results=2,
            )

            assert result["status"] == "success"
            assert "filepath" in result
            # Verify file was created
            filepath = Path(result["filepath"])
            assert filepath.exists()
            assert filepath.suffix == ".md"

            # Read and verify content
            content = filepath.read_text()
            assert content.startswith("---")  # YAML frontmatter
            assert "# Literature Review:" in content
            assert "Test Article 1" in content
            assert result["articles_written"] == 1
            assert "file_size_kb" in result

    @patch("biopython_mcp.database")
    def test_pubmed_review_search_failure(self, mock_database: MagicMock) -> None:
        """Test review when search fails."""
        mock_database.entrez_search.return_value = {
            "success": False,
            "error": "Search failed",
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            result = pubmed.pubmed_review(
                query="test",
                obsidian_vault=tmpdir,
                storage_path="test",
            )

            assert result["status"] == "error"
            assert result["error_type"] == "query_error"

    @patch("biopython_mcp.database")
    def test_pubmed_review_no_results(self, mock_database: MagicMock) -> None:
        """Test review when no articles found."""
        mock_database.entrez_search.return_value = {
            "success": True,
            "ids": [],
            "total_found": 0,
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            result = pubmed.pubmed_review(
                query="test",
                obsidian_vault=tmpdir,
                storage_path="test",
            )

            assert result["status"] == "error"
            assert result["error_type"] == "query_error"
            assert "No articles found" in result["message"]

    @patch("biopython_mcp.database")
    def test_pubmed_review_obsidian_frontmatter(self, mock_database: MagicMock) -> None:
        """Test that Obsidian YAML frontmatter is included in content."""
        mock_database.entrez_search.return_value = {
            "success": True,
            "ids": ["12345"],
            "total_found": 1,
        }

        mock_database.entrez_summary.return_value = {
            "success": True,
            "summaries": [
                {
                    "Id": "12345",
                    "Title": "Test Article",
                    "PubDate": "2024",
                    "FullJournalName": "Test Journal",
                    "ArticleIds": {},
                }
            ],
        }

        mock_database.entrez_fetch.return_value = {"success": False}

        with tempfile.TemporaryDirectory() as tmpdir:
            result = pubmed.pubmed_review(
                query="test query",
                obsidian_vault=tmpdir,
                storage_path="research",
            )

            assert result["status"] == "success"
            assert "filepath" in result

            # Read and verify content
            filepath = Path(result["filepath"])
            content = filepath.read_text()
            # Verify Obsidian YAML frontmatter is present
            assert content.startswith("---")
            assert "title: Literature Review" in content
            assert "tags: [literature-review, pubmed, biopython-mcp]" in content
            assert "status: complete" in content

            # Verify file is in correct location
            assert "research" in str(filepath)
