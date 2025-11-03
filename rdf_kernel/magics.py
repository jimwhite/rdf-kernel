"""
Magic command processor for RDF Kernel.
Handles configuration and mode-switching magics.
"""

import logging
from typing import Optional, List, TYPE_CHECKING

from .constants import DEFAULT_RDF_FORMAT, RDF_FORMATS

if TYPE_CHECKING:
    from .kernel import RDFKernel
    from .sparql_connection import SPARQLConnection


def split_lines(buf: str) -> List[str]:
    """
    Split a buffer into lines, skipping empty lines and comment lines,
    and stripping whitespace.
    """
    return [
        line.strip()
        for line in buf.split("\n")
        if line.strip() and not line.strip().startswith("#")
    ]


class MagicProcessor:
    """
    Process magic commands for the RDF kernel.
    
    Magic commands control the behavior of the kernel, such as:
    - Setting SPARQL endpoint
    - Configuring formats
    - Switching modes
    - Loading data/shapes
    """

    # Available magics with their help text
    MAGICS = {
        "%help": ["", "List all available magic commands"],
        "%lsmagics": ["", "List all available magic commands"],
        
        # Mode control
        "%mode": ["<sparql|shacl|turtle|rdf>", "Set default execution mode"],
        "%format": ["<turtle|n3|xml|json-ld|...>", "Set default RDF format"],
        
        # SPARQL magics
        "%endpoint": ["<url>", "Set SPARQL endpoint URL (REQUIRED for SPARQL queries)"],
        "%sparql": ["", "Execute the cell content as a SPARQL query"],
        "%prefix": ["<name> <uri>", "Add a persistent SPARQL prefix"],
        "%header": ["<line> | OFF", "Add persistent SPARQL header line"],
        "%method": ["<GET|POST>", "Set HTTP method for SPARQL queries"],
        "%format_sparql": ["<json|xml|csv|tsv>", "Set SPARQL result format"],
        "%auth": ["<basic|digest|none> <username> <password>", "Set HTTP authentication"],
        "%qparam": ["<name> <value>", "Add custom query parameter"],
        "%display": ["<raw|table|diagram>", "Set display format for results"],
        "%show": ["<n> | all", "Set maximum number of results to show"],
        "%lang": ["<lang> [...] | all", "Set preferred languages for labels"],
        
        # SHACL magics
        "%shapes": ["", "Load cell content as SHACL shapes"],
        "%data": ["", "Load cell content as RDF data"],
        "%validate": ["", "Validate data graph against shapes graph"],
        
        # Graph operations
        "%clear": ["[data|shapes|all]", "Clear graphs"],
        "%show_graph": ["[data|shapes]", "Show graph contents"],
        "%count": ["[data|shapes]", "Show triple count"],
        "%serialize": ["[turtle|xml|n3|json-ld]", "Serialize and display graph"],
        
        # File operations
        "%load": ["<filename>", "Load RDF data from file"],
        "%save": ["<filename> [data|shapes]", "Save graph to file"],
        
        # Logging
        "%log": ["<critical|error|warning|info|debug>", "Set logging level"],
    }

    def __init__(self, kernel: "RDFKernel", sparql_connection: "SPARQLConnection"):
        """
        Initialize the magic processor.
        
        Args:
            kernel: The RDF kernel instance
            sparql_connection: The SPARQL connection handler
        """
        self.kernel = kernel
        self.sparql_connection = sparql_connection
        self._log = logging.getLogger(__name__)

    def process_magic(self, line: str) -> Optional[str]:
        """
        Process a single magic command.
        
        Args:
            line: The magic command line (starting with %)
            
        Returns:
            Result message or None
        """
        line = line.strip()
        if not line.startswith("%"):
            raise ValueError(f"Not a magic command: {line}")

        # Handle %help and %lsmagics
        if line in ["%help", "%lsmagics"]:
            return self.get_all_magics_help()

        # Split into command and parameters
        parts = line.split(None, 1)
        cmd = parts[0][1:].lower()  # Remove % prefix
        param = parts[1] if len(parts) > 1 else ""

        # Dispatch to appropriate handler
        handler = getattr(self, f"_magic_{cmd}", None)
        if handler:
            return handler(param)
        else:
            return f"Unknown magic command: {line}\nUse %help to see available commands."

    def get_magic_help(self, magic: str) -> Optional[str]:
        """Get help text for a specific magic command."""
        magic = magic.strip()
        if magic in self.MAGICS:
            param, help_text = self.MAGICS[magic]
            return f"{magic} {param}\n\n{help_text}"
        return None

    def get_magic_completions(self, prefix: str) -> List[str]:
        """Get magic command completions."""
        prefix_lower = prefix.lower()
        return [k for k in self.MAGICS.keys() if k.startswith(prefix_lower)]

    def get_all_magics_help(self) -> str:
        """Get help text for all magic commands."""
        lines = ["Available magic commands:", ""]
        
        for magic, (param, help_text) in sorted(self.MAGICS.items()):
            lines.extend([
                f"  {magic} {param}",
                f"    {help_text}",
                ""
            ])
        
        return "\n".join(lines)

    # Mode control magics
    
    def _magic_mode(self, param: str) -> str:
        """Set the default execution mode."""
        param = param.strip().lower()
        valid_modes = ["sparql", "shacl", "turtle", "rdf"]
        
        if not param:
            return f"Current mode: {self.kernel.default_mode}\nValid modes: {', '.join(valid_modes)}"
        
        if param not in valid_modes:
            return f"Invalid mode: {param}\nValid modes: {', '.join(valid_modes)}"
        
        self.kernel.default_mode = param
        return f"Mode set to: {param}"

    def _magic_format(self, param: str) -> str:
        """Set the default RDF format."""
        param = param.strip().lower()
        
        if not param:
            return f"Current format: {self.kernel.default_format}\nValid formats: {', '.join(RDF_FORMATS.keys())}"
        
        if param not in RDF_FORMATS:
            return f"Invalid format: {param}\nValid formats: {', '.join(RDF_FORMATS.keys())}"
        
        self.kernel.default_format = param
        return f"Default format set to: {param}"

    # SPARQL magics
    
    def _magic_endpoint(self, param: str) -> str:
        """Set the SPARQL endpoint."""
        if not param.strip():
            current = self.sparql_connection.get_endpoint()
            if current:
                return f"Current endpoint: {current}"
            else:
                return "No endpoint configured. Usage: %endpoint <url>"
        
        self.sparql_connection.set_endpoint(param.strip())
        return f"SPARQL endpoint set to: {param.strip()}"

    def _magic_sparql(self, param: str) -> str:
        """Switch to SPARQL mode for this cell."""
        self.kernel.default_mode = "sparql"
        return None  # Don't output anything, just switch mode

    def _magic_prefix(self, param: str) -> str:
        """Add a SPARQL prefix."""
        parts = param.split(None, 1)
        if len(parts) != 2:
            return "Usage: %prefix <name> <uri>"
        
        name, uri = parts
        self.sparql_connection.add_prefix(name, uri)
        return f"Added prefix: {name} -> {uri}"

    def _magic_header(self, param: str) -> str:
        """Add or clear SPARQL headers."""
        if param.strip().upper() == "OFF":
            self.sparql_connection.clear_headers()
            return "Cleared all SPARQL headers"
        
        self.sparql_connection.add_header(param)
        return f"Added SPARQL header: {param}"

    def _magic_method(self, param: str) -> str:
        """Set HTTP method for SPARQL queries."""
        param = param.strip().upper()
        if param not in ["GET", "POST"]:
            return "Usage: %method <GET|POST>"
        
        self.sparql_connection.set_method(param)
        return f"HTTP method set to: {param}"

    def _magic_format_sparql(self, param: str) -> str:
        """Set SPARQL result format."""
        param = param.strip().lower()
        valid_formats = ["json", "xml", "csv", "tsv"]
        
        if param not in valid_formats:
            return f"Usage: %format_sparql <{'|'.join(valid_formats)}>"
        
        self.sparql_connection.set_result_format(param)
        return f"SPARQL result format set to: {param}"

    def _magic_auth(self, param: str) -> str:
        """Set HTTP authentication."""
        parts = param.split()
        if len(parts) < 1:
            return "Usage: %auth <basic|digest|none> [<username> <password>]"
        
        auth_type = parts[0].lower()
        if auth_type == "none":
            self.sparql_connection.set_auth(None, None, None)
            return "Authentication disabled"
        
        if len(parts) != 3:
            return "Usage: %auth <basic|digest> <username> <password>"
        
        username, password = parts[1], parts[2]
        self.sparql_connection.set_auth(auth_type, username, password)
        return f"Authentication set: {auth_type}"

    def _magic_qparam(self, param: str) -> str:
        """Add custom query parameter."""
        parts = param.split(None, 1)
        if len(parts) != 2:
            return "Usage: %qparam <name> <value>"
        
        name, value = parts
        self.sparql_connection.add_query_param(name, value)
        return f"Added query parameter: {name} = {value}"

    def _magic_display(self, param: str) -> str:
        """Set display format."""
        param = param.strip().lower()
        valid_formats = ["raw", "table", "diagram"]
        
        if param not in valid_formats:
            return f"Usage: %display <{'|'.join(valid_formats)}>"
        
        self.sparql_connection.set_display_format(param)
        return f"Display format set to: {param}"

    def _magic_show(self, param: str) -> str:
        """Set maximum number of results to show."""
        param = param.strip().lower()
        
        if param == "all":
            self.sparql_connection.set_result_limit(None)
            return "Showing all results"
        
        try:
            limit = int(param)
            if limit < 1:
                return "Limit must be a positive integer or 'all'"
            self.sparql_connection.set_result_limit(limit)
            return f"Result limit set to: {limit}"
        except ValueError:
            return "Usage: %show <n> | all"

    def _magic_lang(self, param: str) -> str:
        """Set preferred languages."""
        if not param.strip():
            current = self.sparql_connection.get_languages()
            return f"Current languages: {', '.join(current)}"
        
        if param.strip().lower() == "all":
            self.sparql_connection.set_languages([])
            return "Accepting all languages"
        
        langs = param.split()
        self.sparql_connection.set_languages(langs)
        return f"Preferred languages set to: {', '.join(langs)}"

    # SHACL magics
    
    def _magic_shapes(self, param: str) -> str:
        """Load SHACL shapes in next cell content."""
        # This is a marker magic - actual loading happens in kernel
        self.kernel.default_mode = "shacl"
        return None  # Content will be processed as shapes

    def _magic_data(self, param: str) -> str:
        """Load RDF data in next cell content."""
        # This is a marker magic - actual loading happens in kernel
        self.kernel.default_mode = "turtle"
        return None  # Content will be processed as data

    def _magic_validate(self, param: str) -> str:
        """Validate data against shapes."""
        return self.kernel._validate_shacl()

    # Graph operations
    
    def _magic_clear(self, param: str) -> str:
        """Clear graphs."""
        param = param.strip().lower()
        
        if param in ["", "all"]:
            self.kernel.data_graph = type(self.kernel.data_graph)()
            self.kernel.shapes_graph = type(self.kernel.shapes_graph)()
            return "Cleared all graphs"
        elif param == "data":
            self.kernel.data_graph = type(self.kernel.data_graph)()
            return "Cleared data graph"
        elif param == "shapes":
            self.kernel.shapes_graph = type(self.kernel.shapes_graph)()
            return "Cleared shapes graph"
        else:
            return "Usage: %clear [data|shapes|all]"

    def _magic_show_graph(self, param: str) -> str:
        """Show graph contents."""
        param = param.strip().lower()
        
        if param == "shapes":
            graph = self.kernel.shapes_graph
            name = "Shapes"
        else:
            graph = self.kernel.data_graph
            name = "Data"
        
        output = [f"{name} graph: {len(graph)} triples"]
        if len(graph) > 0:
            output.append(f"\n{graph.serialize(format='turtle')}")
        
        return "\n".join(output)

    def _magic_count(self, param: str) -> str:
        """Show triple count."""
        param = param.strip().lower()
        
        if param == "shapes":
            count = len(self.kernel.shapes_graph)
            return f"Shapes graph: {count} triples"
        elif param == "data":
            count = len(self.kernel.data_graph)
            return f"Data graph: {count} triples"
        else:
            data_count = len(self.kernel.data_graph)
            shapes_count = len(self.kernel.shapes_graph)
            return f"Data graph: {data_count} triples\nShapes graph: {shapes_count} triples"

    def _magic_serialize(self, param: str) -> str:
        """Serialize and display graph."""
        parts = param.split()
        format_name = parts[0].lower() if parts else "turtle"
        graph_name = parts[1].lower() if len(parts) > 1 else "data"
        
        if format_name not in RDF_FORMATS:
            return f"Unknown format: {format_name}\nValid formats: {', '.join(RDF_FORMATS.keys())}"
        
        graph = self.kernel.shapes_graph if graph_name == "shapes" else self.kernel.data_graph
        
        if len(graph) == 0:
            return f"{graph_name.capitalize()} graph is empty"
        
        return graph.serialize(format=format_name)

    # File operations
    
    def _magic_load(self, param: str) -> str:
        """Load RDF data from file."""
        if not param.strip():
            return "Usage: %load <filename>"
        
        try:
            self.kernel.data_graph.parse(param.strip())
            return f"Loaded data from {param.strip()}"
        except Exception as e:
            return f"Error loading file: {e}"

    def _magic_save(self, param: str) -> str:
        """Save graph to file."""
        parts = param.split()
        if len(parts) < 1:
            return "Usage: %save <filename> [data|shapes]"
        
        filename = parts[0]
        graph_name = parts[1].lower() if len(parts) > 1 else "data"
        
        graph = self.kernel.shapes_graph if graph_name == "shapes" else self.kernel.data_graph
        
        try:
            graph.serialize(destination=filename, format="turtle")
            return f"Saved {graph_name} graph to {filename}"
        except Exception as e:
            return f"Error saving file: {e}"

    # Logging
    
    def _magic_log(self, param: str) -> str:
        """Set logging level."""
        param = param.strip().upper()
        valid_levels = ["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG"]
        
        if param not in valid_levels:
            return f"Usage: %log <{'|'.join(l.lower() for l in valid_levels)}>"
        
        level = getattr(logging, param)
        self.kernel._klog.setLevel(level)
        logging.getLogger("rdf_kernel").setLevel(level)
        
        return f"Logging level set to: {param}"
