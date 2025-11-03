# RDF Kernel Architecture

## Overview

The RDF Kernel is designed as a unified, extensible Jupyter kernel for working with RDF data, SPARQL queries, and SHACL validation. The architecture is modular and follows Jupyter kernel best practices.

## Design Principles

1. **Unified Interface**: Single kernel for multiple RDF technologies
2. **Extensibility**: Easy to add new RDF technologies (OWL, RDFS, etc.)
3. **Modern Python**: Uses Python 3.11+ features and modern dependencies
4. **Magic-Based Configuration**: Extensive magic commands for flexible control
5. **Persistent State**: Settings can be made persistent across cells
6. **Multiple Modes**: Support for different execution modes (SPARQL, SHACL, RDF)

## Component Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Jupyter Frontend                         │
│                  (Notebook / JupyterLab)                     │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          │ ZMQ Protocol
                          │
┌─────────────────────────▼───────────────────────────────────┐
│                      RDFKernel                               │
│  ┌────────────────────────────────────────────────────┐     │
│  │  do_execute(code, ...)                             │     │
│  │    - Split into magic lines and code               │     │
│  │    - Process magics via MagicProcessor             │     │
│  │    - Execute remaining code based on mode          │     │
│  └────────────────────────────────────────────────────┘     │
│                          │                                   │
│         ┌────────────────┼────────────────┐                 │
│         │                │                │                 │
│         ▼                ▼                ▼                 │
│  ┌──────────┐   ┌──────────────┐   ┌──────────┐           │
│  │  Magic   │   │   SPARQL     │   │  SHACL   │           │
│  │Processor │   │ Connection   │   │Validation│           │
│  └──────────┘   └──────────────┘   └──────────┘           │
│         │                │                │                 │
│         │                │                │                 │
│         ▼                ▼                ▼                 │
│  ┌──────────────────────────────────────────┐              │
│  │          RDF Graphs (rdflib)              │              │
│  │  - data_graph: Main RDF data              │              │
│  │  - shapes_graph: SHACL shapes             │              │
│  └──────────────────────────────────────────┘              │
└─────────────────────────────────────────────────────────────┘
                          │
                          │ HTTP/HTTPS
                          │
┌─────────────────────────▼───────────────────────────────────┐
│                   SPARQL Endpoint                            │
│              (DBpedia, Wikidata, etc.)                       │
└─────────────────────────────────────────────────────────────┘
```

## Core Components

### 1. RDFKernel (kernel.py)

The main kernel class that inherits from `ipykernel.kernelbase.Kernel`.

**Responsibilities:**
- Handle cell execution via `do_execute()`
- Manage execution modes (SPARQL, SHACL, Turtle, RDF)
- Maintain RDF graphs (data and shapes)
- Coordinate between magic processor and execution engines
- Provide introspection and completion support

**Key Methods:**
- `do_execute()`: Main execution entry point
- `_process_code()`: Route code to appropriate handler based on mode
- `_execute_sparql()`: Execute SPARQL queries
- `_load_data()`: Load RDF data into graphs
- `_load_shapes()`: Load SHACL shapes
- `_validate_shacl()`: Run SHACL validation

### 2. MagicProcessor (magics.py)

Handles all magic commands for configuration and control.

**Responsibilities:**
- Parse and execute magic commands
- Maintain magic command registry
- Provide help and completion for magics
- Coordinate with kernel for state changes

**Magic Categories:**
1. **Mode Control**: `%mode`, `%format`
2. **SPARQL**: `%endpoint`, `%prefix`, `%header`, `%auth`, etc.
3. **SHACL**: `%shapes`, `%data`, `%validate`
4. **Graph Operations**: `%clear`, `%show_graph`, `%count`, `%serialize`
5. **File Operations**: `%load`, `%save`
6. **Utility**: `%help`, `%log`

### 3. SPARQLConnection (sparql_connection.py)

Manages SPARQL endpoint connections and query execution.

**Responsibilities:**
- Maintain endpoint configuration
- Build queries with prefixes and headers
- Execute queries via SPARQLWrapper
- Format results (table, raw, JSON)
- Handle authentication
- Manage query parameters

**Features:**
- HTTP method configuration (GET/POST)
- Multiple result formats (JSON, XML, CSV, TSV)
- Result limiting and pagination
- Language preferences for labels
- Custom query parameters

### 4. Constants (constants.py)

Central configuration and format definitions.

**Contains:**
- Version information
- Kernel metadata (name, language)
- Supported RDF formats
- SPARQL result formats
- Default settings

## Execution Flow

### Cell Execution Flow

```
1. User enters code in cell
   ↓
2. Jupyter sends execute_request
   ↓
3. RDFKernel.do_execute() receives code
   ↓
4. Split code into lines, remove comments
   ↓
5. Separate magic lines from regular code
   ↓
6. Process each magic line
   │  ↓
   │  MagicProcessor.process_magic()
   │  ↓
   │  Execute magic (change settings, modes, etc.)
   │  ↓
   │  Return result message
   ↓
7. Process remaining code based on current mode
   │
   ├─→ SPARQL mode
   │   ↓
   │   SPARQLConnection.query()
   │   ↓
   │   Format and return results
   │
   ├─→ SHACL mode
   │   ↓
   │   Load as shapes graph
   │   ↓
   │   Return confirmation
   │
   └─→ RDF/Turtle mode
       ↓
       Parse and load into data graph
       ↓
       Return triple count
   ↓
8. Send output to frontend
   ↓
