# Contributing to RDF Kernel

Thank you for your interest in contributing to RDF Kernel!

## Development Setup

1. Clone the repository:
```bash
git clone https://github.com/jimwhite/rdf-kernel.git
cd rdf-kernel
```

2. Create a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install in development mode with dev dependencies:
```bash
pip install -e ".[dev]"
```

4. Install the kernel:
```bash
install-rdf-kernel --user
```

## Code Structure

```
rdf-kernel/
├── rdf_kernel/           # Main package
│   ├── __init__.py       # Package initialization
│   ├── __main__.py       # Entry point
│   ├── kernel.py         # Main kernel class
│   ├── magics.py         # Magic command processor
│   ├── sparql_connection.py  # SPARQL endpoint handling
│   ├── constants.py      # Configuration constants
│   └── install.py        # Kernel installation
├── test_kernel.py        # Test suite
├── examples.ipynb        # Example notebook
├── pyproject.toml        # Project configuration
└── README.md            # Documentation
```

## Running Tests

Run all tests:
```bash
pytest
```

Run with coverage:
```bash
pytest --cov=rdf_kernel --cov-report=html
```

## Code Style

We use Python 3.11+ features and follow PEP 8 style guidelines.

### Key Principles

- **Type hints**: Use type hints for function signatures
- **Docstrings**: Add docstrings to all public functions and classes
- **Clean code**: Keep functions focused and modular
- **Comments**: Add comments for complex logic

## Adding New Features

### Adding a New Magic Command

1. Add the magic to `MAGICS` dict in `magics.py`:
```python
"%mymagic": ["<param>", "Description of what it does"],
```

2. Implement the handler method:
```python
def _magic_mymagic(self, param: str) -> str:
    """Handle the mymagic command."""
    # Implementation here
    return "Result message"
```

3. Add tests in `test_kernel.py`

### Adding Support for a New RDF Technology

1. Add constants to `constants.py` if needed
2. Add processing logic to `kernel.py`
3. Add magic commands to `magics.py` if needed
4. Update documentation in `README.md`
5. Add examples to `examples.ipynb`
6. Add tests

## Testing Your Changes

1. Run the test suite:
```bash
pytest
```

2. Test manually in Jupyter:
```bash
jupyter notebook
```

3. Validate structure:
```bash
python validate_structure.py
```

## Submitting Changes

1. Fork the repository
2. Create a feature branch:
```bash
git checkout -b feature/my-new-feature
```

3. Make your changes and commit:
```bash
git add .
git commit -m "Add feature: description"
```

4. Push to your fork:
```bash
git push origin feature/my-new-feature
```

5. Create a Pull Request on GitHub

## Pull Request Guidelines

- Write clear commit messages
- Add tests for new features
- Update documentation
- Ensure all tests pass
- Keep changes focused and minimal

## Code Review Process

1. Maintainer reviews the PR
2. Address any feedback
3. Once approved, changes are merged

## Questions?

Feel free to open an issue for any questions or discussions!

## License

By contributing, you agree that your contributions will be licensed under the BSD 3-Clause License.
