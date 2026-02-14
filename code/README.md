# SWIFT Banking Code Examples

Ce dossier contient des exemples de code Python pour implémenter un système bancaire conforme aux normes SWIFT et ISO 20022.

## Structure des fichiers

```
code/
├── __init__.py           # Module package
├── bic_validator.py      # Validation des codes BIC/SWIFT
├── iban_validator.py     # Validation IBAN (ISO 13616)
├── iso20022_generator.py # Génération messages ISO 20022
├── mt103_generator.py    # Génération messages MT103 (legacy)
└── README.md             # Ce fichier
```

## Prérequis

- Python 3.10+
- Aucune dépendance externe requise (utilise uniquement la bibliothèque standard)

## Utilisation

### Validation BIC/SWIFT

```python
from bic_validator import BICCode, validate_bic

# Validation simple
is_valid, message = validate_bic("BNPAFRPPXXX")
print(message)  # BIC valide: BNPAFRPPXXX (France)

# Parsing détaillé
bic = BICCode.parse("BNPAFRPPXXX")
print(f"Banque: {bic.bank_code}")      # BNPA
print(f"Pays: {bic.country_code}")      # FR
print(f"Location: {bic.location_code}") # PP
print(f"Agence: {bic.branch_code}")     # XXX
```

### Validation IBAN

```python
from iban_validator import IBAN, validate_iban

# Validation simple
is_valid, message = validate_iban("FR7630006000011234567890189")
print(message)  # IBAN valide (France)

# Parsing détaillé
iban = IBAN("FR7630006000011234567890189")
print(f"Formaté: {iban.formatted}")     # FR76 3000 6000 0112 3456 7890 189
print(f"Pays: {iban.country_name}")     # France
print(f"Clé: {iban.check_digits}")      # 76
print(f"BBAN: {iban.bban}")             # 30006000011234567890189
```

### Génération ISO 20022 (pain.001)

```python
from iso20022_generator import ISO20022Generator, PaymentInstruction, PaymentBatch

# Créer une instruction de paiement
payment = PaymentInstruction(
    instruction_id="INSTR-001",
    amount=1500.00,
    currency="EUR",
    debtor_name="Société ABC",
    debtor_iban="FR7630006000011234567890189",
    debtor_bic="BNPAFRPPXXX",
    creditor_name="Fournisseur XYZ",
    creditor_iban="DE89370400440532013000",
    creditor_bic="COBADEFFXXX",
    remittance_info="Facture 2026-001"
)

# Créer un lot de paiements
batch = PaymentBatch(
    payment_info_id="BATCH-001",
    payments=[payment]
)

# Générer le XML
generator = ISO20022Generator()
xml = generator.generate_pain001(
    message_id="MSG-001",
    initiating_party_name="Société ABC",
    batches=[batch]
)
print(xml)
```

### Génération MT103 (Legacy)

```python
from mt103_generator import MT103Message, Party

# Créer les parties
ordering = Party(
    name="SOCIETE ABC SARL",
    account="FR7630006000011234567890189",
    address_line1="123 RUE DE PARIS",
    address_line2="75001 PARIS"
)

beneficiary = Party(
    name="FOURNISSEUR XYZ GMBH",
    account="DE89370400440532013000",
    address_line1="HAUPTSTRASSE 1",
    address_line2="60311 FRANKFURT"
)

# Créer le message
mt103 = MT103Message(
    sender_reference="REF20260214001",
    bank_operation_code="CRED",
    value_date=datetime.now(),
    currency="EUR",
    amount=15000.00,
    ordering_customer=ordering,
    ordering_institution="BNPAFRPPXXX",
    beneficiary_customer=beneficiary,
    beneficiary_institution="COBADEFFXXX",
    remittance_info="INVOICE 2026-001",
    charges="SHA"
)

# Générer le message
print(mt103.generate())
```

## Exécution des exemples

```bash
# Exécuter chaque module individuellement
python bic_validator.py
python iban_validator.py
python iso20022_generator.py
python mt103_generator.py
```

## Références

- [SWIFT Standards](https://www.swift.com/standards)
- [ISO 20022](https://www.iso20022.org/)
- [ISO 13616 (IBAN)](https://www.iso.org/standard/81090.html)
