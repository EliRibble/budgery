import calendar
import datetime

def parse(d: str) -> datetime.date:
	"Parse a datetime from an ISO representation."
	return datetime.date.fromisoformat(d)

def this_month_end() -> datetime.date:
	"Get the last day of the current month."
	today = datetime.date.today()
	return today.replace(
		day=calendar.monthrange(
			today.year,
			today.month,
		)[1])

def this_month_start() -> datetime.date:
	"Get the first day of the current month."
	return datetime.date.today().replace(day=1)

