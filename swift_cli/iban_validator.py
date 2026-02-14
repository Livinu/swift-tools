#!/usr/bin/env python3
"""
IBAN Validator
Validation des numéros IBAN selon la norme ISO 13616
"""

import re
from dataclasses import dataclass
from typing import Dict, Tuple

# Longueurs IBAN par pays (ISO 13616)
IBAN_LENGTHS: Dict[str, int] = {
    "AD": 24,  # Andorre
    "AT": 20,  # Autriche
    "BE": 16,  # Belgique
    "CH": 21,  # Suisse
    "CY": 28,  # Chypre
    "CZ": 24,  # République Tchèque
    "DE": 22,  # Allemagne
    "DK": 18,  # Danemark
    "EE": 20,  # Estonie
    "ES": 24,  # Espagne
    "FI": 18,  # Finlande
    "FR": 27,  # France
    "GB": 22,  # Royaume-Uni
    "GR": 27,  # Grèce
    "HR": 21,  # Croatie
    "HU": 28,  # Hongrie
    "IE": 22,  # Irlande
    "IS": 26,  # Islande
    "IT": 27,  # Italie
    "LI": 21,  # Liechtenstein
    "LT": 20,  # Lituanie
    "LU": 20,  # Luxembourg
    "LV": 21,  # Lettonie
    "MC": 27,  # Monaco
    "MT": 31,  # Malte
    "NL": 18,  # Pays-Bas
    "NO": 15,  # Norvège
    "PL": 28,  # Pologne
    "PT": 25,  # Portugal
    "RO": 24,  # Roumanie
    "SE": 24,  # Suède
    "SI": 19,  # Slovénie
    "SK": 24,  # Slovaquie
}

# Noms des pays
COUNTRY_NAMES: Dict[str, str] = {
    "AD": "Andorre", "AT": "Autriche", "BE": "Belgique", "CH": "Suisse",
    "CY": "Chypre", "CZ": "République Tchèque", "DE": "Allemagne",
    "DK": "Danemark", "EE": "Estonie", "ES": "Espagne", "FI": "Finlande",
    "FR": "France", "GB": "Royaume-Uni", "GR": "Grèce", "HR": "Croatie",
    "HU": "Hongrie", "IE": "Irlande", "IS": "Islande", "IT": "Italie",
    "LI": "Liechtenstein", "LT": "Lituanie", "LU": "Luxembourg",
    "LV": "Lettonie", "MC": "Monaco", "MT": "Malte", "NL": "Pays-Bas",
    "NO": "Norvège", "PL": "Pologne", "PT": "Portugal", "RO": "Roumanie",
    "SE": "Suède", "SI": "Slovénie", "SK": "Slovaquie",
}


