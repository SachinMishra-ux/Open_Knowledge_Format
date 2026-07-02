import os
from pathlib import Path
from typing import Dict, Union, List
from datetime import datetime
import logging
from google_okf.core.models import Concept
from google_okf.producers.base import BaseProducer

# Import handlers conditionally/safely
try:
    from pypdf import PdfReader
except ImportError:
    PdfReader = None

try:
    import docx
except ImportError:
    docx = None

logger = logging.getLogger(__name__)

class DocumentProducer(BaseProducer):
    """
    Producer that imports flat files (PDF, DOCX, MD, TXT) from a directory 
    and converts them into standard OKF Concepts.
    """
    
    def __init__(
        self, 
        source_dir: Union[Path, str], 
        output_prefix: str = "documents",
        tags: List[str] = None
    ):
        """
        Args:
            source_dir: The directory containing the source documents.
            output_prefix: Subfolder path prefix for concept IDs (e.g. 'documents/playbooks/deploy').
            tags: Global tags to apply to all imported documents.
        """
        self.source_dir = Path(source_dir)
        self.output_prefix = output_prefix
        self.tags = tags or []

    def produce(self) -> Dict[str, Concept]:
        concepts = {}
        if not self.source_dir.exists() or not self.source_dir.is_dir():
            logger.warning(f"Source directory '{self.source_dir}' does not exist or is not a directory.")
            return concepts

        for root, _, files in os.walk(self.source_dir):
            for file in files:
                file_path = Path(root) / file
                ext = file_path.suffix.lower()
                
                if ext not in {".pdf", ".docx", ".md", ".txt"}:
                    continue
                    
                rel_path = file_path.relative_to(self.source_dir)
                # Compute Concept ID: prefix / rel_path_without_extension
                concept_subpath = rel_path.with_suffix("")
                concept_id = f"{self.output_prefix}/{concept_subpath}" if self.output_prefix else str(concept_subpath)
                
                # Replace backslashes on Windows for canonical Concept IDs
                concept_id = concept_id.replace("\\", "/")
                
                try:
                    text_content = self._extract_text(file_path, ext)
                    
                    # Generate a clean description
                    snippet = text_content[:150].strip().replace("\n", " ")
                    description = f"{snippet}..." if len(text_content) > 150 else snippet
                    if not description:
                        description = f"Imported {ext[1:].upper()} file"
                        
                    # File mod timestamp
                    mod_time = datetime.fromtimestamp(file_path.stat().st_mtime)
                    
                    # File URI resource identity
                    resource_uri = file_path.resolve().as_uri()
                    
                    # File-specific tags
                    file_tags = self.tags.copy()
                    file_tags.append(ext[1:])  # add 'pdf', 'docx', etc.
                    
                    concept = Concept(
                        type="Document",
                        title=file_path.stem.replace("_", " ").replace("-", " ").title(),
                        description=description,
                        resource=resource_uri,
                        tags=file_tags,
                        timestamp=mod_time,
                        body=text_content
                    )
                    concepts[concept_id] = concept
                    logger.info(f"Processed document: {rel_path} -> {concept_id}")
                except Exception as e:
                    logger.error(f"Failed to process document {file_path}: {e}")
                    
        return concepts

    def _extract_text(self, path: Path, ext: str) -> str:
        if ext == ".pdf":
            return self._extract_pdf(path)
        elif ext == ".docx":
            return self._extract_docx(path)
        elif ext in {".md", ".txt"}:
            return self._extract_txt_md(path)
        return ""

    def _extract_pdf(self, path: Path) -> str:
        if PdfReader is None:
            raise ImportError("pypdf is required to parse PDF files. Install it via pip/uv.")
        
        reader = PdfReader(path)
        pages_text = []
        for i, page in enumerate(reader.pages):
            text = page.extract_text()
            if text:
                pages_text.append(text)
        return "\n\n".join(pages_text)

    def _extract_docx(self, path: Path) -> str:
        if docx is None:
            raise ImportError("python-docx is required to parse DOCX files. Install it via pip/uv.")
            
        doc = docx.Document(path)
        paragraphs_text = [p.text for p in doc.paragraphs if p.text]
        return "\n".join(paragraphs_text)

    def _extract_txt_md(self, path: Path) -> str:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
            
        # If it is a markdown file with existing frontmatter, strip it to only load the body,
        # or load the frontmatter and override. For simplicity, we extract the raw text,
        # or strip frontmatter if it starts with '---'.
        content_stripped = content.strip()
        if path.suffix.lower() == ".md" and content_stripped.startswith("---"):
            try:
                # split by '---' to extract body
                parts = content_stripped.split("---", 2)
                if len(parts) >= 3:
                    return parts[2].lstrip()
            except Exception:
                pass
                
        return content
