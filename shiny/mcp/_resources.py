from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

SKILLS_DOCS_DIR = (
    Path(__file__).parent.parent
    / ".agents"
    / "skills"
    / "shiny-for-python"
    / "references"
)


def list_mcp_resources() -> List[Dict[str, Any]]:
    resources: List[Dict[str, Any]] = [
        {
            "uri": "shiny://components/catalog",
            "name": "Shiny Component Catalog",
            "description": "Comprehensive index of Shiny for Python UI components, layouts, and renderers.",
            "mimeType": "application/json",
        },
        {
            "uri": "shiny://templates/list",
            "name": "Shiny Application Templates",
            "description": "Catalog of application templates available in Shiny for Python.",
            "mimeType": "application/json",
        },
    ]

    if SKILLS_DOCS_DIR.is_dir():
        for doc_path in sorted(SKILLS_DOCS_DIR.glob("*.md")):
            topic = doc_path.stem
            title = topic.replace("-", " ").title()
            resources.append(
                {
                    "uri": f"shiny://docs/{topic}",
                    "name": f"Shiny Guide: {title}",
                    "description": f"Official reference guide for {title} in Shiny for Python.",
                    "mimeType": "text/markdown",
                }
            )

    return resources


def read_mcp_resource(uri: str) -> Optional[Dict[str, Any]]:
    if uri == "shiny://components/catalog":
        from .._components import COMPONENT_CATALOG

        return {
            "uri": uri,
            "mimeType": "application/json",
            "text": json.dumps(COMPONENT_CATALOG, indent=2),
        }

    if uri == "shiny://templates/list":
        from .._components import TEMPLATE_CATALOG

        return {
            "uri": uri,
            "mimeType": "application/json",
            "text": json.dumps(TEMPLATE_CATALOG, indent=2),
        }

    if uri.startswith("shiny://docs/"):
        topic = uri.removeprefix("shiny://docs/")
        doc_file = SKILLS_DOCS_DIR / f"{topic}.md"
        if doc_file.is_file():
            return {
                "uri": uri,
                "mimeType": "text/markdown",
                "text": doc_file.read_text(encoding="utf-8"),
            }

    return None
