import os
import shutil
import requests
from dotenv import load_dotenv
from delphifmx import *

load_dotenv()

BASE_URL = "http://127.0.0.1:5000"
current_user_id = None
current_user_name = None


class LoginForm(Form):

    def __init__(self, owner):
        self.SetProps(Caption="AI Interior Design - Login", Width=400, Height=380)

        self.title_label = Label(self)
        self.title_label.SetProps(Parent=self, Align="Top", Height=50, Text="AI Interior Design")

        self.layout_main = Layout(self)
        self.layout_main.SetProps(Parent=self, Align="Client")

        # Status label added LAST in code = appears at BOTTOM visually
        self.status_label = Label(self)
        self.status_label.SetProps(Parent=self.layout_main, Align="Top", Height=30, Text="")

        # Email field
        self.email_edit = Edit(self)
        self.email_edit.SetProps(Parent=self.layout_main, Align="Top", Height=35)

        self.email_label = Label(self)
        self.email_label.SetProps(Parent=self.layout_main, Align="Top", Height=25, Text="  Email:")

        # Password field (masked)
        self.pass_edit = Edit(self)
        self.pass_edit.SetProps(Parent=self.layout_main, Align="Top", Height=35, Password=True)

        self.pass_label = Label(self)
        self.pass_label.SetProps(Parent=self.layout_main, Align="Top", Height=25, Text="  Password:")

        # Login / Register buttons
        self.layout_buttons = Layout(self)
        self.layout_buttons.SetProps(Parent=self.layout_main, Align="Top", Height=45)

        self.login_button = Button(self)
        self.login_button.SetProps(Parent=self.layout_buttons, Align="Left", Width=180,
                                   Text="Login", OnClick=self.do_login)

        self.register_button = Button(self)
        self.register_button.SetProps(Parent=self.layout_buttons, Align="Client",
                                      Text="Register", OnClick=self.do_register)

        # Full Name field — plain text, NO Password=True
        self.name_edit = Edit(self)
        self.name_edit.SetProps(Parent=self.layout_main, Align="Top", Height=35)

        self.name_label = Label(self)
        self.name_label.SetProps(Parent=self.layout_main, Align="Top", Height=25, Text="  Full Name:")

    def do_login(self, sender):
        try:
            email = self.email_edit.Text.strip()
            password = self.pass_edit.Text.strip()

            if not email or not password:
                self.status_label.Text = "Please enter email and password"
                return

            response = requests.post(
                f"{BASE_URL}/login",
                json={"email": email, "password": password},
                timeout=10
            )
            data = response.json()

            if response.status_code == 200:
                global current_user_id, current_user_name
                current_user_id = data["user_id"]
                current_user_name = data["name"]

                main_form = MainForm(Application)
                Application.MainForm = main_form
                main_form.Show()
                self.Close()
            else:
                self.status_label.Text = f"Error: {data.get('error', 'Login failed')}"

        except Exception as e:
            self.status_label.Text = f"Error: {str(e)}"

    def do_register(self, sender):
        try:
            name = self.name_edit.Text.strip()
            email = self.email_edit.Text.strip()
            password = self.pass_edit.Text.strip()

            if not name or not email or not password:
                self.status_label.Text = "Please fill all fields"
                return

            response = requests.post(
                f"{BASE_URL}/register",
                json={"name": name, "email": email, "password": password},
                timeout=10
            )
            data = response.json()

            if response.status_code == 201:
                self.status_label.Text = "Registered! Please login now"
            else:
                self.status_label.Text = f"Error: {data.get('error', 'Registration failed')}"

        except Exception as e:
            self.status_label.Text = f"Error: {str(e)}"


