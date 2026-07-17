import os
import time
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from image_generator import generate_image
from database import (
    save_user,
    get_user_by_email,
    save_design,
    get_user_designs,
    initialize_styles,
    get_all_styles,
    test_connection
)

load_dotenv()

app = Flask(__name__)
CORS(app)

test_connection()
initialize_styles()


# ─────────────────────────────────────────
# HEALTH CHECK
# ─────────────────────────────────────────

@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({
        "status": "Server is running",
        "database": "Connected"
    }), 200


# ─────────────────────────────────────────
# USER ROUTES
# ─────────────────────────────────────────

@app.route("/register", methods=["POST"])
def register():
    try:
        data = request.json
        name = data.get("name")
        email = data.get("email")
        password = data.get("password")

        if not name or not email or not password:
            return jsonify({"error": "All fields are required"}), 400

        existing_user = get_user_by_email(email)
        if existing_user:
            return jsonify({"error": "Email already registered"}), 400

        user_id = save_user(name, email, password)
        return jsonify({
            "message": "User registered successfully",
            "user_id": user_id
        }), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/login", methods=["POST"])
def login():
    try:
        data = request.json
        email = data.get("email")
        password = data.get("password")

        if not email or not password:
            return jsonify({"error": "Email and password are required"}), 400

        user = get_user_by_email(email)

        if not user or user["password"] != password:
            return jsonify({"error": "Invalid email or password"}), 401

        return jsonify({
            "message": "Login successful",
            "user_id": str(user["_id"]),
            "name": user["name"]
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ─────────────────────────────────────────
# GENERATE ROUTE
# ─────────────────────────────────────────

@app.route("/generate", methods=["POST"])
def generate():
    try:
        print("🔥 Generate route called!")

        data = request.json
        print(f"📦 Data received: {data}")

        user_id = data.get("user_id")
        prompt = data.get("prompt")
        style = data.get("style", "Modern")
        room_type = data.get("room_type", "Living Room")
        original_image = data.get("original_image", "")

        # ✅ Debug image path
        print(f"📸 Original image path: {original_image}")
        print(f"📸 Image exists: {os.path.exists(original_image) if original_image else False}")

        if not prompt:
            return jsonify({"error": "Prompt is required"}), 400

        print(f"🎨 Generating: {prompt} | Style: {style} | Room: {room_type}")

        # ✅ Pass image path correctly
        image_path, error = generate_image(
            user_prompt=prompt,
            style=style,
            room_type=room_type,
            image_path=original_image if original_image else None
        )

        if error:
            print(f"❌ Generation error: {error}")
            return jsonify({"error": error}), 500

        print(f"✅ Image generated: {image_path}")

        if user_id:
            save_design(
                user_id=user_id,
                prompt=prompt,
                style=style,
                room_type=room_type,
                original_image=original_image,
                generated_image=os.path.basename(image_path)
            )
            print("✅ Design saved to MongoDB!")

        return jsonify({
            "message": "Design generated successfully",
            "image_path": image_path,
            "image_filename": os.path.basename(image_path)
        }), 200

    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return jsonify({"error": str(e)}), 500


# ─────────────────────────────────────────
# DESIGNS ROUTE
# ─────────────────────────────────────────

@app.route("/designs/<user_id>", methods=["GET"])
def get_designs(user_id):
    try:
        designs = get_user_designs(user_id)

        for design in designs:
            design["_id"] = str(design["_id"])
            design["created_at"] = str(design["created_at"])

        return jsonify({
            "designs": designs,
            "total": len(designs)
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ─────────────────────────────────────────
# STYLES ROUTE
# ─────────────────────────────────────────

@app.route("/styles", methods=["GET"])
def get_styles():
    try:
        styles = get_all_styles()

        for style in styles:
            style["_id"] = str(style["_id"])

        return jsonify({
            "styles": styles,
            "total": len(styles)
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, host="0.0.0.0", port=port)