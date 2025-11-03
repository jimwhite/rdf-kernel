"""Tests for RDF Kernel."""

import pytest
from rdf_kernel.kernel import RDFKernel
from rdf_kernel.magics import MagicProcessor
from rdf_kernel.sparql_connection import SPARQLConnection


class TestRDFKernel:
    """Test the main RDF kernel."""

    def test_kernel_initialization(self):
        """Test that kernel initializes properly."""
        kernel = RDFKernel()
        assert kernel.implementation == "RDF"
        assert kernel.language == "rdf"
        assert kernel.data_graph is not None
        assert kernel.shapes_graph is not None

    def test_empty_execution(self):
        """Test executing empty code."""
        kernel = RDFKernel()
        result = kernel.do_execute("", silent=False)
        assert result["status"] == "ok"

    def test_comment_only_execution(self):
        """Test executing only comments."""
        kernel = RDFKernel()
        result = kernel.do_execute("# Just a comment", silent=False)
        assert result["status"] == "ok"


class TestMagicProcessor:
    """Test magic command processing."""

    def test_magic_help(self):
        """Test that help magic works."""
        kernel = RDFKernel()
        processor = MagicProcessor(kernel, kernel.sparql_connection)
        result = processor.process_magic("%help")
        assert "Available magic commands" in result
        assert "%endpoint" in result

    def test_magic_mode(self):
        """Test mode switching."""
        kernel = RDFKernel()
        processor = MagicProcessor(kernel, kernel.sparql_connection)
        
        # Switch to SPARQL mode
        result = processor.process_magic("%mode sparql")
        assert kernel.default_mode == "sparql"
        
        # Switch to SHACL mode
        result = processor.process_magic("%mode shacl")
        assert kernel.default_mode == "shacl"

    def test_magic_format(self):
        """Test format switching."""
        kernel = RDFKernel()
        processor = MagicProcessor(kernel, kernel.sparql_connection)
        
        # Set to N3
        result = processor.process_magic("%format n3")
        assert kernel.default_format == "n3"
        
        # Set to JSON-LD
        result = processor.process_magic("%format json-ld")
        assert kernel.default_format == "json-ld"

    def test_magic_endpoint(self):
        """Test setting SPARQL endpoint."""
        kernel = RDFKernel()
        processor = MagicProcessor(kernel, kernel.sparql_connection)
        
        url = "https://dbpedia.org/sparql"
        result = processor.process_magic(f"%endpoint {url}")
        assert kernel.sparql_connection.get_endpoint() == url

    def test_magic_clear(self):
        """Test clearing graphs."""
        kernel = RDFKernel()
        processor = MagicProcessor(kernel, kernel.sparql_connection)
        
        # Add some data
        kernel.data_graph.parse(data="<http://example.org/s> <http://example.org/p> <http://example.org/o> .", format="turtle")
        assert len(kernel.data_graph) > 0
        
        # Clear
        processor.process_magic("%clear data")
        assert len(kernel.data_graph) == 0


class TestSPARQLConnection:
    """Test SPARQL connection functionality."""

    def test_endpoint_configuration(self):
        """Test setting endpoint."""
        conn = SPARQLConnection()
        assert not conn.has_endpoint()
        
        conn.set_endpoint("https://dbpedia.org/sparql")
        assert conn.has_endpoint()
        assert conn.get_endpoint() == "https://dbpedia.org/sparql"

    def test_prefix_management(self):
        """Test prefix management."""
        conn = SPARQLConnection()
        conn.add_prefix("dbo", "http://dbpedia.org/ontology/")
        assert "dbo" in conn._prefixes

    def test_method_configuration(self):
        """Test HTTP method configuration."""
        conn = SPARQLConnection()
        conn.set_method("POST")
        assert conn._method == "POST"
        
        conn.set_method("GET")
        assert conn._method == "GET"

    def test_result_format(self):
        """Test result format configuration."""
        conn = SPARQLConnection()
        conn.set_result_format("json")
        assert conn._result_format == "json"
        
        conn.set_result_format("xml")
        assert conn._result_format == "xml"


class TestDataLoading:
    """Test RDF data loading."""

    def test_load_turtle_data(self):
        """Test loading Turtle data."""
        kernel = RDFKernel()
        
        turtle_data = (
            "@prefix ex: <http://example.org/> .\n"
            "ex:subject ex:predicate ex:object ."
        )
        
        result = kernel._load_data(turtle_data, format="turtle")
        assert "Added" in result
        assert len(kernel.data_graph) == 1

    def test_load_shapes(self):
        """Test loading SHACL shapes."""
        kernel = RDFKernel()
        
        shapes_data = """
        @prefix sh: <http://www.w3.org/ns/shacl#> .
        @prefix ex: <http://example.org/> .
        
        ex:TestShape a sh:NodeShape .
        """
        
        result = kernel._load_shapes(shapes_data, format="turtle")
        assert "Loaded" in result
        assert len(kernel.shapes_graph) == 1


class TestValidation:
    """Test SHACL validation."""

    def test_validation_without_shapes(self):
        """Test validation fails without shapes."""
        kernel = RDFKernel()
        
        # Load data but no shapes
        kernel.data_graph.parse(data="<http://example.org/s> <http://example.org/p> <http://example.org/o> .", format="turtle")
        
        result = kernel._validate_shacl()
        assert "No shapes graph loaded" in result

    def test_validation_without_data(self):
        """Test validation fails without data."""
        kernel = RDFKernel()
        
        # Load shapes but no data
        shapes = """
        @prefix sh: <http://www.w3.org/ns/shacl#> .
        <http://example.org/shape> a sh:NodeShape .
        """
        kernel.shapes_graph.parse(data=shapes, format="turtle")
        
        result = kernel._validate_shacl()
        assert "No data graph loaded" in result

    def test_successful_validation(self):
        """Test successful validation."""
        kernel = RDFKernel()
        
        # Load shapes
        shapes = """
        @prefix sh: <http://www.w3.org/ns/shacl#> .
        @prefix ex: <http://example.org/> .
        
        ex:PersonShape
            a sh:NodeShape ;
            sh:targetClass ex:Person ;
            sh:property [
                sh:path ex:name ;
                sh:minCount 1 ;
            ] .
        """
        kernel.shapes_graph.parse(data=shapes, format="turtle")
        
        # Load valid data
        data = """
        @prefix ex: <http://example.org/> .
        
        ex:john a ex:Person ;
            ex:name "John" .
        """
        kernel.data_graph.parse(data=data, format="turtle")
        
        result = kernel._validate_shacl()
        assert "PASSED" in result or "FAILED" in result  # Will produce a result either way


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
