"""Export and import service for conversations."""

import json
from datetime import datetime
from typing import AsyncGenerator


class ExportService:
    """Service for exporting and importing conversations."""

    # Current schema version
    SCHEMA_VERSION = "1.0.0"

    def export_to_markdown(
        self,
        conversation: dict,
        messages: list[dict],
    ) -> str:
        """
        Export conversation to Markdown format.
        """
        lines = [
            f"# {conversation.get('title', 'Untitled Conversation')}",
            "",
            f"**Model:** {conversation.get('model', 'Unknown')}",
            f"**Created:** {conversation.get('created_at', 'Unknown')}",
            f"**Updated:** {conversation.get('updated_at', 'Unknown')}",
            "",
            "---",
            "",
        ]

        for msg in messages:
            role = msg.get("role", "unknown")
            content = msg.get("content", "")
            timestamp = msg.get("created_at", "")

            # Format timestamp
            if timestamp:
                try:
                    dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
                    timestamp_str = dt.strftime("%Y-%m-%d %H:%M:%S")
                except ValueError:
                    timestamp_str = timestamp
            else:
                timestamp_str = ""

            # Add message
            lines.append(f"### {role.capitalize()} ({timestamp_str})")
            lines.append("")
            lines.append(content)
            lines.append("")
            lines.append("---")
            lines.append("")

        return "\n".join(lines)

    def export_to_json(
        self,
        conversation: dict,
        messages: list[dict],
    ) -> str:
        """
        Export conversation to JSON format.
        """
        export_data = {
            "schema_version": self.SCHEMA_VERSION,
            "exported_at": datetime.utcnow().isoformat(),
            "conversation": conversation,
            "messages": messages,
        }
        return json.dumps(export_data, indent=2, ensure_ascii=False)

    async def export_to_pdf_html(
        self,
        conversation: dict,
        messages: list[dict],
    ) -> str:
        """
        Generate HTML for PDF conversion.
        Note: Actual PDF generation would require a library like weasyprint or xhtml2pdf.
        This returns styled HTML that can be converted to PDF.
        """
        html_messages = []
        for msg in messages:
            role = msg.get("role", "unknown")
            content = msg.get("content", "")
            timestamp = msg.get("created_at", "")

            # Simple markdown-to-HTML conversion
            content_html = (
                content.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            )
            # Code blocks
            content_html = self._convert_markdown_to_html(content_html)

            timestamp_str = ""
            if timestamp:
                try:
                    dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
                    timestamp_str = dt.strftime("%Y-%m-%d %H:%M:%S")
                except ValueError:
                    timestamp_str = timestamp

            html_messages.append(
                f"""
                <div class="message {role}">
                    <div class="message-header">
                        <span class="role">{role.capitalize()}</span>
                        <span class="timestamp">{timestamp_str}</span>
                    </div>
                    <div class="message-content">{content_html}</div>
                </div>
                """
            )

        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>{conversation.get("title", "Conversation")}</title>
            <style>
                body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; line-height: 1.6; max-width: 800px; margin: 0 auto; padding: 40px 20px; }}
                h1 {{ border-bottom: 2px solid #333; padding-bottom: 10px; }}
                .metadata {{ color: #666; font-size: 0.9em; margin-bottom: 20px; }}
                .message {{ margin: 20px 0; padding: 15px; border-radius: 8px; }}
                .message.user {{ background: #f0f0f0; }}
                .message.assistant {{ background: #e8f4fd; }}
                .message.system {{ background: #fff3cd; }}
                .message-header {{ display: flex; justify-content: space-between; margin-bottom: 10px; font-size: 0.85em; }}
                .role {{ font-weight: bold; text-transform: uppercase; }}
                .timestamp {{ color: #666; }}
                .message-content {{ white-space: pre-wrap; }}
                pre {{ background: #1e1e1e; color: #d4d4d4; padding: 15px; border-radius: 5px; overflow-x: auto; }}
                code {{ background: #f5f5f5; padding: 2px 5px; border-radius: 3px; }}
            </style>
        </head>
        <body>
            <h1>{conversation.get("title", "Conversation")}</h1>
            <div class="metadata">
                <p><strong>Model:</strong> {conversation.get("model", "Unknown")}</p>
                <p><strong>Created:</strong> {conversation.get("created_at", "Unknown")}</p>
            </div>
            {"".join(html_messages)}
        </body>
        </html>
        """
        return html

    def _convert_markdown_to_html(self, text: str) -> str:
        """Basic markdown to HTML conversion."""
        import re

        # Code blocks
        text = re.sub(
            r"```(\w+)?\n(.*?)```", r"<pre><code>\2</code></pre>", text, flags=re.DOTALL
        )
        # Inline code
        text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
        # Bold
        text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
        # Italic
        text = re.sub(r"\*([^*]+)\*", r"<em>\1</em>", text)
        # Links
        text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', text)
        # Line breaks
        text = text.replace("\n", "<br>")
        return text

    def import_from_json(self, json_str: str) -> dict:
        """
        Import conversation from JSON format.
        Returns the conversation and messages data.
        """
        try:
            data = json.loads(json_str)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON: {e}")

        # Validate schema version
        schema_version = data.get("schema_version", "1.0.0")
        if schema_version != self.SCHEMA_VERSION:
            # Could add migration logic here
            pass

        # Validate required fields
        if "conversation" not in data:
            raise ValueError("Missing 'conversation' field")
        if "messages" not in data:
            raise ValueError("Missing 'messages' field")

        return {
            "conversation": data["conversation"],
            "messages": data["messages"],
        }

    def import_from_markdown(self, markdown_str: str) -> dict:
        """
        Import conversation from Markdown format.
        Basic parsing - more complex markdown would need a proper parser.
        """
        lines = markdown_str.strip().split("\n")

        conversation = {
            "title": "Imported Conversation",
            "model": None,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
        }

        messages = []
        current_role = None
        current_content = []
        current_timestamp = None

        for line in lines:
            line = line.rstrip()

            # Title
            if line.startswith("# "):
                conversation["title"] = line[2:].strip()
                continue

            # Metadata
            if line.startswith("**") and ":" in line:
                continue

            # Separator
            if line == "---":
                if current_role and current_content:
                    messages.append(
                        {
                            "role": current_role,
                            "content": "\n".join(current_content).strip(),
                            "created_at": current_timestamp
                            or datetime.utcnow().isoformat(),
                        }
                    )
                current_role = None
                current_content = []
                current_timestamp = None
                continue

            # Message header
            if line.startswith("### "):
                # Save previous message
                if current_role and current_content:
                    messages.append(
                        {
                            "role": current_role,
                            "content": "\n".join(current_content).strip(),
                            "created_at": current_timestamp
                            or datetime.utcnow().isoformat(),
                        }
                    )

                # Parse new header
                header = line[4:].strip()
                if " (" in header:
                    parts = header.rsplit(" (", 1)
                    current_role = parts[0].lower()
                    current_timestamp = parts[1].rstrip(")") if len(parts) > 1 else None
                else:
                    current_role = header.lower()
                current_content = []
                continue

            # Content
            if current_role:
                current_content.append(line)

        # Don't forget last message
        if current_role and current_content:
            messages.append(
                {
                    "role": current_role,
                    "content": "\n".join(current_content).strip(),
                    "created_at": current_timestamp or datetime.utcnow().isoformat(),
                }
            )

        return {"conversation": conversation, "messages": messages}


# Singleton instance
export_service = ExportService()
