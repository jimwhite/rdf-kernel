"""Install the RDF kernel spec."""

import json
import os
import sys
import argparse
from pathlib import Path
from jupyter_client.kernelspec import KernelSpecManager


def install_kernel_spec(user=True, prefix=None):
    """
    Install the RDF kernel specification.
    
    Args:
        user: Install for current user (True) or system-wide (False)
        prefix: Installation prefix
        
    Returns:
        Exit code (0 for success, 1 for error)
    """
    # Create the kernel.json specification
    kernel_json = {
        "argv": [
            sys.executable,
            "-m",
            "rdf_kernel",
            "-f",
            "{connection_file}"
        ],
        "display_name": "RDF",
        "language": "rdf",
        "interrupt_mode": "signal",
        "metadata": {
            "debugger": False
        }
    }
    
    # Get the directory where this script is located
    here = Path(__file__).parent.absolute()
    
    # Create a temporary directory for kernel spec
    kernel_spec_dir = here / "kernel_spec"
    kernel_spec_dir.mkdir(exist_ok=True)
    
    # Write kernel.json
    kernel_json_path = kernel_spec_dir / "kernel.json"
    with open(kernel_json_path, "w") as f:
        json.dump(kernel_json, f, indent=2)
    
    # Install the kernel spec
    ksm = KernelSpecManager()
    
    print("Installing RDF kernel spec...")
    try:
        ksm.install_kernel_spec(
            str(kernel_spec_dir),
            kernel_name="rdf",
            user=user,
            prefix=prefix,
            replace=True
        )
        print("RDF kernel installed successfully!")
        print(f"Kernel installed for {'user' if user else 'system'}")
        
        # Show where it was installed
        kernel_dir = ksm.get_kernel_spec("rdf").resource_dir
        print(f"Kernel spec installed to: {kernel_dir}")
        
        return 0
        
    except Exception as e:
        print(f"Error installing kernel spec: {e}", file=sys.stderr)
        return 1


def main():
    """Main entry point for kernel installation."""
    parser = argparse.ArgumentParser(
        description="Install the RDF Jupyter kernel spec"
    )
    parser.add_argument(
        "--user",
        action="store_true",
        default=True,
        help="Install for the current user (default)"
    )
    parser.add_argument(
        "--system",
        action="store_true",
        help="Install system-wide"
    )
    parser.add_argument(
        "--prefix",
        help="Installation prefix"
    )
    
    args = parser.parse_args()
    
    # Determine user vs system
    user = not args.system if not args.prefix else args.user
    
    return install_kernel_spec(user=user, prefix=args.prefix)


if __name__ == "__main__":
    sys.exit(main())
