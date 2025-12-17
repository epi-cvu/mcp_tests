import datetime
import os.path
import re
import json

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]

def clean_summary(summary):
    """Supprime les tags du type [XXX] - au début du summary"""
    return re.sub(r"^\[.*?\]\s*-\s*", "", summary).strip()

def merge_intervals(intervals):
    """Fusionne les intervalles qui se chevauchent et retourne la durée totale en heures"""
    if not intervals:
        return 0.0
    # Trier par début
    intervals.sort(key=lambda x: x[0])
    merged = [intervals[0]]
    for start, end in intervals[1:]:
        last_start, last_end = merged[-1]
        if start <= last_end:
            merged[-1][1] = max(last_end, end)
        else:
            merged.append([start, end])
    # Somme des durées
    total = sum((end - start).total_seconds() / 3600 for start, end in merged)
    return total

def add_tna(day, total):
    whole_eight = ["Monday", "Tuesday", "Thursday"]
    if day in whole_eight:
        return f"{str(8 - total)}/8"
    else:
        return f"{str(7.5 - total)}/7.5"

def retrieve_data(output=None):
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    try:
        service = build("calendar", "v3", credentials=creds)

        now = datetime.datetime.now(tz=datetime.timezone.utc)
        this_week_monday = now - datetime.timedelta(days=now.isoweekday() - 1)
        last_monday = this_week_monday - datetime.timedelta(days=7)
        last_friday = last_monday + datetime.timedelta(days=4, hours=23, minutes=59, seconds=59)

        timeMin = last_monday.replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
        timeMax = last_friday.isoformat()

        events_result = service.events().list(
            calendarId="primary",
            timeMin=timeMin,
            timeMax=timeMax,
            singleEvents=True,
            orderBy="startTime",
        ).execute()

        events = events_result.get("items", [])
        if not events:
            print("No events found.")
            return

        week_hours = {}

        intervals_per_day = {}

        for event in events:
            event_type = event.get("eventType", "")
            if event_type in ["workingLocation", "outOfOffice"]:
                continue

            start_str = event["start"].get("dateTime", event["start"].get("date"))
            end_str = event["end"].get("dateTime", event["end"].get("date"))
            start_dt = datetime.datetime.fromisoformat(start_str)
            end_dt = datetime.datetime.fromisoformat(end_str)
            day_key = start_dt.strftime("%Y-%m-%d")
            day_name = start_dt.strftime("%A")
            summary = event.get("summary", "Sans titre")

            if day_key not in week_hours:
                week_hours[day_key] = {
                    "day_name": day_name,
                    "events": {},
                    "total_day_hours": 0.0
                }
                intervals_per_day[day_key] = []

            delta_hours = (end_dt - start_dt).total_seconds() / 3600
            week_hours[day_key]["events"][summary] = week_hours[day_key]["events"].get(summary, 0.0) + delta_hours

            intervals_per_day[day_key].append([start_dt, end_dt])

        for day_key, intervals in intervals_per_day.items():
            week_hours[day_key]["total_day_hours"] = merge_intervals(intervals)
            week_hours[day_key]["TNA"] = add_tna(week_hours[day_key]["day_name"], week_hours[day_key]["total_day_hours"])
    
        if output == None:
            print(json.dumps(week_hours, indent=4, ensure_ascii=False))
            return json.dumps(week_hours, indent=4, ensure_ascii=False)
        else:
            if os.path.isdir(output):
                output_path = os.path.join(output, "output.json")
            else:
                output_path = output
            print(json.dumps(week_hours, indent=4, ensure_ascii=False))
            print(f"Fichier enregistré sous : {output_path}.")
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(week_hours, f, indent=4, ensure_ascii=False)
                
    except HttpError as error:
        print(f"An error occurred: {error}")
        
    
def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Récupère les informations et simplifie Google Calendar pour la saisie dans Fitnet.")
    parser.add_argument('--output', '-o', required=False, help="Chemin ou enregistrer le output.json")

    args = parser.parse_args()
    
    retrieve_data(args.output)
    
if __name__ == "__main__":
    main()
