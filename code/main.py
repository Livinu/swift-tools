#!/usr/bin/env python3
"""
SWIFT Banking System CLI
========================

Outil en ligne de commande pour valider et générer des messages bancaires
conformes aux normes SWIFT et ISO 20022.

Utilisation:
    python main.py <commande> [options]

Commandes disponibles:
    validate-bic     Valider un code BIC/SWIFT
    validate-iban    Valider un numéro IBAN
    generate-pain001 Générer un message ISO 20022 pain.001
    generate-mt103   Générer un message MT103 (legacy SWIFT)
    batch-validate   Valider un fichier de BIC/IBAN
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

from bic_validator import BICCode, validate_bic
from iban_validator import IBAN, validate_iban
from iso20022_generator import (
    ISO20022Generator,
    PaymentInstruction,
    PaymentBatch,
    Address,
)
from mt103_generator import MT103Message, Party


class SwiftCLI:
    """Interface en ligne de commande pour le système SWIFT"""
    
    def __init__(self):
        self.parser = self._create_parser()
    
    def _create_parser(self) -> argparse.ArgumentParser:
        """Crée le parser principal avec tous les sous-parsers"""
        parser = argparse.ArgumentParser(
            prog="swift-cli",
            description="Outil CLI pour les opérations bancaires SWIFT/ISO 20022",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Exemples d'utilisation:
  %(prog)s validate-bic BNPAFRPPXXX
  %(prog)s validate-iban "FR76 3000 6000 0112 3456 7890 189"
  %(prog)s generate-pain001 --config payment.json --output message.xml
  %(prog)s generate-mt103 --amount 1500 --currency EUR --debtor-iban FR7630006000011234567890189
  %(prog)s batch-validate --file accounts.txt --type iban
            """
        )
        
        parser.add_argument(
            "--version", "-v",
            action="version",
            version="%(prog)s 1.0.0"
        )
        
        parser.add_argument(
            "--json", "-j",
            action="store_true",
            help="Sortie au format JSON"
        )
        
        subparsers = parser.add_subparsers(
            dest="command",
            title="Commandes",
            description="Commandes disponibles"
        )
        
        # Sous-parser: validate-bic
        bic_parser = subparsers.add_parser(
            "validate-bic",
            help="Valider un code BIC/SWIFT"
        )
        bic_parser.add_argument(
            "bic",
            help="Code BIC à valider (8 ou 11 caractères)"
        )
        
        # Sous-parser: validate-iban
        iban_parser = subparsers.add_parser(
            "validate-iban",
            help="Valider un numéro IBAN"
        )
        iban_parser.add_argument(
            "iban",
            help="Numéro IBAN à valider"
        )
        
        # Sous-parser: generate-pain001
        pain001_parser = subparsers.add_parser(
            "generate-pain001",
            help="Générer un message ISO 20022 pain.001"
        )
        pain001_parser.add_argument(
            "--config", "-c",
            type=str,
            help="Fichier JSON de configuration du paiement"
        )
        pain001_parser.add_argument(
            "--output", "-o",
            type=str,
            help="Fichier de sortie XML (défaut: stdout)"
        )
        pain001_parser.add_argument(
            "--message-id",
            type=str,
            default=None,
            help="Identifiant du message (généré automatiquement si non fourni)"
        )
        pain001_parser.add_argument(
            "--initiator",
            type=str,
            default="CLI User",
            help="Nom de l'initiateur du paiement"
        )
        # Arguments pour paiement simple sans fichier config
        pain001_parser.add_argument("--amount", type=float, help="Montant du paiement")
        pain001_parser.add_argument("--currency", type=str, default="EUR", help="Devise (défaut: EUR)")
        pain001_parser.add_argument("--debtor-name", type=str, help="Nom du débiteur")
        pain001_parser.add_argument("--debtor-iban", type=str, help="IBAN du débiteur")
        pain001_parser.add_argument("--debtor-bic", type=str, help="BIC du débiteur")
        pain001_parser.add_argument("--creditor-name", type=str, help="Nom du créditeur")
        pain001_parser.add_argument("--creditor-iban", type=str, help="IBAN du créditeur")
        pain001_parser.add_argument("--creditor-bic", type=str, help="BIC du créditeur")
        pain001_parser.add_argument("--remittance-info", type=str, default="Payment", help="Information de remise")
        
        # Sous-parser: generate-mt103
        mt103_parser = subparsers.add_parser(
            "generate-mt103",
            help="Générer un message MT103 (legacy SWIFT)"
        )
        mt103_parser.add_argument(
            "--config", "-c",
            type=str,
            help="Fichier JSON de configuration du paiement"
        )
        mt103_parser.add_argument(
            "--output", "-o",
            type=str,
            help="Fichier de sortie (défaut: stdout)"
        )
        mt103_parser.add_argument("--reference", type=str, help="Référence de la transaction")
        mt103_parser.add_argument("--amount", type=float, help="Montant du paiement")
        mt103_parser.add_argument("--currency", type=str, default="EUR", help="Devise")
        mt103_parser.add_argument("--debtor-name", type=str, help="Nom du débiteur")
        mt103_parser.add_argument("--debtor-iban", type=str, help="IBAN du débiteur")
        mt103_parser.add_argument("--debtor-bic", type=str, help="BIC du débiteur")
        mt103_parser.add_argument("--creditor-name", type=str, help="Nom du créditeur")
        mt103_parser.add_argument("--creditor-iban", type=str, help="IBAN du créditeur")
        mt103_parser.add_argument("--creditor-bic", type=str, help="BIC du créditeur")
        mt103_parser.add_argument("--remittance-info", type=str, default="Payment", help="Information de remise")
        mt103_parser.add_argument("--charges", type=str, default="SHA", choices=["SHA", "OUR", "BEN"], help="Type de frais")
        
        # Sous-parser: batch-validate
        batch_parser = subparsers.add_parser(
            "batch-validate",
            help="Valider un fichier de BIC ou IBAN"
        )
        batch_parser.add_argument(
            "--file", "-f",
            type=str,
            required=True,
            help="Fichier contenant les codes à valider (un par ligne)"
        )
        batch_parser.add_argument(
            "--type", "-t",
            type=str,
            required=True,
            choices=["bic", "iban"],
            help="Type de codes à valider"
        )
        batch_parser.add_argument(
            "--output", "-o",
            type=str,
            help="Fichier de sortie pour le rapport"
        )
        
        return parser
    
    def run(self, args: Optional[list] = None) -> int:
        """Exécute la commande CLI"""
        parsed_args = self.parser.parse_args(args)
        
        if not parsed_args.command:
            self.parser.print_help()
            return 1
        
        try:
            if parsed_args.command == "validate-bic":
                return self._validate_bic(parsed_args)
            elif parsed_args.command == "validate-iban":
                return self._validate_iban(parsed_args)
            elif parsed_args.command == "generate-pain001":
                return self._generate_pain001(parsed_args)
            elif parsed_args.command == "generate-mt103":
                return self._generate_mt103(parsed_args)
            elif parsed_args.command == "batch-validate":
                return self._batch_validate(parsed_args)
            else:
                self.parser.print_help()
                return 1
        except Exception as e:
            self._error(str(e), parsed_args.json if hasattr(parsed_args, 'json') else False)
            return 1
    
    def _output(self, data: dict, as_json: bool = False) -> None:
        """Affiche le résultat"""
        if as_json:
            print(json.dumps(data, indent=2, ensure_ascii=False))
        else:
            for key, value in data.items():
                print(f"{key}: {value}")
    
    def _error(self, message: str, as_json: bool = False) -> None:
        """Affiche une erreur"""
        if as_json:
            print(json.dumps({"error": message}, indent=2), file=sys.stderr)
        else:
            print(f"Erreur: {message}", file=sys.stderr)
    
    def _validate_bic(self, args) -> int:
        """Valide un code BIC"""
        is_valid, message = validate_bic(args.bic)
        
        result = {
            "input": args.bic,
            "valid": is_valid,
            "message": message
        }
        
        if is_valid:
            bic = BICCode.parse(args.bic)
            result.update({
                "bank_code": bic.bank_code,
                "country_code": bic.country_code,
                "country_name": bic.get_country_name(),
                "location_code": bic.location_code,
                "branch_code": bic.branch_code,
                "is_primary_office": bic.is_primary_office
            })
        
        self._output(result, args.json)
        return 0 if is_valid else 1
    
    def _validate_iban(self, args) -> int:
        """Valide un IBAN"""
        iban = IBAN(args.iban)
        is_valid, message = iban.validate()
        
        result = {
            "input": args.iban,
            "formatted": iban.formatted,
            "valid": is_valid,
            "message": message
        }
        
        if is_valid:
            result.update({
                "country_code": iban.country_code,
                "country_name": iban.country_name,
                "check_digits": iban.check_digits,
                "bban": iban.bban
            })
        
        self._output(result, args.json)
        return 0 if is_valid else 1
    
    def _generate_pain001(self, args) -> int:
        """Génère un message pain.001"""
        generator = ISO20022Generator()
        
        if args.config:
            # Charger depuis fichier JSON
            with open(args.config, 'r') as f:
                config = json.load(f)
            
            payments = []
            for idx, p in enumerate(config.get("payments", [])):
                payment = PaymentInstruction(
                    instruction_id=p.get("instruction_id", f"INSTR-{idx+1:04d}"),
                    amount=p["amount"],
                    currency=p.get("currency", "EUR"),
                    debtor_name=p["debtor"]["name"],
                    debtor_iban=p["debtor"]["iban"],
                    debtor_bic=p["debtor"]["bic"],
                    creditor_name=p["creditor"]["name"],
                    creditor_iban=p["creditor"]["iban"],
                    creditor_bic=p["creditor"]["bic"],
                    remittance_info=p.get("remittance_info", "Payment")
                )
                payments.append(payment)
            
            batch = PaymentBatch(
                payment_info_id=config.get("batch_id", f"BATCH-{datetime.now().strftime('%Y%m%d%H%M%S')}"),
                payments=payments
            )
            
            message_id = args.message_id or config.get("message_id", f"MSG-{datetime.now().strftime('%Y%m%d%H%M%S')}")
            initiator = args.initiator or config.get("initiator", "CLI User")
            
        else:
            # Arguments en ligne de commande
            if not all([args.amount, args.debtor_name, args.debtor_iban, args.debtor_bic,
                       args.creditor_name, args.creditor_iban, args.creditor_bic]):
                self._error("Arguments manquants. Utilisez --config ou fournissez tous les arguments requis.")
                return 1
            
            payment = PaymentInstruction(
                instruction_id=f"INSTR-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                amount=args.amount,
                currency=args.currency,
                debtor_name=args.debtor_name,
                debtor_iban=args.debtor_iban,
                debtor_bic=args.debtor_bic,
                creditor_name=args.creditor_name,
                creditor_iban=args.creditor_iban,
                creditor_bic=args.creditor_bic,
                remittance_info=args.remittance_info
            )
            
            batch = PaymentBatch(
                payment_info_id=f"BATCH-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                payments=[payment]
            )
            
            message_id = args.message_id or f"MSG-{datetime.now().strftime('%Y%m%d%H%M%S')}"
            initiator = args.initiator
        
        xml_output = generator.generate_pain001(
            message_id=message_id,
            initiating_party_name=initiator,
            batches=[batch]
        )
        
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(xml_output)
            print(f"Message pain.001 généré: {args.output}")
        else:
            print(xml_output)
        
        return 0
    
    def _generate_mt103(self, args) -> int:
        """Génère un message MT103"""
        if args.config:
            with open(args.config, 'r') as f:
                config = json.load(f)
            
            ordering = Party(
                name=config["debtor"]["name"],
                account=config["debtor"]["iban"],
                address_line1=config["debtor"].get("address_line1"),
                address_line2=config["debtor"].get("address_line2")
            )
            
            beneficiary = Party(
                name=config["creditor"]["name"],
                account=config["creditor"]["iban"],
                address_line1=config["creditor"].get("address_line1"),
                address_line2=config["creditor"].get("address_line2")
            )
            
            mt103 = MT103Message(
                sender_reference=config.get("reference", f"REF{datetime.now().strftime('%Y%m%d%H%M%S')}")[:16],
                bank_operation_code="CRED",
                value_date=datetime.now(),
                currency=config.get("currency", "EUR"),
                amount=config["amount"],
                ordering_customer=ordering,
                ordering_institution=config["debtor"]["bic"],
                beneficiary_customer=beneficiary,
                beneficiary_institution=config["creditor"]["bic"],
                remittance_info=config.get("remittance_info", "Payment"),
                charges=config.get("charges", "SHA")
            )
        else:
            if not all([args.amount, args.debtor_name, args.debtor_iban, args.debtor_bic,
                       args.creditor_name, args.creditor_iban, args.creditor_bic]):
                self._error("Arguments manquants. Utilisez --config ou fournissez tous les arguments requis.")
                return 1
            
            ordering = Party(
                name=args.debtor_name.upper()[:35],
                account=args.debtor_iban
            )
            
            beneficiary = Party(
                name=args.creditor_name.upper()[:35],
                account=args.creditor_iban
            )
            
            mt103 = MT103Message(
                sender_reference=args.reference or f"REF{datetime.now().strftime('%Y%m%d%H%M%S')}"[:16],
                bank_operation_code="CRED",
                value_date=datetime.now(),
                currency=args.currency,
                amount=args.amount,
                ordering_customer=ordering,
                ordering_institution=args.debtor_bic,
                beneficiary_customer=beneficiary,
                beneficiary_institution=args.creditor_bic,
                remittance_info=args.remittance_info.upper(),
                charges=args.charges
            )
        
        # Validation
        errors = mt103.validate()
        if errors:
            for error in errors:
                self._error(error)
            return 1
        
        output = mt103.generate()
        
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(output)
            print(f"Message MT103 généré: {args.output}")
        else:
            print(output)
        
        return 0
    
    def _batch_validate(self, args) -> int:
        """Valide un fichier de BIC ou IBAN"""
        results = []
        valid_count = 0
        invalid_count = 0
        
        with open(args.file, 'r') as f:
            lines = [line.strip() for line in f if line.strip()]
        
        for line in lines:
            if args.type == "bic":
                is_valid, message = validate_bic(line)
            else:
                is_valid, message = validate_iban(line)
            
            results.append({
                "input": line,
                "valid": is_valid,
                "message": message
            })
            
            if is_valid:
                valid_count += 1
            else:
                invalid_count += 1
        
        summary = {
            "total": len(results),
            "valid": valid_count,
            "invalid": invalid_count,
            "results": results
        }
        
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(summary, f, indent=2, ensure_ascii=False)
            print(f"Rapport généré: {args.output}")
            print(f"Total: {len(results)} | Valides: {valid_count} | Invalides: {invalid_count}")
        else:
            if hasattr(args, 'json') and args.json:
                print(json.dumps(summary, indent=2, ensure_ascii=False))
            else:
                print(f"\n{'='*60}")
                print(f"Rapport de validation ({args.type.upper()})")
                print(f"{'='*60}")
                for r in results:
                    status = "✓" if r["valid"] else "✗"
                    print(f"{status} {r['input']:40} : {r['message']}")
                print(f"{'='*60}")
                print(f"Total: {len(results)} | Valides: {valid_count} | Invalides: {invalid_count}")
        
        return 0 if invalid_count == 0 else 1


def main():
    """Point d'entrée principal"""
    cli = SwiftCLI()
    sys.exit(cli.run())


if __name__ == "__main__":
    main()
