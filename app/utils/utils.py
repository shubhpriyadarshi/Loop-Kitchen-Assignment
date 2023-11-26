from datetime import datetime, timedelta
import pandas as pd
from app.models.business_hours.models import BusinessHours
from app.models.timezones.models import Timezones
from app.models.store_status.models import StoreStatus
from app.utils.time import utc_to_local

# Define a function to check if a store is within business hours
def is_within_hours(timestamp, store_id):
    # Get the day of week and time of the store
    day_of_week = timestamp.weekday()
    time = timestamp.time()
    # Get the start and end time of the store for that day
    hours = BusinessHours.query.filter_by(
        store_id=store_id, day=day_of_week).first()
    if hours is None:
        # Assume the store is open 24*7 if data is missing
        return True
    else:
        start_time = hours.start_time_local
        end_time = hours.end_time_local
        # Check if the time is within the start and end time
        return start_time <= time <= end_time


# Define a function to generate the report
def generate_report():
    store_status = StoreStatus.query.order_by(
        StoreStatus.timestamp_utc.desc()
    ).first()
    if store_status:
        # Get the current timestamp
        current_timestamp = datetime.now()
        # Define the time intervals for the report
        last_hour = current_timestamp - timedelta(hours=1)
        last_day = current_timestamp - timedelta(days=1)
        last_week = current_timestamp - timedelta(weeks=1)
        # Create an empty dataframe for the report

        report = pd.DataFrame(columns=[
            "store_id", "uptime_last_hour", "uptime_last_day",
            "uptime_last_week", "downtime_last_hour", "downtime_last_day", "downtime_last_week"
        ])

        # Loop through the unique store ids
        for row in StoreStatus.query.with_entities(StoreStatus.store_id).distinct():
            store_id = row.store_id
            # Calculate the uptime and downtime for each time interval
            uptime_last_hour, downtime_last_hour = calculate_uptime_downtime(
                store_id, last_hour, current_timestamp)
            uptime_last_day, downtime_last_day = calculate_uptime_downtime(
                store_id, last_day, current_timestamp)
            uptime_last_week, downtime_last_week = calculate_uptime_downtime(
                store_id, last_week, current_timestamp)
            # Append the row to the report dataframe
            new_row = pd.DataFrame([
                {
                    "store_id": store_id,
                    "uptime_last_hour": uptime_last_hour,
                    "uptime_last_day": uptime_last_day,
                    "uptime_last_week": uptime_last_week,
                    "downtime_last_hour": downtime_last_hour,
                    "downtime_last_day": downtime_last_day,
                    "downtime_last_week": downtime_last_week
                }
            ])
            if report.empty:
                report = new_row
            else:
                report = pd.concat([report, new_row], ignore_index=True)
        return report
    else:
        print("No StoreStatus record found.")


# Define a function to calculate the uptime and downtime for a store
def calculate_uptime_downtime(store_id, start_date, end_date):
    # Get the timezone of the store
    timezone = Timezones.query.filter_by(
        store_id=store_id).first().timezone_str
    # Convert the start and end date to local timezone
    start_date_local = utc_to_local(start_date, timezone)
    end_date_local = utc_to_local(end_date, timezone)
    # Get the status of the store within the date range
    status = StoreStatus.query.filter(StoreStatus.store_id == store_id, StoreStatus.timestamp_utc >=
                                      start_date, StoreStatus.timestamp_utc <= end_date).order_by(StoreStatus.timestamp_utc).all()
    # Initialize the uptime and downtime to zero
    uptime = 0
    downtime = 0
    # Initialize an empty list to store the business_hour_slots of status within each business hour
    business_hour_slots = []
    # Loop through the days between the start and end date
    for day in range((end_date_local - start_date_local).days + 1):
        # Get the date for the current day
        date = start_date_local + timedelta(days=day)
        # Get the business hours for the store for that day
        hours = BusinessHours.query.filter_by(
            store_id=store_id, day=date.weekday()).all()
        # Loop through the business hours
        for hour in hours:
            # Get the start and end time of the business hour
            start_time = hour.start_time_local
            end_time = hour.end_time_local
            # Get the start and end datetime for the business hour
            start_datetime = datetime.combine(date, start_time)
            end_datetime = datetime.combine(date, end_time)
            # Get the status of the store within the business hour
            slot = [row for row in status if start_datetime.timestamp() <=
                    utc_to_local(row.timestamp_utc, timezone).timestamp() <= end_datetime.timestamp()]
            # Append the slot to the list if it is not empty
            if slot:
                business_hour_slots.append(slot)
    # Loop through the business_hour_slots
    for slot in business_hour_slots:
        # Get the first and last observations
        first_obs = slot[0]
        last_obs = slot[-1]
        # Convert the timestamps to local timezone
        first_timestamp = utc_to_local(first_obs.timestamp_utc, timezone)
        last_timestamp = utc_to_local(last_obs.timestamp_utc, timezone)
        # Apply the interpolation logic based on the first and last status
        if len(slot) <= 2:
            if first_obs.status == last_obs.status:
                # If the first and last observations are both active, assume the store was active for the entire interval
                if first_obs.status == "active":
                    uptime += (last_timestamp -
                               first_timestamp).total_seconds()
                # If the first and last observations are both inactive, assume the store was inactive for the entire interval
                else:
                    downtime += (last_timestamp -
                                 first_timestamp).total_seconds()
            else:
                # If the first observation is active and the last observation is inactive, assume the store became inactive at the midpoint of the interval
                if first_obs.status == "active":
                    midpoint = first_timestamp + \
                        (last_timestamp - first_timestamp) / 2
                    uptime += (midpoint - first_timestamp).total_seconds()
                    downtime += (last_timestamp - midpoint).total_seconds()
                # If the first observation is inactive and the last observation is active, assume the store became active at the midpoint of the interval
                else:
                    midpoint = first_timestamp + \
                        (last_timestamp - first_timestamp) / 2
                    downtime += (midpoint - first_timestamp).total_seconds()
                    uptime += (last_timestamp - midpoint).total_seconds()
        # If there are more than two observations, use the timestamps of the observations to calculate the uptime and downtime
        if len(slot) > 2:
            # Loop through the slot
            for i, row in enumerate(slot):
                # Convert the timestamp to local timezone
                timestamp = utc_to_local(row.timestamp_utc, timezone)
                # Get the next timestamp or the end of the slot
                if i < len(slot) - 1:
                    next_timestamp = utc_to_local(
                        slot[i+1].timestamp_utc, timezone)
                else:
                    next_timestamp = last_timestamp
                # Calculate the duration between the timestamps
                duration = (next_timestamp - timestamp).total_seconds()
                # Add the duration to the uptime or downtime based on the status
                if row.status == "active":
                    uptime += duration
                else:
                    downtime += duration
    # Return the uptime and downtime in hours
    return uptime / 3600, downtime / 3600
