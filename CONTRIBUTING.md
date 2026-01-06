# Contributing to BioPython MCP

Thank you for your interest in contributing to BioPython MCP! This document provides guidelines and instructions for contributing.

## Code of Conduct

By participating in this project, you agree to abide by our code of conduct:

- Be respectful and inclusive
- Welcome newcomers and help them get started
- Focus on what is best for the community
- Show empathy towards other community members

## Getting Started

### Development Setup

1. **Fork the repository**
   ```bash
   git clone https://github.com/yourusername/biopython-mcp.git
   cd biopython-mcp
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install development dependencies**
   ```bash
   pip install -e ".[dev]"
   ```

4. **Install pre-commit hooks**
   ```bash
   pre-commit install
   ```

### Development Workflow

1. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**
   - Write code following our style guidelines
   - Add tests for new functionality
   - Update documentation as needed

3. **Run tests and checks**
   ```bash
   # Run tests
   pytest

   # Run type checking
   mypy biopython_mcp/

   # Run linting
   black src/ tests/
   ruff check src/ tests/

   # Run all pre-commit hooks
   pre-commit run --all-files
   ```

4. **Commit your changes**
   ```bash
   git add .
   git commit -m "feat: add new feature"
   ```

5. **Push and create a pull request**
   ```bash
   git push origin feature/your-feature-name
   ```

## Contribution Guidelines

### Code Style

We follow these style guidelines:

- **Black** for code formatting (line length: 100)
- **Ruff** for linting
- **PEP 8** for general Python style
- **Type hints** required for all functions
- **Docstrings** required for all public functions and classes

### Type Hints

All functions must include type hints:

```python
def calculate_gc_content(sequence: str) -> dict[str, Any]:
    """
    Calculate GC content of a sequence.

    Args:
        sequence: DNA or RNA sequence

    Returns:
        Dictionary containing GC content and statistics
    """
    pass
```

### Docstrings

Use Google-style docstrings:

```python
def example_function(param1: str, param2: int) -> bool:
    """
    Brief description of function.

    Longer description if needed.

    Args:
        param1: Description of param1
        param2: Description of param2

    Returns:
        Description of return value

    Raises:
        ValueError: When input is invalid
    """
    pass
```

### Testing

- Write tests for all new features
- Maintain or improve code coverage
- Use pytest fixtures for common test data
- Mock external API calls

Example test:

```python
def test_translate_sequence() -> None:
    """Test DNA translation."""
    result = translate_sequence("ATGGCC")
    assert result["success"] is True
    assert result["protein_sequence"] == "MA"
```

### Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `test:` Test updates
- `refactor:` Code refactoring
- `style:` Code style changes
- `chore:` Maintenance tasks

Examples:
```
feat: add support for protein structure prediction
fix: correct GC content calculation for RNA
docs: update installation instructions
test: add tests for alignment functions
```

### Pull Request Process

1. **Update documentation** for any new features
2. **Add tests** that cover your changes
3. **Ensure all tests pass** and pre-commit hooks succeed
4. **Update CHANGELOG** if applicable
5. **Reference related issues** in the PR description
6. **Request review** from maintainers

### PR Description Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
Describe testing performed

## Checklist
- [ ] Tests added/updated
- [ ] Documentation updated
- [ ] Type hints added
- [ ] Pre-commit hooks pass
- [ ] All tests pass
```

## Areas for Contribution

### High Priority

- Additional BioPython tool integrations
- Performance optimizations
- Documentation improvements
- Test coverage improvements
- Bug fixes

### New Features

- BLAST search integration
- Protein structure prediction
- Sequence feature annotation
- Custom HMM profile support
- Batch processing capabilities

### Documentation

- Usage examples
- Tutorial notebooks
- API documentation
- Video tutorials
- Blog posts

### Testing

- Unit tests
- Integration tests
- Performance benchmarks
- Edge case coverage

## Reporting Bugs

### Before Submitting

1. Check existing issues
2. Test with the latest version
3. Collect relevant information

### Bug Report Template

```markdown
**Describe the bug**
Clear description of the bug

**To Reproduce**
Steps to reproduce:
1. Call function X with parameter Y
2. See error

**Expected behavior**
What should happen

**Actual behavior**
What actually happens

**Environment**
- OS: [e.g., macOS 13.0]
- Python version: [e.g., 3.11]
- BioPython MCP version: [e.g., 0.1.0]

**Additional context**
Any other relevant information
```

## Requesting Features

### Feature Request Template

```markdown
**Feature Description**
Clear description of the feature

**Use Case**
Why is this feature needed?

**Proposed Solution**
How should this work?

**Alternatives Considered**
Other approaches you've considered

**Additional Context**
Any other relevant information
```

## Code Review Process

### For Contributors

- Respond to review comments promptly
- Make requested changes in new commits
- Update the PR description if scope changes
- Be open to feedback and suggestions

### For Reviewers

- Be constructive and respectful
- Explain the reasoning behind suggestions
- Approve when changes meet standards
- Help contributors improve their code

## Development Tips

### Running Specific Tests

```bash
# Run specific test file
pytest tests/test_sequence.py

# Run specific test
pytest tests/test_sequence.py::test_translate_sequence

# Run with verbose output
pytest -v

# Run with coverage
pytest --cov=biopython_mcp --cov-report=html
```

### Debugging

```bash
# Run with debugging
pytest --pdb

# Run with print statements visible
pytest -s
```

### Type Checking

```bash
# Check specific file
mypy biopython_mcp/sequence.py

# Check all source
mypy biopython_mcp/

# Generate coverage report
mypy --html-report mypy-report src/
```

## Release Process

Maintainers handle releases following this process:

1. Update version in `pyproject.toml`
2. Update `CHANGELOG.md`
3. Create release tag
4. GitHub Actions publishes to PyPI
5. Announce release

## Questions?

- Open a [Discussion](https://github.com/kmaneesh/biopython-mcp/discussions)
- Ask in [Issues](https://github.com/kmaneesh/biopython-mcp/issues)
- Email maintainers

## Recognition

Contributors are recognized in:
- README acknowledgments
- CHANGELOG entries
- GitHub contributors page
- Release notes

Thank you for contributing to BioPython MCP!
