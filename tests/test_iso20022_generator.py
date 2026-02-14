#!/usr/bin/env python3
"""
Tests for ISO 20022 Message Generator
"""

import pytest
import sys
import os
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'swift_cli'))

from iso20022_generator import (
    ISO20022Generator,
    PaymentInstruction,
    PaymentBatch,
    Address,
)


class TestPaymentInstruction:
    """Test cases for PaymentInstruction dataclass"""

    def test_create_payment_instruction(self):
        """Test creating a payment instruction"""
        payment = PaymentInstruction(
            instruction_id='TEST-001',
            amount=1000.00,
            currency='EUR',
            debtor_name='Test Debtor',
            debtor_iban='FR7630006000011234567890189',
            debtor_bic='BNPAFRPPXXX',
            creditor_name='Test Creditor',
            creditor_iban='DE89370400440532013000',
            creditor_bic='COBADEFFXXX',
            remittance_info='Test Payment'
        )
        
        assert payment.instruction_id == 'TEST-001'
        assert payment.amount == 1000.00
        assert payment.currency == 'EUR'

    def test_end_to_end_id_generated(self):
        """Test that end_to_end_id is auto-generated if not provided"""
        payment = PaymentInstruction(
            instruction_id='TEST-001',
            amount=1000.00,
            currency='EUR',
            debtor_name='Test Debtor',
            debtor_iban='FR7630006000011234567890189',
            debtor_bic='BNPAFRPPXXX',
            creditor_name='Test Creditor',
            creditor_iban='DE89370400440532013000',
            creditor_bic='COBADEFFXXX',
            remittance_info='Test Payment'
        )
        
        assert payment.end_to_end_id is not None
        assert len(payment.end_to_end_id) <= 35

    def test_custom_end_to_end_id(self):
        """Test providing custom end_to_end_id"""
        payment = PaymentInstruction(
            instruction_id='TEST-001',
            amount=1000.00,
            currency='EUR',
            debtor_name='Test Debtor',
            debtor_iban='FR7630006000011234567890189',
            debtor_bic='BNPAFRPPXXX',
            creditor_name='Test Creditor',
            creditor_iban='DE89370400440532013000',
            creditor_bic='COBADEFFXXX',
            remittance_info='Test Payment',
            end_to_end_id='CUSTOM-E2E-ID'
        )
        
        assert payment.end_to_end_id == 'CUSTOM-E2E-ID'


class TestPaymentBatch:
    """Test cases for PaymentBatch dataclass"""

    def test_create_payment_batch(self):
        """Test creating a payment batch"""
        payment = PaymentInstruction(
            instruction_id='TEST-001',
            amount=1000.00,
            currency='EUR',
            debtor_name='Test Debtor',
            debtor_iban='FR7630006000011234567890189',
            debtor_bic='BNPAFRPPXXX',
            creditor_name='Test Creditor',
            creditor_iban='DE89370400440532013000',
            creditor_bic='COBADEFFXXX',
            remittance_info='Test Payment'
        )
        
        batch = PaymentBatch(
            payment_info_id='BATCH-001',
            payments=[payment]
        )
        
        assert batch.payment_info_id == 'BATCH-001'
        assert len(batch.payments) == 1

    def test_batch_total_amount(self):
        """Test batch total amount calculation"""
        payment1 = PaymentInstruction(
            instruction_id='TEST-001',
            amount=1000.00,
            currency='EUR',
            debtor_name='Test Debtor',
            debtor_iban='FR7630006000011234567890189',
            debtor_bic='BNPAFRPPXXX',
            creditor_name='Test Creditor',
            creditor_iban='DE89370400440532013000',
            creditor_bic='COBADEFFXXX',
            remittance_info='Test Payment 1'
        )
        
        payment2 = PaymentInstruction(
            instruction_id='TEST-002',
            amount=500.00,
            currency='EUR',
            debtor_name='Test Debtor',
            debtor_iban='FR7630006000011234567890189',
            debtor_bic='BNPAFRPPXXX',
            creditor_name='Test Creditor 2',
            creditor_iban='GB82WEST12345698765432',
            creditor_bic='WESTGB2LXXX',
            remittance_info='Test Payment 2'
        )
        
        batch = PaymentBatch(
            payment_info_id='BATCH-001',
            payments=[payment1, payment2]
        )
        
        assert batch.total_amount == 1500.00
        assert batch.transaction_count == 2


