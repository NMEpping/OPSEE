# Contributing to OPSEE

Thank you for considering contributing to OPSEE! This document provides guidelines and instructions for contributing.

## Code of Conduct

This project adheres to a code of conduct adapted from the Contributor Covenant. By participating, you are expected to uphold this code.

**Our Standards**:
- Be respectful and inclusive
- Welcome diverse perspectives
- Focus on constructive feedback
- Prioritize the community's best interests

## How to Contribute

### Reporting Issues

- **Search existing issues** before creating a new one
- **Use issue templates** when available
- **Provide clear descriptions** including steps to reproduce
- **Include context**: OS, Python version, dependency versions

### Suggesting Enhancements

- **Describe the use case** clearly
- **Explain why** the enhancement would be useful
- **Provide examples** of how it would work
- **Consider backward compatibility**

### Pull Requests

1. **Fork the repository** and create a feature branch
2. **Make your changes** following code style guidelines
3. **Add tests** for new functionality
4. **Update documentation** as needed
5. **Submit a pull request** with a clear description

## Development Setup

```bash
# Clone your fork
git clone https://github.com/yourusername/opsee.git
cd opsee

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -r requirements.txt
pip install -e .

# Install development dependencies
pip install pytest black flake8 mypy
```

## Code Style

- **Python**: Follow PEP 8 style guide
- **Formatting**: Use `black` for code formatting
- **Linting**: Pass `flake8` checks
- **Type hints**: Add type annotations where appropriate
- **Docstrings**: Use Google-style docstrings

```bash
# Format code
black src/ opsee_workflow.ipynb

# Check linting
flake8 src/

# Type checking
mypy src/
```

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src tests/

# Run specific test
pytest tests/test_dexpi_parser.py
```

## Documentation

- **Inline comments** for complex logic
- **Docstrings** for all public functions/classes
- **README updates** for new features
- **Notebook markdown cells** for workflow steps

## Commit Messages

Use clear, descriptive commit messages:

```
<type>: <short summary>

<detailed description if needed>

<reference to issues>
```

**Types**: feat, fix, docs, style, refactor, test, chore

**Example**:
```
feat: Add HPLC data integration support

- Implement HPLC file parser
- Add widget for HPLC-to-instrument linking
- Update profile schema with HPLCData entity type

Closes #42
```

## Branch Naming

- `feature/description` - New features
- `fix/description` - Bug fixes
- `docs/description` - Documentation updates
- `refactor/description` - Code refactoring

## Review Process

1. **Automated checks** must pass (linting, tests)
2. **At least one maintainer** reviews the PR
3. **Address feedback** in subsequent commits
4. **Squash commits** if requested before merge

## Areas for Contribution

### High Priority
- Example datasets (GC, HPLC, spectroscopy)
- Additional analytical instrument integrations
- Improved validation error messages
- Documentation improvements

### Medium Priority
- Performance optimizations
- UI/UX enhancements in widgets
- Additional DEXPI element support
- Export format options

### Nice to Have
- Web-based interface
- Cloud storage integration
- Real-time data acquisition support
- Multi-language support

## Release Process

Maintainers handle releases:
1. Update version in `setup.py` and `__init__.py`
2. Update CHANGELOG.md
3. Create release tag
4. Build and publish to PyPI

## Questions?

- **GitHub Discussions** for general questions
- **GitHub Issues** for bug reports and feature requests
- **Email** opsee-support@example.org for private inquiries

## License

By contributing, you agree that your contributions will be licensed under the Apache License 2.0.

---

Thank you for helping improve OPSEE!
