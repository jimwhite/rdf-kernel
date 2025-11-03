"""Constants for the RDF Kernel."""

__version__ = "1.0.0"

KERNEL_NAME = "rdf"
LANGUAGE = "rdf"
DISPLAY_NAME = "RDF"

# Default languages for text labels
DEFAULT_TEXT_LANG = ["en", "es", "fr", "de", "it"]

# Supported RDF formats
RDF_FORMATS = {
    "turtle": ["ttl", "text/turtle"],
    "n3": ["n3", "text/n3"],
    "nt": ["nt", "application/n-triples"],
    "xml": ["rdf", "application/rdf+xml"],
    "json-ld": ["jsonld", "application/ld+json"],
    "trig": ["trig", "application/trig"],
    "nquads": ["nq", "application/n-quads"],
}

# Default format for RDF data
DEFAULT_RDF_FORMAT = "turtle"

# SPARQL result formats
SPARQL_RESULT_FORMATS = {
    "json": "application/sparql-results+json",
    "xml": "application/sparql-results+xml",
    "csv": "text/csv",
    "tsv": "text/tab-separated-values",
}
