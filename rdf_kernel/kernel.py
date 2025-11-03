"""
The main RDF Kernel class for Jupyter.
Provides unified interface for SPARQL queries and SHACL validation.
"""

import logging
import sys
import traceback
from typing import Any, Dict, Optional

from ipykernel.kernelbase import Kernel
from traitlets import List
from rdflib import Graph
from pyshacl import validate
import SPARQLWrapper

from .constants import __version__, LANGUAGE, DEFAULT_RDF_FORMAT
from .magics import MagicProcessor, split_lines
from .sparql_connection import SPARQLConnection


class RDFKernel(Kernel):
    """
    A Jupyter kernel for RDF processing with SPARQL and SHACL support.
    
    This kernel provides:
    - SPARQL query execution against endpoints
    - SHACL validation of RDF data
    - Multiple RDF format support
    - Magic commands for configuration
    """

    # Kernel info
    implementation = "RDF"
    implementation_version = __version__
    banner = "RDF Kernel - SPARQL and SHACL support"
    language = LANGUAGE
    language_version = "1.0"
    language_info = {
        "name": "rdf",
        "mimetype": "text/turtle",
        "file_extension": ".ttl",
        "codemirror_mode": {"name": "turtle"},
        "pygments_lexer": "turtle",
    }

    # Help links
    help_links = List([
        {
            "text": "SPARQL 1.1",
            "url": "https://www.w3.org/TR/sparql11-overview/",
        },
        {
            "text": "SHACL",
            "url": "https://www.w3.org/TR/shacl/",
        },
        {
            "text": "RDFLib",
            "url": "https://rdflib.readthedocs.io/",
        },
    ])

    def __init__(self, **kwargs):
        """Initialize the RDF kernel."""
        super().__init__(**kwargs)
        
        # Set up logging
        self._klog = logging.getLogger(__name__)
        self._klog.setLevel(logging.WARNING)
        
        # Initialize RDF graphs
        self.data_graph = Graph()
        self.shapes_graph = Graph()
        
        # Initialize SPARQL connection
        self.sparql_connection = SPARQLConnection()
        
        # Initialize magic processor
        self.magic_processor = MagicProcessor(
            kernel=self,
            sparql_connection=self.sparql_connection
        )
        
        # Default settings
        self.default_format = DEFAULT_RDF_FORMAT
        self.default_mode = "sparql"  # Can be: sparql, shacl, turtle, etc.
        
        self._klog.info("RDF Kernel initialized")

    def do_execute(
        self,
        code: str,
        silent: bool,
        store_history: bool = True,
        user_expressions: Optional[Dict[str, Any]] = None,
        allow_stdin: bool = False,
    ) -> Dict[str, Any]:
        """
        Execute code in the kernel.
        
        This method handles:
        - Magic commands (starting with %)
        - SPARQL queries (when in SPARQL mode or with %sparql magic)
        - SHACL validation (when in SHACL mode or with %validate magic)
        - RDF data loading (default mode)
        """
        if not code.strip():
            return self._success_response()

        try:
            # Split into lines and remove empty lines/comments
            code_lines = split_lines(code)
            if not code_lines:
                return self._success_response()

            # Check for magic commands
            magic_lines = []
            remaining_code = []
            
            for line in code_lines:
                if line.startswith("%"):
                    magic_lines.append(line)
                else:
                    remaining_code.append(line)

            # Process magic commands first
            if magic_lines:
                for magic_line in magic_lines:
                    result = self.magic_processor.process_magic(magic_line)
                    if result and not silent:
                        self._send_output(result)

            # Process remaining code based on mode
            if remaining_code:
                remaining_code_str = "\n".join(remaining_code)
                result = self._process_code(remaining_code_str)
                
                if result and not silent:
                    self._send_output(result)

            return self._success_response()

        except Exception as e:
            return self._error_response(e)

    def _process_code(self, code: str) -> Optional[str]:
        """
        Process code based on the current mode.
        
        Args:
            code: The code to process
            
        Returns:
            Result message or None
        """
        if not code.strip():
            return None

        mode = self.default_mode.lower()
        
        if mode == "sparql":
            return self._execute_sparql(code)
        elif mode == "shacl":
            return self._load_shapes(code)
        elif mode == "turtle" or mode == "rdf":
            return self._load_data(code, format=self.default_format)
        else:
            # Default: treat as RDF data
            return self._load_data(code, format=self.default_format)

    def _execute_sparql(self, query: str) -> Optional[str]:
        """Execute a SPARQL query."""
        if not self.sparql_connection.has_endpoint():
            return "Error: No SPARQL endpoint configured. Use %endpoint <url> to set one."
        
        return self.sparql_connection.query(query, num=self.execution_count)

    def _load_data(self, data: str, format: str = "turtle") -> str:
        """Load RDF data into the data graph."""
        try:
            before_count = len(self.data_graph)
            self.data_graph.parse(data=data, format=format)
            after_count = len(self.data_graph)
            added_count = after_count - before_count
            return f"Added {added_count} triples to data graph. Total: {after_count} triples."
        except Exception as e:
            raise Exception(f"Error parsing RDF data: {e}")

    def _load_shapes(self, shapes: str, format: str = "turtle") -> str:
        """Load SHACL shapes into the shapes graph."""
        try:
            self.shapes_graph = Graph()
            self.shapes_graph.parse(data=shapes, format=format)
            return f"Loaded shapes graph with {len(self.shapes_graph)} triples."
        except Exception as e:
            raise Exception(f"Error parsing SHACL shapes: {e}")

    def _validate_shacl(self) -> str:
        """Validate data graph against shapes graph."""
        if len(self.shapes_graph) == 0:
            return "Error: No shapes graph loaded. Use %shapes magic to load shapes first."
        if len(self.data_graph) == 0:
            return "Error: No data graph loaded. Load some data first."

        conforms, results_graph, results_text = validate(
            self.data_graph,
            shacl_graph=self.shapes_graph,
            inference="rdfs",
            abort_on_first=False,
        )

        output = []
        output.append(f"Validation {'PASSED' if conforms else 'FAILED'}")
        output.append(f"\n{results_text}")

        return "\n".join(output)

    def _send_output(self, text: str, stream: str = "stdout"):
        """Send output to the frontend."""
        self.send_response(
            self.iopub_socket,
            "stream",
            {"name": stream, "text": str(text) + "\n"},
        )

    def _success_response(self) -> Dict[str, Any]:
        """Return a success response."""
        return {
            "status": "ok",
            "execution_count": self.execution_count,
            "payload": [],
            "user_expressions": {},
        }

    def _error_response(self, error: Exception) -> Dict[str, Any]:
        """Return an error response."""
        error_msg = traceback.format_exc()
        tb_lines = error_msg.split('\n')

        self._send_output(error_msg, stream="stderr")

        return {
            "status": "error",
            "execution_count": self.execution_count,
            "ename": type(error).__name__,
            "evalue": str(error),
            "traceback": tb_lines,
        }

    def do_inspect(self, code: str, cursor_pos: int, detail_level: int = 0) -> Dict[str, Any]:
        """
        Handle introspection requests.
        
        Provides help for magic commands and SPARQL keywords.
        """
        # Find the token at cursor
        token = self._token_at_cursor(code, cursor_pos)
        
        info = None
        if token.startswith("%"):
            info = self.magic_processor.get_magic_help(token)
        
        return {
            "status": "ok",
            "data": {"text/plain": info} if info else {},
            "metadata": {},
            "found": info is not None,
        }

    def do_complete(self, code: str, cursor_pos: int) -> Dict[str, Any]:
        """
        Handle completion requests.
        
        Provides completion for magic commands and SPARQL keywords.
        """
        token, start = self._token_at_cursor_with_pos(code, cursor_pos)
        
        matches = []
        if token.startswith("%"):
            matches = self.magic_processor.get_magic_completions(token)
        
        if matches:
            return {
                "status": "ok",
                "cursor_start": start,
                "cursor_end": start + len(token),
                "matches": matches,
            }
        
        return {"status": "ok", "matches": []}

    def _token_at_cursor(self, code: str, pos: int) -> str:
        """Extract the token at the cursor position."""
        token, _ = self._token_at_cursor_with_pos(code, pos)
        return token

    def _token_at_cursor_with_pos(self, code: str, pos: int) -> tuple:
        """
        Find the token at the cursor position.
        
        Returns:
            Tuple of (token, start_position)
        """
        end = start = pos
        cl = len(code)
        
        # Go forwards while we get alphanumeric chars
        while end < cl and (code[end].isalnum() or code[end] == "_"):
            end += 1
        
        # Go backwards while we get alphanumeric chars
        while start > 0 and (code[start - 1].isalnum() or code[start - 1] == "_"):
            start -= 1
        
        # If previous character is a %, add it (potential magic)
        if start > 0 and code[start - 1] == "%":
            start -= 1
        
        return code[start:end], start


if __name__ == "__main__":
    from ipykernel.kernelapp import IPKernelApp
    IPKernelApp.launch_instance(kernel_class=RDFKernel)
