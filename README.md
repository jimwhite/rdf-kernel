# RDF Kernel for Jupyter

A unified Jupyter kernel for RDF processing with support for SPARQL queries and SHACL validation.

## Features

- **SPARQL Queries**: Execute SPARQL queries against any SPARQL endpoint
- **SHACL Validation**: Validate RDF data against SHACL shapes
- **Multiple RDF Formats**: Support for Turtle, N3, RDF/XML, JSON-LD, TriG, N-Quads
- **Magic Commands**: Extensive magic commands for configuration and mode switching
- **Persistent Settings**: Set defaults that apply to subsequent cells
- **Modern Python**: Requires Python 3.11+ and ipykernel>=6.30

## Installation

### From Source

```bash
pip install -e .
install-rdf-kernel --user
```

### Requirements

- Python 3.11 or higher
- ipykernel >= 6.30
- rdflib >= 7.0.0
- SPARQLWrapper >= 2.0.0
- pyshacl >= 0.25.0

## Usage

### Basic Examples

#### SPARQL Queries

```sparql
%endpoint https://dbpedia.org/sparql
%prefix dbo: <http://dbpedia.org/ontology/>

SELECT ?city ?population
WHERE {
  ?city a dbo:City ;
        dbo:country <http://dbpedia.org/resource/France> ;
        dbo:populationTotal ?population .
}
LIMIT 10
```

#### SHACL Validation

```turtle
# Load shapes
%shapes
@prefix sh: <http://www.w3.org/ns/shacl#> .
@prefix ex: <http://example.org/> .

ex:PersonShape
    a sh:NodeShape ;
    sh:targetClass ex:Person ;
    sh:property [
        sh:path ex:name ;
        sh:minCount 1 ;
        sh:datatype xsd:string ;
    ] .
```

```turtle
# Load data
%data
@prefix ex: <http://example.org/> .

ex:john a ex:Person ;
    ex:name "John Doe" .

ex:jane a ex:Person .
```

```python
# Validate
%validate
```

### Magic Commands

#### Mode Control

- `%mode <sparql|shacl|turtle|rdf>` - Set default execution mode
- `%format <turtle|n3|xml|json-ld|...>` - Set default RDF format

#### SPARQL Configuration

- `%endpoint <url>` - Set SPARQL endpoint (required for queries)
- `%prefix <name> <uri>` - Add persistent SPARQL prefix
- `%header <line>` - Add persistent SPARQL header
- `%method <GET|POST>` - Set HTTP method
- `%auth <basic|digest|none> <user> <pass>` - Set authentication
- `%format_sparql <json|xml|csv|tsv>` - Set result format
- `%display <raw|table|diagram>` - Set display format
- `%show <n>` or `%show all` - Set result limit
- `%lang <lang> [...]` - Set preferred languages for labels

#### SHACL Operations

- `%shapes` - Load cell content as SHACL shapes
- `%data` - Load cell content as RDF data
- `%validate` - Validate data against shapes

#### Graph Operations

- `%clear [data|shapes|all]` - Clear graphs
- `%show_graph [data|shapes]` - Display graph contents
- `%count [data|shapes]` - Show triple count
- `%serialize [format] [graph]` - Serialize and display graph

#### File Operations

- `%load <filename>` - Load RDF data from file
- `%save <filename> [data|shapes]` - Save graph to file

#### Other

- `%help` or `%lsmagics` - List all magic commands
- `%log <level>` - Set logging level (critical|error|warning|info|debug)

## Modes of Operation

The kernel supports multiple modes that determine how cell content is interpreted:

1. **SPARQL Mode** (`%mode sparql`): Execute cells as SPARQL queries
2. **SHACL Mode** (`%mode shacl`): Load cells as SHACL shapes
3. **Turtle Mode** (`%mode turtle`): Load cells as RDF data in Turtle format
4. **RDF Mode** (`%mode rdf`): Load cells as RDF data in default format

Modes can be set persistently with `%mode` or temporarily with specific magics like `%sparql`, `%shapes`, or `%data`.

## Examples

### Example 1: Query DBpedia

```sparql
%endpoint https://dbpedia.org/sparql
%prefix dbo: <http://dbpedia.org/ontology/>
%prefix dbr: <http://dbpedia.org/resource/>

SELECT ?person ?birthPlace WHERE {
  ?person dbo:birthPlace dbr:Paris ;
          a dbo:Scientist .
} LIMIT 5
```

### Example 2: SHACL Validation

```python
# Set mode to work with shapes
%mode shacl
```

```turtle
# Define shapes
@prefix sh: <http://www.w3.org/ns/shacl#> .
@prefix ex: <http://example.org/> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

ex:EmailShape
    a sh:NodeShape ;
    sh:targetClass ex:User ;
    sh:property [
        sh:path ex:email ;
        sh:minCount 1 ;
        sh:pattern "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$" ;
    ] ;
    sh:property [
        sh:path ex:age ;
        sh:datatype xsd:integer ;
        sh:minInclusive 0 ;
        sh:maxInclusive 150 ;
    ] .
```

```python
# Switch to data mode
%mode turtle
```

```turtle
# Add test data
@prefix ex: <http://example.org/> .

ex:user1 a ex:User ;
    ex:email "valid@example.com" ;
    ex:age 25 .

ex:user2 a ex:User ;
    ex:email "invalid-email" ;
    ex:age 200 .
```

```python
# Validate
%validate
```

### Example 3: Working with Local Data

```python
%load data/my_ontology.ttl
%count data
```

```sparql
# Query the loaded data
%mode sparql
%endpoint http://localhost:3030/mydata

SELECT * WHERE {
  ?s ?p ?o .
} LIMIT 10
```

## Architecture

The kernel is built with an extensible architecture:

- **kernel.py**: Main kernel class handling execution
- **magics.py**: Magic command processor
- **sparql_connection.py**: SPARQL endpoint connection and query execution
- **constants.py**: Configuration constants

This design makes it easy to add support for additional RDF technologies in the future.

## Development

### Running Tests

```bash
pytest
```

### Installing in Development Mode

```bash
pip install -e ".[dev]"
install-rdf-kernel --user
```

## License

BSD 3-Clause License (see LICENSE file)

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## Credits

This kernel combines and extends functionality from:
- [sparql-kernel](https://github.com/paulovn/sparql-kernel) by Paulo Villegas
- [shacl-kernel](https://github.com/jimwhite/shacl-kernel) by Jim White

## Future Plans

- Support for additional RDF technologies (RDFS, OWL)
- Graph visualization
- Query optimization hints
- Interactive query builder
- Integration with popular triple stores
