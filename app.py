import os
import sqlite3
import logging
from dotenv import load_dotenv

# Load environment configuration early before service modules initialize
load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))

from flask import Flask, render_template, request, jsonify, redirect, session, flash
from werkzeug.security import generate_password_hash, check_password_hash

# Modular services and agronomic data
from services.language_service import normalize_farmer_input, detect_language
from services.ai_service import (
    ask_agricultural_chat,
    analyze_crop_image,
    generate_dynamic_ai_recommendation,
    process_voice_query,
    transcribe_farmer_audio
)
from services.price_service import get_crop_prices
from services.developer_service import (
    is_developer_query,
    get_developer_profile_response,
    DEVELOPER_PROFILE,
    get_developer_photo_url
)
from agri_data.fertilizers import FERTILIZERS_CATALOG, calculate_fertilizer_guidance
from agri_data.rules import evaluate_agronomic_recommendation

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, "templates"),
    static_folder=os.path.join(BASE_DIR, "static")
)
# Secure secret key handling via environment variable (Phase 12)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "agriguide_prod_secure_secret_key_2026")
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure application logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("agriguide")


# =========================
# DATABASE SETUP & MIGRATION
# =========================

DB_PATH = "/tmp/agriguide.db" if os.environ.get("VERCEL") else os.path.join(os.path.dirname(os.path.abspath(__file__)), "agriguide.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


# =========================
# HOME
# =========================

@app.route("/")
def home():
    return render_template("index.html")


# =========================
# LOGIN
# =========================

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        if not email or not password:
            flash("Please enter both email and password.", "error")
            return render_template("login.html")

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute("SELECT id, name, email, password FROM users WHERE email = ?", (email,))
        user = cursor.fetchone()

        if user:
            user_id, user_name, user_email, stored_pw = user
            authenticated = False

            # Phase 11: Check Werkzeug password hash
            if stored_pw.startswith(("scrypt:", "pbkdf2:")):
                authenticated = check_password_hash(stored_pw, password)
            else:
                # Phase 11: Legacy plaintext password migration without locking existing accounts
                if stored_pw == password:
                    authenticated = True
                    try:
                        new_hash = generate_password_hash(password)
                        cursor.execute("UPDATE users SET password = ? WHERE id = ?", (new_hash, user_id))
                        conn.commit()
                        logger.info(f"Successfully migrated password hash for user ID {user_id}")
                    except Exception as e:
                        logger.warning(f"Password rehash update failed: {e}")

            conn.close()

            if authenticated:
                session["user_id"] = user_id
                session["user_name"] = user_name
                session["user_email"] = user_email
                return redirect("/dashboard")

        conn.close()
        # Phase 13: Clean flash message instead of raw <script>alert(...)
        flash("Invalid email or password. Please try again.", "error")
        return render_template("login.html")

    return render_template("login.html")


# =========================
# REGISTER
# =========================

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        if not name or not email or not password:
            flash("All fields are required.", "error")
            return render_template("register.html")

        if password != confirm_password:
            flash("Passwords do not match.", "error")
            return render_template("register.html")

        if len(password) < 6:
            flash("Password must be at least 6 characters long.", "error")
            return render_template("register.html")

        # Phase 11: Hash password with Werkzeug before storing
        hashed_password = generate_password_hash(password)

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO users (name, email, password)
                VALUES (?, ?, ?)
            """, (name, email, hashed_password))

            conn.commit()
            conn.close()

            # Phase 13: Clean flash message on successful registration
            flash("Registration successful! Please login.", "success")
            return redirect("/login")

        except sqlite3.IntegrityError:
            conn.close()
            flash("This email is already registered. Please log in or use another email.", "error")
            return render_template("register.html")

    return render_template("register.html")


# =========================
# DASHBOARD
# =========================

@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        flash("Please log in to access your dashboard.", "error")
        return redirect("/login")

    user_name = session.get("user_name", "Farmer")
    return render_template("dashboard.html", user_name=user_name)


# =========================
# LOGOUT
# =========================

@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out safely.", "success")
    return redirect("/login")


# =========================
# FERTILIZERS (Phase 14)
# =========================

@app.route("/fertilizers")
def fertilizers():
    if "user_id" not in session:
        return redirect("/login")

    search_query = request.args.get("search", "").strip().lower()
    calc_crop = request.args.get("crop", "rice").strip().lower()
    calc_acres = request.args.get("acres", "1")

    try:
        acres_val = float(calc_acres)
    except (ValueError, TypeError):
        acres_val = 1.0

    # Filter catalog if search query provided
    all_fertilizers = list(FERTILIZERS_CATALOG.values())
    if search_query:
        filtered = [
            f for f in all_fertilizers
            if search_query in f["name_en"].lower()
            or search_query in f["name_te"].lower()
            or search_query in f["primary_nutrient"].lower()
            or search_query in f["description_en"].lower()
        ]
    else:
        filtered = all_fertilizers

    # Calculate dosage with safety caveats
    dosage_info = calculate_fertilizer_guidance(calc_crop, acres_val)

    return render_template(
        "fertilizers.html",
        fertilizers=filtered,
        dosage=dosage_info,
        search_query=search_query,
        selected_crop=calc_crop,
        selected_acres=acres_val
    )


# =========================
# PRICES (Phase 15)
# =========================


@app.route("/prices")
def prices():
    if "user_id" not in session:
        return redirect("/login")

    search_query = request.args.get("q", "").strip()

    # Correct common crop spelling mistakes
    crop_corrections = {
        "tomoto": "tomato",
        "tamato": "tomato",
        "tomatoes": "tomato",
        "cotten": "cotton",
        "cottn": "cotton",
        "sugercane": "sugarcane",
        "sugar cane": "sugarcane",
        "ground nut": "groundnut",
        "groundnuts": "groundnut",
        "chili": "chilli",
        "padi": "paddy",
    }

    corrected_query = search_query.lower().strip()
    corrected_query = crop_corrections.get(
        corrected_query, corrected_query
    )

    price_data = get_crop_prices(corrected_query)

    return render_template(
        "prices.html",
        prices=price_data["prices"],
        is_live=price_data["is_live"],
        data_source=price_data["data_source"],
        disclaimer_en=price_data["disclaimer_en"],
        disclaimer_te=price_data["disclaimer_te"],
        search_query=search_query
    )



# =========================
# DYNAMIC CROP RECOMMENDATION (Phases 3, 4, 5, 6, 7, 8)
# =========================

@app.route("/recommendation", methods=["GET", "POST"])
def recommendation():
    if "user_id" not in session:
        return redirect("/login")

    rec_data = None
    user_inputs = {
        "soil": "",
        "season": "",
        "water": "",
        "crop_preference": "",
        "farmer_notes": "",
        "language": "te"
    }

    if request.method == "POST":
        # Backward compatibility with existing fields: soil, season, water
        soil = request.form.get("soil", "").strip()
        season = request.form.get("season", "").strip()
        water = request.form.get("water", "").strip()
        crop_pref = request.form.get("crop_preference", "").strip()
        farmer_notes = request.form.get("farmer_notes", "").strip()
        lang_pref = request.form.get("language", "te").strip()

        user_inputs = {
            "soil": soil,
            "season": season,
            "water": water,
            "crop_preference": crop_pref,
            "farmer_notes": farmer_notes,
            "language": lang_pref
        }

        # Phase 4: Language normalization layer
        normalized = normalize_farmer_input(
            soil=soil,
            season=season,
            water=water,
            crop_preference=crop_pref,
            farmer_query=farmer_notes,
            language_pref=lang_pref
        )

        # Phase 5: Try dynamic AI generation first
        ai_result = generate_dynamic_ai_recommendation(normalized)

        if ai_result and isinstance(ai_result, dict) and "primary_crops" in ai_result and len(ai_result["primary_crops"]) > 0:
            rec_data = ai_result
            rec_data["source"] = "AI Agronomist (Gemini)"
        else:
            # Phase 6: Local Agronomic Fallback Layer (Ensures application always outputs rich dynamic data)
            logger.info("Using local agronomic fallback database for recommendation")
            rec_data = evaluate_agronomic_recommendation(normalized)
            rec_data["source"] = "AgriGuide Agronomic Reference System"

        # If AJAX JSON request, return JSON
        if request.headers.get("Accept") == "application/json" or request.is_json:
            return jsonify(rec_data)

    return render_template(
        "recommendation.html",
        recommendation=rec_data,
        inputs=user_inputs
    )


# =========================
# CHATBOT PAGE
# =========================

@app.route("/chatbot")
def chatbot():
    if "user_id" not in session:
        return redirect("/login")

    return render_template("chatbot.html")


# =========================
# CHATBOT API (Phase 2 & Phase 9)
# =========================

@app.route("/chat", methods=["POST"])
def chat():
    if "user_id" not in session:
        return jsonify({"reply": "Please log in to use the chatbot."}), 401

    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"reply": "Please enter a question and try again."}), 400

    message = data.get("message", "")
    if not isinstance(message, str):
        return jsonify({"reply": "Please enter your question as text."}), 400

    message = message.strip()
    if not message:
        return jsonify({"reply": "Please type a question first."}), 400
    if len(message) > 4000:
        return jsonify({"reply": "Please keep your question under 4,000 characters."}), 400

    history = data.get("history", [])

    # Check for developer / project development intent
    if is_developer_query(message):
        return jsonify(get_developer_profile_response(message))

    # Process query through bilingual AI service
    result = ask_agricultural_chat(message, conversation_history=history)
    logger.info(
        f"[/chat] Processed query (len={len(message)}): provider={result.get('provider')}, "
        f"lang={result.get('language')}, configured={result.get('configured')}"
    )
    return jsonify(result)


# =========================
# AI DIAGNOSTIC STATUS API
# =========================

@app.route("/api/ai-status")
def ai_status():
    """
    Safe diagnostic endpoint returning AI provider configuration status without secrets.
    Allows farmers and administrators to verify that GEMINI_API_KEY is active in production.
    """
    from services.ai_service import check_ai_configuration
    return jsonify(check_ai_configuration())


# =========================
# IMAGE UPLOAD VISION API (Phase 10)
# =========================

@app.route("/chat-image", methods=["POST"])
def chat_image():
    if "user_id" not in session:
        return jsonify({"reply": "Please log in to upload crop images.", "success": False}), 401

    if "image" not in request.files:
        return jsonify({"reply": "No image file was provided in the request.", "success": False}), 400

    file = request.files["image"]
    if file.filename == "":
        return jsonify({"reply": "Please select a valid image file.", "success": False}), 400

    # Validate file extension
    allowed_extensions = {".png", ".jpg", ".jpeg", ".webp"}
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in allowed_extensions:
        return jsonify({
            "reply": "Unsupported file format. Please upload a PNG, JPG, JPEG, or WEBP image.",
            "success": False
        }), 400

    image_bytes = file.read()
    # Limit to 5MB to avoid denial of service and memory overflow
    if len(image_bytes) > 5 * 1024 * 1024:
        return jsonify({
            "reply": "Image size exceeds 5MB limit. Please upload a smaller photo.",
            "success": False
        }), 400

    caption = request.form.get("caption", "").strip()
    mime_type = file.mimetype or "image/jpeg"

    # Analyze crop image using Gemini multimodal vision
    result = analyze_crop_image(image_bytes, mime_type, user_caption=caption)
    return jsonify(result)


# =========================
# VOICE AUDIO API (STT & Voice Chat)
# =========================

@app.route("/chat-voice", methods=["POST"])
def chat_voice():
    if "user_id" not in session:
        return jsonify({"reply": "Please log in to use voice assistance.", "success": False}), 401

    if "audio" not in request.files:
        return jsonify({"reply": "No audio file was received in the request.", "success": False}), 400

    file = request.files["audio"]
    if file.filename == "":
        return jsonify({"reply": "Audio recording was empty. Please try speaking again.", "success": False}), 400

    audio_bytes = file.read()
    if len(audio_bytes) < 100:
        return jsonify({"reply": "Audio recording was too short or empty.", "success": False}), 400

    # Max 10MB audio limit
    if len(audio_bytes) > 10 * 1024 * 1024:
        return jsonify({"reply": "Audio size exceeds limit. Please record a shorter message.", "success": False}), 400

    mime_type = file.mimetype or "audio/wav"
    language_hint = request.form.get("language", "te")

    result = process_voice_query(audio_bytes, mime_type, language_hint=language_hint)
    return jsonify(result)


@app.route("/transcribe-audio", methods=["POST"])
def transcribe_audio():
    if "user_id" not in session:
        return jsonify({"reply": "Please log in to transcribe voice.", "success": False}), 401

    if "audio" not in request.files:
        return jsonify({"reply": "No audio file was received.", "success": False}), 400

    file = request.files["audio"]
    if file.filename == "":
        return jsonify({"reply": "Audio recording was empty.", "success": False}), 400

    audio_bytes = file.read()
    if len(audio_bytes) < 100:
        return jsonify({"reply": "Audio recording was too short or empty.", "success": False}), 400

    if len(audio_bytes) > 10 * 1024 * 1024:
        return jsonify({"reply": "Audio file too large.", "success": False}), 400

    mime_type = file.mimetype or "audio/wav"
    language_hint = request.form.get("language", "te")

    result = transcribe_farmer_audio(audio_bytes, mime_type, language_hint=language_hint)
    return jsonify(result)


# =========================
# DEVELOPERS
# =========================

@app.route("/developers")
def developers():
    user_logged_in = "user_id" in session
    profile = dict(DEVELOPER_PROFILE)
    profile["photo_url"] = get_developer_photo_url()
    return render_template("developers.html", developer=profile, user_logged_in=user_logged_in)


# =========================
# START APPLICATION
# =========================
init_db()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)