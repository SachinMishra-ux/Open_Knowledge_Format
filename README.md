# google-okf

[![PyPI version](https://img.shields.io/pypi/v/google-okf.svg)](https://pypi.org/project/google-okf/)
[![Python versions](https://img.shields.io/pypi/pyversions/google-okf.svg)](https://pypi.org/project/google-okf/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

`google-okf` is a production-grade, open-source Python library designed to automatically connect to various enterprise data sources and convert them into the standard **Google Open Knowledge Format (OKF)**. 

By standardizing database schemas, collections, documentation, playbooks, and APIs into clean Markdown files with structured YAML frontmatter, `google-okf` acts as the critical intermediate context-assembly layer for Retrieval-Augmented Generation (RAG) pipelines and agentic AI systems.

---

## What is Google OKF?

The **Open Knowledge Format (OKF v0.1)** is an open, vendor-neutral standard introduced by Google Cloud to formalize the "LLM Wiki" pattern. Instead of feeding raw, fragmented, and inconsistent documentation or database formats directly into vector databases, OKF structures knowledge into a unified, version-controlled (Git-friendly) directory tree:
1. **YAML Frontmatter**: Self-describing metadata for routing, filtering, and identification (requires a `type` field; recommends `title`, `description`, `resource` URI, `tags`, and `timestamp`).
2. **Markdown Body**: Structurally clean, human- and LLM-readable text content.
3. **Semantic Links**: Standard markdown links mapping relationships between concepts, enabling AI agents to walk and traverse a semantic knowledge graph.

---

## Features

* **BaseProducer Interface**: Simple, abstract class to write custom connectors for any internal system.
* **Flat File Connector**: Imports a directory of documents (PDFs, DOCX, Markdown, TXT), extracts text, and maps them to OKF concepts.
* **SQL Database Connector**: Connects to relational databases (MySQL, PostgreSQL, SQLite, etc. using SQLAlchemy) and auto-generates Markdown schemas with interactive cross-referenced links for foreign key relationships.
* **MongoDB NoSQL Connector**: Connects to MongoDB, samples collection documents, dynamically infers schema structures, and generates collection concepts.
* **CLI Tool (`google-okf`)**: Initialize bundles, run producers, and validate/lint OKF link consistency.

---

## Installation

Install the package via `pip`:
```bash
pip install google-okf
```

Or using `uv` (recommended):
```bash
uv add google-okf
```

---

## Command Line Interface (CLI)

The library provides a CLI tool named `google-okf`.

### 1. Initialize a Bundle
Create a blank OKF folder structure with default subdirectories:
```bash
google-okf init my_knowledge_bundle
```

### 2. Run a Producer
Run a connector to extract metadata from a source and write it into a bundle folder:

**Flat Files:**
```bash
google-okf produce --type files --src-dir ./raw_documents --out-dir my_knowledge_bundle
```

**MySQL / Relational DB:**
```bash
google-okf produce --type mysql --uri "mysql+pymysql://user:pass@host:port/dbname?ssl-mode=REQUIRED" --out-dir my_knowledge_bundle
```

**MongoDB:**
```bash
google-okf produce --type mongodb --uri "mongodb+srv://user:pass@cluster.mongodb.net/" --db-name "my_database" --out-dir my_knowledge_bundle
```

### 3. Using a Configuration File
You can also store connection details in a YAML config file (`config.yaml`):
```yaml
producer: mysql
uri: "mysql+pymysql://user:pass@host:port/dbname?ssl-mode=REQUIRED"
output_dir: "my_knowledge_bundle"
```
And run it with:
```bash
google-okf produce --config config.yaml
```

### 4. Lint and Validate Compliance
Verify that all YAML frontmatter compiles, required fields are present, and all internal relative markdown links resolve correctly:
```bash
google-okf lint my_knowledge_bundle
```

---

## Programmatic Usage

### 1. Flat Files Import
```python
from google_okf import DocumentProducer, write_bundle

# Initialize producer for a folder of documents
producer = DocumentProducer(
    source_dir="./financial_statements",
    output_prefix="documents/financials",
    tags=["finance", "annual-report"]
)

# Extract and write to bundle
concepts = producer.produce()
write_bundle("my_okf_bundle", concepts)
```

### 2. MySQL / SQL Database Import
```python
from google_okf import MySQLProducer, write_bundle

# Connection URI (uses SQLAlchemy syntax)
connection_uri = "mysql+pymysql://user:pass@host:16512/defaultdb?ssl-mode=REQUIRED"

producer = MySQLProducer(
    connection_uri=connection_uri,
    output_prefix="database/tables",
    schema="default"  # Optional schema filter
)

# Extract tables, column types, keys, and links
concepts = producer.produce()
write_bundle("my_okf_bundle", concepts)
```

### 3. MongoDB Collection Schema Inference
```python
from google_okf import MongoDBProducer, write_bundle

producer = MongoDBProducer(
    connection_uri="mongodb+srv://user:pass@cluster.mongodb.net/?appName=Cluster",
    database_name="upi_db",
    output_prefix="database/collections",
    sample_size=15  # Number of documents to sample for type inference
)

# Sample documents, infer schemas, and write collections
concepts = producer.produce()
write_bundle("my_okf_bundle", concepts)
```

---

## Troubleshooting

### MongoDB SSL Handshake Failures (`TLSV1_ALERT_INTERNAL_ERROR`)
When connecting to a MongoDB Atlas cluster, you may encounter the following error:
```text
SSL handshake failed: ac-xxx-shard.mongodb.net:27017: [SSL: TLSV1_ALERT_INTERNAL_ERROR] tlsv1 alert internal error (_ssl.c:1010)
```

#### Root Cause
This is a secure connection rejection enforced by the MongoDB Atlas cluster. It occurs because the client IP address from which your script is running is **not whitelisted** in your Atlas database security settings. Passing `tlsAllowInvalidCertificates=True` or modifying certificates in code **will not** bypass this, as the server firewall terminates the TLS negotiation immediately at the TCP/TLS layer.

#### Solution
1. Log in to your **[MongoDB Atlas Console](https://cloud.mongodb.com/)**.
2. Under the **Security** header in the left sidebar, click **Network Access**.
3. Click **+ Add IP Address**.
4. Click **Add Current IP Address** to authorize your local machine, or input `0.0.0.0/0` (Allow Access from Anywhere) to permit connections from any network (useful for transient cloud deployments).
5. Click **Confirm** and wait 1–2 minutes for the access list to deploy.

### MySQL / PyMySQL SSL Connection Parameter Crashing
When passing connection URLs that require SSL (e.g. from providers like Aiven or AWS RDS), using `ssl-mode=REQUIRED` in query parameters can cause the PyMySQL driver to throw an exception: `Connection.__init__() got an unexpected keyword argument 'ssl-mode'`.

#### Solution
`google-okf` automatically intercepts query parameters containing `ssl-mode`, `ssl_mode`, or `ssl=true`. It strips them from the raw connection string so the driver does not crash, and configures the engine to pass the required SSL context parameters (`connect_args={"ssl": {}}`) under the hood to ensure an encrypted channel. No manual dictionary setup is necessary.

---

## Contributing & Testing

Development is managed using `uv` or `pip`. To run unit tests locally:
```bash
# Clone the repository
git clone https://github.com/SachinMishra-ux/Open_Knowledge_Format.git
cd Open_Knowledge_Format

# Sync dependencies and run tests
uv sync
uv run python -m unittest discover tests
```

---

## License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
