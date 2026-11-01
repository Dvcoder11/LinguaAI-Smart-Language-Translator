
import os
from functools import wraps

from flask import (
    Flask,
    render_template,
    request,
    jsonify,
    redirect,
    url_for,
    session,
    flash
)

from dotenv import load_dotenv
from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)

from services.translator import (
    translate_text_with_details,
    get_service_status
)

from services.openrouter_client import get_client_status

from services.history import (
    initialize_database,
    create_user,
    get_user_by_email,
    get_user_by_id,
    save_translation,
    get_translation_history,
    delete_all_history
)


# ==========================================
# 1. APPLICATION CONFIGURATION
# ==========================================

load_dotenv()

app = Flask(__name__)

secret_key = os.getenv("FLASK_SECRET_KEY")

if not secret_key:
    raise RuntimeError(
        "FLASK_SECRET_KEY is missing from your .env file."
    )

app.secret_key = secret_key

app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=False,
    PERMANENT_SESSION_LIFETIME=3600
)

initialize_database()


# ==========================================
# 2. LOGIN REQUIRED DECORATOR
# ==========================================

def login_required(function):

    @wraps(function)
    def wrapper(*args, **kwargs):

        if "user_id" not in session:

            if request.path in [
                "/translate",
                "/history",
                "/history/delete"
            ]:

                return jsonify({
                    "error": "Please log in to continue."
                }), 401

            return redirect(url_for("login"))

        return function(*args, **kwargs)

    return wrapper


# ==========================================
# 3. REGISTRATION
# ==========================================

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        username = request.form.get(
            "username", ""
        ).strip()

        email = request.form.get(
            "email", ""
        ).strip().lower()

        password = request.form.get(
            "password", ""
        )

        if not username or not email or not password:

            flash("Please fill in all fields.", "error")
            return render_template("register.html")

        if len(username) < 3 or len(username) > 30:

            flash(
                "Username must contain 3 to 30 characters.",
                "error"
            )
            return render_template("register.html")

        if len(password) < 8:

            flash(
                "Password must contain at least 8 characters.",
                "error"
            )
            return render_template("register.html")

        password_hash = generate_password_hash(password)

        user_id = create_user(
            username,
            email,
            password_hash
        )

        if user_id is None:

            flash(
                "This email is already registered.",
                "error"
            )
            return render_template("register.html")

        session.clear()
        session["user_id"] = user_id
        session.permanent = True

        flash("Account created successfully!", "success")

        return redirect(url_for("home"))

    return render_template("register.html")


# ==========================================
# 4. LOGIN
# ==========================================

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form.get(
            "email", ""
        ).strip().lower()

        password = request.form.get(
            "password", ""
        )

        user = get_user_by_email(email)

        if (
            user is None
            or not check_password_hash(
                user["password_hash"],
                password
            )
        ):

            flash(
                "Invalid email or password.",
                "error"
            )

            return render_template("login.html")

        session.clear()
        session["user_id"] = user["id"]
        session.permanent = True

        return redirect(url_for("home"))

    return render_template("login.html")


# ==========================================
# 5. LOGOUT
# ==========================================

@app.route("/logout")
def logout():

    session.clear()

    flash("You have been logged out.", "success")

    return redirect(url_for("login"))


# ==========================================
# 6. HOME PAGE
# ==========================================

@app.route("/")
@login_required
def home():

    user = get_user_by_id(session["user_id"])

    if user is None:

        session.clear()
        return redirect(url_for("login"))

    return render_template(
        "index.html",
        user=user
    )


# ==========================================
# 7. HISTORY PAGE
# ==========================================

@app.route("/history-page")
@login_required
def history_page():

    user = get_user_by_id(session["user_id"])

    return render_template(
        "history.html",
        user=user
    )


# ==========================================
# 8. HEALTH CHECK
# ==========================================

@app.route("/health")
def health_check():

    return jsonify({
        "status": "success",
        "message": "Language Translator backend is running!"
    }), 200


# ==========================================
# 9. SERVICE STATUS
# ==========================================

@app.route("/service-status")
def service_status():

    return jsonify({
        "translation_service": get_service_status(),
        "api_client": get_client_status()
    }), 200


# ==========================================
# 10. TRANSLATION API
# ==========================================

@app.route("/translate", methods=["POST"])
@login_required
def translate():

    data = request.get_json(silent=True)

    if not isinstance(data, dict):

        return jsonify({
            "error": "Invalid request. JSON data is required."
        }), 400

    text = data.get("text")
    source_language = data.get("source_language")
    target_language = data.get("target_language")

    try:

        result = translate_text_with_details(
            text,
            source_language,
            target_language
        )

        translated_text = result["translated_text"]

        save_translation(
            text,
            translated_text,
            result["source_language"],
            result["target_language"],
            session["user_id"]
        )

        return jsonify({
            "status": "success",
            "translated_text": translated_text,
            "detected_language": result["detected_language"],
            "detected_language_code": result["detected_language_code"],
            "source_language": result["source_language"],
            "target_language": result["target_language"],
            "message": "Translation completed successfully."
        }), 200

    except ValueError as error:

        return jsonify({"error": str(error)}), 400

    except RuntimeError as error:

        return jsonify({"error": str(error)}), 502

    except Exception:

        app.logger.exception("Translation processing failed")

        return jsonify({
            "error": "An internal server error occurred."
        }), 500


# ==========================================
# 11. GET USER HISTORY
# ==========================================

@app.route("/history", methods=["GET"])
@login_required
def history():

    try:

        records = get_translation_history(
            session["user_id"]
        )

        return jsonify({
            "status": "success",
            "total_records": len(records),
            "history": records
        }), 200

    except Exception:

        app.logger.exception("History retrieval failed")

        return jsonify({
            "error": "Unable to retrieve translation history."
        }), 500


# ==========================================
# 12. DELETE USER HISTORY
# ==========================================

@app.route("/history/delete", methods=["POST"])
@login_required
def delete_history():

    try:

        delete_all_history(session["user_id"])

        return jsonify({
            "status": "success",
            "message": "Your translation history was deleted successfully."
        }), 200

    except Exception:

        app.logger.exception("History deletion failed")

        return jsonify({
            "error": "Unable to delete translation history."
        }), 500


# ==========================================
# 13. RUN APPLICATION
# ==========================================

if __name__ == "__main__":

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )
