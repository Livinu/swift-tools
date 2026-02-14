#!/usr/bin/env python3
"""
BIC/SWIFT Code Validator
Validation et parsing des codes BIC (Bank Identifier Code)
"""

import re
from dataclasses import dataclass
from typing import Optional


@dataclass
class BICCode:
    """Représentation d'un code BIC/SWIFT"""
    bank_code: str      # 4 lettres
    country_code: str   # 2 lettres (ISO 3166)
    location_code: str  # 2 caractères alphanumériques
    branch_code: Optional[str] = None  # 3 caractères (optionnel)
    
    @property
    def full_code(self) -> str:
        """Retourne le code BIC complet"""
        base = f"{self.bank_code}{self.country_code}{self.location_code}"
        return f"{base}{self.branch_code}" if self.branch_code else base
    
    @property
    def is_primary_office(self) -> bool:
        """Vérifie si c'est le siège principal (XXX ou absent)"""
        return self.branch_code is None or self.branch_code == "XXX"
    
    @classmethod
    def parse(cls, bic: str) -> "BICCode":
        """
        Parse un code BIC/SWIFT
        
        Args:
            bic: Code BIC de 8 ou 11 caractères
            
        Returns:
            BICCode: Instance du code BIC parsé
            
        Raises:
            ValueError: Si le format est invalide
        """
        bic = bic.upper().strip()
        
        if len(bic) not in (8, 11):
            raise ValueError(
                f"Le code BIC doit contenir 8 ou 11 caractères, reçu {len(bic)}"
            )
        
        pattern = r'^([A-Z]{4})([A-Z]{2})([A-Z0-9]{2})([A-Z0-9]{3})?$'
        match = re.match(pattern, bic)
        
        if not match:
            raise ValueError(f"Format BIC invalide: {bic}")
        
        return cls(
            bank_code=match.group(1),
            country_code=match.group(2),
            location_code=match.group(3),
            branch_code=match.group(4)
        )
    
    def validate(self) -> bool:
        """
        Valide le format du code BIC
        
        Returns:
            bool: True si le format est valide
        """
        try:
            BICCode.parse(self.full_code)
            return True
        except ValueError:
            return False
    
    def get_country_name(self) -> str:
        """Retourne le nom du pays basé sur le code ISO"""
        countries = {
            "FR": "France",
            "DE": "Allemagne", 
            "GB": "Royaume-Uni",
            "US": "États-Unis",
            "ES": "Espagne",
            "IT": "Italie",
            "BE": "Belgique",
            "NL": "Pays-Bas",
            "CH": "Suisse",
            "LU": "Luxembourg",
            "AT": "Autriche",
            "PT": "Portugal",
        }
        return countries.get(self.country_code, "Inconnu")
    
    def __str__(self) -> str:
        return self.full_code
    
    def __repr__(self) -> str:
        return f"BICCode('{self.full_code}')"


def validate_bic(bic: str) -> tuple[bool, str]:
    """
    Valide un code BIC et retourne le résultat
    
    Args:
        bic: Code BIC à valider
        
    Returns:
        tuple: (is_valid, message)
    """
    try:
        parsed = BICCode.parse(bic)
        return True, f"BIC valide: {parsed.full_code} ({parsed.get_country_name()})"
    except ValueError as e:
        return False, str(e)


# Exemples de codes BIC connus
KNOWN_BICS = {
    "BNPAFRPP": "BNP Paribas (France)",
    "COBADEFF": "Commerzbank (Allemagne)",
    "DEUTDEFF": "Deutsche Bank (Allemagne)",
    "BARCGB22": "Barclays (UK)",
    "CHASUS33": "JPMorgan Chase (USA)",
    "SOGEFRPP": "Société Générale (France)",
    "CRLYFRPP": "Crédit Lyonnais (France)",
    "AGRIFRPP": "Crédit Agricole (France)",
}


if __name__ == "__main__":
    print("=" * 60)
    print("BIC/SWIFT Code Validator")
    print("=" * 60)
    
    # Test avec différents codes BIC
    test_codes = [
        "BNPAFRPPXXX",  # BNP Paribas avec code agence
        "BNPAFRPP",     # BNP Paribas sans code agence
        "COBADEFFXXX",  # Commerzbank
        "DEUTDEFF",     # Deutsche Bank
        "INVALID",      # Code invalide
        "BNPA",         # Trop court
    ]
    
    print("\nValidation de codes BIC:")
    print("-" * 60)
    
    for code in test_codes:
        is_valid, message = validate_bic(code)
        status = "✓" if is_valid else "✗"
        print(f"{status} {code:15} : {message}")
    
    print("\n" + "-" * 60)
    print("\nDétails d'un code BIC valide:")
    print("-" * 60)
    
    bic = BICCode.parse("BNPAFRPPXXX")
    print(f"Code complet    : {bic.full_code}")
    print(f"Code banque     : {bic.bank_code}")
    print(f"Code pays       : {bic.country_code} ({bic.get_country_name()})")
    print(f"Code localisation: {bic.location_code}")
    print(f"Code agence     : {bic.branch_code}")
    print(f"Siège principal : {'Oui' if bic.is_primary_office else 'Non'}")
