# Système de paiement SWIFT et norme ISO 20022

## Introduction

Ce document explique le fonctionnement du système de paiement SWIFT et la norme ISO 20022, avec des exemples de code pratiques pour implémenter un système bancaire conforme.

---

## Qu'est-ce que SWIFT ?

**SWIFT** (Society for Worldwide Interbank Financial Telecommunication) est un réseau de messagerie sécurisé permettant aux institutions financières d'échanger des informations standardisées sur les transactions financières.

### Composants clés

#### 1. Code BIC/SWIFT

Identifiant unique de 8 ou 11 caractères composé de :

| Position | Longueur | Description | Exemple |
|----------|----------|-------------|---------|
| 1-4 | 4 lettres | Code banque | BNPA |
| 5-6 | 2 lettres | Code pays (ISO 3166) | FR |
| 7-8 | 2 caractères | Code localisation | PP |
| 9-11 | 3 caractères | Code agence (optionnel) | XXX |

**Exemple complet** : `BNPAFRPPXXX` (BNP Paribas, France, Paris, Siège)

#### 2. Types de messages SWIFT (MT - Message Type)

| Code | Description | Usage |
|------|-------------|-------|
| MT103 | Single Customer Credit Transfer | Transfert client individuel |
| MT202 | General Financial Institution Transfer | Transfert interbancaire |
| MT940 | Customer Statement Message | Relevé de compte |
| MT950 | Statement Message | Relevé bancaire |
| MT199 | Free Format Message | Message libre |

---

## Norme ISO 20022

ISO 20022 est le nouveau standard XML qui remplace progressivement les messages MT SWIFT. Il utilise des messages **MX** avec une structure XML plus riche et plus détaillée.

### Avantages d'ISO 20022

- **Richesse des données** : Plus d'informations structurées
- **Interopérabilité** : Standard universel
- **Automatisation** : Traitement STP (Straight-Through Processing)
- **Traçabilité** : Meilleur suivi des transactions

### Types de messages principaux

| Catégorie | Code | Description |
|-----------|------|-------------|
| **pain** | pain.001 | Customer Credit Transfer Initiation |
| **pain** | pain.002 | Customer Payment Status Report |
| **pacs** | pacs.008 | FI to FI Customer Credit Transfer |
| **pacs** | pacs.002 | FI to FI Payment Status Report |
| **camt** | camt.052 | Bank to Customer Account Report |
| **camt** | camt.053 | Bank to Customer Statement |
| **camt** | camt.054 | Bank to Customer Debit/Credit Notification |

### Structure d'un message ISO 20022

```
Document
└── CstmrCdtTrfInitn (pain.001)
    ├── GrpHdr (Group Header)
    │   ├── MsgId
    │   ├── CreDtTm
    │   ├── NbOfTxs
    │   ├── CtrlSum
    │   └── InitgPty
    └── PmtInf (Payment Information)
        ├── PmtInfId
        ├── PmtMtd
        ├── Dbtr (Debtor)
        ├── DbtrAcct
        ├── DbtrAgt
        └── CdtTrfTxInf (Credit Transfer Transaction)
            ├── PmtId
            ├── Amt
            ├── CdtrAgt
            ├── Cdtr
            ├── CdtrAcct
            └── RmtInf
```

---

## Validation IBAN

L'IBAN (International Bank Account Number) est validé selon l'algorithme ISO 13616 :

### Structure IBAN

| Élément | Position | Description |
|---------|----------|-------------|
| Code pays | 1-2 | Lettres ISO 3166 |
| Clé de contrôle | 3-4 | 2 chiffres |
| BBAN | 5+ | Basic Bank Account Number |

### Longueurs par pays

| Pays | Code | Longueur |
|------|------|----------|
| France | FR | 27 |
| Allemagne | DE | 22 |
| Royaume-Uni | GB | 22 |
| Espagne | ES | 24 |
| Italie | IT | 27 |
| Belgique | BE | 16 |
| Pays-Bas | NL | 18 |
| Suisse | CH | 21 |

### Algorithme de validation

1. Réorganiser : déplacer les 4 premiers caractères à la fin
2. Convertir les lettres en chiffres (A=10, B=11, ..., Z=35)
3. Calculer modulo 97
4. Résultat doit être égal à 1

---

## Exemples de code

Les exemples de code sont disponibles dans le dossier `code/` :

| Fichier | Description |
|---------|-------------|
| [bic_validator.py](code/bic_validator.py) | Validation et parsing des codes BIC/SWIFT |
| [iban_validator.py](code/iban_validator.py) | Validation IBAN selon ISO 13616 |
| [iso20022_generator.py](code/iso20022_generator.py) | Génération de messages pain.001 (ISO 20022) |
| [mt103_generator.py](code/mt103_generator.py) | Génération de messages MT103 (format legacy) |

### Utilisation rapide

```bash
# Validation d'un code BIC
python code/bic_validator.py

# Validation d'un IBAN
python code/iban_validator.py

# Génération d'un message ISO 20022
python code/iso20022_generator.py

# Génération d'un message MT103
python code/mt103_generator.py
```

---

## Structure de projet recommandée

```
swift_banking_system/
├── __init__.py
├── validators/
│   ├── __init__.py
│   ├── bic_validator.py
│   └── iban_validator.py
├── generators/
│   ├── __init__.py
│   ├── iso20022_generator.py
│   └── mt103_generator.py
├── schemas/
│   ├── pain.001.001.09.xsd
│   ├── pacs.008.001.08.xsd
│   └── camt.053.001.08.xsd
├── tests/
│   ├── test_bic.py
│   ├── test_iban.py
│   └── test_messages.py
└── config/
    └── bank_codes.json
```

---

## Points importants à retenir

### Migration MT → MX

- SWIFT migre vers ISO 20022 (échéance novembre 2025)
- Les messages MT seront progressivement dépréciés
- La coexistence MT/MX est supportée pendant la transition

### Bonnes pratiques

1. **Validation stricte** : Toujours valider IBAN et BIC avant envoi
2. **Traçabilité** : Chaque message doit avoir un ID unique (MsgId, InstrId)
3. **Conformité** : Respecter les schémas XSD officiels ISO 20022
4. **Sécurité** : Utiliser des canaux sécurisés (TLS, signatures)
5. **Archivage** : Conserver les messages pendant la durée légale

### Ressources officielles

- [SWIFT](https://www.swift.com/)
- [ISO 20022](https://www.iso20022.org/)
- [SWIFT Message Reference](https://www.swift.com/standards/category-api)

---

## Changelog

| Date | Version | Description |
|------|---------|-------------|
| 2026-02-14 | 1.0 | Création initiale du document |
