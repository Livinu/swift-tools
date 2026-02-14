#!/usr/bin/env python3
"""
SWIFT MT103 Message Generator
Génération de messages MT103 (Single Customer Credit Transfer)
Format legacy pré-ISO 20022
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List
import re


@dataclass
class Party:
    """Représentation d'une partie (client/banque)"""
    name: str
    account: Optional[str] = None
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    address_line3: Optional[str] = None
    
    def to_lines(self, max_lines: int = 4, line_length: int = 35) -> List[str]:
        """Convertit en lignes formatées SWIFT"""
        lines = []
        if self.account:
            lines.append(f"/{self.account}")
        lines.append(self.name[:line_length])
        if self.address_line1:
            lines.append(self.address_line1[:line_length])
        if self.address_line2:
            lines.append(self.address_line2[:line_length])
        if self.address_line3:
            lines.append(self.address_line3[:line_length])
        return lines[:max_lines]


@dataclass 
class MT103Message:
    """
    Message SWIFT MT103 - Single Customer Credit Transfer
    
    Structure des blocs SWIFT:
    - Block 1: Basic Header
    - Block 2: Application Header
    - Block 3: User Header (optionnel)
    - Block 4: Text Block (contenu du message)
    - Block 5: Trailer
    """
    
    # Identifiants
    sender_reference: str           # :20: Transaction Reference Number
    bank_operation_code: str        # :23B: Bank Operation Code
    
    # Montant et date
    value_date: datetime            # :32A: Value Date
    currency: str                   # :32A: Currency
    amount: float                   # :32A: Amount
    
    # Parties
    ordering_customer: Party        # :50K: Ordering Customer
    ordering_institution: str       # :52A: Ordering Institution BIC
    beneficiary_customer: Party     # :59: Beneficiary Customer
    beneficiary_institution: str    # :57A: Account With Institution BIC
    
    # Informations additionnelles
    remittance_info: str            # :70: Remittance Information
    charges: str = "SHA"            # :71A: Details of Charges (SHA/OUR/BEN)
    
    # En-têtes (optionnels, générés automatiquement si non fournis)
    sender_bic: str = "BNPAFRPPAXXX"
    receiver_bic: str = "COBADEFFXXX"
    
    # Champs optionnels
    instructed_amount: Optional[float] = None  # :33B:
    instruction_code: Optional[str] = None     # :23E:
    sender_to_receiver_info: Optional[str] = None  # :72:
    
    def _format_amount(self, amount: float) -> str:
        """Formate le montant selon le standard SWIFT (virgule décimale)"""
        return f"{amount:.2f}".replace(".", ",")
    
    def _generate_block1(self) -> str:
        """Block 1: Basic Header"""
        # F = FIN, 01 = Application ID, sender BIC, session/sequence
        return f"{{1:F01{self.sender_bic}0000000000}}"
    
    def _generate_block2(self) -> str:
        """Block 2: Application Header Input"""
        # I = Input, 103 = MT103, receiver BIC, N = Normal priority
        return f"{{2:I103{self.receiver_bic}N}}"
    
    def _generate_block3(self) -> str:
        """Block 3: User Header"""
        return "{3:{108:MT103}}"
    
    def _generate_block4(self) -> str:
        """Block 4: Text Block - Le contenu principal du message"""
        lines = ["{4:"]
        
        # :20: Transaction Reference Number (obligatoire)
        lines.append(f":20:{self.sender_reference[:16]}")
        
        # :23B: Bank Operation Code (obligatoire)
        lines.append(f":23B:{self.bank_operation_code}")
        
        # :23E: Instruction Code (optionnel)
        if self.instruction_code:
            lines.append(f":23E:{self.instruction_code}")
        
        # :32A: Value Date/Currency/Amount (obligatoire)
        date_str = self.value_date.strftime("%y%m%d")
        amount_str = self._format_amount(self.amount)
        lines.append(f":32A:{date_str}{self.currency}{amount_str}")
        
        # :33B: Currency/Instructed Amount (optionnel)
        if self.instructed_amount:
            inst_amount_str = self._format_amount(self.instructed_amount)
            lines.append(f":33B:{self.currency}{inst_amount_str}")
        
        # :50K: Ordering Customer (obligatoire)
        lines.append(":50K:" + "\n".join(self.ordering_customer.to_lines()))
        
        # :52A: Ordering Institution (optionnel mais recommandé)
        lines.append(f":52A:{self.ordering_institution}")
        
        # :57A: Account With Institution (optionnel)
        lines.append(f":57A:{self.beneficiary_institution}")
        
        # :59: Beneficiary Customer (obligatoire)
        lines.append(":59:" + "\n".join(self.beneficiary_customer.to_lines()))
        
        # :70: Remittance Information (optionnel)
        # Limité à 4 lignes de 35 caractères
        remit_lines = [self.remittance_info[i:i+35] 
                       for i in range(0, len(self.remittance_info), 35)][:4]
        lines.append(":70:" + "\n".join(remit_lines))
        
        # :71A: Details of Charges (obligatoire)
        lines.append(f":71A:{self.charges}")
        
        # :72: Sender to Receiver Information (optionnel)
        if self.sender_to_receiver_info:
            s2r_lines = [self.sender_to_receiver_info[i:i+35]
                        for i in range(0, len(self.sender_to_receiver_info), 35)][:6]
            lines.append(":72:" + "\n".join(s2r_lines))
        
        lines.append("-}")
        return "\n".join(lines)
    
    def _generate_block5(self) -> str:
        """Block 5: Trailer"""
        # CHK = Checksum (simplifié pour l'exemple)
        return "{5:{CHK:123456789ABC}}"
    
    def generate(self) -> str:
        """
        Génère le message MT103 complet au format SWIFT
        
        Returns:
            str: Message MT103 formaté
        """
        blocks = [
            self._generate_block1(),
            self._generate_block2(),
            self._generate_block3(),
            self._generate_block4(),
            self._generate_block5(),
        ]
        return "\n".join(blocks)
    
    def validate(self) -> List[str]:
        """
        Valide le message MT103
        
        Returns:
            List[str]: Liste des erreurs de validation (vide si valide)
        """
        errors = []
        
        # Validation :20: (1-16 caractères)
        if not self.sender_reference or len(self.sender_reference) > 16:
            errors.append(":20: Sender Reference doit contenir 1-16 caractères")
        
        # Validation :23B: (4 caractères alphabétiques)
        if not re.match(r'^[A-Z]{4}$', self.bank_operation_code):
            errors.append(":23B: Bank Operation Code doit être 4 lettres (ex: CRED)")
        
        # Validation :32A: Currency (3 lettres ISO)
        if not re.match(r'^[A-Z]{3}$', self.currency):
            errors.append(":32A: Currency doit être un code ISO 3 lettres (ex: EUR)")
        
        # Validation :32A: Amount (positif)
        if self.amount <= 0:
            errors.append(":32A: Amount doit être positif")
        
        # Validation :71A: Charges
        if self.charges not in ("SHA", "OUR", "BEN"):
            errors.append(":71A: Charges doit être SHA, OUR ou BEN")
        
        # Validation BIC
        bic_pattern = r'^[A-Z]{4}[A-Z]{2}[A-Z0-9]{2}([A-Z0-9]{3})?$'
        if not re.match(bic_pattern, self.ordering_institution):
            errors.append(":52A: Ordering Institution BIC invalide")
        if not re.match(bic_pattern, self.beneficiary_institution):
            errors.append(":57A: Beneficiary Institution BIC invalide")
        
        return errors


