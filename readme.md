## Loop Kitchen Assignment


## Problem statement

Loop monitors several restaurants in the US and needs to monitor if the store is online or not. All restaurants are supposed to be online during their business hours. Due to some unknown reasons, a store might go inactive for a few hours. Restaurant owners want to get a report of the how often this happened in the past.

We want to build backend APIs that will help restaurant owners achieve this goal.


## Data output requirement

Output report in csv format to the user that has the following schema

`store_id, uptime_last_hour(in minutes), uptime_last_day(in hours), update_last_week(in hours), downtime_last_hour(in minutes), downtime_last_day(in hours), downtime_last_week(in hours)`


## Data Import

import the files inside the data folder

- data/store status
- data/Menu hours
- data/bq-results-20230125-202210-1674678181880

## Install

```
pip install -r requirements.txt
```

## Run the app

```
python run.py
```


## Trigger report generation

### Request

```
curl --request GET \
  --url http://127.0.0.1:5000/reports/trigger_report
```

### Response

```
{
  "report_id": "2f42f578e7d6484ea170f6d71c0c790e"
}
```

## Get the status of the report or the csv

### Request

```
curl --request GET \
  --url 'http://localhost:5000/reports/get_report?report_id=2f42f578e7d6484ea170f6d71c0c790e' \
  --header 'Content-Type: application/json'
```

### Response

Process Running

```
{
  "report_id": "2f42f578e7d6484ea170f6d71c0c790e"
}

```

Report Generated - CSV File
