import os
from pathlib import Path
from typing import Dict, Union, List, Tuple
import re
from google_okf.core.models import Concept

RESERVED_FILENAMES = {"index.md", "log.md"}

def read_concept(file_path: Union[Path, str]) -> Concept:
    """
    Read a single concept file from disk.
    
    Args:
        file_path: Path to the concept markdown file.
        
    Returns:
        A parsed Concept instance.
    """
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    return Concept.from_file_content(content)

def read_bundle(bundle_dir: Union[Path, str]) -> Dict[str, Concept]:
    """
    Scan and read an entire OKF bundle directory.
    
    Args:
        bundle_dir: Path to the bundle directory.
        
    Returns:
        A dictionary mapping Concept IDs (relative paths without '.md') to Concept instances.
    """
    bundle_path = Path(bundle_dir)
    concepts = {}
    
    if not bundle_path.exists() or not bundle_path.is_dir():
        return concepts
        
    for root, _, files in os.walk(bundle_path):
        for file in files:
            if not file.endswith(".md"):
                continue
            if file in RESERVED_FILENAMES:
                continue
                
            full_path = Path(root) / file
            # Compute relative path as Concept ID
            rel_path = full_path.relative_to(bundle_path)
            concept_id = str(rel_path.with_suffix("")).replace("\\", "/")
            
            try:
                concepts[concept_id] = read_concept(full_path)
            except Exception as e:
                # We can raise or log, let's raise for strict validation or capture it
                raise ValueError(f"Error reading concept file '{rel_path}': {e}") from e
                
    return concepts

def validate_bundle_links(bundle_dir: Union[Path, str]) -> List[Tuple[str, str, str]]:
    """
    Validate that all internal markdown links between concepts in the bundle are valid.
    
    Args:
        bundle_dir: Path to the bundle directory.
        
    Returns:
        A list of tuples: (source_concept_id, target_link_path, error_message) for broken links.
    """
    bundle_path = Path(bundle_dir)
    concepts = read_bundle(bundle_path)
    broken_links = []
    
    # Regular expression to match markdown links: [text](link)
    # Exclude external links starting with http://, https://, mailto:, etc.
    link_pattern = re.compile(r"\[([^\]]*)\]\((?!https?://|mailto:|#)([^\)]+)\)")
    
    for concept_id, concept in concepts.items():
        # The file location relative to the bundle
        concept_file_path = bundle_path / f"{concept_id}.md"
        concept_dir = concept_file_path.parent
        
        # Find all local links in the markdown body
        matches = link_pattern.findall(concept.body)
        for text, link in matches:
            # Clean anchors (e.g. table.md#column-id -> table.md)
            clean_link = link.split("#")[0]
            if not clean_link:
                continue
                
            # Resolve the link relative to the concept file directory
            target_path = (concept_dir / clean_link).resolve()
            
            # Check if target file exists and is within the bundle
            try:
                # Try to check if target is inside bundle_path (resolve to make sure)
                resolved_bundle_path = bundle_path.resolve()
                if not target_path.exists():
                    broken_links.append((
                        concept_id,
                        link,
                        f"Target file '{target_path.relative_to(resolved_bundle_path)}' does not exist."
                    ))
                elif not str(target_path).startswith(str(resolved_bundle_path)):
                    broken_links.append((
                        concept_id,
                        link,
                        "Link points outside the bundle directory."
                    ))
            except ValueError:
                # relative_to can raise ValueError if target_path is not under bundle_path
                broken_links.append((
                    concept_id,
                    link,
                    "Link points outside the bundle directory."
                ))
                
    return broken_links
