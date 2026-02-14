"""
SWIFT Banking System - Code Examples

Ce module contient des exemples de code pour implémenter
un système bancaire conforme aux normes SWIFT et ISO 20022.

Modules disponibles:
- bic_validator: Validation des codes BIC/SWIFT
- iban_validator: Validation des numéros IBAN (ISO 13616)
- iso20022_generator: Génération de messages ISO 20022 (pain.001)
- mt103_generator: Génération de messages MT103 (format legacy)

Exemple d'utilisation:
    from swift.code.bic_validator import BICCode, validate_bic
    from swift.code.iban_validator import IBAN, validate_iban
    from swift.code.iso20022_generator import ISO20022Generator, PaymentInstruction
    from swift.code.mt103_generator import MT103Message, Party
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
