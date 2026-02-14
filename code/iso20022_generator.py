#!/usr/bin/env python3
"""
ISO 20022 Message Generator
Génération de messages pain.001 (Customer Credit Transfer Initiation)
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional
import xml.etree.ElementTree as ET
from xml.dom import minidom
import uuid


@dataclass
class Address:
    """Adresse postale"""
    street: Optional[str] = None
    building_number: Optional[str] = None
    postal_code: Optional[str] = None
    city: Optional[str] = None
    country: str = "FR"


@dataclass
class PaymentInstruction:
    """Instruction de paiement individuelle"""
    instruction_id: str
    amount: float
    currency: str
    debtor_name: str
    debtor_iban: str
    debtor_bic: str
    creditor_name: str
    creditor_iban: str
    creditor_bic: str
    remittance_info: str
    end_to_end_id: Optional[str] = None
    debtor_address: Optional[Address] = None
    creditor_address: Optional[Address] = None
    
    def __post_init__(self):
        if self.end_to_end_id is None:
            self.end_to_end_id = str(uuid.uuid4())[:35]


@dataclass
class PaymentBatch:
    """Lot de paiements"""
    payment_info_id: str
    payment_method: str = "TRF"  # TRF = Transfer
    batch_booking: bool = True
    service_level: str = "SEPA"
    requested_execution_date: Optional[datetime] = None
    payments: List[PaymentInstruction] = field(default_factory=list)
    
    def __post_init__(self):
        if self.requested_execution_date is None:
            self.requested_execution_date = datetime.utcnow()
    
    @property
    def total_amount(self) -> float:
        return sum(p.amount for p in self.payments)
    
    @property
    def transaction_count(self) -> int:
        return len(self.payments)


class ISO20022Generator:
    """
    Générateur de messages ISO 20022
    Supporte pain.001.001.09 (Customer Credit Transfer Initiation)
    """
    
    # Namespace pour pain.001.001.09
    NAMESPACE = "urn:iso:std:iso:20022:tech:xsd:pain.001.001.09"
    
    def __init__(self):
        self.ns = {"": self.NAMESPACE}
    
    def _create_element(self, parent: ET.Element, tag: str, text: Optional[str] = None) -> ET.Element:
        """Crée un élément XML avec texte optionnel"""
        elem = ET.SubElement(parent, tag)
        if text is not None:
            elem.text = str(text)
        return elem
    
    def _add_address(self, parent: ET.Element, address: Address) -> None:
        """Ajoute une adresse postale"""
        pstl_adr = self._create_element(parent, "PstlAdr")
        if address.street:
            self._create_element(pstl_adr, "StrtNm", address.street)
        if address.building_number:
            self._create_element(pstl_adr, "BldgNb", address.building_number)
        if address.postal_code:
            self._create_element(pstl_adr, "PstCd", address.postal_code)
        if address.city:
            self._create_element(pstl_adr, "TwnNm", address.city)
        self._create_element(pstl_adr, "Ctry", address.country)
    
    def generate_pain001(
        self,
        message_id: str,
        initiating_party_name: str,
        batches: List[PaymentBatch],
        initiating_party_id: Optional[str] = None,
    ) -> str:
        """
        Génère un message pain.001 (Customer Credit Transfer Initiation)
        
        Args:
            message_id: Identifiant unique du message
            initiating_party_name: Nom de l'initiateur du paiement
            batches: Liste des lots de paiements
            initiating_party_id: Identifiant optionnel de l'initiateur
            
        Returns:
            str: Message XML formaté
        """
        # Racine du document
        root = ET.Element("Document", xmlns=self.NAMESPACE)
        cstmr_cdt_trf = self._create_element(root, "CstmrCdtTrfInitn")
        
        # Calcul des totaux
        total_transactions = sum(b.transaction_count for b in batches)
        total_amount = sum(b.total_amount for b in batches)
        
        # ========== GROUP HEADER ==========
        grp_hdr = self._create_element(cstmr_cdt_trf, "GrpHdr")
        self._create_element(grp_hdr, "MsgId", message_id)
        self._create_element(grp_hdr, "CreDtTm", datetime.utcnow().isoformat())
        self._create_element(grp_hdr, "NbOfTxs", str(total_transactions))
        self._create_element(grp_hdr, "CtrlSum", f"{total_amount:.2f}")
        
        # Initiating Party
        initg_pty = self._create_element(grp_hdr, "InitgPty")
        self._create_element(initg_pty, "Nm", initiating_party_name)
        
        if initiating_party_id:
            initg_pty_id = self._create_element(initg_pty, "Id")
            org_id = self._create_element(initg_pty_id, "OrgId")
            othr = self._create_element(org_id, "Othr")
            self._create_element(othr, "Id", initiating_party_id)
        
        # ========== PAYMENT INFORMATION ==========
        for batch in batches:
            pmt_inf = self._create_element(cstmr_cdt_trf, "PmtInf")
            self._create_element(pmt_inf, "PmtInfId", batch.payment_info_id)
            self._create_element(pmt_inf, "PmtMtd", batch.payment_method)
            self._create_element(pmt_inf, "BtchBookg", str(batch.batch_booking).lower())
            self._create_element(pmt_inf, "NbOfTxs", str(batch.transaction_count))
            self._create_element(pmt_inf, "CtrlSum", f"{batch.total_amount:.2f}")
            
            # Payment Type Information
            pmt_tp_inf = self._create_element(pmt_inf, "PmtTpInf")
            svc_lvl = self._create_element(pmt_tp_inf, "SvcLvl")
            self._create_element(svc_lvl, "Cd", batch.service_level)
            
            # Requested Execution Date
            reqd_exctn_dt = self._create_element(pmt_inf, "ReqdExctnDt")
            self._create_element(reqd_exctn_dt, "Dt", 
                               batch.requested_execution_date.date().isoformat())
            
            # Debtor Information (from first payment in batch)
            if batch.payments:
                first_payment = batch.payments[0]
                
                # Debtor
                dbtr = self._create_element(pmt_inf, "Dbtr")
                self._create_element(dbtr, "Nm", first_payment.debtor_name)
                if first_payment.debtor_address:
                    self._add_address(dbtr, first_payment.debtor_address)
                
                # Debtor Account
                dbtr_acct = self._create_element(pmt_inf, "DbtrAcct")
                dbtr_acct_id = self._create_element(dbtr_acct, "Id")
                self._create_element(dbtr_acct_id, "IBAN", first_payment.debtor_iban)
                
                # Debtor Agent
                dbtr_agt = self._create_element(pmt_inf, "DbtrAgt")
                fin_instn_id = self._create_element(dbtr_agt, "FinInstnId")
                self._create_element(fin_instn_id, "BICFI", first_payment.debtor_bic)
            
            # Credit Transfer Transactions
            for payment in batch.payments:
                cdt_trf_tx = self._create_element(pmt_inf, "CdtTrfTxInf")
                
                # Payment Identification
                pmt_id = self._create_element(cdt_trf_tx, "PmtId")
                self._create_element(pmt_id, "InstrId", payment.instruction_id)
                self._create_element(pmt_id, "EndToEndId", payment.end_to_end_id)
                
                # Amount
                amt = self._create_element(cdt_trf_tx, "Amt")
                instd_amt = ET.SubElement(amt, "InstdAmt", Ccy=payment.currency)
                instd_amt.text = f"{payment.amount:.2f}"
                
                # Creditor Agent
                cdtr_agt = self._create_element(cdt_trf_tx, "CdtrAgt")
                cdtr_fin_instn = self._create_element(cdtr_agt, "FinInstnId")
                self._create_element(cdtr_fin_instn, "BICFI", payment.creditor_bic)
                
                # Creditor
                cdtr = self._create_element(cdt_trf_tx, "Cdtr")
                self._create_element(cdtr, "Nm", payment.creditor_name)
                if payment.creditor_address:
                    self._add_address(cdtr, payment.creditor_address)
                
                # Creditor Account
                cdtr_acct = self._create_element(cdt_trf_tx, "CdtrAcct")
                cdtr_acct_id = self._create_element(cdtr_acct, "Id")
                self._create_element(cdtr_acct_id, "IBAN", payment.creditor_iban)
                
                # Remittance Information
                rmt_inf = self._create_element(cdt_trf_tx, "RmtInf")
                self._create_element(rmt_inf, "Ustrd", payment.remittance_info)
        
        # Formatage XML avec indentation
        xml_str = ET.tostring(root, encoding="unicode")
        return minidom.parseString(xml_str).toprettyxml(indent="  ")
    
    def save_to_file(self, xml_content: str, filename: str) -> None:
        """Sauvegarde le message XML dans un fichier"""
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(xml_content)


def create_sample_payment() -> PaymentInstruction:
    """Crée un exemple de paiement"""
    return PaymentInstruction(
        instruction_id="INSTR-2026-001",
        amount=1500.00,
        currency="EUR",
        debtor_name="Société ABC SARL",
        debtor_iban="FR7630006000011234567890189",
        debtor_bic="BNPAFRPPXXX",
        debtor_address=Address(
            street="123 Avenue des Champs-Élysées",
            postal_code="75008",
            city="Paris",
            country="FR"
        ),
        creditor_name="Fournisseur XYZ GmbH",
        creditor_iban="DE89370400440532013000",
        creditor_bic="COBADEFFXXX",
        creditor_address=Address(
            street="Hauptstraße 1",
            postal_code="60311",
            city="Frankfurt",
            country="DE"
        ),
        remittance_info="Facture 2026-001 - Prestation de services"
    )


if __name__ == "__main__":
    print("=" * 70)
    print("ISO 20022 pain.001 Generator")
    print("=" * 70)
    
    # Création du générateur
    generator = ISO20022Generator()
    
    # Création d'exemples de paiements
    payment1 = create_sample_payment()
    
    payment2 = PaymentInstruction(
        instruction_id="INSTR-2026-002",
        amount=2500.00,
        currency="EUR",
        debtor_name="Société ABC SARL",
        debtor_iban="FR7630006000011234567890189",
        debtor_bic="BNPAFRPPXXX",
        creditor_name="Partner Ltd",
        creditor_iban="GB82WEST12345698765432",
        creditor_bic="WESTGB2LXXX",
        remittance_info="Invoice INV-2026-042"
    )
    
    # Création d'un lot de paiements
    batch = PaymentBatch(
        payment_info_id="BATCH-2026-02-14-001",
        payments=[payment1, payment2]
    )
    
    # Génération du message
    xml_message = generator.generate_pain001(
        message_id=f"MSG-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        initiating_party_name="Société ABC SARL",
        initiating_party_id="FR12345678901234",
        batches=[batch]
    )
    
    print("\nMessage pain.001 généré:")
    print("-" * 70)
    print(xml_message)
    
    # Optionnel: sauvegarde dans un fichier
    # generator.save_to_file(xml_message, "pain001_sample.xml")
    # print("\nMessage sauvegardé dans pain001_sample.xml")
