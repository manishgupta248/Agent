from datetime import datetime, timedelta, timezone
from googleapiclient.discovery import build

from config.google.auth import get_google_credentials


def _get_calendar_service():
    creds = get_google_credentials()
    return build("calendar", "v3", credentials=creds)


def get_upcoming_events(days_ahead: int = 7, max_results: int = 10) -> str:
    """
    Fetches upcoming calendar events for the next N days.
    """
    service = _get_calendar_service()

    now = datetime.now(timezone.utc)
    end = now + timedelta(days=days_ahead)

    events_result = (
        service.events()
        .list(
            calendarId="primary",
            timeMin=now.isoformat(),
            timeMax=end.isoformat(),
            maxResults=max_results,
            singleEvents=True,
            orderBy="startTime",
        )
        .execute()
    )
    events = events_result.get("items", [])

    if not events:
        return f"No upcoming events in the next {days_ahead} days."

    summaries = []
    for event in events:
        start = event["start"].get("dateTime", event["start"].get("date", "Unknown"))
        title = event.get("summary", "(no title)")
        location = event.get("location", "")
        description = event.get("description", "")

        line = f"- {title} | Start: {start}"
        if location:
            line += f" | Location: {location}"
        if description:
            line += f" | Notes: {description[:100]}"
        summaries.append(line)

    return f"Upcoming events ({len(summaries)} found):\n" + "\n".join(summaries)


def create_calendar_event(
    title: str,
    start_datetime: str,
    end_datetime: str,
    description: str = "",
    location: str = "",
) -> str:
    """
    Creates a new event in Google Calendar.
    start_datetime and end_datetime must be ISO 8601 format:
    e.g. '2026-07-02T10:00:00+05:30' for IST
    """
    service = _get_calendar_service()

    event_body = {
        "summary": title,
        "start": {"dateTime": start_datetime, "timeZone": "Asia/Kolkata"},
        "end": {"dateTime": end_datetime, "timeZone": "Asia/Kolkata"},
    }
    if description:
        event_body["description"] = description
    if location:
        event_body["location"] = location

    created = (
        service.events()
        .insert(calendarId="primary", body=event_body)
        .execute()
    )

    return (
        f"Event created: '{created.get('summary')}' "
        f"on {created['start'].get('dateTime')}. "
        f"Link: {created.get('htmlLink', 'N/A')}"
    )


def delete_calendar_event(event_title: str) -> str:
    """
    Deletes the next upcoming event matching the given title.
    Searches within the next 30 days.
    """
    service = _get_calendar_service()

    now = datetime.now(timezone.utc)
    end = now + timedelta(days=30)

    events_result = (
        service.events()
        .list(
            calendarId="primary",
            timeMin=now.isoformat(),
            timeMax=end.isoformat(),
            maxResults=20,
            singleEvents=True,
            orderBy="startTime",
            q=event_title,
        )
        .execute()
    )
    events = events_result.get("items", [])

    if not events:
        return f"No upcoming event found matching '{event_title}'."

    event = events[0]
    service.events().delete(calendarId="primary", eventId=event["id"]).execute()

    return f"Deleted event: '{event.get('summary')}' scheduled at {event['start'].get('dateTime', event['start'].get('date'))}."