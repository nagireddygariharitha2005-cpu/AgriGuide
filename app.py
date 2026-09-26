from flask import Flask, render_template, request, jsonify, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = "agriguide_secret_key"


# =========================
# DATABASE SETUP
# =========================

def init_db():

    conn = sqlite3.connect("agriguide.db")
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

        email = request.form["email"]
        password = request.form["password"]

        conn = sqlite3.connect("agriguide.db")
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM users WHERE email = ? AND password = ?",
            (email, password)
        )

        user = cursor.fetchone()

        conn.close()

        if user:

            session["user_id"] = user[0]
            session["user_name"] = user[1]
            session["user_email"] = user[2]

            return redirect("/dashboard")

        return """
        <script>
            alert("Invalid email or password");
            window.location.href="/login";
        </script>
        """

    return render_template("login.html")


# =========================
# REGISTER
# =========================

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]
        confirm_password = request.form["confirm_password"]

        if password != confirm_password:

            return """
            <script>
                alert("Passwords do not match");
                window.location.href="/register";
            </script>
            """

        conn = sqlite3.connect("agriguide.db")
        cursor = conn.cursor()

        try:

            cursor.execute("""
                INSERT INTO users (name, email, password)
                VALUES (?, ?, ?)
            """, (name, email, password))

            conn.commit()
            conn.close()

            return """
            <script>
                alert("Registration successful!");
                window.location.href="/login";
            </script>
            """

        except sqlite3.IntegrityError:

            conn.close()

            return """
            <script>
                alert("Email already registered!");
                window.location.href="/register";
            </script>
            """

    return render_template("register.html")


# =========================
# DASHBOARD
# =========================

@app.route("/dashboard")
def dashboard():

    if "user_id" not in session:

        return redirect("/login")

    user_name = session.get(
        "user_name",
        "Farmer"
    )

    return render_template(
        "dashboard.html",
        user_name=user_name
    )


# =========================
# LOGOUT
# =========================

@app.route("/logout")
def logout():

    session.clear()

    return redirect("/login")


# =========================
# FERTILIZERS
# =========================

@app.route("/fertilizers")
def fertilizers():

    if "user_id" not in session:

        return redirect("/login")

    return render_template(
        "fertilizers.html"
    )


# =========================
# PRICES
# =========================

@app.route("/prices")
def prices():

    if "user_id" not in session:

        return redirect("/login")

    return render_template(
        "prices.html"
    )


# =========================
# CROP RECOMMENDATION
# =========================

@app.route(
    "/recommendation",
    methods=["GET", "POST"]
)
def recommendation():

    if "user_id" not in session:

        return redirect("/login")

    result = ""

    if request.method == "POST":

        soil = request.form["soil"]
        season = request.form["season"]
        water = request.form["water"]

        if soil == "black" and season == "kharif":

            result = "Rice or Cotton"

        elif soil == "red" and water == "low":

            result = "Millets or Groundnut"

        elif season == "rabi":

            result = "Wheat or Chickpea"

        elif season == "summer" and water == "high":

            result = "Rice or Vegetables"

        else:

            result = "Maize or suitable local crops"

    return render_template(
        "recommendation.html",
        recommendation=result
    )


# =========================
# CHATBOT PAGE
# =========================

@app.route("/chatbot")
def chatbot():

    if "user_id" not in session:

        return redirect("/login")

    return render_template(
        "chatbot.html"
    )


# =========================
# CHATBOT API
# =========================

