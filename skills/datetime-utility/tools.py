from datetime import datetime, timedelta, timezone

from langchain_core.tools import tool


@tool
def get_current_time(timezone_name: str = "UTC") -> dict:
    """Returns the current date and time in UTC.

    Args:
        timezone_name: Timezone identifier (currently supports 'UTC').
    """
    now = datetime.now(timezone.utc)
    return {
        "current_iso": now.isoformat(),
        "date": now.strftime("%Y-%m-%d"),
        "time": now.strftime("%H:%M:%S"),
        "day_of_week": now.strftime("%A"),
        "timezone": "UTC",
        "status": "success",
    }


@tool
def calculate_date_difference(date_start: str, date_end: str) -> dict:
    """Calculates the difference between two dates in days, hours, and seconds.

    Args:
        date_start: Start date in 'YYYY-MM-DD' or 'YYYY-MM-DD HH:MM:SS' format.
        date_end: End date in 'YYYY-MM-DD' or 'YYYY-MM-DD HH:MM:SS' format.
    """
    formats = ["%Y-%m-%d", "%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S"]

    def parse_dt(val: str) -> datetime:
        for fmt in formats:
            try:
                return datetime.strptime(val.strip(), fmt)
            except ValueError:
                pass
        raise ValueError(f"Unable to parse date '{val}'. Supported formats: YYYY-MM-DD, ISO.")

    try:
        dt1 = parse_dt(date_start)
        dt2 = parse_dt(date_end)
        delta = dt2 - dt1
        total_seconds = delta.total_seconds()
        days = delta.days
        hours = round(total_seconds / 3600, 2)

        return {
            "date_start": date_start,
            "date_end": date_end,
            "days_difference": days,
            "total_hours": hours,
            "total_seconds": int(total_seconds),
            "is_future": total_seconds > 0,
            "status": "success",
        }
    except Exception as e:
        return {"error": str(e), "status": "error"}


@tool
def offset_date(base_date: str, days: int = 0, hours: int = 0, minutes: int = 0) -> dict:
    """Calculates a future or past date by adding or subtracting an offset from a base date.

    Args:
        base_date: Base date string (e.g. '2026-09-05' or 'now').
        days: Number of days to add (use negative to subtract).
        hours: Number of hours to add.
        minutes: Number of minutes to add.
    """
    formats = ["%Y-%m-%d", "%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S"]

    def parse_dt(val: str) -> datetime:
        if val.lower() == "now":
            return datetime.now(timezone.utc).replace(tzinfo=None)
        for fmt in formats:
            try:
                return datetime.strptime(val.strip(), fmt)
            except ValueError:
                pass
        raise ValueError(f"Unable to parse date '{val}'.")

    try:
        base_dt = parse_dt(base_date)
        delta = timedelta(days=days, hours=hours, minutes=minutes)
        result_dt = base_dt + delta

        return {
            "base_date": base_date,
            "offset_applied": {"days": days, "hours": hours, "minutes": minutes},
            "result_date": result_dt.strftime("%Y-%m-%d"),
            "result_iso": result_dt.isoformat(),
            "day_of_week": result_dt.strftime("%A"),
            "status": "success",
        }
    except Exception as e:
        return {"error": str(e), "status": "error"}


SKILL_TOOLS = [get_current_time, calculate_date_difference, offset_date]
