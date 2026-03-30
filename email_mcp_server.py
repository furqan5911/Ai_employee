#!/usr/bin/env python3
"""
Email MCP Server — Simple SMTP email sending for AI Employee.

This MCP server enables AI agents to send emails via SMTP.
Supports Gmail, Outlook, and any SMTP provider.

Environment Variables (optional, will prompt if not set):
    SMTP_SERVER: SMTP server hostname (e.g., smtp.gmail.com)
    SMTP_PORT: SMTP port (default: 587 for TLS)
    SMTP_USER: SMTP username/email
    SMTP_PASSWORD: SMTP password or app password
    EMAIL_FROM: Default from address

Usage:
    # Direct
    python email_mcp_server.py

    # Via MCP client (Claude Desktop settings.json)
    {
      "mcpServers": {
        "email": {
          "command": "python",
          "args": ["/path/to/email_mcp_server.py"]
        }
      }
    }
"""

import os
import smtplib
import asyncio
from email.message import EmailMessage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from typing import Any
from mcp.server import Server
from mcp.types import Tool, TextContent
from pydantic import BaseModel, Field

# ─── Configuration ─────────────────────────────────────────────────────────────

SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
EMAIL_FROM = os.getenv("EMAIL_FROM", "")

# ─── MCP Server Setup ───────────────────────────────────────────────────────────

server = Server("email-server")

# ─── Tool Schemas ────────────────────────────────────────────────────────────────


class SendEmailParams(BaseModel):
    """Parameters for sending an email."""
    to: str = Field(..., description="Recipient email address")
    subject: str = Field(..., description="Email subject")
    body: str = Field(..., description="Email body (plain text)")
    html_body: str = Field("", description="Email body (HTML, optional)")
    from_addr: str = Field("", description="From email address (optional, uses default if not specified)")


class SendEmailWithAttachmentParams(BaseModel):
    """Parameters for sending an email with attachments."""
    to: str = Field(..., description="Recipient email address")
    subject: str = Field(..., description="Email subject")
    body: str = Field(..., description="Email body (plain text)")
    html_body: str = Field("", description="Email body (HTML, optional)")
    attachments: list[str] = Field(default_factory=list, description="List of file paths to attach")
    from_addr: str = Field("", description="From email address (optional, uses default if not specified)")


# ─── Email Functions ─────────────────────────────────────────────────────────────

def create_email(
    to: str,
    subject: str,
    body: str,
    html_body: str = "",
    from_addr: str = "",
    attachments: list[str] | None = None
) -> EmailMessage | MIMEMultipart:
    """Create an email message object."""

    # Use multipart if we have attachments or HTML
    if attachments or html_body:
        msg = MIMEMultipart()
        msg.attach(MIMEText(body, "plain"))
        if html_body:
            msg.attach(MIMEText(html_body, "html"))
    else:
        msg = EmailMessage()
        msg.set_content(body)

    msg["Subject"] = subject
    msg["To"] = to
    msg["From"] = from_addr or EMAIL_FROM or SMTP_USER

    # Add attachments
    if attachments:
        for file_path in attachments:
            try:
                with open(file_path, "rb") as f:
                    part = MIMEBase("application", "octet-stream")
                    part.set_payload(f.read())
                    encoders.encode_base64(part)

                filename = os.path.basename(file_path)
                part.add_header(
                    "Content-Disposition",
                    f"attachment; filename= {filename}"
                )
                msg.attach(part)
            except Exception as e:
                print(f"[WARNING] Could not attach {file_path}: {e}")

    return msg


async def send_email(
    to: str,
    subject: str,
    body: str,
    html_body: str = "",
    from_addr: str = "",
    attachments: list[str] | None = None
) -> dict[str, Any]:
    """Send an email via SMTP."""

    # Check if credentials are configured
    if not SMTP_USER or not SMTP_PASSWORD:
        return {
            "success": False,
            "error": "SMTP credentials not configured. Please set SMTP_USER and SMTP_PASSWORD environment variables.",
            "configuration_hint": "For Gmail, use an App Password: https://support.google.com/accounts/answer/185833"
        }

    try:
        # Create the message
        msg = create_email(to, subject, body, html_body, from_addr, attachments)

        # Connect to SMTP server and send
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.send_message(msg)

        return {
            "success": True,
            "message": f"Email sent successfully to {to}",
            "to": to,
            "subject": subject,
            "attachments": len(attachments) if attachments else 0
        }

    except smtplib.SMTPAuthenticationError as e:
        return {
            "success": False,
            "error": f"Authentication failed: {str(e)}",
            "hint": "For Gmail, make sure you're using an App Password, not your regular password"
        }

    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to send email: {str(e)}"
        }


# ─── MCP Tools ─────────────────────────────────────────────────────────────────

@server.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools."""
    return [
        Tool(
            name="send_email",
            description="Send a plain text email",
            inputSchema=SendEmailParams.model_json_schema()
        ),
        Tool(
            name="send_email_with_attachments",
            description="Send an email with file attachments",
            inputSchema=SendEmailWithAttachmentParams.model_json_schema()
        ),
        Tool(
            name="check_email_config",
            description="Check if email is configured and ready to send",
            inputSchema={}
        )
    ]


@server.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Handle tool calls."""

    if name == "send_email":
        params = SendEmailParams(**arguments)
        result = await send_email(
            to=params.to,
            subject=params.subject,
            body=params.body,
            html_body=params.html_body,
            from_addr=params.from_addr
        )
        return [TextContent(type="text", text=str(result))]

    elif name == "send_email_with_attachments":
        params = SendEmailWithAttachmentParams(**arguments)
        result = await send_email(
            to=params.to,
            subject=params.subject,
            body=params.body,
            html_body=params.html_body,
            from_addr=params.from_addr,
            attachments=params.attachments
        )
        return [TextContent(type="text", text=str(result))]

    elif name == "check_email_config":
        config_status = {
            "configured": bool(SMTP_USER and SMTP_PASSWORD),
            "smtp_server": SMTP_SERVER,
            "smtp_port": SMTP_PORT,
            "email_from": EMAIL_FROM or SMTP_USER or "Not set",
            "has_user": bool(SMTP_USER),
            "has_password": bool(SMTP_PASSWORD),
            "setup_instructions": {
                "gmail": "1. Go to Google Account settings > Security > 2-Step Verification\n2. Generate an App Password\n3. Set SMTP_USER to your Gmail address\n4. Set SMTP_PASSWORD to the App Password (16 characters)",
                "outlook": "Set SMTP_USER to your Outlook email, SMTP_PASSWORD to your password",
                "other": "Set SMTP_SERVER, SMTP_PORT, SMTP_USER, and SMTP_PASSWORD for your provider"
            }
        }
        return [TextContent(type="text", text=str(config_status))]

    else:
        return [TextContent(type="text", text=f"Unknown tool: {name}")]


# ─── Main Entry Point ───────────────────────────────────────────────────────────

async def main():
    """Run the MCP server."""
    from mcp.server.stdio import stdio_server

    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
