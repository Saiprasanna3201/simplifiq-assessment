import os
import uuid
from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv
from scraper import enrich_company
from pdf_generator import generate_pdf
from mailer import send_email
from sheets import log_to_sheet
from drive import upload_to_drive

load_dotenv()

app = Flask(__name__)
os.makedirs("outputs", exist_ok=True)


def validate_lead(data):
    """Validate required fields and return errors list."""
    errors = []
    required = ["name", "email", "company", "website", "industry"]
    for field in required:
        if not data.get(field, "").strip():
            errors.append(f"{field} is required")
    if data.get("email") and "@" not in data["email"]:
        errors.append("Invalid email address")
    return errors


@app.route("/", methods=["GET"])
def index():
    return render_template("form.html")


@app.route("/submit", methods=["POST"])
def submit_lead():
    lead = {
        "name":       request.form.get("name", "").strip(),
        "email":      request.form.get("email", "").strip(),
        "company":    request.form.get("company", "").strip(),
        "website":    request.form.get("website", "").strip(),
        "industry":   request.form.get("industry", "").strip(),
        "role":       request.form.get("role", "").strip(),
        "message":    request.form.get("message", "").strip(),
    }

    errors = validate_lead(lead)
    if errors:
        return jsonify({"status": "error", "errors": errors}), 400

    try:
        # Step 1: Enrich company data
        print(f"[1/4] Enriching data for {lead['company']}...")
        enriched = enrich_company(lead)

        # Step 2: Generate PDF report
        print(f"[2/4] Generating PDF report...")
        report_id = str(uuid.uuid4())[:8]
        pdf_path = f"outputs/{lead['company'].replace(' ', '_')}_{report_id}.pdf"
        generate_pdf(lead, enriched, pdf_path)

        # Step 3: Send email with PDF
        print(f"[3/4] Sending email to {lead['email']}...")
        send_email(lead, pdf_path)

        # Step 4: Bonus — log + archive
        print(f"[4/4] Logging and archiving...")
        sheet_status = "ok"
        drive_status = "ok"

        try:
            log_to_sheet(lead, pdf_path)
        except Exception as e:
            sheet_status = f"failed: {e}"
            print(f"  [sheets] {sheet_status}")

        try:
            upload_to_drive(pdf_path)
        except Exception as e:
            drive_status = f"failed: {e}"
            print(f"  [drive] {drive_status}")

        return jsonify({
            "status": "success",
            "message": f"Report generated and sent to {lead['email']}",
            "pdf": pdf_path,
            "sheets": sheet_status,
            "drive": drive_status,
        })

    except Exception as e:
        print(f"Pipeline error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True, port=5000)
