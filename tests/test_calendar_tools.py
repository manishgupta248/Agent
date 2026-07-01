from tools.calendar_tools import get_upcoming_events, create_calendar_event, delete_calendar_event

def test_calendar():
    print("=== Upcoming Events ===")
    print(get_upcoming_events(days_ahead=7))

    print("\n=== Creating Event ===")
    print(create_calendar_event(
        title="Agent Test Meeting",
        start_datetime="2026-07-03T10:00:00+05:30",
        end_datetime="2026-07-03T10:30:00+05:30",
        description="Created by AI agent",
        location="Delhi"
    ))

    print("\n=== Deleting Event ===")
    print(delete_calendar_event("Agent Test Meeting"))

if __name__ == "__main__":
    test_calendar()