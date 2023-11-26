from flask import Blueprint, jsonify, request, send_file, current_app as app
import uuid
import threading
from app.utils.utils import generate_report
import os

reports = Blueprint('reports', __name__)

report_id_status = {}

@reports.route("/trigger_report", methods=["GET"])
def trigger_report():
    # Generate a random report id
    report_id = uuid.uuid4().hex
    # Set the status to running
    report_id_status[report_id] = "Running"
    # Generate the report in a separate thread
    threading.Thread(target=run_report, args=(
        app._get_current_object(), report_id)).start()
    # Return the report id as json
    return jsonify({"report_id": report_id})

# Define the /get_report endpoint
@reports.route("/get_report", methods=["GET"])
def get_report():
    # Get the report id from the query parameter
    report_id = request.args.get("report_id")
    # Check if the report id is valid
    if report_id in report_id_status:
        # Get the status of the report
        status = report_id_status[report_id]
        # If the status is complete, send the csv file as attachment
        if status == "Complete":
            return send_file(f"../reports/report_{report_id}.csv", as_attachment=True)
        # Else, return the status as json
        else:
            return jsonify({"status": status})
    # Else, return an error message as json
    else:
        return jsonify({"error": "Invalid report id"})


def run_report(app, report_id):
    with app.app_context():
        # Generate the report
        report = generate_report()
        # Create the reports directory if it doesn't exist
        if not os.path.exists("reports"):
            os.makedirs("reports")
        # Save the report as a csv file
        report.to_csv(f"reports/report_{report_id}.csv", index=False)
        # Set the status to complete
        report_id_status[report_id] = "Complete"
