import unittest
import tempfile
from pathlib import Path
from datetime import datetime
from google_okf.core.models import Concept
from google_okf.core.writer import write_concept, write_bundle
from google_okf.core.reader import read_concept, read_bundle, validate_bundle_links

class TestCoreOKF(unittest.TestCase):
    
    def test_concept_serialization(self):
        timestamp = datetime(2026, 7, 2, 12, 0, 0)
        concept = Concept(
            type="Metric",
            title="Active Users",
            description="Daily Active Users count.",
            resource="metric://dau",
            tags=["business", "kpi"],
            timestamp=timestamp,
            body="## DAU Calculation\n\nDaily Active Users is calculated by summing unique user IDs per day."
        )
        
        file_content = concept.to_file_content()
        
        # Verify YAML frontmatter delimiters exist
        self.assertTrue(file_content.startswith("---"))
        self.assertIn("type: Metric", file_content)
        self.assertIn("title: Active Users", file_content)
        self.assertIn("resource: metric://dau", file_content)
        self.assertIn("tags:\n- business\n- kpi", file_content)
        self.assertIn("timestamp: '2026-07-02T12:00:00'", file_content)
        self.assertIn("Daily Active Users is calculated by summing unique user IDs per day.", file_content)
        
        # Parse it back
        parsed_concept = Concept.from_file_content(file_content)
        self.assertEqual(parsed_concept.type, "Metric")
        self.assertEqual(parsed_concept.title, "Active Users")
        self.assertEqual(parsed_concept.resource, "metric://dau")
        self.assertEqual(parsed_concept.tags, ["business", "kpi"])
        self.assertEqual(parsed_concept.body.strip(), "## DAU Calculation\n\nDaily Active Users is calculated by summing unique user IDs per day.")

    def test_writer_and_reader(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            concept = Concept(
                type="Playbook",
                title="Incident Response",
                body="Step 1: Identify\nStep 2: Contain"
            )
            
            concept_id = "procedures/incident_response"
            file_path = write_concept(tmp_path, concept_id, concept)
            
            self.assertTrue(file_path.exists())
            self.assertEqual(file_path, tmp_path / "procedures" / "incident_response.md")
            
            # Read back individual concept
            loaded = read_concept(file_path)
            self.assertEqual(loaded.type, "Playbook")
            self.assertEqual(loaded.title, "Incident Response")
            self.assertEqual(loaded.body.strip(), "Step 1: Identify\nStep 2: Contain")
            
            # Read bundle
            bundle = read_bundle(tmp_path)
            self.assertIn("procedures/incident_response", bundle)
            self.assertEqual(bundle["procedures/incident_response"].title, "Incident Response")

    def test_validation_links(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            
            # Create two concepts
            # Concept A links to Concept B correctly
            # Concept A also has a broken link to Concept C
            concept_a = Concept(
                type="Page",
                title="Page A",
                body="Here is a link to [Page B](page_b.md) and a broken link to [Page C](page_c.md)."
            )
            concept_b = Concept(
                type="Page",
                title="Page B",
                body="I link back to no one."
            )
            
            write_concept(tmp_path, "page_a", concept_a)
            write_concept(tmp_path, "page_b", concept_b)
            
            broken_links = validate_bundle_links(tmp_path)
            
            # We expect exactly one broken link (page_c.md does not exist)
            self.assertEqual(len(broken_links), 1)
            source_id, target_link, error_msg = broken_links[0]
            self.assertEqual(source_id, "page_a")
            self.assertEqual(target_link, "page_c.md")
            self.assertIn("does not exist", error_msg)

if __name__ == "__main__":
    unittest.main()
