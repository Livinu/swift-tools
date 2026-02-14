"""SWIFT Banking CLI
=================

A command-line tool for SWIFT banking operations and ISO 20022 message generation.

Modules:
    - bic_validator: BIC/SWIFT code validation
    - iban_validator: IBAN validation (ISO 13616)
    - iso20022_generator: ISO 20022 pain.001 message generation
    - mt103_generator: Legacy SWIFT MT103 message generation
    - main: CLI entry point

Example usage:
    from swift_cli import BICCode, validate_bic
    from swift_cli import IBAN, validate_iban
    from swift_cli import ISO20022Generator, PaymentInstruction
    from swift_cli import MT103Message, Party
"""

__version__ = "1.0.0"
__author__ = "Livinus Tuyisenge"

from .bic_validator import BICCode, validate_bic
from .iban_validator import IBAN, validate_iban
from .iso20022_generator import ISO20022Generator, PaymentInstruction, PaymentBatch
from .mt103_generator import MT103Message, Party

__all__ = [
    "BICCode",
    "validate_bic",
    "IBAN", 
    "validate_iban",
    "ISO20022Generator",
    "PaymentInstruction",
    "PaymentBatch",
    "MT103Message",
    "Party",
]