9. Return execution result
```

### Magic Processing Flow

```
1. Magic line starts with %
   ↓
2. Extract command and parameters
   ↓
3. Look up handler method (_magic_<command>)
   ↓
4. Execute handler with parameters
   ↓
5. Handler updates kernel state
   ↓
6. Return result message
```

## State Management

### Kernel State

The kernel maintains several types of state:

1. **Execution Mode** (`default_mode`)
   - Current: sparql, shacl, turtle, rdf
   - Determines how cell content is interpreted

2. **RDF Graphs** (via rdflib)
   - `data_graph`: Main RDF data
   - `shapes_graph`: SHACL shapes
   - Persistent across cells

3. **SPARQL Configuration** (via SPARQLConnection)
   - Endpoint URL
   - Prefixes
   - Headers
   - Authentication
   - Result format
   - Display preferences

4. **Format Settings**
   - Default RDF format (turtle, n3, xml, json-ld, etc.)
   - SPARQL result format (json, xml, csv, tsv)
   - Display format (raw, table, diagram)

### State Persistence

Settings persist across cells within a session:
- Magic commands modify state
- State is maintained until explicitly changed
- New cells inherit current state

## Extension Points

The architecture is designed to be easily extensible:

### Adding New RDF Technologies

1. Add constants to `constants.py`
2. Add processing method to `kernel.py`:
   ```python
   def _execute_mytechnology(self, code: str) -> str:
       # Implementation
       pass
   ```
3. Add mode to `_process_code()` routing
4. Add magic commands to `magics.py` if needed

### Adding New Magic Commands

1. Add to `MAGICS` dict in `magics.py`:
   ```python
   "%mymagic": ["<params>", "Help text"],
   ```
2. Implement handler:
   ```python
   def _magic_mymagic(self, param: str) -> str:
       # Implementation
       return "Result"
   ```

### Adding New Result Formatters

1. Add format to `SPARQLConnection._format_results()`
2. Add format option to magic commands
3. Update constants if needed

## Dependencies

### Core Dependencies

- **ipykernel** (>=6.30): Jupyter kernel infrastructure
- **rdflib** (>=7.0.0): RDF graph handling and parsing
- **SPARQLWrapper** (>=2.0.0): SPARQL endpoint communication
- **pyshacl** (>=0.25.0): SHACL validation
- **traitlets** (>=5.0): Configuration and type checking
- **pygments** (>=2.0): Syntax highlighting

### Why These Versions?

- **Python 3.11+**: Modern Python features, better performance
- **ipykernel 6.30+**: Latest kernel protocol, modern APIs
- **rdflib 7.0+**: Latest RDF handling, better performance
- **SPARQLWrapper 2.0+**: Modern SPARQL support
- **pyshacl 0.25+**: Latest SHACL features

## Design Decisions

### Why a Unified Kernel?

Instead of separate kernels for SPARQL and SHACL:
- Easier workflow: Load data, define shapes, validate in one notebook
- Shared state: Graphs accessible across different operations
- Extensible: Can add more RDF technologies without new kernels
- Better UX: Single kernel to learn and install

### Why Magic-Based Configuration?

Magics provide:
- Clear, explicit configuration
- Self-documenting (via `%help`)
- Non-intrusive to code
- Persistent settings across cells
- Jupyter-native pattern

### Why Mode-Based Execution?

Modes allow:
- Natural workflows (query mode, validation mode)
- Sensible defaults (RDF data loads as data)
- Explicit control when needed (via `%mode`)
- Easy to understand and teach

### Why Both Data and Shapes Graphs?

Separation provides:
- Clear distinction between data and constraints
- Reusable shapes across different datasets
- Clean validation workflow
- Standard SHACL pattern

## Performance Considerations

### Graph Management

- Graphs are kept in memory (rdflib)
- Large datasets may require external triple store
- Use SPARQL mode for remote querying

### Query Execution

- Queries executed remotely (no local storage)
- Result limiting prevents overwhelming output
- Streaming not yet implemented (future enhancement)

### State Management

- Minimal state overhead
- Configuration is lightweight
- Graphs can be cleared with `%clear`

## Future Enhancements

Potential additions to the architecture:

1. **Additional Technologies**
   - RDFS inference
   - OWL reasoning
   - Named graph support
   - SPARQL UPDATE support

2. **Visualization**
   - Graph diagrams
   - Query result visualizations
   - SHACL validation reports

3. **Performance**
   - Result streaming
   - Async query execution
   - Connection pooling

4. **Integration**
   - Triple store backends
   - Git-based RDF storage
   - Collaborative features

5. **Developer Tools**
   - Query profiling
   - Schema validation
   - Data quality reports

## Testing Strategy

### Unit Tests
- Test each component in isolation
- Mock dependencies where appropriate
- Cover magic commands thoroughly

### Integration Tests
- Test kernel execution end-to-end
- Test with real SPARQL endpoints
- Test SHACL validation workflows

### Structure Tests
- Validate code structure
- Check syntax
- Verify class/function presence

## Security Considerations

### SPARQL Endpoints
- No query injection protection (user controls queries)
- HTTPS recommended for sensitive endpoints
- Authentication supported (basic, digest)

### File Operations
- `%load` and `%save` have file system access
- Users should be cautious with file paths
- No arbitrary code execution from data

### Graph Data
- In-memory storage only
- No automatic persistence
- Users control what data is loaded

## Conclusion

The RDF Kernel provides a solid, extensible foundation for RDF work in Jupyter. The modular architecture makes it easy to add new features while maintaining simplicity for users.
