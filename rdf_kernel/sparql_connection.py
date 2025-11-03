"""
SPARQL connection and query execution.
Based on the sparql-kernel connection module.
"""

import json
import logging
from typing import Optional, Dict, List
import SPARQLWrapper
from SPARQLWrapper import SPARQLWrapper as Wrapper


class SPARQLConnection:
    """
    Manages SPARQL endpoint connections and query execution.
    """

    def __init__(self):
        """Initialize the SPARQL connection."""
        self._log = logging.getLogger(__name__)
        
        # Connection settings
        self._endpoint: Optional[str] = None
        self._wrapper: Optional[Wrapper] = None
        
        # Query configuration
        self._prefixes: Dict[str, str] = {}
        self._headers: List[str] = []
        self._method = "POST"
        self._result_format = "json"
        self._display_format = "table"
        self._result_limit: Optional[int] = 100
        self._languages: List[str] = ["en"]
        
        # Authentication
        self._auth_type: Optional[str] = None
        self._username: Optional[str] = None
        self._password: Optional[str] = None
        
        # Custom parameters
        self._query_params: Dict[str, str] = {}

    def has_endpoint(self) -> bool:
        """Check if an endpoint is configured."""
        return self._endpoint is not None

    def get_endpoint(self) -> Optional[str]:
        """Get the current endpoint URL."""
        return self._endpoint

    def set_endpoint(self, url: str):
        """Set the SPARQL endpoint URL."""
        self._endpoint = url
        self._wrapper = Wrapper(url)
        self._configure_wrapper()
        self._log.info(f"Endpoint set to: {url}")

    def _configure_wrapper(self):
        """Configure the SPARQLWrapper with current settings."""
        if not self._wrapper:
            return
        
        # Set method
        if self._method == "POST":
            self._wrapper.setMethod(SPARQLWrapper.POST)
        else:
            self._wrapper.setMethod(SPARQLWrapper.GET)
        
        # Set result format
        if self._result_format == "json":
            self._wrapper.setReturnFormat(SPARQLWrapper.JSON)
        elif self._result_format == "xml":
            self._wrapper.setReturnFormat(SPARQLWrapper.XML)
        elif self._result_format == "csv":
            self._wrapper.setReturnFormat(SPARQLWrapper.CSV)
        elif self._result_format == "tsv":
            self._wrapper.setReturnFormat(SPARQLWrapper.TSV)
        
        # Set authentication
        if self._auth_type and self._username and self._password:
            if self._auth_type == "basic":
                self._wrapper.setHTTPAuth(SPARQLWrapper.BASIC)
            elif self._auth_type == "digest":
                self._wrapper.setHTTPAuth(SPARQLWrapper.DIGEST)
            self._wrapper.setCredentials(self._username, self._password)
        
        # Set custom parameters
        for name, value in self._query_params.items():
            self._wrapper.addParameter(name, value)

    def add_prefix(self, name: str, uri: str):
        """Add a persistent SPARQL prefix."""
        self._prefixes[name] = uri
        self._log.debug(f"Added prefix: {name} -> {uri}")

    def add_header(self, header: str):
        """Add a persistent SPARQL header line."""
        self._headers.append(header)
        self._log.debug(f"Added header: {header}")

    def clear_headers(self):
        """Clear all persistent headers."""
        self._headers.clear()
        self._log.debug("Cleared all headers")

    def set_method(self, method: str):
        """Set HTTP method (GET or POST)."""
        self._method = method.upper()
        if self._wrapper:
            self._configure_wrapper()

    def set_result_format(self, format: str):
        """Set SPARQL result format."""
        self._result_format = format.lower()
        if self._wrapper:
            self._configure_wrapper()

    def set_display_format(self, format: str):
        """Set display format for results."""
        self._display_format = format.lower()

    def set_result_limit(self, limit: Optional[int]):
        """Set maximum number of results to show."""
        self._result_limit = limit

    def get_languages(self) -> List[str]:
        """Get preferred languages."""
        return self._languages

    def set_languages(self, langs: List[str]):
        """Set preferred languages."""
        self._languages = langs

    def set_auth(self, auth_type: Optional[str], username: Optional[str], password: Optional[str]):
        """Set HTTP authentication."""
        self._auth_type = auth_type
        self._username = username
        self._password = password
        if self._wrapper:
            self._configure_wrapper()

    def add_query_param(self, name: str, value: str):
        """Add a custom query parameter."""
        self._query_params[name] = value
        if self._wrapper:
            self._configure_wrapper()

    def _build_query(self, query: str) -> str:
        """
        Build the complete query with prefixes and headers.
        
        Args:
            query: The base SPARQL query
            
        Returns:
            Complete query string
        """
        parts = []
        
        # Add prefixes
        for name, uri in self._prefixes.items():
            parts.append(f"PREFIX {name}: <{uri}>")
        
        # Add headers
        parts.extend(self._headers)
        
        # Add the query
        parts.append(query)
        
        return "\n".join(parts)

    def query(self, query: str, num: int = 0) -> str:
        """
        Execute a SPARQL query.
        
        Args:
            query: The SPARQL query to execute
            num: Execution number (for logging)
            
        Returns:
            Formatted results as a string
        """
        if not self._wrapper:
            raise Exception("No SPARQL endpoint configured. Use %endpoint to set one.")
        
        # Build complete query
        full_query = self._build_query(query)
        self._log.debug(f"Executing query #{num}:\n{full_query}")
        
        try:
            # Set the query
            self._wrapper.setQuery(full_query)
            
            # Execute
            results = self._wrapper.query()
            
            # Convert and format results
            return self._format_results(results)
            
        except Exception as e:
            self._log.error(f"Query error: {e}")
            raise Exception(f"SPARQL query error: {e}")

    def _format_results(self, results) -> str:
        """
        Format query results for display.
        
        Args:
            results: SPARQLWrapper query results
            
        Returns:
            Formatted result string
        """
        try:
            if self._result_format == "json":
                data = results.convert()
                return self._format_json_results(data)
            else:
                # For other formats, return raw data
                return str(results.response.read().decode('utf-8'))
        except Exception as e:
            self._log.error(f"Error formatting results: {e}")
            return f"Error formatting results: {e}"

    def _format_json_results(self, data: dict) -> str:
        """
        Format JSON results.
        
        Args:
            data: JSON result data
            
        Returns:
            Formatted string
        """
        if "results" in data and "bindings" in data["results"]:
            bindings = data["results"]["bindings"]
            
            if not bindings:
                return "No results"
            
            if self._display_format == "table":
                return self._format_table(data["head"]["vars"], bindings)
            else:
                # Raw format
                return json.dumps(data, indent=2)
        elif "boolean" in data:
            # ASK query result
            return f"Result: {data['boolean']}"
        else:
            # Unknown format, return as JSON
            return json.dumps(data, indent=2)

    def _format_table(self, variables: List[str], bindings: List[dict]) -> str:
        """
        Format results as a text table.
        
        Args:
            variables: Variable names
            bindings: Result bindings
            
        Returns:
            Formatted table string
        """
        # Apply limit
        display_bindings = bindings
        if self._result_limit and len(bindings) > self._result_limit:
            display_bindings = bindings[:self._result_limit]
            truncated = True
        else:
            truncated = False
        
        # Calculate column widths
        widths = {var: len(var) for var in variables}
        for binding in display_bindings:
            for var in variables:
                if var in binding:
                    value = self._get_binding_value(binding[var])
                    widths[var] = max(widths[var], len(value))
        
        # Build table
        lines = []
        
        # Header
        header = " | ".join(var.ljust(widths[var]) for var in variables)
        lines.append(header)
        lines.append("-" * len(header))
        
        # Rows
        for binding in display_bindings:
            row = " | ".join(
                self._get_binding_value(binding.get(var, {})).ljust(widths[var])
                for var in variables
            )
            lines.append(row)
        
        # Footer
        result_count = len(bindings)
        if truncated:
            lines.append(f"\n({self._result_limit} of {result_count} results shown)")
        else:
            lines.append(f"\n({result_count} result{'s' if result_count != 1 else ''})")
        
        return "\n".join(lines)

    def _get_binding_value(self, binding: dict) -> str:
        """
        Extract value from a binding.
        
        Args:
            binding: SPARQL binding dictionary
            
        Returns:
            String value
        """
        if not binding:
            return ""
        
        if "value" in binding:
            value = binding["value"]
            binding_type = binding.get("type", "")
            
            if binding_type == "uri":
                # For URIs, show the full URI or abbreviate if possible
                return value
            elif binding_type == "literal":
                # For literals, show value with language tag if present
                lang = binding.get("xml:lang")
                if lang:
                    return f"{value}@{lang}"
                return value
            else:
                return str(value)
        
        return str(binding)
