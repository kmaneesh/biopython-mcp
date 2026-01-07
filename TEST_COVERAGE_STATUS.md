# Test Coverage Improvement Status

## Current Status

**Coverage improved from 35% to 50.5%** ✅

## Breakdown by Module

| Module | Before | Current | Target | Status |
|--------|--------|---------|--------|--------|
| sequence.py | 86% | 86% | 90% | ✅ Almost there |
| server.py | 81% | 81% | 90% | ✅ Almost there |
| alignment.py | 71% | 71% | 90% | ⚠️ Needs ~20 more lines |
| utils.py | 42% | ~75% | 90% | ✅ Good progress |
| structure.py | 11% | ~60% | 90% | ⚠️ Tests added but need fixes |
| phylo.py | 12% | ~55% | 90% | ⚠️ Tests added but need fixes |
| **database.py** | **31%** | **31%** | **90%** | ❌ **HIGHEST PRIORITY** |
| pubmed.py | 8% | ~40% | 90% | ⚠️ Tests added but need fixes |

## What Was Added

### ✅ Completed Tests

1. **test_utils.py** (comprehensive)
   - All validation functions
   - FASTA parsing
   - Molecular weight calculations
   - Rate limiting
   - ID parsing
   - Error formatting
   - Complete caching system tests

2. **test_structure.py** (basic coverage)
   - PDB structure fetching
   - Structure statistics calculation
   - Active site finding

3. **test_phylo.py** (basic coverage)
   - Phylogenetic tree building (UPGMA, NJ)
   - Distance matrix calculation
   - Tree drawing

4. **test_pubmed.py** (basic coverage)
   - PMC article fetching
   - URL generation functions
   - Review generation (multiple formats)

## Issues to Fix

### 1. Test Failures (20 failures)

**pubmed.py tests:**
- Mock `database` module import issue (imported inside function)
- HTTP fetch mocking not working correctly (getting 301 redirects)

**phylo.py tests:**
- `matplotlib` attribute error (not imported at module level)
- API response format mismatch (expects "tree" key, gets "tree_newick")
- Distance matrix format mismatch (expects "matrix", gets "distance_matrix")

**Fix strategy:**
```python
# For pubmed tests, patch where it's used:
@patch("biopython_mcp.modules.pubmed.httpx.get", autospec=True)

# For phylo tests, import matplotlib at module level or mock differently
```

### 2. database.py - The Big Gap (31% → 90%)

**Needs ~200 lines of test code covering:**
- ✅ Core Entrez tools (partially covered by existing tests with @pytest.mark.entrez)
- ❌ entrez_link() function (new in Phase 3)
- ❌ All error paths
- ❌ Cache behavior (use_cache parameter)
- ❌ clinvar_variant_lookup() edge cases
- ❌ gene_info_fetch() edge cases
- ❌ pubmed_search() with year filters
- ❌ variant_literature_link()

**Recommended approach:**
Create `tests/test_database_unit.py` with mocked Bio.Entrez calls:
```python
@patch("biopython_mcp.database.Entrez")
def test_entrez_search_with_cache(mock_entrez):
    # Mock Entrez.esearch
    # Test cache behavior
    # Test error handling
```

### 3. Small Gaps

**alignment.py (71% → 90%):**
- Test MSA placeholder function
- Test error cases in calculate_alignment_score

**sequence.py (86% → 90%):**
- Test edge cases (empty sequences, invalid formats)

## Recommended Next Steps

### Priority 1: Fix Existing Test Failures
1. Fix pubmed test mocking issues
2. Fix phylo test API format mismatches
3. Run tests to verify all pass

### Priority 2: Add database.py Unit Tests
Create comprehensive mocked unit tests for database.py covering:
- All entrez_* functions with mocking
- Error handling paths
- Cache behavior
- Edge cases

### Priority 3: Fill Remaining Gaps
- Add edge case tests for alignment.py
- Add edge case tests for sequence.py

## How to Run Tests

```bash
# Run all tests with coverage
uv run pytest --cov=biopython_mcp --cov-report=term-missing

# Run specific test file
uv run pytest tests/test_utils.py -v

# Run without skipping (requires NCBI credentials)
RUN_ENTREZ_TESTS=1 NCBI_EMAIL=your@email.com uv run pytest
```

## Estimated Effort to Reach 90%

- Fix test failures: **1-2 hours**
- Add database.py mocked tests: **3-4 hours**
- Fill remaining gaps: **1 hour**

**Total: 5-7 hours of focused testing work**

## Notes

- Current tests use mocking to avoid external API dependencies
- Some existing tests use `@pytest.mark.entrez` and are skipped without credentials
- The new tests follow the same patterns as existing tests
- All new tests include docstrings and clear assertions
