from pathlib import Path
from typing import Dict, List, Optional, Union, Any, Set
from datetime import datetime
import logging
from google_okf.core.models import Concept
from google_okf.producers.base import BaseProducer

# Import pymongo safely
try:
    import pymongo
except ImportError:
    pymongo = None

logger = logging.getLogger(__name__)

class MongoDBProducer(BaseProducer):
    """
    Producer that connects to a MongoDB database, infers schema metadata 
    by sampling documents in collections, and outputs OKF Concepts.
    """
    
    def __init__(
        self, 
        connection_uri: str, 
        database_name: str,
        output_prefix: str = "database/collections",
        sample_size: int = 10,
        collections: Optional[List[str]] = None,
        exclude_collections: Optional[List[str]] = None
    ):
        """
        Args:
            connection_uri: MongoDB connection string (e.g. 'mongodb://user:pass@host:port/').
            database_name: Name of the MongoDB database to inspect.
            output_prefix: Subfolder path prefix for concept IDs (e.g. 'database/collections').
            sample_size: Number of documents to sample per collection to infer schemas.
            collections: List of specific collection names to include (if None, all collections are included).
            exclude_collections: List of collection names to exclude.
        """
        self.connection_uri = connection_uri
        self.database_name = database_name
        self.output_prefix = output_prefix
        self.sample_size = sample_size
        self.collections = collections
        self.exclude_collections = exclude_collections or []

    def produce(self) -> Dict[str, Concept]:
        concepts = {}
        if pymongo is None:
            raise ImportError("pymongo is required to run MongoDBProducer. Install it via pip/uv.")
            
        logger.info(f"Connecting to MongoDB database '{self.database_name}'...")
        client = pymongo.MongoClient(self.connection_uri)
        
        try:
            db = client[self.database_name]
            # list_collection_names filters out system collections by default
            col_names = db.list_collection_names()
            
            for col_name in col_names:
                # Filter collections
                if self.collections and col_name not in self.collections:
                    continue
                if col_name in self.exclude_collections:
                    continue
                    
                concept_id = f"{self.output_prefix}/{col_name}" if self.output_prefix else col_name
                concept_id = concept_id.replace("\\", "/")
                
                try:
                    concept = self._inspect_collection(db, col_name)
                    concepts[concept_id] = concept
                    logger.info(f"Processed collection: {col_name} -> {concept_id}")
                except Exception as e:
                    logger.error(f"Failed to inspect MongoDB collection {col_name}: {e}")
                    
        except Exception as e:
            logger.error(f"MongoDB connection or inspection error: {e}")
            raise e
        finally:
            client.close()
            
        return concepts

    def _inspect_collection(self, db, col_name: str) -> Concept:
        collection = db[col_name]
        
        # Sample documents
        sampled_docs = list(collection.find().limit(self.sample_size))
        num_sampled = len(sampled_docs)
        
        # Infer schemas
        inferred_schema = self._merge_schemas(sampled_docs)
        
        # Format the schema for YAML frontmatter
        yaml_fields = []
        for field, types in inferred_schema.items():
            yaml_fields.append({
                "name": field,
                "types": types
            })
            
        extra_metadata = {
            "database_name": self.database_name,
            "collection_name": col_name,
            "sample_size_used": num_sampled,
            "fields": yaml_fields
        }
        
        # Generate Markdown body
        body_lines = [
            f"# Collection: {col_name}",
            "",
            f"This collection contains JSON documents in the '{self.database_name}' MongoDB database.",
            "",
            f"## Inferred Schema (Sampled {num_sampled} documents)",
            "",
            "| Field Path | Inferred Type(s) | Notes |",
            "| :--- | :--- | :--- |"
        ]
        
        for field, types in sorted(inferred_schema.items()):
            types_str = " or ".join(f"`{t}`" for t in types)
            notes = ""
            if field == "_id":
                notes = "Primary Key (usually ObjectId)"
            elif len(types) > 1:
                notes = "⚠️ Schema variance: multiple types detected"
                
            body_lines.append(f"| `{field}` | {types_str} | {notes} |")
            
        # Parse connection string to remove credentials for security
        parsed_uri = self.connection_uri
        if "@" in parsed_uri:
            # Strip credentials (mongodb://user:pass@host/ -> mongodb://***@host/)
            prefix = parsed_uri.split("://")[0]
            host_part = parsed_uri.split("@")[1]
            parsed_uri = f"{prefix}://***@{host_part}"
            
        resource_uri = f"{parsed_uri.rstrip('/')}/{self.database_name}/{col_name}"
        
        return Concept(
            type="NoSQL Collection",
            title=f"Collection: {col_name}",
            description=f"Auto-generated schema for collection {col_name} via schema inference.",
            resource=resource_uri,
            timestamp=datetime.now(),
            tags=["mongodb", "nosql", "collection"],
            body="\n".join(body_lines),
            **extra_metadata
        )

    def _infer_schema(self, val: Any, current_prefix: str = "", schema: Optional[Dict[str, Set[str]]] = None) -> Dict[str, Set[str]]:
        if schema is None:
            schema = {}
            
        if isinstance(val, dict):
            for k, v in val.items():
                field_path = f"{current_prefix}.{k}" if current_prefix else k
                if field_path not in schema:
                    schema[field_path] = set()
                schema[field_path].add("dict")
                self._infer_schema(v, field_path, schema)
        elif isinstance(val, list):
            # For list, record that this field is a list
            if current_prefix:
                if current_prefix not in schema:
                    schema[current_prefix] = set()
                # Inspect list elements
                el_types = set()
                for el in val:
                    el_type = type(el).__name__
                    if isinstance(el, dict):
                        el_type = "dict"
                        self._infer_schema(el, f"{current_prefix}[]", schema)
                    el_types.add(el_type)
                
                el_types_str = f"list[{', '.join(sorted(list(el_types)))}]" if el_types else "list[empty]"
                schema[current_prefix].add(el_types_str)
        else:
            if current_prefix:
                if current_prefix not in schema:
                    schema[current_prefix] = set()
                schema[current_prefix].add(type(val).__name__)
                
        return schema

    def _merge_schemas(self, docs: List[Dict[str, Any]]) -> Dict[str, List[str]]:
        merged = {}
        for doc in docs:
            # We treat the root document as a dictionary of fields
            for k, v in doc.items():
                if k not in merged:
                    merged[k] = set()
                if isinstance(v, dict):
                    merged[k].add("dict")
                    doc_schema = self._infer_schema(v, k)
                    for field, types in doc_schema.items():
                        if field not in merged:
                            merged[field] = set()
                        merged[field].update(types)
                elif isinstance(v, list):
                    el_types = set()
                    for el in v:
                        el_type = type(el).__name__
                        if isinstance(el, dict):
                            el_type = "dict"
                            # Recursively inspect list element dicts
                            doc_schema = self._infer_schema(el, f"{k}[]")
                            for field, types in doc_schema.items():
                                if field not in merged:
                                    merged[field] = set()
                                merged[field].update(types)
                        el_types.add(el_type)
                    
                    types_str = f"list[{', '.join(sorted(list(el_types)))}]" if el_types else "list[empty]"
                    merged[k].add(types_str)
                else:
                    merged[k].add(type(v).__name__)
                    
        # Convert sets to sorted lists of type names
        return {field: sorted(list(types)) for field, types in merged.items()}
