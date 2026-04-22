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
        self.SetProps(
            Caption="AI Interior Design - Login",
            Width=500,
            Height=650
        )

        # ── Status Label (very bottom) ──
        self.status_label = Label(self)
        self.status_label.SetProps(
            Parent=self,
            Align="Bottom",
            Height=35,
            Text=""
        )

        # ── Buttons ──
        self.layout_buttons = Layout(self)
        self.layout_buttons.SetProps(
            Parent=self,
            Align="Bottom",
            Height=52
        )

        self.login_button = Button(self)
        self.login_button.SetProps(
            Parent=self.layout_buttons,
            Align="Left",
            Width=235,
            Text="Login",
            OnClick=self.do_login
        )

        self.register_button = Button(self)
        self.register_button.SetProps(
            Parent=self.layout_buttons,
            Align="Client",
            Text="Register",
            OnClick=self.do_register
        )

        # ── Password Field ──
        self.pass_edit = Edit(self)
        self.pass_edit.SetProps(
            Parent=self,
            Align="Bottom",
            Height=42,
            Password=True
        )

        self.pass_label = Label(self)
        self.pass_label.SetProps(
            Parent=self,
            Align="Bottom",
            Height=28,
            Text="  Password"
        )

        # ── Spacer ──
        self.sp2 = Panel(self)
        self.sp2.SetProps(Parent=self, Align="Bottom", Height=6)

        # ── Email Field ──
        self.email_edit = Edit(self)
        self.email_edit.SetProps(
            Parent=self,
            Align="Bottom",
            Height=42
        )

        self.email_label = Label(self)
        self.email_label.SetProps(
            Parent=self,
            Align="Bottom",
            Height=28,
            Text="  Email Address"
        )

        # ── Spacer ──
        self.sp1 = Panel(self)
        self.sp1.SetProps(Parent=self, Align="Bottom", Height=6)

        # ── Full Name Field ──
        self.name_edit = Edit(self)
        self.name_edit.SetProps(
            Parent=self,
            Align="Bottom",
            Height=42
        )

        self.name_label = Label(self)
        self.name_label.SetProps(
            Parent=self,
            Align="Bottom",
            Height=28,
            Text="  Full Name"
        )

        # ── Divider ──
        self.divider = Panel(self)
        self.divider.SetProps(
            Parent=self,
            Align="Bottom",
            Height=12
        )

        # ── TOP BANNER fills remaining space ──
        self.top_banner = Panel(self)
        self.top_banner.SetProps(
            Parent=self,
            Align="Client"
        )

        # ── Subtitle on top of image ──
        self.subtitle_label = Label(self)
        self.subtitle_label.SetProps(
            Parent=self.top_banner,
            Align="Bottom",
            Height=38,
            Text="  Transform your empty room into a dream space"
        )

        # ── Title on top of image ──
        self.title_label = Label(self)
        self.title_label.SetProps(
            Parent=self.top_banner,
            Align="Bottom",
            Height=50,
            Text="  Welcome to AI Interior Design App"
        )

        # ── Background image fills entire banner ──
        self.banner_image = ImageControl(self)
        self.banner_image.SetProps(
            Parent=self.top_banner,
            Align="Client"
        )

        # ── Load banner image ──
        try:
            banner_path = os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                "banner.jpg"
            )
            if os.path.exists(banner_path):
                self.banner_image.LoadFromFile(banner_path)
                print("Banner loaded successfully!")
            else:
                print(f"Banner not found at: {banner_path}")
        except Exception as e:
            print(f"Banner error: {e}")

    def do_login(self, sender):
        try:
            email = self.email_edit.Text.strip()
            password = self.pass_edit.Text.strip()

            if not email or not password:
                self.status_label.Text = "  Please enter email and password"
                return

            self.status_label.Text = "  Logging in please wait..."
            Application.ProcessMessages()

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
                self.status_label.Text = f"  Error: {data.get('error', 'Login failed')}"

        except requests.exceptions.ConnectionError:
            self.status_label.Text = "  Cannot connect to server. Is backend running?"
        except Exception as e:
            self.status_label.Text = f"  Error: {str(e)}"

    def do_register(self, sender):
        try:
            name = self.name_edit.Text.strip()
            email = self.email_edit.Text.strip()
            password = self.pass_edit.Text.strip()

            if not name or not email or not password:
                self.status_label.Text = "  Please fill all fields"
                return

            self.status_label.Text = "  Registering please wait..."
            Application.ProcessMessages()

            response = requests.post(
                f"{BASE_URL}/register",
                json={"name": name, "email": email, "password": password},
                timeout=10
            )
            data = response.json()

            if response.status_code == 201:
                self.status_label.Text = "  Registered successfully! Please login now"
            else:
                self.status_label.Text = f"  Error: {data.get('error', 'Registration failed')}"

        except requests.exceptions.ConnectionError:
            self.status_label.Text = "  Cannot connect to server. Is backend running?"
        except Exception as e:
            self.status_label.Text = f"  Error: {str(e)}"


