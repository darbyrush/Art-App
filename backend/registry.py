from backend.services.fetchers.cleveland import fetch_from_cleveland
from backend.services.fetchers.met import fetch_from_met
from backend.services.fetchers.chicago import fetch_from_chicago  # Art Institute of Chicago

SOURCES = {
    "cleveland": fetch_from_cleveland,
    "met": fetch_from_met,
    "chicago": fetch_from_chicago  
}