#!/usr/bin/env python3
"""
Tests for SWIFT MT103 Message Generator
"""

import pytest
import sys
import os
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'swift_cli'))

from mt103_generator import MT103Message, Party, BANK_OPERATION_CODES, CHARGE_TYPES


class TestParty:
    """Test cases for Party dataclass"""

    def test_create_party_basic(self):
        """Test creating a basic party"""
        party = Party(name='TEST COMPANY')
        assert party.name == 'TEST COMPANY'
        assert party.account is None

    def test_create_party_with_account(self):
        """Test creating a party with account"""
        party = Party(
            name='TEST COMPANY',
            account='FR7630006000011234567890189'
        )
        assert party.name == 'TEST COMPANY'
        assert party.account == 'FR7630006000011234567890189'

    def test_create_party_with_address(self):
        """Test creating a party with address"""
        party = Party(
            name='TEST COMPANY',
            account='FR7630006000011234567890189',
            address_line1='123 RUE DE PARIS',
            address_line2='75001 PARIS'
        )
        assert party.address_line1 == '123 RUE DE PARIS'
        assert party.address_line2 == '75001 PARIS'

    def test_to_lines_with_account(self):
        """Test to_lines method with account"""
        party = Party(
            name='TEST COMPANY',
            account='FR7630006000011234567890189'
        )
        lines = party.to_lines()
        assert '/FR7630006000011234567890189' in lines
        assert 'TEST COMPANY' in lines

    def test_to_lines_truncation(self):
        """Test that lines are truncated to max length"""
        party = Party(
            name='A' * 50  # More than 35 chars
        )
        lines = party.to_lines()
        assert len(lines[0]) <= 35