class MainForm(Form):

    def __init__(self, owner):
        self.selected_file_path = None
        self.generated_image_path = None
        self.SetProps(Caption="AI Interior Design", Width=950, Height=650)

        # ── Top Bar ──
        self.layout_top = Layout(self)
        self.layout_top.SetProps(Parent=self, Align="Top", Height=50)

        self.app_title = Label(self)
        self.app_title.SetProps(Parent=self.layout_top, Align="Client", Text="  AI Powered Interior Design")

        self.history_button = Button(self)
        self.history_button.SetProps(Parent=self.layout_top, Align="Right", Width=130, Text="My Designs", OnClick=self.show_history)

        self.logout_button = Button(self)
        self.logout_button.SetProps(Parent=self.layout_top, Align="Right", Width=100, Text="Logout", OnClick=self.do_logout)

        # ── Left Panel ──
        self.layout_left = Layout(self)
        self.layout_left.SetProps(Parent=self, Align="Left", Width=320)

        self.room_label = Label(self)
        self.room_label.SetProps(Parent=self.layout_left, Align="Top", Height=25, Text="  Select Room Type:")

        self.room_combo = ComboBox(self)
        self.room_combo.SetProps(Parent=self.layout_left, Align="Top", Height=35)
        for room in ["Living Room", "Bedroom", "Kitchen", "Bathroom", "Dining Room", "Home Office", "Kids Room", "Balcony"]:
            self.room_combo.Items.Add(room)
        self.room_combo.ItemIndex = 0

        self.style_label = Label(self)
        self.style_label.SetProps(Parent=self.layout_left, Align="Top", Height=25, Text="  Select Design Style:")

        self.style_combo = ComboBox(self)
        self.style_combo.SetProps(Parent=self.layout_left, Align="Top", Height=35)
        for style in ["Modern", "Classic", "Vintage", "Luxury", "Scandinavian", "Bohemian", "Industrial", "Japanese"]:
            self.style_combo.Items.Add(style)
        self.style_combo.ItemIndex = 0

        self.prompt_label = Label(self)
        self.prompt_label.SetProps(Parent=self.layout_left, Align="Top", Height=25, Text="  Custom Prompt:")

        self.prompt_memo = Memo(self)
        self.prompt_memo.SetProps(Parent=self.layout_left, Align="Top", Height=80, Text="Cozy living room with warm lighting")

        self.upload_button = Button(self)
        self.upload_button.SetProps(Parent=self.layout_left, Align="Top", Height=40, Text="Select Room Image", OnClick=self.upload_image)

        self.generate_button = Button(self)
        self.generate_button.SetProps(Parent=self.layout_left, Align="Top", Height=45, Text="Generate Design", OnClick=self.generate_design)

        self.orig_label = Label(self)
        self.orig_label.SetProps(Parent=self.layout_left, Align="Top", Height=25, Text="  Original Image:")

        self.img_original = ImageControl(self)
        self.img_original.SetProps(Parent=self.layout_left, Align="Client")

        # ── Right Panel ──
        self.result_layout = Layout(self)
        self.result_layout.SetProps(Parent=self, Align="Top", Height=40)

        self.result_label = Label(self)
        self.result_label.SetProps(Parent=self.result_layout, Align="Client", Text="  Generated Design:")

        self.download_button = Button(self)
        self.download_button.SetProps(
            Parent=self.result_layout,
            Align="Right",
            Width=150,
            Text="Download Image",
            OnClick=self.download_image
        )

        self.img_result = ImageControl(self)
        self.img_result.SetProps(Parent=self, Align="Client")

        # ── Status Bar ──
        self.status_bar = Label(self)
        self.status_bar.SetProps(Parent=self, Align="Bottom", Height=30, Text="Status: Ready")

    def upload_image(self, sender):
        dialog = OpenDialog(self)
        dialog.Filter = "Images|*.png;*.jpg;*.jpeg"
        if dialog.Execute():
            self.selected_file_path = dialog.FileName
            self.img_original.LoadFromFile(self.selected_file_path)
            self.status_bar.Text = "Status: Image loaded. Click Generate Design!"

    def generate_design(self, sender):
        if not self.selected_file_path:
            self.status_bar.Text = "Status: Please select a room image first!"
            return

        try:
            prompt = self.prompt_memo.Text.strip()
            style = self.style_combo.Items.Strings[self.style_combo.ItemIndex]
            room_type = self.room_combo.Items.Strings[self.room_combo.ItemIndex]

            if not prompt:
                prompt = "Beautiful interior design"

            self.status_bar.Text = "Status: Generating design please wait..."
            Application.ProcessMessages()

            print(f"Calling /generate with prompt={prompt} style={style} room={room_type}")

            response = requests.post(
                "http://127.0.0.1:5000/generate",
                json={
                    "user_id": current_user_id,
                    "prompt": prompt,
                    "style": style,
                    "room_type": room_type,
                    "original_image": self.selected_file_path
                },
                timeout=300
            )

            print(f"Got response: {response.status_code}")
            data = response.json()

            if response.status_code == 200:
                image_path = data.get("image_path")
                self.generated_image_path = image_path
                self.img_result.LoadFromFile(image_path)
                self.status_bar.Text = "Status: Design generated! Click Download to save image!"
            else:
                self.status_bar.Text = f"Status: Error - {data.get('error')}"

        except requests.exceptions.Timeout:
            self.status_bar.Text = "Status: Timed out. Please try again."

        except requests.exceptions.ConnectionError:
            self.status_bar.Text = "Status: Cannot connect to backend!"

        except Exception as e:
            self.status_bar.Text = f"Status: Error - {str(e)}"

    def download_image(self, sender):
        try:
            if not self.generated_image_path:
                self.status_bar.Text = "Status: No image generated yet!"
                return

            dialog = SaveDialog(self)
            dialog.Filter = "PNG Image|*.png"
            dialog.FileName = "my_interior_design.png"

            if dialog.Execute():
                save_path = dialog.FileName
                shutil.copy2(self.generated_image_path, save_path)
                self.status_bar.Text = f"Status: Image downloaded successfully!"
                print(f"✅ Image saved to: {save_path}")

        except Exception as e:
            self.status_bar.Text = f"Status: Download error - {str(e)}"
            print(f"Download error: {e}")

    def show_history(self, sender):
        try:
            response = requests.get(f"{BASE_URL}/designs/{current_user_id}", timeout=10)
            data = response.json()
            designs = data.get("designs", [])
            self.status_bar.Text = f"Status: Found {len(designs)} designs in history"
        except Exception as e:
            self.status_bar.Text = f"Status: Error - {str(e)}"

    def do_logout(self, sender):
        global current_user_id, current_user_name
        current_user_id = None
        current_user_name = None
        login_form = LoginForm(Application)
        Application.MainForm = login_form
        login_form.Show()
        self.Close()


def main():
    Application.Initialize()
    Application.Title = "AI Interior Design"
    form = LoginForm(Application)
    Application.MainForm = form
    form.Show()
    Application.Run()


if __name__ == "__main__":
    main()