# Codes d'opération bancaire courants
BANK_OPERATION_CODES = {
    "CRED": "Credit Transfer",
    "CRTS": "Credit Transfer for Securities",
    "SPAY": "Special Payment",
    "SPRI": "Priority Payment",
    "SSTD": "Standard Payment",
}

# Types de frais
CHARGE_TYPES = {
    "SHA": "Shared (frais partagés entre émetteur et bénéficiaire)",
    "OUR": "Our (tous les frais à la charge de l'émetteur)",
    "BEN": "Beneficiary (tous les frais à la charge du bénéficiaire)",
}


def create_sample_mt103() -> MT103Message:
    """Crée un exemple de message MT103"""
    return MT103Message(
        sender_reference="REF20260214001",
        bank_operation_code="CRED",
        value_date=datetime.now(),
        currency="EUR",
        amount=15000.00,
        ordering_customer=Party(
            name="SOCIETE ABC SARL",
            account="FR7630006000011234567890189",
            address_line1="123 RUE DE PARIS",
            address_line2="75001 PARIS",
            address_line3="FRANCE"
        ),
        ordering_institution="BNPAFRPPXXX",
        beneficiary_customer=Party(
            name="FOURNISSEUR XYZ GMBH",
            account="DE89370400440532013000",
            address_line1="HAUPTSTRASSE 1",
            address_line2="60311 FRANKFURT",
            address_line3="GERMANY"
        ),
        beneficiary_institution="COBADEFFXXX",
        remittance_info="INVOICE 2026-001 PAYMENT FOR SERVICES",
        charges="SHA",
        sender_to_receiver_info="/ACC/URGENT PAYMENT"
    )


if __name__ == "__main__":
    print("=" * 70)
    print("SWIFT MT103 Message Generator")
    print("=" * 70)
    
    # Création d'un message exemple
    mt103 = create_sample_mt103()
    
    # Validation
    errors = mt103.validate()
    if errors:
        print("\n⚠️  Erreurs de validation:")
        for error in errors:
            print(f"  - {error}")
    else:
        print("\n✓ Message valide")
    
    # Génération du message
    print("\n" + "-" * 70)
    print("Message MT103 généré:")
    print("-" * 70)
    print(mt103.generate())
    
    # Information sur les codes
    print("\n" + "-" * 70)
    print("Référence des codes:")
    print("-" * 70)
    
    print("\nCodes d'opération bancaire (:23B:):")
    for code, desc in BANK_OPERATION_CODES.items():
        print(f"  {code}: {desc}")
    
    print("\nTypes de frais (:71A:):")
    for code, desc in CHARGE_TYPES.items():
        print(f"  {code}: {desc}")
