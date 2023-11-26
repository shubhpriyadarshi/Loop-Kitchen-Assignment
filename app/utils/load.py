import pandas as pd
from datetime import datetime
from app.database import db
from sqlalchemy.dialects.postgresql import insert
from app import create_app
from app.models.timezones.models import Timezones
from app.models.store_status.models import StoreStatus
from app.models.business_hours.models import BusinessHours


def load_data():
    app = create_app()

    with app.app_context():
        db.create_all()
        timezones_df = pd.read_csv(
            'data/bq-results-20230125-202210-1674678181880.csv')
        store_status_df = pd.read_csv('data/store status.csv')
        business_hours_df = pd.read_csv('data/Menu hours.csv')

        # Get a list of all unique store_ids
        all_store_ids = pd.concat(
            [timezones_df['store_id'], store_status_df['store_id'], business_hours_df['store_id']]).dropna().unique().tolist()

        for store_id in all_store_ids:
            # Check if the store_id exists in the timezones_df
            if store_id not in timezones_df['store_id'].values:
                # If not, assume the timezone is 'America/Chicago'
                stmt = insert(Timezones).values(
                    store_id=int(store_id), timezone_str='America/Chicago').on_conflict_do_nothing(index_elements=['store_id'])
                db.session.execute(stmt)

            # Check if the store_id exists in the business_hours_df
            if store_id not in business_hours_df['store_id'].values:
                # If not, assume the store is open 24*7
                start_time_local = datetime.strptime(
                    '00:00:00', '%H:%M:%S').time()
                end_time_local = datetime.strptime(
                    '23:59:59', '%H:%M:%S').time()
                for day in ['0', '2', '3', '4', '5', '6', '7']:
                    stmt = insert(BusinessHours).values(store_id=store_id, day=day, start_time_local=start_time_local,
                                                        end_time_local=end_time_local).on_conflict_do_nothing(index_elements=['store_id', 'day', 'start_time_local'])
                    db.session.execute(stmt)

            db.session.commit()

        for _, row in timezones_df.iterrows():
            stmt = insert(Timezones).values(
                store_id=row['store_id'], timezone_str=row['timezone_str']).on_conflict_do_nothing(index_elements=['store_id'])
            db.session.execute(stmt)
        db.session.commit()

        store_status_df = store_status_df.dropna(subset=['timestamp_utc'])
        store_status_df.drop_duplicates(
            subset=['store_id', 'timestamp_utc'], inplace=True)
        for _, row in store_status_df.iterrows():
            try:
                timestamp_utc = datetime.strptime(
                    row['timestamp_utc'], "%Y-%m-%d %H:%M:%S.%f %Z")
            except ValueError:
                timestamp_utc = datetime.strptime(
                    row['timestamp_utc'], "%Y-%m-%d %H:%M:%S %Z")
            stmt = insert(StoreStatus).values(
                store_id=row['store_id'], timestamp_utc=timestamp_utc, status=row['status'])
            db.session.execute(stmt)
        db.session.commit()

        business_hours_df = business_hours_df.dropna(subset=['store_id'])
        for _, row in business_hours_df.iterrows():
            stmt = insert(BusinessHours).values(
                store_id=row['store_id'], day=row['day'], start_time_local=pd.to_datetime(row['start_time_local']).time(), end_time_local=pd.to_datetime(row['end_time_local']).time()).on_conflict_do_nothing(index_elements=['store_id', 'day', 'start_time_local'])
            db.session.execute(stmt)
        db.session.commit()
