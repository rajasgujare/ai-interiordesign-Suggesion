from datetime import datetime


class Design:

    def __init__(self, user_id, prompt, style, room_type, original_image, generated_image):
        self.user_id = user_id
        self.prompt = prompt
        self.style = style
        self.room_type = room_type
        self.original_image = original_image
        self.generated_image = generated_image
        self.created_at = datetime.now()
        self.status = "completed"

    def to_dict(self):
        return {
            "user_id": self.user_id,
            "prompt": self.prompt,
            "style": self.style,
            "room_type": self.room_type,
            "original_image": self.original_image,
            "generated_image": self.generated_image,
            "created_at": self.created_at,
            "status": self.status
        }