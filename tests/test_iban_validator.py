#!/usr/bin/env python3
"""
Tests for IBAN Validator
"""

import pytest
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'swift_cli'))

from iban_validator import IBAN, validate_iban


class TestIBANValidation:
    """Test cases for IBAN validation"""

    def test_valid_iban_france(self):
        """Test validation of valid French IBAN"""
        is_valid, message = validate_iban('FR7630006000011234567890189')
        assert is_valid is True
        assert 'France' in message

    def test_valid_iban_germany(self):
        """Test validation of valid German IBAN"""
        is_valid, message = validate_iban('DE89370400440532013000')
        assert is_valid is True

    def test_valid_iban_uk(self):
        """Test validation of valid UK IBAN"""
        is_valid, message = validate_iban('GB82WEST12345698765432')
        assert is_valid is True

    def test_valid_iban_spain(self):
        """Test validation of valid Spanish IBAN"""
        is_valid, message = validate_iban('ES9121000418450200051332')
        assert is_valid is True

    def test_valid_iban_belgium(self):
        """Test validation of valid Belgian IBAN"""
        is_valid, message = validate_iban('BE68539007547034')
        assert is_valid is True

    def test_invalid_iban_wrong_checksum(self):
        """Test that IBAN with wrong checksum is invalid"""
        # Changed last digit from 9 to 8
        is_valid, message = validate_iban('FR7630006000011234567890188')
        assert is_valid is False
        assert 'contrôle' in message.lower() or 'invalid' in message.lower()

    def test_invalid_iban_format(self):
        """Test that IBAN with invalid format is rejected"""
        is_valid, message = validate_iban('INVALID123')
        assert is_valid is False

    def test_invalid_iban_too_short(self):
        """Test that IBAN that is too short is invalid"""
        is_valid, message = validate_iban('FR76')
        assert is_valid is False

    def test_invalid_iban_wrong_length_for_country(self):
        """Test that IBAN with wrong length for country is invalid"""
        # French IBAN should be 27 chars, this is 25
        is_valid, message = validate_iban('FR76300060000112345678901')
        assert is_valid is False


class TestIBANParsing:
    """Test cases for IBAN parsing and properties"""

    def test_country_code(self):
        """Test country code extraction"""
        iban = IBAN('FR7630006000011234567890189')
        assert iban.country_code == 'FR'

    def test_check_digits(self):
        """Test check digits extraction"""
        iban = IBAN('FR7630006000011234567890189')
        assert iban.check_digits == '76'

    def test_bban(self):
        """Test BBAN extraction"""
        iban = IBAN('FR7630006000011234567890189')
        assert iban.bban == '30006000011234567890189'

    def test_country_name_france(self):
        """Test country name for France"""
        iban = IBAN('FR7630006000011234567890189')
        assert iban.country_name == 'France'

    def test_country_name_germany(self):
        """Test country name for Germany"""
        iban = IBAN('DE89370400440532013000')
        assert iban.country_name == 'Allemagne'

    def test_formatted_output(self):
        """Test IBAN formatting with spaces"""
        iban = IBAN('FR7630006000011234567890189')
        formatted = iban.formatted
        assert formatted == 'FR76 3000 6000 0112 3456 7890 189'

    def test_raw_iban_cleaned(self):
        """Test that raw IBAN is cleaned of spaces"""
        iban = IBAN('FR76 3000 6000 0112 3456 7890 189')
        assert iban.raw_iban == 'FR7630006000011234567890189'


class TestIBANGeneration:
    """Test cases for IBAN generation"""

    def test_generate_check_digits_france(self):
        """Test check digit generation for French IBAN"""
        check_digits = IBAN.generate_check_digits('FR', '30006000011234567890189')
        assert check_digits == '76'

    def test_generate_check_digits_germany(self):
        """Test check digit generation for German IBAN"""
        check_digits = IBAN.generate_check_digits('DE', '370400440532013000')
        assert check_digits == '89'

    def test_create_valid_iban(self):
        """Test creating a valid IBAN from country and BBAN"""
        iban = IBAN.create('FR', '30006000011234567890189')
        is_valid, _ = iban.validate()
        assert is_valid is True
        assert iban.raw_iban == 'FR7630006000011234567890189'


class TestIBANEdgeCases:
    """Edge case tests for IBAN validation"""

    def test_iban_with_spaces(self):
        """Test IBAN with spaces is handled correctly"""
        is_valid, _ = validate_iban('FR76 3000 6000 0112 3456 7890 189')
        assert is_valid is True

    def test_lowercase_iban(self):
        """Test lowercase IBAN is normalized"""
        is_valid, _ = validate_iban('fr7630006000011234567890189')
        assert is_valid is True

    def test_unknown_country_code(self):
        """Test IBAN with unknown country code"""
        iban = IBAN('XX001234567890')
        assert iban.country_name == 'Inconnu'
