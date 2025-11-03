"""Entry point for the RDF kernel."""

from ipykernel.kernelapp import IPKernelApp
from .kernel import RDFKernel


def main():
    """Launch the RDF kernel."""
    IPKernelApp.launch_instance(kernel_class=RDFKernel)


if __name__ == "__main__":
    main()
