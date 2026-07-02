from datetime import datetime
from typing import List, Optional, Dict, Any
import yaml
from pydantic import BaseModel, ConfigDict, Field

class Concept(BaseModel):
    model_config = ConfigDict(extra='allow')

    type: str
    title: Optional[str] = None
    description: Optional[str] = None
    resource: Optional[str] = None
    tags: Optional[List[str]] = Field(default_factory=list)
    timestamp: Optional[datetime] = None
    body: str = ""

    def get_frontmatter(self) -> Dict[str, Any]:
        """Return a dictionary of the frontmatter fields (excluding body)."""
        data = self.model_dump(exclude={"body"}, exclude_none=True)
        # Add any extra attributes dynamically added to the model
        if self.model_extra:
            data.update(self.model_extra)
        return data

    def to_file_content(self) -> str:
        """Serialize the concept into the standard OKF file format (YAML frontmatter + Markdown body)."""
        frontmatter = self.get_frontmatter()
        
        # Serialize timestamp in ISO format
        if isinstance(frontmatter.get("timestamp"), datetime):
            frontmatter["timestamp"] = frontmatter["timestamp"].isoformat()
            
        yaml_str = yaml.safe_dump(frontmatter, sort_keys=False, allow_unicode=True)
        return f"---\n{yaml_str}---\n\n{self.body}"

    @classmethod
    def from_file_content(cls, content: str) -> "Concept":
        """Parse a standard OKF markdown file with YAML frontmatter into a Concept instance."""
        content = content.strip()
        if not content.startswith("---"):
            raise ValueError("Invalid OKF file format: must start with '---' frontmatter delimiter")
            
        parts = content.split("---", 2)
        if len(parts) < 3:
            raise ValueError("Invalid OKF file format: missing closing '---' frontmatter delimiter")
            
        yaml_content = parts[1]
        body = parts[2].lstrip()
        
        frontmatter = yaml.safe_load(yaml_content) or {}
        if "type" not in frontmatter:
            raise ValueError("Invalid OKF file format: 'type' is a required field in frontmatter")
            
        return cls(**frontmatter, body=body)
