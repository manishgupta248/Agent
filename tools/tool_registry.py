from tools.drive_tools import upload_file_to_drive
from tools.gmail_tools import fetch_unread_emails, send_email
from tools.calendar_tools import get_upcoming_events, create_calendar_event, delete_calendar_event

from tools.file_tools import (
    read_text_file,
    write_text_file,
    read_csv_summary,
    read_excel_summary,
)

# Maps tool name -> actual Python function
TOOL_FUNCTIONS = {
    "read_text_file": read_text_file,
    "write_text_file": write_text_file,
    "read_csv_summary": read_csv_summary,
    "read_excel_summary": read_excel_summary,
    "fetch_unread_emails": fetch_unread_emails,
    "send_email": send_email,
    "upload_file_to_drive": upload_file_to_drive,
    "get_upcoming_events": get_upcoming_events,
    "create_calendar_event": create_calendar_event,
    "delete_calendar_event": delete_calendar_event,
}

# Description sent to the LLM so it knows what tools exist and how to call them
TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "read_text_file",
            "description": "Read the full contents of a .txt file from the data folder.",
            "parameters": {
                "type": "object",
                "properties": {"filename": {"type": "string"}},
                "required": ["filename"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "write_text_file",
            "description": "Write text content to a .txt file in the data folder.",
            "parameters": {
                "type": "object",
                "properties": {
                    "filename": {"type": "string"},
                    "content": {"type": "string"},
                },
                "required": ["filename", "content"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "read_csv_summary",
            "description": "Read a CSV file and return row/column counts and a preview.",
            "parameters": {
                "type": "object",
                "properties": {"filename": {"type": "string"}},
                "required": ["filename"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "read_excel_summary",
            "description": "Read an Excel file and return row/column counts and a preview.",
            "parameters": {
                "type": "object",
                "properties": {
                    "filename": {"type": "string"},
                    "sheet_name": {"type": "string"},
                },
                "required": ["filename"],
            },
        },
    },
    {
    "type": "function",
    "function": {
        "name": "fetch_unread_emails",
        "description": "Fetch the most recent unread emails from Gmail inbox, including sender, subject, and a short snippet.",
        "parameters": {
            "type": "object",
            "properties": {
                "max_results": {"type": "integer", "description": "Number of emails to fetch (default 5)"}
            },
            "required": [],
        },
    },
},
    {
    "type": "function",
    "function": {
        "name": "upload_file_to_drive",
        "description": "Upload a file from the local data/ folder to Google Drive.",
        "parameters": {
            "type": "object",
            "properties": {
                "filename": {"type": "string"},
                "drive_folder_id": {"type": "string"}
            },
            "required": ["filename"],
        },
    },
},
    {
    "type": "function",
    "function": {
        "name": "send_email",
        "description": "Send an email from your Gmail account.",
        "parameters": {
            "type": "object",
            "properties": {
                "to": {"type": "string", "description": "Recipient email address"},
                "subject": {"type": "string", "description": "Email subject line"},
                "body": {"type": "string", "description": "Plain text email body"}
            },
            "required": ["to", "subject", "body"],
        },
    },
},
    {
    "type": "function",
    "function": {
        "name": "get_upcoming_events",
        "description": "Fetch upcoming events from Google Calendar.",
        "parameters": {
            "type": "object",
            "properties": {
                "days_ahead": {"type": "integer", "description": "Number of days ahead to look for events (default 7)"},
                "max_results": {"type": "integer", "description": "Maximum number of events to fetch (default 10)"}
            },
            "required": [],
        },
    },
},
    {
    "type": "function",
    "function": {
        "name": "create_calendar_event",
        "description": "Create a new event in Google Calendar.",
        "parameters": {
            "type": "object",
            "properties": {
                "title": {"type": "string", "description": "Title of the event"},
                "start_datetime": {"type": "string", "description": "Start date and time in ISO 8601 format"},
                "end_datetime": {"type": "string", "description": "End date and time in ISO 8601 format"},
                "description": {"type": "string", "description": "(Optional) Description or notes for the event"},
                "location": {"type": "string", "description": "(Optional) Location of the event"}
            },
            "required": ["title", "start_datetime", "end_datetime"],
        },
    },
},
    {
    "type": "function",
    "function": {
        "name": "delete_calendar_event",
        "description": "Delete an event from Google Calendar.",
        "parameters": {
            "type": "object",
            "properties": {
                "event_id": {"type": "string", "description": "The ID of the event to delete"}
            },
            "required": ["event_id"],
        },
    },
}, 

]