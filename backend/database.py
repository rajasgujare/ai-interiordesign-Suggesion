import os
import certifi
from datetime import datetime
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

# Connect to MongoDB with certifi
client = MongoClient(
    os.environ.get("MONGODB_URI"),
    tlsCAFile=certifi.where()
)

db = client["interior_design"]

# Collections
users_collection = db["users"]
designs_collection = db["designs"]
styles_collection = db["styles"]


def save_user(name, email, password):
    """Save a new user to the database."""
    user = {
        "name": name,
        "email": email,
        "password": password,
        "created_at": datetime.now(),
        "total_designs": 0
    }
    result = users_collection.insert_one(user)
    return str(result.inserted_id)


def get_user_by_email(email):
    """Find a user by email."""
    return users_collection.find_one({"email": email})


def save_design(user_id, prompt, style, room_type, original_image, generated_image):
    """Save a generated design to the database."""
    design = {
        "user_id": user_id,
        "prompt": prompt,
        "style": style,
        "room_type": room_type,
        "original_image": original_image,
        "generated_image": generated_image,
        "created_at": datetime.now(),
        "status": "completed"
    }
    result = designs_collection.insert_one(design)

    # Update user total designs count
    users_collection.update_one(
        {"_id": user_id},
        {"$inc": {"total_designs": 1}}
    )

    return str(result.inserted_id)


def get_user_designs(user_id):
    """Get all designs for a specific user."""
    return list(designs_collection.find({"user_id": user_id}))


def save_style(name, description, prompt_keywords, preview_image):
    """Save a design style to the database."""
    style = {
        "name": name,
        "description": description,
        "prompt_keywords": prompt_keywords,
        "preview_image": preview_image
    }
    result = styles_collection.insert_one(style)
    return str(result.inserted_id)


def get_all_styles():
    """Get all available design styles."""
    return list(styles_collection.find())


def initialize_styles():
    """Initialize default styles if not already in database."""
    if styles_collection.count_documents({}) == 0:
        default_styles = [
            {
                "name": "Modern",
                "description": "Clean lines, neutral colors",
                "prompt_keywords": "modern minimalist clean neutral colors",
                "preview_image": ""
            },
            {
                "name": "Classic",
                "description": "Elegant, symmetrical, traditional",
                "prompt_keywords": "classic elegant traditional symmetrical",
                "preview_image": ""
            },
            {
                "name": "Vintage",
                "description": "Retro furniture, warm tones",
                "prompt_keywords": "vintage retro warm antique furniture",
                "preview_image": ""
            },
            {
                "name": "Luxury",
                "description": "Gold accents, marble, velvet",
                "prompt_keywords": "luxury gold marble velvet expensive",
                "preview_image": ""
            },
            {
                "name": "Scandinavian",
                "description": "Minimalist, natural wood, white",
                "prompt_keywords": "scandinavian minimalist wood white cozy",
                "preview_image": ""
            },
            {
                "name": "Bohemian",
                "description": "Colorful, eclectic, artistic",
                "prompt_keywords": "bohemian colorful eclectic artistic",
                "preview_image": ""
            },
            {
                "name": "Industrial",
                "description": "Exposed brick, metal, raw wood",
                "prompt_keywords": "industrial brick metal raw wood urban",
                "preview_image": ""
            },
            {
                "name": "Japanese",
                "description": "Zen, minimal, natural materials",
                "prompt_keywords": "japanese zen minimal natural peaceful",
                "preview_image": ""
            }
        ]
        styles_collection.insert_many(default_styles)
        print("✅ Default styles initialized in database!")


def test_connection():
    """Test MongoDB connection."""
    try:
        client.admin.command("ping")
        print("✅ MongoDB Connected Successfully!")
        return True
    except Exception as e:
        print(f"❌ MongoDB Connection Failed: {e}")
        return False


# Initialize when file runs
if __name__ == "__main__":
    test_connection()
    initialize_styles()