class TestMT103Message:
    """Test cases for MT103Message"""

    @pytest.fixture
    def sample_mt103(self):
        """Create a sample MT103 message for testing"""
        ordering = Party(
            name='TEST COMPANY',
            account='FR7630006000011234567890189'
        )
        beneficiary = Party(
            name='BENEFICIARY LTD',
            account='DE89370400440532013000'
        )
        
        return MT103Message(
            sender_reference='REF123456789',
            bank_operation_code='CRED',
            value_date=datetime(2026, 2, 14),
            currency='EUR',
            amount=5000.00,
            ordering_customer=ordering,
            ordering_institution='BNPAFRPPXXX',
            beneficiary_customer=beneficiary,
            beneficiary_institution='COBADEFFXXX',
            remittance_info='TEST PAYMENT',
            charges='SHA'
        )

    def test_validate_valid_message(self, sample_mt103):
        """Test validation of valid MT103 message"""
        errors = sample_mt103.validate()
        assert len(errors) == 0

    def test_validate_invalid_reference(self):
        """Test validation fails for invalid reference"""
        ordering = Party(name='TEST')
        beneficiary = Party(name='BENEFICIARY')
        
        mt103 = MT103Message(
            sender_reference='',  # Empty reference
            bank_operation_code='CRED',
            value_date=datetime.now(),
            currency='EUR',
            amount=1000.00,
            ordering_customer=ordering,
            ordering_institution='BNPAFRPPXXX',
            beneficiary_customer=beneficiary,
            beneficiary_institution='COBADEFFXXX',
            remittance_info='TEST',
            charges='SHA'
        )
        
        errors = mt103.validate()
        assert len(errors) > 0
        assert any(':20:' in e for e in errors)

    def test_validate_invalid_operation_code(self):
        """Test validation fails for invalid bank operation code"""
        ordering = Party(name='TEST')
        beneficiary = Party(name='BENEFICIARY')
        
        mt103 = MT103Message(
            sender_reference='REF123',
            bank_operation_code='INVALID',  # Invalid code
            value_date=datetime.now(),
            currency='EUR',
            amount=1000.00,
            ordering_customer=ordering,
            ordering_institution='BNPAFRPPXXX',
            beneficiary_customer=beneficiary,
            beneficiary_institution='COBADEFFXXX',
            remittance_info='TEST',
            charges='SHA'
        )
        
        errors = mt103.validate()
        assert len(errors) > 0
        assert any(':23B:' in e for e in errors)

    def test_validate_invalid_currency(self):
        """Test validation fails for invalid currency"""
        ordering = Party(name='TEST')
        beneficiary = Party(name='BENEFICIARY')
        
        mt103 = MT103Message(
            sender_reference='REF123',
            bank_operation_code='CRED',
            value_date=datetime.now(),
            currency='EURO',  # Invalid (should be 3 chars)
            amount=1000.00,
            ordering_customer=ordering,
            ordering_institution='BNPAFRPPXXX',
            beneficiary_customer=beneficiary,
            beneficiary_institution='COBADEFFXXX',
            remittance_info='TEST',
            charges='SHA'
        )
        
        errors = mt103.validate()
        assert len(errors) > 0
        assert any(':32A:' in e for e in errors)

    def test_validate_negative_amount(self):
        """Test validation fails for negative amount"""
        ordering = Party(name='TEST')
        beneficiary = Party(name='BENEFICIARY')
        
        mt103 = MT103Message(
            sender_reference='REF123',
            bank_operation_code='CRED',
            value_date=datetime.now(),
            currency='EUR',
            amount=-100.00,  # Negative
            ordering_customer=ordering,
            ordering_institution='BNPAFRPPXXX',
            beneficiary_customer=beneficiary,
            beneficiary_institution='COBADEFFXXX',
            remittance_info='TEST',
            charges='SHA'
        )
        
        errors = mt103.validate()
        assert len(errors) > 0

    def test_validate_invalid_charges(self):
        """Test validation fails for invalid charges type"""
        ordering = Party(name='TEST')
        beneficiary = Party(name='BENEFICIARY')
        
        mt103 = MT103Message(
            sender_reference='REF123',
            bank_operation_code='CRED',
            value_date=datetime.now(),
            currency='EUR',
            amount=1000.00,
            ordering_customer=ordering,
            ordering_institution='BNPAFRPPXXX',
            beneficiary_customer=beneficiary,
            beneficiary_institution='COBADEFFXXX',
            remittance_info='TEST',
            charges='INVALID'  # Invalid
        )
        
        errors = mt103.validate()
        assert len(errors) > 0
        assert any(':71A:' in e for e in errors)

    def test_generate_contains_reference(self, sample_mt103):
        """Test generated message contains reference"""
        message = sample_mt103.generate()
        assert ':20:REF123456789' in message

    def test_generate_contains_operation_code(self, sample_mt103):
        """Test generated message contains operation code"""
        message = sample_mt103.generate()
        assert ':23B:CRED' in message

    def test_generate_contains_charges(self, sample_mt103):
        """Test generated message contains charges"""
        message = sample_mt103.generate()
        assert ':71A:SHA' in message

    def test_generate_contains_blocks(self, sample_mt103):
        """Test generated message contains all blocks"""
        message = sample_mt103.generate()
        assert '{1:' in message  # Block 1
        assert '{2:' in message  # Block 2
        assert '{3:' in message  # Block 3
        assert '{4:' in message  # Block 4
        assert '{5:' in message  # Block 5

    def test_generate_amount_format(self, sample_mt103):
        """Test amount is formatted with comma decimal separator"""
        message = sample_mt103.generate()
        # Amount should be 5000,00 (European format)
        assert '5000,00' in message


class TestConstants:
    """Test cases for module constants"""

    def test_bank_operation_codes(self):
        """Test bank operation codes are defined"""
        assert 'CRED' in BANK_OPERATION_CODES
        assert 'SPAY' in BANK_OPERATION_CODES

    def test_charge_types(self):
        """Test charge types are defined"""
        assert 'SHA' in CHARGE_TYPES
        assert 'OUR' in CHARGE_TYPES
        assert 'BEN' in CHARGE_TYPES