class MainForm(Form):

    def __init__(self, owner):
        self.selected_file_path = None
        self.generated_image_path = None

        self.SetProps(
            Caption=f"AI Interior Design  -  Welcome {current_user_name}!",
            Width=1150,
            Height=740
        )

        # ── Status Bar ──
        self.status_bar = Label(self)
        self.status_bar.SetProps(
            Parent=self,
            Align="Bottom",
            Height=34,
            Text="   Ready  -  Select style, room type and upload image to get started!"
        )

        # ── Top Navigation Bar ──
        self.layout_top = Layout(self)
        self.layout_top.SetProps(
            Parent=self,
            Align="Top",
            Height=58
        )

        self.app_title = Label(self)
        self.app_title.SetProps(
            Parent=self.layout_top,
            Align="Client",
            Text=f"   AI Interior Design   |   Welcome, {current_user_name}!"
        )

        self.logout_button = Button(self)
        self.logout_button.SetProps(
            Parent=self.layout_top,
            Align="Right",
            Width=115,
            Text="Logout",
            OnClick=self.do_logout
        )

        self.history_button = Button(self)
        self.history_button.SetProps(
            Parent=self.layout_top,
            Align="Right",
            Width=145,
            Text="My Designs",
            OnClick=self.show_history
        )

        # ── Left Control Panel ──
        self.layout_left = Layout(self)
        self.layout_left.SetProps(
            Parent=self,
            Align="Left",
            Width=345
        )

        # Original Image fills remaining left space
        self.img_original = ImageControl(self)
        self.img_original.SetProps(
            Parent=self.layout_left,
            Align="Client"
        )

        # Added in reverse order for correct display
        self.orig_label = Label(self)
        self.orig_label.SetProps(
            Parent=self.layout_left,
            Align="Bottom",
            Height=30,
            Text="   Original Room Image:"
        )

        self.sp5 = Panel(self)
        self.sp5.SetProps(Parent=self.layout_left, Align="Bottom", Height=8)

        self.generate_button = Button(self)
        self.generate_button.SetProps(
            Parent=self.layout_left,
            Align="Bottom",
            Height=52,
            Text="Generate AI Design",
            OnClick=self.generate_design
        )

        self.sp4 = Panel(self)
        self.sp4.SetProps(Parent=self.layout_left, Align="Bottom", Height=6)

        self.upload_button = Button(self)
        self.upload_button.SetProps(
            Parent=self.layout_left,
            Align="Bottom",
            Height=46,
            Text="Select Room Image",
            OnClick=self.upload_image
        )

        self.sp3 = Panel(self)
        self.sp3.SetProps(Parent=self.layout_left, Align="Bottom", Height=6)

        self.prompt_memo = Memo(self)
        self.prompt_memo.SetProps(
            Parent=self.layout_left,
            Align="Bottom",
            Height=80,
            Text="Cozy living room with warm lighting and wooden floors"
        )

        self.prompt_label = Label(self)
        self.prompt_label.SetProps(
            Parent=self.layout_left,
            Align="Bottom",
            Height=28,
            Text="   Custom Prompt:"
        )

        self.sp2 = Panel(self)
        self.sp2.SetProps(Parent=self.layout_left, Align="Bottom", Height=6)

        self.style_combo = ComboBox(self)
        self.style_combo.SetProps(
            Parent=self.layout_left,
            Align="Bottom",
            Height=38
        )
        for style in ["Modern", "Classic", "Vintage", "Luxury",
                      "Scandinavian", "Bohemian", "Industrial", "Japanese"]:
            self.style_combo.Items.Add(style)
        self.style_combo.ItemIndex = 0

        self.style_label = Label(self)
        self.style_label.SetProps(
            Parent=self.layout_left,
            Align="Bottom",
            Height=28,
            Text="   Design Style:"
        )

        self.sp1 = Panel(self)
        self.sp1.SetProps(Parent=self.layout_left, Align="Bottom", Height=6)

        self.room_combo = ComboBox(self)
        self.room_combo.SetProps(
            Parent=self.layout_left,
            Align="Bottom",
            Height=38
        )
        for room in ["Living Room", "Bedroom", "Kitchen",
                     "Bathroom", "Dining Room", "Home Office",
                     "Kids Room", "Balcony"]:
            self.room_combo.Items.Add(room)
        self.room_combo.ItemIndex = 0

        self.room_label = Label(self)
        self.room_label.SetProps(
            Parent=self.layout_left,
            Align="Bottom",
            Height=28,
            Text="   Room Type:"
        )

        # ── Right Panel ──
        self.result_layout = Layout(self)
        self.result_layout.SetProps(
            Parent=self,
            Align="Top",
            Height=48
        )

        self.result_label = Label(self)
        self.result_label.SetProps(
            Parent=self.result_layout,
            Align="Client",
            Text="   AI Generated Interior Design Result:"
        )

        self.download_button = Button(self)
        self.download_button.SetProps(
            Parent=self.result_layout,
            Align="Right",
            Width=175,
            Text="Download Image",
            OnClick=self.download_image
        )

        self.img_result = ImageControl(self)
        self.img_result.SetProps(
            Parent=self,
            Align="Client"
        )

    def upload_image(self, sender):
        dialog = OpenDialog(self)
        dialog.Filter = "Images|*.png;*.jpg;*.jpeg"
        if dialog.Execute():
            self.selected_file_path = dialog.FileName
            self.img_original.LoadFromFile(self.selected_file_path)
            self.status_bar.Text = "   Image loaded! Click Generate AI Design!"

    def generate_design(self, sender):
        if not self.selected_file_path:
            self.status_bar.Text = "   Please select a room image first!"
            return

        try:
            prompt = self.prompt_memo.Text.strip()
            style = self.style_combo.Items.Strings[self.style_combo.ItemIndex]
            room_type = self.room_combo.Items.Strings[self.room_combo.ItemIndex]

            if not prompt:
                prompt = "Beautiful interior design with modern furniture"

            self.status_bar.Text = "   AI is generating your dream interior, please wait..."
            self.generate_button.Enabled = False
            self.upload_button.Enabled = False
            Application.ProcessMessages()

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

            data = response.json()

            if response.status_code == 200:
                image_path = data.get("image_path")
                self.generated_image_path = image_path
                self.img_result.LoadFromFile(image_path)
                self.status_bar.Text = "   Design generated! Click Download Image to save!"
            else:
                self.status_bar.Text = f"   Error: {data.get('error', 'Unknown error')}"

        except requests.exceptions.Timeout:
            self.status_bar.Text = "   Request timed out. Please try again."
        except requests.exceptions.ConnectionError:
            self.status_bar.Text = "   Cannot connect to backend server!"
        except Exception as e:
            self.status_bar.Text = f"   Error: {str(e)}"
        finally:
            self.generate_button.Enabled = True
            self.upload_button.Enabled = True
            Application.ProcessMessages()

    def download_image(self, sender):
        try:
            if not self.generated_image_path:
                self.status_bar.Text = "   No image generated yet!"
                return

            dialog = SaveDialog(self)
            dialog.Filter = "PNG Image|*.png"
            dialog.FileName = "my_interior_design.png"

            if dialog.Execute():
                save_path = dialog.FileName
                shutil.copy2(self.generated_image_path, save_path)
                self.status_bar.Text = "   Image downloaded successfully!"

        except Exception as e:
            self.status_bar.Text = f"   Download error: {str(e)}"

    def show_history(self, sender):
        try:
            response = requests.get(
                f"{BASE_URL}/designs/{current_user_id}",
                timeout=10
            )
            data = response.json()
            designs = data.get("designs", [])

            if not designs:
                self.status_bar.Text = "   No designs found in history yet!"
                return

            self.status_bar.Text = f"   Found {len(designs)} designs in your history!"
            print(f"\n{'='*60}")
            print(f"  YOUR DESIGN HISTORY  ({len(designs)} total)")
            print(f"{'='*60}")
            for i, design in enumerate(designs[-5:], 1):
                print(f"  {i}. Style: {design['style']} | Room: {design['room_type']}")
                print(f"     Prompt: {design['prompt'][:60]}...")
                print(f"     Date: {design['created_at'][:10]}")
                print()

        except Exception as e:
            self.status_bar.Text = f"   Error: {str(e)}"

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