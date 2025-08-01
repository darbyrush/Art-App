from backend.services.fetchers.cleveland import fetch_from_cleveland
from backend.services.fetchers.met import fetch_from_met
from backend.services.fetchers.chicago import fetch_from_chicago  
# from backend.services.fetchers.rijks import fetch_from_rijks
from backend.services.fetchers.harvard import fetch_from_harvard
from backend.services.fetchers.smithsonian import fetch_from_smithsonian

SOURCES = {
    "cleveland": fetch_from_cleveland,
    "met": fetch_from_met,
    "chicago": fetch_from_chicago,
    # "rijks": fetch_from_rijks,
    "harvard": fetch_from_harvard,
    "smithsonian": fetch_from_smithsonian,
}