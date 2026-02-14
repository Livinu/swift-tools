#!/usr/bin/env python3
"""
Tests for BIC/SWIFT Code Validator
"""

import pytest
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'code'))

from bic_validator import BICCode, validate_bic


class TestBICValidation:
    """Test cases for BIC validation"""

    def test_valid_bic_with_branch(self):
        """Test validation of valid BIC with branch code"""
        is_valid, message = validate_bic('BNPAFRPPXXX')
        assert is_valid is True
        assert 'valide' in message.lower() or 'valid' in message.lower()

    def test_valid_bic_without_branch(self):
        """Test validation of valid BIC without branch code (8 chars)"""
        is_valid, message = validate_bic('DEUTDEFF')
        assert is_valid is True

    def test_valid_bic_german_bank(self):
        """Test validation of German bank BIC"""
        is_valid, message = validate_bic('COBADEFFXXX')
        assert is_valid is True

    def test_invalid_bic_too_short(self):
        """Test that BIC with less than 8 characters is invalid"""
        is_valid, message = validate_bic('BNPA')
        assert is_valid is False

    def test_invalid_bic_wrong_format(self):
        """Test that BIC with invalid format is rejected"""
        is_valid, message = validate_bic('INVALID')
        assert is_valid is False

    def test_invalid_bic_numeric_bank_code(self):
        """Test that BIC with numeric bank code is invalid"""
        is_valid, message = validate_bic('1234FRPP')
        assert is_valid is False

    def test_invalid_bic_too_long(self):
        """Test that BIC with more than 11 characters is invalid"""
        is_valid, message = validate_bic('BNPAFRPPXXXX')
        assert is_valid is False


class TestBICParsing:
    """Test cases for BIC parsing"""

    def test_parse_full_bic(self):
        """Test parsing of full 11-character BIC"""
        bic = BICCode.parse('BNPAFRPPXXX')
        assert bic.bank_code == 'BNPA'
        assert bic.country_code == 'FR'
        assert bic.location_code == 'PP'
        assert bic.branch_code == 'XXX'

    def test_parse_short_bic(self):
        """Test parsing of 8-character BIC"""
        bic = BICCode.parse('DEUTDEFF')
        assert bic.bank_code == 'DEUT'
        assert bic.country_code == 'DE'
        assert bic.location_code == 'FF'
        assert bic.branch_code is None

    def test_full_code_property(self):
        """Test full_code property returns complete BIC"""
        bic = BICCode.parse('BNPAFRPPXXX')
        assert bic.full_code == 'BNPAFRPPXXX'

    def test_is_primary_office_xxx(self):
        """Test that XXX branch is identified as primary office"""
        bic = BICCode.parse('BNPAFRPPXXX')
        assert bic.is_primary_office is True

    def test_is_primary_office_no_branch(self):
        """Test that no branch code is identified as primary office"""
        bic = BICCode.parse('DEUTDEFF')
        assert bic.is_primary_office is True

    def test_get_country_name_france(self):
        """Test country name lookup for France"""
        bic = BICCode.parse('BNPAFRPP')
        assert bic.get_country_name() == 'France'

    def test_get_country_name_germany(self):
        """Test country name lookup for Germany"""
        bic = BICCode.parse('COBADEFF')
        assert bic.get_country_name() == 'Allemagne'

    def test_parse_invalid_raises_error(self):
        """Test that parsing invalid BIC raises ValueError"""
        with pytest.raises(ValueError):
            BICCode.parse('INVALID')

    def test_parse_too_short_raises_error(self):
        """Test that parsing too short BIC raises ValueError"""
        with pytest.raises(ValueError):
            BICCode.parse('BNP')


class TestBICEdgeCases:
    """Edge case tests for BIC validation"""

    def test_lowercase_bic_is_normalized(self):
        """Test that lowercase BIC is converted to uppercase"""
        is_valid, _ = validate_bic('bnpafrppxxx')
        assert is_valid is True

    def test_bic_with_spaces_stripped(self):
        """Test that BIC with surrounding spaces is handled"""
        is_valid, _ = validate_bic('  BNPAFRPPXXX  ')
        assert is_valid is True

    def test_alphanumeric_location_code(self):
        """Test BIC with alphanumeric location code"""
        is_valid, _ = validate_bic('CHASUS33XXX')
        assert is_valid is True
