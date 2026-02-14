# SWIFT Banking CLI 🏦

[![CI/CD Pipeline](https://github.com/your-repo/swift-tools/actions/workflows/ci.yml/badge.svg)](https://github.com/your-repo/swift-tools/actions)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Outil en ligne de commande pour les opérations bancaires SWIFT et la génération de messages ISO 20022.

---

## 📦 Installation

### Installation via pip (recommandé)

```bash
# Installation depuis le répertoire local
pip install .

# Installation en mode développement (avec dépendances de dev)
pip install -e ".[dev]"

# Installation depuis GitHub (si publié)
pip install git+https://github.com/your-repo/swift-tools.git
```

### Installation via Docker

```bash
# Build de l'image
docker compose build

# Ou avec le script wrapper
./swift-cli.sh build
```

### Vérification de l'installation

```bash
# Vérifier que la commande est disponible
swift-cli --version

# Afficher l'aide
swift-cli --help
```

---

## 🚀 Utilisation

### Commandes disponibles

| Commande | Description |
|----------|-------------|
| `validate-bic` | Valider un code BIC/SWIFT |
| `validate-iban` | Valider un numéro IBAN |
| `generate-pain001` | Générer un message ISO 20022 pain.001 |
| `generate-mt103` | Générer un message MT103 (legacy SWIFT) |
| `batch-validate` | Valider un fichier de BIC/IBAN |

### Validation de codes BIC

```bash
# Valider un code BIC
swift-cli validate-bic BNPAFRPPXXX

# Sortie JSON
swift-cli --json validate-bic BNPAFRPPXXX
```

**Exemple de sortie :**
```
input: BNPAFRPPXXX
valid: True
message: BIC valide: BNPAFRPPXXX (France)
bank_code: BNPA
country_code: FR
country_name: France
location_code: PP
branch_code: XXX
is_primary_office: True
```

### Validation d'IBAN

```bash
# Valider un IBAN français
swift-cli validate-iban FR7630006000011234567890189

# Avec espaces (entre guillemets)
swift-cli validate-iban "FR76 3000 6000 0112 3456 7890 189"
```

### Génération de messages ISO 20022 (pain.001)

```bash
# Avec un fichier de configuration JSON
swift-cli generate-pain001 --config data/sample_payment.json --output output/payment.xml

# Avec des paramètres en ligne de commande
swift-cli generate-pain001 \
  --amount 1500.00 \
  --currency EUR \
  --debtor-name "ACME Corporation" \
  --debtor-iban FR7630006000011234567890189 \
  --debtor-bic BNPAFRPPXXX \
  --creditor-name "Supplier Ltd" \
  --creditor-iban DE89370400440532013000 \
  --creditor-bic COBADEFFXXX \
  --remittance-info "Invoice INV-2026-001" \
  --output output/payment.xml
```

### Génération de messages MT103 (legacy SWIFT)

```bash
# Avec des paramètres en ligne de commande
swift-cli generate-mt103 \
  --amount 5000.00 \
  --currency EUR \
  --debtor-name "ACME Corporation" \
  --debtor-iban FR7630006000011234567890189 \
  --debtor-bic BNPAFRPPXXX \
  --creditor-name "Supplier Ltd" \
  --creditor-iban DE89370400440532013000 \
  --creditor-bic COBADEFFXXX \
  --remittance-info "PAYMENT" \
  --charges SHA \
  --output output/mt103.txt
```

### Validation par lot

```bash
# Valider un fichier d'IBAN
swift-cli batch-validate --file data/ibans.txt --type iban --output output/report.json

# Valider un fichier de BIC
swift-cli batch-validate --file data/bics.txt --type bic
```

---

## 🐳 Utilisation avec Docker

```bash
# Utiliser le script wrapper (recommandé)
./swift-cli.sh validate-bic BNPAFRPPXXX
./swift-cli.sh validate-iban FR7630006000011234567890189
./swift-cli.sh generate-pain001 --config /data/sample_payment.json --output /app/output/payment.xml

# Ou directement avec docker compose
docker compose run --rm swift validate-bic BNPAFRPPXXX
```

---

## 📂 Structure du projet

```
swift-tools/
├── swift_cli/                 # Package Python
│   ├── __init__.py
│   ├── main.py               # Point d'entrée CLI
│   ├── bic_validator.py      # Validation BIC/SWIFT
│   ├── iban_validator.py     # Validation IBAN (ISO 13616)
│   ├── iso20022_generator.py # Génération pain.001
│   └── mt103_generator.py    # Génération MT103
├── tests/                     # Tests unitaires
│   ├── test_bic_validator.py
│   ├── test_iban_validator.py
│   ├── test_iso20022_generator.py
│   └── test_mt103_generator.py
├── data/                      # Fichiers de configuration exemple
│   └── sample_payment.json
├── output/                    # Fichiers générés
├── .github/workflows/         # CI/CD GitHub Actions
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml            # Configuration du projet Python
└── README.md
```

---

## 🧪 Développement

### Installation des dépendances de développement

```bash
pip install -e ".[dev]"
```

### Exécution des tests

```bash
# Tous les tests
pytest tests/ -v

# Avec couverture
pytest tests/ -v --cov=swift_cli --cov-report=html

# Tests spécifiques
pytest tests/test_bic_validator.py -v
```

### Formatage du code

```bash
# Formatter avec Black
black swift_cli/ tests/ --line-length 120

# Vérifier avec flake8
flake8 swift_cli/ --max-line-length=120

# Vérifier les types avec mypy
mypy swift_cli/ --ignore-missing-imports
```

---

## 📚 Documentation technique

### Qu'est-ce que SWIFT ?

**SWIFT** (Society for Worldwide Interbank Financial Telecommunication) est un réseau de messagerie sécurisé permettant aux institutions financières d'échanger des informations standardisées sur les transactions financières.

#### Structure d'un code BIC/SWIFT

| Position | Longueur | Description | Exemple |
|----------|----------|-------------|---------|
| 1-4 | 4 lettres | Code banque | BNPA |
| 5-6 | 2 lettres | Code pays (ISO 3166) | FR |
| 7-8 | 2 caractères | Code localisation | PP |
| 9-11 | 3 caractères | Code agence (optionnel) | XXX |

**Exemple** : `BNPAFRPPXXX` = BNP Paribas, France, Paris, Siège

### Norme ISO 20022

ISO 20022 est le nouveau standard XML qui remplace progressivement les messages MT SWIFT.

#### Types de messages principaux

| Catégorie | Code | Description |
|-----------|------|-------------|
| **pain** | pain.001 | Customer Credit Transfer Initiation |
| **pain** | pain.002 | Customer Payment Status Report |
| **pacs** | pacs.008 | FI to FI Customer Credit Transfer |
| **camt** | camt.053 | Bank to Customer Statement |

### Validation IBAN (ISO 13616)

| Pays | Code | Longueur |
|------|------|----------|
| France | FR | 27 |
| Allemagne | DE | 22 |
| Royaume-Uni | GB | 22 |
| Espagne | ES | 24 |
| Belgique | BE | 16 |

---

## 📄 Licence

MIT License - voir le fichier [LICENSE](LICENSE) pour plus de détails.

---

## 👤 Auteur

**Livinus TUYISENGE**
- Email: livinus.tuyisenge@proton.me

---

## 📝 Changelog

| Date | Version | Description |
|------|---------|-------------|
| 2026-02-14 | 1.0.0 | Version initiale avec CLI pip installable |
