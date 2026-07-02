import os
from pathlib import Path
from typing import Dict, Union
from google_okf.core.models import Concept

def write_concept(bundle_dir: Union[Path, str], concept_id: str, concept: Concept) -> Path:
    """
    Save a Concept to the bundle directory.
    
    Args:
        bundle_dir: The root directory of the OKF bundle.
        concept_id: The relative path/identity of the concept (e.g. 'tables/users').
        concept: The Concept model instance.
        
    Returns:
        The absolute path to the written file.
    """
    bundle_path = Path(bundle_dir)
    # Ensure the concept_id doesn't end with .md
    if concept_id.endswith(".md"):
        concept_id = concept_id[:-3]
        
    file_path = bundle_path / f"{concept_id}.md"
    
    # Create parent directories if they don't exist
    file_path.parent.mkdir(parents=True, exist_ok=True)
    
    file_content = concept.to_file_content()
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(file_content)
        
    return file_path

def write_bundle(bundle_dir: Union[Path, str], concepts: Dict[str, Concept]) -> None:
    """
    Write a collection of concepts into a bundle directory.
    
    Args:
        bundle_dir: The root directory of the OKF bundle.
        concepts: A dictionary mapping concept IDs (e.g. 'tables/users') to Concept objects.
    """
    bundle_path = Path(bundle_dir)
    bundle_path.mkdir(parents=True, exist_ok=True)
    
    for concept_id, concept in concepts.items():
        write_concept(bundle_path, concept_id, concept)
