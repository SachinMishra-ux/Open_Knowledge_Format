import unittest
from unittest.mock import MagicMock, patch
import tempfile
from pathlib import Path
from google_okf.producers.document import DocumentProducer
from google_okf.producers.mysql import MySQLProducer
from google_okf.producers.mongodb import MongoDBProducer

class TestProducers(unittest.TestCase):

    def test_document_producer_txt_md(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            
            # Create a dummy text file
            sub_dir = tmp_path / "playbooks"
            sub_dir.mkdir()
            txt_file = sub_dir / "setup_guide.txt"
            with open(txt_file, "w", encoding="utf-8") as f:
                f.write("Line 1 of setup guide.\nLine 2 of setup guide.")
                
            producer = DocumentProducer(source_dir=tmp_path, output_prefix="docs")
            concepts = producer.produce()
            
            self.assertIn("docs/playbooks/setup_guide", concepts)
            concept = concepts["docs/playbooks/setup_guide"]
            self.assertEqual(concept.type, "Document")
            self.assertEqual(concept.title, "Setup Guide")
            self.assertEqual(concept.body.strip(), "Line 1 of setup guide.\nLine 2 of setup guide.")
            self.assertEqual(concept.tags, ["txt"])
            self.assertTrue(concept.resource.startswith("file://"))

    @patch("google_okf.producers.mysql.create_engine")
    @patch("google_okf.producers.mysql.inspect")
    def test_mysql_producer(self, mock_inspect, mock_create_engine):
        # Set up mock engine and inspector
        mock_engine = MagicMock()
        mock_create_engine.return_value = mock_engine
        
        mock_inspector = MagicMock()
        mock_inspect.return_value = mock_inspector
        
        # Configure inspector mock behavior
        mock_inspector.get_table_names.return_value = ["users"]
        mock_inspector.get_columns.return_value = [
            {"name": "id", "type": "INTEGER", "nullable": False, "default": None},
            {"name": "email", "type": "VARCHAR(255)", "nullable": True, "default": None}
        ]
        mock_inspector.get_pk_constraint.return_value = {"constrained_columns": ["id"]}
        mock_inspector.get_foreign_keys.return_value = []
        mock_inspector.bind.url.database = "test_db"
        
        producer = MySQLProducer(connection_uri="mysql+pymysql://test_user@localhost/test_db", output_prefix="db")
        concepts = producer.produce()
        
        self.assertIn("db/users", concepts)
        concept = concepts["db/users"]
        self.assertEqual(concept.type, "Database Table")
        self.assertEqual(concept.title, "Table: users")
        self.assertIn("database_name", concept.model_extra)
        self.assertEqual(concept.model_extra["database_name"], "test_db")
        
        # Verify columns in extra data
        cols = concept.model_extra["columns"]
        self.assertEqual(len(cols), 2)
        self.assertEqual(cols[0]["name"], "id")
        self.assertTrue(cols[0]["primary_key"])
        self.assertEqual(cols[1]["name"], "email")
        self.assertFalse(cols[1]["primary_key"])
        
        # Verify markdown body content
        self.assertIn("| `id` | `INTEGER` | 🔑 Yes | No |  |  |", concept.body)
        self.assertIn("| `email` | `VARCHAR(255)` |  | Yes |  |  |", concept.body)

    @patch("google_okf.producers.mongodb.pymongo.MongoClient")
    def test_mongodb_producer(self, mock_mongo_client):
        # Set up mock client, db, and collection
        mock_client = MagicMock()
        mock_mongo_client.return_value = mock_client
        
        mock_db = MagicMock()
        mock_client.__getitem__.return_value = mock_db
        
        mock_collection = MagicMock()
        mock_db.list_collection_names.return_value = ["orders"]
        mock_db.__getitem__.return_value = mock_collection
        
        # Configure sample documents
        mock_collection.find.return_value.limit.return_value = [
            {"_id": "123", "total": 99.99, "items": ["apple", "banana"]},
            {"_id": "456", "total": 120.00, "status": "completed"}
        ]
        
        producer = MongoDBProducer(connection_uri="mongodb://localhost:27017/", database_name="test_mongodb", output_prefix="mongo")
        concepts = producer.produce()
        
        self.assertIn("mongo/orders", concepts)
        concept = concepts["mongo/orders"]
        self.assertEqual(concept.type, "NoSQL Collection")
        self.assertEqual(concept.title, "Collection: orders")
        self.assertEqual(concept.model_extra["collection_name"], "orders")
        
        # Inferred fields should contain _id, total, items, status
        fields = {f["name"]: f["types"] for f in concept.model_extra["fields"]}
        self.assertIn("_id", fields)
        self.assertIn("total", fields)
        self.assertIn("items", fields)
        self.assertIn("status", fields)
        
        self.assertEqual(fields["total"], ["float"])
        self.assertEqual(fields["items"], ["list[str]"])
        self.assertEqual(fields["status"], ["str"])
        
        # Verify markdown body content
        self.assertIn("| `_id` | `str` | Primary Key (usually ObjectId) |", concept.body)
        self.assertIn("| `total` | `float` |  |", concept.body)

if __name__ == "__main__":
    unittest.main()
