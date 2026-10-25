"""ctiac: cyber threat intelligence as code.

The intelligence program held as version-controlled records, with the claims it
makes about itself enforced as CI gates. See docs/CONCEPT.md.

The code is a reference implementation. It exists to show that the gates are
mechanically enforceable rather than aspirational, not to be a platform.
"""
__all__ = ["loader", "schema", "cli", "sanitiser", "canary"]
__version__ = "0.1.0"