@dataclass
class IBAN:
    """Représentation et validation d'un numéro IBAN"""
    raw_iban: str
    
    def __post_init__(self):
        """Nettoie l'IBAN à la création"""
        self.raw_iban = self.raw_iban.replace(" ", "").upper()
    
    @property
    def formatted(self) -> str:
        """IBAN formaté avec espaces tous les 4 caractères"""
        return " ".join(
            self.raw_iban[i:i+4] 
            for i in range(0, len(self.raw_iban), 4)
        )
    
    @property
    def country_code(self) -> str:
        """Code pays (2 premières lettres)"""
        return self.raw_iban[:2]
    
    @property
    def check_digits(self) -> str:
        """Chiffres de contrôle (positions 3-4)"""
        return self.raw_iban[2:4]
    
    @property
    def bban(self) -> str:
        """Basic Bank Account Number (après les 4 premiers caractères)"""
        return self.raw_iban[4:]
    
    @property
    def country_name(self) -> str:
        """Nom du pays"""
        return COUNTRY_NAMES.get(self.country_code, "Inconnu")
    
    def validate(self) -> Tuple[bool, str]:
        """
        Valide l'IBAN selon l'algorithme ISO 13616
        
        Returns:
            tuple: (is_valid, message)
        """
        iban = self.raw_iban
        
        # Vérification du format de base
        if not re.match(r'^[A-Z]{2}[0-9]{2}[A-Z0-9]+$', iban):
            return False, "Format IBAN invalide (doit commencer par 2 lettres + 2 chiffres)"
        
        # Vérification de la longueur minimale
        if len(iban) < 15:
            return False, f"IBAN trop court: {len(iban)} caractères (minimum 15)"
        
        # Vérification de la longueur par pays
        country = iban[:2]
        if country in IBAN_LENGTHS:
            expected_length = IBAN_LENGTHS[country]
            if len(iban) != expected_length:
                return False, (
                    f"Longueur incorrecte pour {country} ({self.country_name}): "
                    f"attendu {expected_length}, reçu {len(iban)}"
                )
        else:
            # Pays non reconnu, vérification basique uniquement
            pass
        
        # Algorithme de validation MOD-97 (ISO 7064)
        # Étape 1: Réorganiser (déplacer les 4 premiers caractères à la fin)
        rearranged = iban[4:] + iban[:4]
        
        # Étape 2: Conversion des lettres en chiffres (A=10, B=11, ..., Z=35)
        numeric = ""
        for char in rearranged:
            if char.isalpha():
                numeric += str(ord(char) - ord('A') + 10)
            else:
                numeric += char
        
        # Étape 3: Vérification MOD 97
        remainder = int(numeric) % 97
        if remainder != 1:
            return False, f"Clé de contrôle IBAN invalide (reste: {remainder}, attendu: 1)"
        
        return True, f"IBAN valide ({self.country_name})"
    
    @classmethod
    def generate_check_digits(cls, country_code: str, bban: str) -> str:
        """
        Génère les chiffres de contrôle pour un BBAN donné
        
        Args:
            country_code: Code pays ISO (2 lettres)
            bban: Basic Bank Account Number
            
        Returns:
            str: Les 2 chiffres de contrôle
        """
        # Construction de l'IBAN temporaire avec "00" comme clé
        temp_iban = bban + country_code + "00"
        
        # Conversion en numérique
        numeric = ""
        for char in temp_iban.upper():
            if char.isalpha():
                numeric += str(ord(char) - ord('A') + 10)
            else:
                numeric += char
        
        # Calcul de la clé
        check = 98 - (int(numeric) % 97)
        return f"{check:02d}"
    
    @classmethod
    def create(cls, country_code: str, bban: str) -> "IBAN":
        """
        Crée un IBAN valide à partir d'un code pays et d'un BBAN
        
        Args:
            country_code: Code pays ISO (2 lettres)
            bban: Basic Bank Account Number
            
        Returns:
            IBAN: Instance IBAN avec clé de contrôle calculée
        """
        check_digits = cls.generate_check_digits(country_code, bban)
        return cls(f"{country_code}{check_digits}{bban}")
    
    def __str__(self) -> str:
        return self.formatted
    
    def __repr__(self) -> str:
        return f"IBAN('{self.raw_iban}')"


def validate_iban(iban_str: str) -> Tuple[bool, str]:
    """
    Fonction utilitaire pour valider un IBAN
    
    Args:
        iban_str: Chaîne IBAN à valider
        
    Returns:
        tuple: (is_valid, message)
    """
    iban = IBAN(iban_str)
    return iban.validate()


if __name__ == "__main__":
    print("=" * 70)
    print("IBAN Validator - ISO 13616")
    print("=" * 70)
    
    # IBANs de test
    test_ibans = [
        "FR76 3000 6000 0112 3456 7890 189",  # France (valide)
        "DE89 3704 0044 0532 0130 00",        # Allemagne (valide)
        "GB82 WEST 1234 5698 7654 32",        # UK (valide)
        "ES91 2100 0418 4502 0005 1332",      # Espagne (valide)
        "IT60 X054 2811 1010 0000 0123 456",  # Italie (valide)
        "BE68 5390 0754 7034",                # Belgique (valide)
        "FR76 3000 6000 0112 3456 7890 188",  # France (clé invalide)
        "INVALID123",                          # Format invalide
        "XX00 1234 5678",                      # Pays inconnu
    ]
    
    print("\nValidation d'IBANs:")
    print("-" * 70)
    
    for iban_str in test_ibans:
        iban = IBAN(iban_str)
        is_valid, message = iban.validate()
        status = "✓" if is_valid else "✗"
        print(f"{status} {iban.formatted:40} : {message}")
    
    print("\n" + "-" * 70)
    print("\nDétails d'un IBAN valide:")
    print("-" * 70)
    
    iban = IBAN("FR7630006000011234567890189")
    is_valid, _ = iban.validate()
    
    print(f"IBAN brut       : {iban.raw_iban}")
    print(f"IBAN formaté    : {iban.formatted}")
    print(f"Code pays       : {iban.country_code} ({iban.country_name})")
    print(f"Clé de contrôle : {iban.check_digits}")
    print(f"BBAN            : {iban.bban}")
    print(f"Valide          : {'Oui' if is_valid else 'Non'}")
    
    print("\n" + "-" * 70)
    print("\nGénération d'un IBAN:")
    print("-" * 70)
    
    # Génération d'un IBAN à partir d'un BBAN
    new_iban = IBAN.create("FR", "30006000011234567890189")
    is_valid, message = new_iban.validate()
    print(f"IBAN généré     : {new_iban.formatted}")
    print(f"Validation      : {message}")
