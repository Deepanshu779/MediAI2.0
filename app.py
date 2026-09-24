import os
from pathlib import Path
from flask import Flask, render_template, request, jsonify, send_file

from predict import predict_disease
from groq_helper import get_ai_advice, get_chat_response
from report_generator import generate_report
from utils import (
    calculate_bmi,
    bmi_status,
    calculate_risk,
    temperature_status,
    spo2_status,
    emergency_check,
    health_score,
    health_summary,
    calculate_bmr,
    calculate_hydration,
    calculate_target_heart_rate,
    calculate_map,
    parse_precautions_list,
    parse_ai_sections,
    get_all_symptoms_catalog
)

app = Flask(__name__)
BASE_DIR = Path(__file__).resolve().parent

# Helper Parsers
def parse_int(value, default=0):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default

def parse_float(value, default=0.0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


# =========================================================
# ROUTES
# =========================================================

@app.route("/")
def home():
    """
    Landing Page with interactive 3D WebGL hero, anatomical system explorer,
    real-time health calculators, and platform overview.
    """
    symptom_catalog = get_all_symptoms_catalog()
    has_api_key = bool(os.getenv("GROQ_API_KEY", "").strip())
    return render_template(
        "pages/home.html",
        symptom_catalog=symptom_catalog,
        has_api_key=has_api_key
    )


@app.route("/assessment")
def assessment():
    """
    4-Step Guided Clinical Health Assessment Wizard.
    """
    symptom_catalog = get_all_symptoms_catalog()
    has_api_key = bool(os.getenv("GROQ_API_KEY", "").strip())
    return render_template(
        "pages/assessment.html",
        symptom_catalog=symptom_catalog,
        has_api_key=has_api_key
    )


@app.route("/assistant")
def assistant():
    """
    Real-time AI Clinical Health Companion & Triage Chat.
    """
    has_api_key = bool(os.getenv("GROQ_API_KEY", "").strip())
    return render_template(
        "pages/assistant.html",
        has_api_key=has_api_key
    )


@app.route("/predict", methods=["POST"])
def predict():
    """
    Process clinical assessment submission, run offline ML differential analysis,
    generate AI clinical care guidance, build PDF, and render Result Dashboard.
    """
    # 1. Demographics
    name = request.form.get("name", "Patient").strip() or "Patient"
    age = parse_int(request.form.get("age"), default=30)
    gender = request.form.get("gender", "Not Specified")

    # 2. Physical & Biometrics
    height = parse_float(request.form.get("height"), default=170.0)
    weight = parse_float(request.form.get("weight"), default=65.0)
    temperature = request.form.get("temperature", "").strip()
    spo2 = request.form.get("spo2", "").strip()

    # 3. Symptoms Extraction
    selected_symptoms = request.form.getlist("symptoms")
    other_symptoms = request.form.get("other_symptoms", "").strip()

    if other_symptoms:
        for s in other_symptoms.split(","):
            s_clean = s.strip().lower()
            if s_clean and s_clean not in [x.lower() for x in selected_symptoms]:
                selected_symptoms.append(s_clean)

    if not selected_symptoms:
        symptom_catalog = get_all_symptoms_catalog()
        return render_template(
            "pages/assessment.html",
            error="Please select at least one symptom or describe your symptoms before proceeding.",
            symptom_catalog=symptom_catalog,
            has_api_key=bool(os.getenv("GROQ_API_KEY", "").strip())
        )

    symptoms_str = ", ".join(selected_symptoms)

    # 4. Clinical Context
    duration = request.form.get("duration") or "1-3 Days"
    severity = request.form.get("severity") or "Mild"
    progress = request.form.get("progress") or "Stable"
    contact = request.form.get("contact") or "No known exposure"
    history_list = request.form.getlist("history")
    history = ", ".join(history_list) if history_list else "None reported"
    emergency = request.form.getlist("emergency")

    # 5. Health & Physiological Calculations
    bmi = calculate_bmi(height, weight)
    bmi_result = bmi_status(bmi)
    risk = calculate_risk(age, severity, temperature, spo2)
    temp_status = temperature_status(temperature)
    oxygen_status = spo2_status(spo2)
    emergency_detected = emergency_check(emergency)
    score = health_score(risk, bmi)
    summary = health_summary(score)

    bmr = calculate_bmr(weight, height, age, gender)
    hydration = calculate_hydration(weight)
    target_hr = calculate_target_heart_rate(age)

    # 6. Machine Learning Prediction Engine
    disease, confidence, precaution, predictions = predict_disease(symptoms_str)

    if confidence < 30.0:
        disease_display = "Inconclusive / Overlapping Symptom Complex"
    else:
        disease_display = disease

    # 7. AI Clinical Advice Engine
    try:
        ai_response = get_ai_advice(
            age=age,
            gender=gender,
            symptoms=symptoms_str,
            disease=disease_display,
            duration=duration,
            severity=severity,
            history=history,
            bmi=bmi,
            risk=risk,
            temperature=temperature,
            spo2=spo2,
            progress=progress,
            contact=contact,
            emergency=emergency
        )
    except Exception as e:
        ai_response = f"Clinical Assessment: {str(e)}"

    precautions_list = parse_precautions_list(precaution)
    ai_sections = parse_ai_sections(ai_response)
    has_api_key = bool(os.getenv("GROQ_API_KEY", "").strip())

    # 8. Generate PDF Report
    try:
        generate_report(
            name=name,
            age=age,
            gender=gender,
            height=height,
            weight=weight,
            bmi=bmi,
            risk=risk,
            temperature=temperature,
            temperature_status=temp_status,
            spo2=spo2,
            spo2_status=oxygen_status,
            health_score=score,
            health_summary=summary,
            symptoms=symptoms_str,
            duration=duration,
            severity=severity,
            progress=progress,
            contact=contact,
            history=history,
            emergency=emergency,
            disease=disease_display,
            confidence=confidence,
            precaution=precaution,
            ai_response=ai_response
        )
    except Exception as e:
        print("PDF generation error:", e)

    # 9. Render 3D Diagnostic Dashboard
    return render_template(
        "pages/result.html",
        name=name,
        age=age,
        gender=gender,
        height=height,
        weight=weight,
        bmi=bmi,
        bmi_status=bmi_result,
        risk=risk,
        temperature=temperature or "Not Provided",
        temperature_status=temp_status,
        spo2=spo2 or "Not Provided",
        spo2_status=oxygen_status,
        health_score=score,
        health_summary=summary,
        bmr=bmr,
        hydration=hydration,
        target_hr=target_hr,
        emergency_detected=emergency_detected,
        emergency_list=emergency,
        symptoms=symptoms_str,
        selected_symptoms=selected_symptoms,
        duration=duration,
        severity=severity,
        progress=progress,
        contact=contact,
        history=history,
        disease=disease_display,
        confidence=round(confidence, 1),
        precaution=precaution,
        precautions_list=precautions_list,
        ai_response=ai_response,
        ai_sections=ai_sections,
        predictions=predictions,
        has_api_key=has_api_key
    )


# =========================================================
# JSON API ENDPOINTS
# =========================================================

@app.route("/api/chat", methods=["POST"])
def api_chat():
    """
    Asynchronous JSON chat endpoint for AI Assistant.
    """
    data = request.get_json() or {}
    messages = data.get("messages", [])
    if not messages:
        return jsonify({"error": "No messages provided"}), 400

    response_text = get_chat_response(messages)
    return jsonify({"response": response_text})


@app.route("/api/symptoms")
def api_symptoms():
    """
    Returns full symptom catalog with categories for autocomplete and 3D mapping.
    """
    return jsonify(get_all_symptoms_catalog())


@app.route("/api/calculate-vitals", methods=["POST"])
def api_calculate_vitals():
    """
    Live real-time vitals and biometrics calculator endpoint.
    """
    data = request.get_json() or {}
    height = parse_float(data.get("height"), default=170.0)
    weight = parse_float(data.get("weight"), default=65.0)
    age = parse_int(data.get("age"), default=30)
    gender = data.get("gender", "Male")
    temp = data.get("temperature", "")
    spo2 = data.get("spo2", "")
    systolic = data.get("systolic")
    diastolic = data.get("diastolic")

    bmi = calculate_bmi(height, weight)
    bm_stat = bmi_status(bmi)
    temp_stat = temperature_status(temp)
    spo2_stat = spo2_status(spo2)
    bmr = calculate_bmr(weight, height, age, gender)
    hydration = calculate_hydration(weight)
    target_hr = calculate_target_heart_rate(age)
    map_val = calculate_map(systolic, diastolic) if systolic and diastolic else None

    return jsonify({
        "bmi": bmi,
        "bmi_status": bm_stat,
        "temperature_status": temp_stat,
        "spo2_status": spo2_stat,
        "bmr": bmr,
        "hydration_liters": hydration,
        "target_heart_rate": target_hr,
        "map": map_val
    })


@app.route("/report/preview")
def preview_report():
    """Preview the latest generated PDF before downloading it."""
    pdf_path = BASE_DIR / "static" / "report.pdf"
    if not pdf_path.exists():
        return jsonify({"error": "Report not generated yet"}), 404
    return render_template("pages/report_preview.html")


@app.route("/report/download")
def download_report():
    """Serve the generated PDF inline for preview or as an attachment for download."""
    pdf_path = BASE_DIR / "static" / "report.pdf"
    if pdf_path.exists():
        inline = request.args.get("inline") == "1"
        return send_file(
            pdf_path,
            as_attachment=not inline,
            download_name="MediAI_Health_Assessment_Report.pdf",
            mimetype="application/pdf"
        )
    return jsonify({"error": "Report not generated yet"}), 404


if __name__ == "__main__":
    app.run(debug=True, port=5000)