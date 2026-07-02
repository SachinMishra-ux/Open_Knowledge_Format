from pathlib import Path
from typing import Dict, List, Optional, Union
from datetime import datetime
import logging
from google_okf.core.models import Concept
from google_okf.producers.base import BaseProducer

# Import SQLAlchemy utilities safely
try:
    from sqlalchemy import create_engine, inspect
except ImportError:
    create_engine = inspect = None

logger = logging.getLogger(__name__)

class MySQLProducer(BaseProducer):
    """
    Producer that connects to a MySQL (or other SQL databases using SQLAlchemy) 
    and generates OKF Concepts representing the schema, tables, and relationships.
    """
    
    def __init__(
        self, 
        connection_uri: str, 
        output_prefix: str = "database/tables",
        schema: Optional[str] = None,
        tables: Optional[List[str]] = None,
        exclude_tables: Optional[List[str]] = None
    ):
        """
        Args:
            connection_uri: SQLAlchemy-compatible connection string (e.g. 'mysql+pymysql://user:pass@host:port/db').
            output_prefix: Subfolder path prefix for concept IDs (e.g. 'database/tables').
            schema: Optional database schema name to inspect.
            tables: List of specific table names to include (if None, all tables are included).
            exclude_tables: List of table names to exclude.
        """
        self.connection_uri = connection_uri
        self.output_prefix = output_prefix
        self.schema = schema
        self.tables = tables
        self.exclude_tables = exclude_tables or []

    def produce(self) -> Dict[str, Concept]:
        concepts = {}
        if create_engine is None:
            raise ImportError("SQLAlchemy is required to run MySQLProducer. Install it via pip/uv.")
            
        logger.info(f"Connecting to database to generate OKF concepts...")
        
        connect_args = {}
        uri = self.connection_uri
        
        # Parse query params to handle SSL arguments for PyMySQL/Aiven
        if "?" in uri:
            import urllib.parse
            base_url, query_str = uri.split("?", 1)
            params = urllib.parse.parse_qs(query_str)
            
            # Check for ssl-mode, ssl_mode, or ssl
            has_ssl = False
            for k in list(params.keys()):
                if k.lower() in ("ssl-mode", "ssl_mode", "ssl"):
                    val = params[k][0].lower()
                    if val in ("required", "true", "1", "preferred"):
                        has_ssl = True
                        # Remove it from connection params so PyMySQL doesn't crash
                        params.pop(k)
                        
            # Reconstruct URI without the invalid param
            if has_ssl:
                connect_args["ssl"] = {}
                new_query = urllib.parse.urlencode(params, doseq=True)
                uri = f"{base_url}?{new_query}" if new_query else base_url
                logger.info("SSL mode required. Configured connection with SSL context.")

        engine = create_engine(uri, connect_args=connect_args)
        
        try:
            inspector = inspect(engine)
            db_tables = inspector.get_table_names(schema=self.schema)
            
            for table_name in db_tables:
                # Filter tables
                if self.tables and table_name not in self.tables:
                    continue
                if table_name in self.exclude_tables:
                    continue
                    
                concept_id = f"{self.output_prefix}/{table_name}" if self.output_prefix else table_name
                concept_id = concept_id.replace("\\", "/")
                
                try:
                    concept = self._inspect_table(inspector, table_name)
                    concepts[concept_id] = concept
                    logger.info(f"Processed table: {table_name} -> {concept_id}")
                except Exception as e:
                    logger.error(f"Failed to inspect table {table_name}: {e}")
                    
        except Exception as e:
            logger.error(f"Database connection or inspection error: {e}")
            raise e
        finally:
            engine.dispose()
            
        return concepts

    def _inspect_table(self, inspector, table_name: str) -> Concept:
        # Get column details
        columns_info = inspector.get_columns(table_name, schema=self.schema)
        pk_info = inspector.get_pk_constraint(table_name, schema=self.schema) or {}
        pk_cols = pk_info.get("constrained_columns", [])
        
        # Get foreign key details
        fks = inspector.get_foreign_keys(table_name, schema=self.schema) or []
        
        # Build column maps for the YAML frontmatter
        yaml_columns = []
        for col in columns_info:
            col_name = col["name"]
            is_pk = col_name in pk_cols
            
            # Check if this column is a foreign key
            fk_ref = None
            for fk in fks:
                if col_name in fk["constrained_columns"]:
                    idx = fk["constrained_columns"].index(col_name)
                    ref_table = fk["referred_table"]
                    ref_col = fk["referred_columns"][idx]
                    fk_ref = {
                        "table": ref_table,
                        "column": ref_col
                    }
                    break
                    
            yaml_columns.append({
                "name": col_name,
                "type": str(col["type"]),
                "nullable": col["nullable"],
                "default": str(col.get("default")) if col.get("default") is not None else None,
                "primary_key": is_pk,
                "foreign_key": fk_ref
            })
            
        # Build YAML frontmatter structure
        extra_metadata = {
            "columns": yaml_columns,
            "database_name": getattr(inspector.bind, "dialect", None) and inspector.bind.url.database or "unknown",
            "schema_name": self.schema or "default"
        }
        
        # Generate Markdown body
        body_lines = [
            f"# Table: {table_name}",
            "",
            "## Schema Information",
            "",
            "| Column | Type | Primary Key? | Nullable? | Default | Foreign Key Reference |",
            "| :--- | :--- | :---: | :---: | :--- | :--- |"
        ]
        
        for col in yaml_columns:
            pk_str = "🔑 Yes" if col["primary_key"] else ""
            null_str = "Yes" if col["nullable"] else "No"
            default_str = f"`{col['default']}`" if col["default"] else ""
            
            fk_str = ""
            if col["foreign_key"]:
                ref = col["foreign_key"]
                # Use Markdown link to cross-reference related table concept in the bundle
                target_link = f"{ref['table']}.md"
                fk_str = f"🔗 references [{ref['table']}]({target_link})(`{ref['column']}`)"
                
            body_lines.append(
                f"| `{col['name']}` | `{col['type']}` | {pk_str} | {null_str} | {default_str} | {fk_str} |"
            )
            
        # Add relationships section if foreign keys exist
        if fks:
            body_lines.append("")
            body_lines.append("## Relationships")
            body_lines.append("")
            for fk in fks:
                ref_table = fk["referred_table"]
                constrained = ", ".join(fk["constrained_columns"])
                referred = ", ".join(fk["referred_columns"])
                body_lines.append(
                    f"- Columns `({constrained})` reference [{ref_table}]({ref_table}.md) `({referred})`"
                )
                
        # Safe URI generation for resource
        connection_url = str(inspector.bind.url)
        # Strip password from resource URI to protect secrets
        if "@" in connection_url:
            parts = connection_url.split("@")
            prefix = parts[0].split("://")[0]
            connection_url = f"{prefix}://***@{parts[1]}"
        resource_uri = f"{connection_url}/{table_name}"
        
        return Concept(
            type="Database Table",
            title=f"Table: {table_name}",
            description=f"Auto-generated schema and relationships metadata for table {table_name}.",
            resource=resource_uri,
            timestamp=datetime.now(),
            tags=["database", "table", "sql"],
            body="\n".join(body_lines),
            **extra_metadata
        )