@app.route("/chat", methods=["POST"])
def chat():

    if "user_id" not in session:

        return jsonify({
            "reply": "Please login first."
        })


    data = request.get_json() or {}


    message = data.get(
        "message",
        ""
    ).strip()


    selected_language = data.get(
        "language",
        "en-US"
    )


    message_lower = message.lower()


    # =========================
    # DEVELOPER QUESTIONS
    # =========================

    developer_keywords = [

        "who developed",
        "who develop",
        "who created",
        "who create",
        "who made",
        "who is the developer",
        "developer of",
        "developed this project",
        "created this project",
        "made this project",
        "who built",
        "who build",
        "developer name",
        "project developer"

    ]


    if any(
        keyword in message_lower
        for keyword in developer_keywords
    ):

        if selected_language == "te-IN":

            reply = (
                "ఈ AgriGuide ప్రాజెక్ట్‌ను "
                "Haritha Nagireddygari అభివృద్ధి చేశారు."
            )

        else:

            reply = (
                "This AgriGuide project was developed by "
                "Haritha Nagireddygari."
            )

        return jsonify({
            "reply": reply
        })


    # =========================
    # TELUGU SCRIPT DETECTION
    # =========================

    is_telugu_script = any(
        "\u0C00" <= char <= "\u0C7F"
        for char in message
    )


    # =========================
    # ROMANIZED TELUGU DETECTION
    # =========================

    roman_telugu_words = [

        "vari",
        "panta",
        "pantaku",
        "eruvu",
        "eruvulu",
        "manchidi",
        "manchive",
        "nela",
        "neelu",
        "neeti",
        "raithu",
        "vyavasayam",
        "vyavasaya",
        "polam",
        "vittanalu",
        "vittanam",
        "dhanam",
        "verusenaga",
        "mokkalu",
        "panta",
        "kharif",
        "rabi",
        "vesavi",
        "mirapakaya",
        "pasupu",
        "patti",
        "mokku",
        "ఎరువు"
    ]


    is_roman_telugu = any(
        word in message_lower
        for word in roman_telugu_words
    )


    # =========================
    # TELUGU MODE
    # =========================

    if (
        selected_language == "te-IN"
        or is_telugu_script
        or is_roman_telugu
    ):


        # -------------------------
        # GREETING
        # -------------------------

        if (
            "హలో" in message
            or "నమస్కారం" in message
            or "హాయ్" in message
            or "hello" in message_lower
            or "hi" in message_lower
            or "hlo" in message_lower
        ):

            reply = (
                "నమస్కారం రైతు! 👋 "
                "అగ్రిగైడ్‌కు స్వాగతం. "
                "పంటలు, ఎరువులు, నేల లేదా వ్యవసాయం "
                "గురించి మీరు నన్ను అడగవచ్చు."
            )


        # -------------------------
        # RICE
        # -------------------------

        elif (
            "వరి" in message
            or "vari" in message_lower
        ):

            reply = (
                "వరి పంటకు సాధారణంగా మంచి నీటి లభ్యత "
                "మరియు అనుకూలమైన నేల పరిస్థితులు అవసరం. "
                "ఎరువుల ఎంపికను నేల పరీక్ష మరియు పంట "
                "అవసరాల ఆధారంగా చేయడం మంచిది."
            )


        # -------------------------
        # FERTILIZER
        # -------------------------

        elif (
            "ఎరువు" in message
            or "ఎరువులు" in message
            or "eruvu" in message_lower
            or "eruvulu" in message_lower
        ):

            reply = (
                "ఎరువులు పంటలకు అవసరమైన పోషకాలను "
                "అందిస్తాయి. పంట మరియు నేల పరిస్థితులకు "
                "అనుగుణంగా సరైన ఎరువును ఎంచుకోవాలి."
            )


        # -------------------------
        # CROP
        # -------------------------

        elif (
            "పంట" in message
            or "panta" in message_lower
            or "pantaku" in message_lower
        ):

            reply = (
                "పంట ఎంపికలో నేల రకం, కాలం మరియు "
                "నీటి లభ్యత వంటి అంశాలను పరిగణలోకి "
                "తీసుకోవాలి."
            )


        # -------------------------
        # SOIL
        # -------------------------

        elif (
            "నేల" in message
            or "nela" in message_lower
        ):

            reply = (
                "నేల రకం పంట ఎంపికలో ముఖ్యమైన అంశం. "
                "వేర్వేరు నేలలకు వేర్వేరు పంటలు "
                "అనుకూలంగా ఉండవచ్చు."
            )


        # -------------------------
        # WATER
        # -------------------------

        elif (
            "నీరు" in message
            or "నీటి" in message
            or "neeru" in message_lower
            or "neeti" in message_lower
        ):

            reply = (
                "పంటకు అవసరమైన నీటి పరిమాణం పంట రకం, "
                "నేల మరియు కాలాన్ని బట్టి మారుతుంది."
            )


        # -------------------------
        # DEFAULT TELUGU
        # -------------------------

        else:

            reply = (
                "నేను AgriGuide Assistant. "
                "పంటలు, ఎరువులు, నేల, నీరు మరియు "
                "వ్యవసాయం గురించి తెలుగులో మీ ప్రశ్న అడగండి."
            )


    # =========================
    # ENGLISH MODE
    # =========================

    else:


        # -------------------------
        # GREETING
        # -------------------------

        if (
            "hello" in message_lower
            or "hi" in message_lower
            or "hlo" in message_lower
        ):

            reply = (
                "Hello farmer! 👋 "
                "How can I help you today?"
            )


        # -------------------------
        # FERTILIZER
        # -------------------------

        elif "fertilizer" in message_lower:

            reply = (
                "Fertilizers provide nutrients to crops. "
                "Choose fertilizers according to the "
                "crop and soil conditions."
            )


        # -------------------------
        # RICE
        # -------------------------

        elif "rice" in message_lower:

            reply = (
                "Rice generally needs good water "
                "availability and suitable soil conditions."
            )


        # -------------------------
        # CROP
        # -------------------------

        elif "crop" in message_lower:

            reply = (
                "I can help with crop information based "
                "on soil, season and water availability."
            )


        # -------------------------
        # SOIL
        # -------------------------

        elif "soil" in message_lower:

            reply = (
                "Soil type is important when selecting "
                "crops. Different crops grow better in "
                "different soil conditions."
            )


        # -------------------------
        # WATER
        # -------------------------

        elif "water" in message_lower:

            reply = (
                "Water requirements depend on the crop, "
                "soil type and season."
            )


        # -------------------------
        # DEFAULT ENGLISH
        # -------------------------

        else:

            reply = (
                "I am AgriGuide Assistant. "
                "Please ask me about crops, fertilizers, "
                "soil, water or farming."
            )


    return jsonify({
        "reply": reply
    })


# =========================
# DEVELOPERS
# =========================

@app.route("/developers")
def developers():

    if "user_id" not in session:

        return redirect("/login")

    return render_template(
        "developers.html"
    )


# =========================
# INITIALIZE DATABASE
# =========================

init_db()


# =========================
# START APPLICATION
# =========================

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000
    )