class TestISO20022Generator:
    """Test cases for ISO20022Generator"""

    @pytest.fixture
    def sample_payment(self):
        """Create a sample payment for testing"""
        return PaymentInstruction(
            instruction_id='TEST-001',
            amount=1000.00,
            currency='EUR',
            debtor_name='Test Debtor',
            debtor_iban='FR7630006000011234567890189',
            debtor_bic='BNPAFRPPXXX',
            creditor_name='Test Creditor',
            creditor_iban='DE89370400440532013000',
            creditor_bic='COBADEFFXXX',
            remittance_info='Test Payment'
        )

    @pytest.fixture
    def sample_batch(self, sample_payment):
        """Create a sample batch for testing"""
        return PaymentBatch(
            payment_info_id='BATCH-001',
            payments=[sample_payment]
        )

    def test_generate_pain001_xml_declaration(self, sample_batch):
        """Test that generated XML has proper declaration"""
        generator = ISO20022Generator()
        xml = generator.generate_pain001(
            message_id='MSG-TEST-001',
            initiating_party_name='Test Company',
            batches=[sample_batch]
        )
        
        assert '<?xml' in xml

    def test_generate_pain001_root_element(self, sample_batch):
        """Test that generated XML has CstmrCdtTrfInitn root"""
        generator = ISO20022Generator()
        xml = generator.generate_pain001(
            message_id='MSG-TEST-001',
            initiating_party_name='Test Company',
            batches=[sample_batch]
        )
        
        assert 'CstmrCdtTrfInitn' in xml

    def test_generate_pain001_message_id(self, sample_batch):
        """Test that message ID is included in XML"""
        generator = ISO20022Generator()
        xml = generator.generate_pain001(
            message_id='MSG-TEST-001',
            initiating_party_name='Test Company',
            batches=[sample_batch]
        )
        
        assert 'MSG-TEST-001' in xml

    def test_generate_pain001_amount(self, sample_batch):
        """Test that amount is correctly formatted in XML"""
        generator = ISO20022Generator()
        xml = generator.generate_pain001(
            message_id='MSG-TEST-001',
            initiating_party_name='Test Company',
            batches=[sample_batch]
        )
        
        assert '1000.00' in xml

    def test_generate_pain001_instruction_id(self, sample_batch):
        """Test that instruction ID is included in XML"""
        generator = ISO20022Generator()
        xml = generator.generate_pain001(
            message_id='MSG-TEST-001',
            initiating_party_name='Test Company',
            batches=[sample_batch]
        )
        
        assert 'TEST-001' in xml

    def test_generate_pain001_namespace(self, sample_batch):
        """Test that ISO 20022 namespace is included"""
        generator = ISO20022Generator()
        xml = generator.generate_pain001(
            message_id='MSG-TEST-001',
            initiating_party_name='Test Company',
            batches=[sample_batch]
        )
        
        assert 'urn:iso:std:iso:20022' in xml

    def test_generate_pain001_creditor_info(self, sample_batch):
        """Test that creditor information is included"""
        generator = ISO20022Generator()
        xml = generator.generate_pain001(
            message_id='MSG-TEST-001',
            initiating_party_name='Test Company',
            batches=[sample_batch]
        )
        
        assert 'Test Creditor' in xml
        assert 'DE89370400440532013000' in xml
        assert 'COBADEFFXXX' in xml

    def test_generate_pain001_debtor_info(self, sample_batch):
        """Test that debtor information is included"""
        generator = ISO20022Generator()
        xml = generator.generate_pain001(
            message_id='MSG-TEST-001',
            initiating_party_name='Test Company',
            batches=[sample_batch]
        )
        
        assert 'Test Debtor' in xml
        assert 'FR7630006000011234567890189' in xml
        assert 'BNPAFRPPXXX' in xml


class TestAddress:
    """Test cases for Address dataclass"""

    def test_create_address(self):
        """Test creating an address"""
        address = Address(
            street='123 Main Street',
            postal_code='75001',
            city='Paris',
            country='FR'
        )
        
        assert address.street == '123 Main Street'
        assert address.postal_code == '75001'
        assert address.city == 'Paris'
        assert address.country == 'FR'

    def test_address_default_country(self):
        """Test default country is FR"""
        address = Address()
        assert address.country == 'FR'
