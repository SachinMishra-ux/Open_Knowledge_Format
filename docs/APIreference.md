# API Reference

This page describes the core models, utility functions, and source producers exposed by the `google-okf` library.

---

## Core Models

### `Concept`
Represents a single OKF document consisting of YAML frontmatter and a Markdown body.

??? note "Example Usage"
    ```python
    from datetime import datetime
    from google_okf import Concept

    concept = Concept(
        type="Database Table",
        title="Table: users",
        description="Stores user accounts information",
        resource="mysql://localhost/users",
        tags=["database", "sql"],
        timestamp=datetime.now(),
        body="# Table: users\n\nThis table contains user data."
    )
    # Serialize to standard OKF string format
    file_content = concept.to_file_content()
    ```

| Field Name | Type | Required? | Description |
| :--- | :--- | :---: | :--- |
| `type` | `str` | **Yes** | The concept type (e.g. `Database Table`, `Document`, `Metric`). |
| `title` | `Optional[str]` | No | Human-readable display name. |
| `description` | `Optional[str]` | No | Brief summary snippet of the concept. |
| `resource` | `Optional[str]` | No | Canonical URI identifying the underlying asset. |
| `tags` | `Optional[List[str]]` | No | List of metadata tags. Defaults to `[]`. |
| `timestamp` | `Optional[datetime]` | No | Date and time when the concept was last modified. |
| `body` | `str` | No | Free-form markdown content. Defaults to `""`. |

---

## Core I/O Functions

### `write_concept`
Writes a single `Concept` file to a bundle directory.

```python
from google_okf import write_concept
write_concept(bundle_dir="my_bundle", concept_id="tables/users", concept=concept)
```

| Argument | Type | Description |
| :--- | :--- | :--- |
| `bundle_dir` | `Union[Path, str]` | The root directory of the OKF bundle. |
| `concept_id` | `str` | Relative path identifying the concept (e.g. `tables/users`). |
| `concept` | `Concept` | The `Concept` instance to write. |

* **Returns**: `Path` - The absolute path of the written file.

---

### `write_bundle`
Writes a dictionary of concepts into a bundle directory structure.

```python
from google_okf import write_bundle
concepts = {"tables/users": concept_a, "documents/guide": concept_b}
write_bundle(bundle_dir="my_bundle", concepts=concepts)
```

| Argument | Type | Description |
| :--- | :--- | :--- |
| `bundle_dir` | `Union[Path, str]` | The root directory of the OKF bundle. |
| `concepts` | `Dict[str, Concept]` | Dict mapping Concept IDs to `Concept` instances. |

---

### `read_concept`
Parses a single OKF Markdown file into a `Concept` instance.

```python
from google_okf import read_concept
concept = read_concept("my_bundle/tables/users.md")
```

| Argument | Type | Description |
| :--- | :--- | :--- |
| `file_path` | `Union[Path, str]` | Path to the OKF markdown file. |

* **Returns**: `Concept` - The parsed concept object.

---

### `read_bundle`
Scans and parses an entire OKF bundle directory, returning all concepts.

```python
from google_okf import read_bundle
concepts = read_bundle("my_bundle")
```

| Argument | Type | Description |
| :--- | :--- | :--- |
| `bundle_dir` | `Union[Path, str]` | The root directory of the OKF bundle. |

* **Returns**: `Dict[str, Concept]` - Map of Concept IDs (relative paths without `.md` extension) to parsed concepts.

---

### `validate_bundle_links`
Scans all concepts in a bundle and validates that all internal markdown relative links point to existing files.

```python
from google_okf import validate_bundle_links
broken_links = validate_bundle_links("my_bundle")
```

| Argument | Type | Description |
| :--- | :--- | :--- |
| `bundle_dir` | `Union[Path, str]` | The root directory of the OKF bundle. |

* **Returns**: `List[Tuple[str, str, str]]` - List of broken link tuples: `(source_concept_id, target_link, error_details)`.

---

## Connectors & Producers

### `DocumentProducer`
Extracts text and metadata from files (PDF, DOCX, MD, TXT) in a directory and maps them to OKF concepts.

??? note "Example"
    ```python
    from google_okf import DocumentProducer
    producer = DocumentProducer(source_dir="./docs", output_prefix="documents")
    concepts = producer.produce()
    ```

| Parameter | Type | Default | Description |
| :--- | :--- | :---: | :--- |
| `source_dir` | `Union[Path, str]` | *Required* | Directory containing the source documents. |
| `output_prefix` | `str` | `"documents"` | Prefix subfolder for concept IDs (e.g. `documents/deploy`). |
| `tags` | `List[str]` | `[]` | List of global tags to apply to all imported documents. |

* **Returns**: `Dict[str, Concept]` - Extracted document concepts.

---

### `MySQLProducer`
Connects to SQL databases (MySQL, SQLite, PostgreSQL, etc. via SQLAlchemy), inspects tables, column metadata, primary/foreign keys, and outputs OKF table concepts.

??? note "Example"
    ```python
    from google_okf import MySQLProducer
    producer = MySQLProducer(
        connection_uri="mysql+pymysql://user:pass@host:port/dbname?ssl-mode=REQUIRED",
        output_prefix="database/tables"
    )
    concepts = producer.produce()
    ```

| Parameter | Type | Default | Description |
| :--- | :--- | :---: | :--- |
| `connection_uri` | `str` | *Required* | SQLAlchemy connection string. |
| `output_prefix` | `str` | `"database/tables"`| Prefix subfolder for concept IDs. |
| `schema` | `Optional[str]` | `None` | Inspect a specific database schema name. |
| `tables` | `Optional[List[str]]`| `None` | Restrict extraction to these specific table names. |
| `exclude_tables` | `Optional[List[str]]`| `None` | Exclude these table names from extraction. |

* **Returns**: `Dict[str, Concept]` - Extracted table concepts.

---

### `MongoDBProducer`
Connects to MongoDB, samples collections to dynamically infer BSON/Python schemas, and outputs OKF collection concepts.

??? note "Example"
    ```python
    from google_okf import MongoDBProducer
    producer = MongoDBProducer(
        connection_uri="mongodb+srv://user:pass@cluster.mongodb.net/",
        database_name="upi_db",
        output_prefix="database/collections"
    )
    concepts = producer.produce()
    ```

| Parameter | Type | Default | Description |
| :--- | :--- | :---: | :--- |
| `connection_uri` | `str` | *Required* | MongoDB connection URI. |
| `database_name` | `str` | *Required* | Name of the database to inspect. |
| `output_prefix` | `str` | `"database/collections"`| Prefix subfolder for concept IDs. |
| `sample_size` | `int` | `10` | Number of documents to sample per collection for schema inference. |
| `collections` | `Optional[List[str]]`| `None` | Include only these specific collection names. |
| `exclude_collections`| `Optional[List[str]]`| `None` | Exclude these collection names. |

* **Returns**: `Dict[str, Concept]` - Extracted collection concepts.
