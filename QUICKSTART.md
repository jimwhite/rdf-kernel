# Quick Start Guide for RDF Kernel

## Installation

### Step 1: Install dependencies

```bash
pip install -r requirements.txt
```

Or install the package directly (which will install all dependencies):

```bash
pip install -e .
```

### Step 2: Register the kernel with Jupyter

```bash
install-rdf-kernel --user
```

### Step 3: Verify installation

Check that the kernel is installed:

```bash
jupyter kernelspec list
```

You should see `rdf` in the list of available kernels.

### Step 4: Start Jupyter

```bash
jupyter notebook
```

Or use JupyterLab:

```bash
jupyter lab
```

### Step 5: Create a new notebook

1. Click "New" in Jupyter Notebook (or the "+" icon in JupyterLab)
2. Select "RDF" from the kernel list
3. Start querying!

## First SPARQL Query

Try this in your first cell:

```sparql
%endpoint https://dbpedia.org/sparql
%prefix dbo: <http://dbpedia.org/ontology/>
%mode sparql
```

Then in the next cell:

```sparql
SELECT ?city ?population
WHERE {
  ?city a dbo:City ;
        dbo:country <http://dbpedia.org/resource/France> ;
        dbo:populationTotal ?population .
}
ORDER BY DESC(?population)
LIMIT 5
```

## First SHACL Validation

In a new cell, define shapes:

```python
%shapes
```

```turtle
@prefix sh: <http://www.w3.org/ns/shacl#> .
@prefix ex: <http://example.org/> .

ex:PersonShape
    a sh:NodeShape ;
    sh:targetClass ex:Person ;
    sh:property [
        sh:path ex:name ;
        sh:minCount 1 ;
    ] .
```

Then add data:

```python
%data
```

```turtle
@prefix ex: <http://example.org/> .

ex:john a ex:Person ;
    ex:name "John Doe" .
```

And validate:

```python
%validate
```

## Getting Help

Use `%help` in any cell to see all available magic commands.

## Example Notebook

Open `examples.ipynb` for more comprehensive examples.

## Troubleshooting

### Kernel not appearing in Jupyter

Make sure you ran `install-rdf-kernel --user` after installation.

### Import errors

Make sure all dependencies are installed:
```bash
pip install -r requirements.txt
```

### SPARQL queries not working

Make sure you've set an endpoint:
```sparql
%endpoint https://your-sparql-endpoint.com/sparql
```

### Need more help?

Check the main README.md or open an issue on GitHub.
