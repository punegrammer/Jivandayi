from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window 
from kivy.utils import get_color_from_hex
from kivy.metrics import dp
from kivy.uix.image import Image
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Set screen size
Window.size = (360, 640)
Window.clearcolor = (0.678, 0.847, 0.902, 1)

# Google Sheets Setup
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("creds.json", scope)
client = gspread.authorize(creds)
sheet = client.open_by_url("https://docs.google.com/spreadsheets/d/1IgyYH6SZnmAnj4gIZ6YI5iS2fozE7gX4FQ5gWpYPbzs/edit#gid=1893301728")
login_sheet = sheet.worksheet("Login")
driver_sheet = sheet.worksheet("Driver Details")
rent_sheet = sheet.worksheet("Rent")
maintance_sheet = sheet.worksheet("Maintance Report")


class LoginScreen(Screen):
    def __init__(self, **kwargs):
        super(LoginScreen, self).__init__(**kwargs)
        self.build_ui()

    def build_ui(self):
        self.clear_widgets()
        layout = BoxLayout(orientation='vertical', padding=dp(30), spacing=dp(20))

        layout.add_widget(Image(source='amb_logo.png'))
        layout.add_widget(Label(text="JEEVANDAYI \n AMBULANCE", font_size=50, bold=True, color=get_color_from_hex("#0077cc")))
        layout.add_widget(Label(text="\nMr.Santosh Dagadu Lonari \n                   Owner", font_size=30, bold=True, color=get_color_from_hex("#040a0e")))
        layout.add_widget(Label(text="Login", font_size=25, color=get_color_from_hex("#0077cc")))

        self.login_id = TextInput(hint_text="Login ID", multiline=False, size_hint_y=None, height=40)
        self.password = TextInput(hint_text="Password", password=True, multiline=False, size_hint_y=None, height=40)
        layout.add_widget(self.login_id)
        layout.add_widget(self.password)

        login_btn = Button(text="Login", size_hint_y=None, height=45, background_color=get_color_from_hex("#2196F3"), background_normal='')
        login_btn.bind(on_press=self.verify_login)
        layout.add_widget(login_btn)

        self.error_label = Label(text="", color=(1, 0, 0, 1))
        layout.add_widget(self.error_label)

        self.add_widget(layout)

    def verify_login(self, instance):
        entered_login = self.login_id.text.strip()
        entered_password = self.password.text.strip()
        data = login_sheet.get_all_records()
        for row in data:
            if str(row['Login ID']) == entered_login and str(row['Password']) == entered_password:
                App.get_running_app().driver_name = row['Driver Name']
                self.manager.current = "dashboard"
                return
        self.error_label.text = "❌ Invalid login or password"


class DashboardScreen(Screen):
    def __init__(self, **kwargs):
        super(DashboardScreen, self).__init__(**kwargs)
        self.build_ui()

    def build_ui(self):
        self.clear_widgets()
        layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(15))
        layout.add_widget(Image(source='amb_logo.png'))

        self.welcome = Label(text="Welcome!", font_size=50, bold=True, color=get_color_from_hex("#0c0c0c"))
        layout.add_widget(self.welcome)

        btn_style = {"size_hint_y": None, "height": 50, "background_color": get_color_from_hex("#4CAF50"), "background_normal": ""}

        btn1 = Button(text="🚑 Rent Form", **btn_style)
        btn1.bind(on_press=lambda x: setattr(self.manager, 'current', 'rent'))
        layout.add_widget(btn1)
        
        btn2 = Button(text="🛠 Maintenance Report", **btn_style)
        btn2.bind(on_press=lambda x: setattr(self.manager, 'current', 'maintenance'))
        layout.add_widget(btn2)

        btn3 = Button(text="🧑‍✈️ Driver Details", **btn_style)
        btn3.bind(on_press=lambda x: setattr(self.manager, 'current', 'driver'))
        layout.add_widget(btn3)

        logout_btn = Button(text="🔒 Logout", size_hint_y=None, height=45, background_color=get_color_from_hex("#f44336"), background_normal='')
        logout_btn.bind(on_press=self.logout)
        layout.add_widget(logout_btn)

        self.add_widget(layout)

    def on_enter(self):
        self.welcome.text = f"Welcome , {App.get_running_app().driver_name}!"

    def logout(self, instance):
        App.get_running_app().driver_name = ""
        self.manager.current = "login"


class RentScreen(Screen):
    def __init__(self, **kwargs):
        super(RentScreen, self).__init__(**kwargs)
        self.build_ui()

    def build_ui(self):
        self.clear_widgets()
        main_layout = BoxLayout(orientation='vertical', spacing=10)
        main_layout.add_widget(Button(text="← Back", size_hint_y=None, height=40,
                                      background_color=get_color_from_hex("#f44336"), background_normal='',
                                      on_press=lambda x: setattr(self.manager, 'current', 'dashboard')))

        scroll = ScrollView()
        form_layout = GridLayout(cols=2, size_hint_y=None, spacing=10, padding=20)
        form_layout.bind(minimum_height=form_layout.setter('height'))

        fields = ["Date", "Patient Name", "Relatives Name", "Address", "Ambulance Number", "Driver Name",
                  "Form", "To", "Start K/M", "End KM", "Other Charges ICE",
                  "Total Rent", "Balance", "Paid Types"]

        today = datetime.now().strftime("%d-%m-%Y")
        self.inputs = {}
        for field in fields:
            form_layout.add_widget(Label(text=field, color=get_color_from_hex("#0c0c0c")))
            ti = TextInput(multiline=False, size_hint_y=None, height=40)
            if field.lower() == "date":
                ti.text = today
            form_layout.add_widget(ti)
            self.inputs[field] = ti

        submit_btn = Button(text="Submit", size_hint_y=None, height=50,
                            background_color=get_color_from_hex("#03A9F4"), background_normal='')
        submit_btn.bind(on_press=self.submit_rent)
        form_layout.add_widget(submit_btn)
        form_layout.add_widget(Label())

        scroll.add_widget(form_layout)
        main_layout.add_widget(scroll)
        self.add_widget(main_layout)

    def submit_rent(self, instance):
        rent_data = {field: self.inputs[field].text for field in self.inputs}
        rent_sheet.append_row(list(rent_data.values()))
        print("Rent form submitted")


class MaintenanceScreen(Screen):
    def __init__(self, **kwargs):
        super(MaintenanceScreen, self).__init__(**kwargs)
        self.build_ui()

    def build_ui(self):
        self.clear_widgets()
        main_layout = BoxLayout(orientation='vertical', spacing=10)
        main_layout.add_widget(Button(text="← Back", size_hint_y=None, height=40,
                                      background_color=get_color_from_hex("#f44336"), background_normal='',
                                      on_press=lambda x: setattr(self.manager, 'current', 'dashboard')))

        scroll = ScrollView()
        layout = GridLayout(cols=2, spacing=10, padding=20, size_hint_y=None)
        layout.bind(minimum_height=layout.setter('height'))

        fields = ["Date", "Ambulance Number", "Meter Reading", "Maintance Details", "Parts Changing Details",
                  "Bill No", "Bill Amount", "Garage Name", "Mechanic Name", "Driver Name", "Intructions"]

        today = datetime.now().strftime("%d-%m-%Y")
        self.inputs = {}
        for field in fields:
            layout.add_widget(Label(text=field, color=get_color_from_hex("#0c0c0c")))
            ti = TextInput(multiline=False, size_hint_y=None, height=40)
            if field.lower() == "date":
                ti.text = today
            layout.add_widget(ti)
            self.inputs[field] = ti

        submit_btn = Button(text="Submit", size_hint_y=None, height=50,
                            background_color=get_color_from_hex("#03A9F4"), background_normal='')
        submit_btn.bind(on_press=self.submit_maintenance)
        layout.add_widget(submit_btn)
        layout.add_widget(Label())

        scroll.add_widget(layout)
        main_layout.add_widget(scroll)
        self.add_widget(main_layout)

    def submit_maintenance(self, instance):
        maintenance_data = {field: self.inputs[field].text for field in self.inputs}
        maintance_sheet.append_row(list(maintenance_data.values()))
        print("Maintenance details submitted")


class DriverScreen(Screen):
    def __init__(self, **kwargs):
        super(DriverScreen, self).__init__(**kwargs)
        self.build_ui()

    def build_ui(self):
        self.clear_widgets()
        main_layout = BoxLayout(orientation='vertical', spacing=10)
        main_layout.add_widget(Button(text="← Back", size_hint_y=None, height=40,
                                      background_color=get_color_from_hex("#f44336"), background_normal='',
                                      on_press=lambda x: setattr(self.manager, 'current', 'dashboard')))

        scroll = ScrollView()
        layout = GridLayout(cols=2, spacing=10, padding=20, size_hint_y=None)
        layout.bind(minimum_height=layout.setter('height'))

        fields = ["D.Name", "Date", "In", "Out", "Location", "Advance amount"]

        today = datetime.now().strftime("%d-%m-%Y")
        self.inputs = {}
        for field in fields:
            layout.add_widget(Label(text=field, color=get_color_from_hex("#0c0c0c")))
            ti = TextInput(multiline=False, size_hint_y=None, height=40)
            if field.lower() == "date":
                ti.text = today
            layout.add_widget(ti)
            self.inputs[field] = ti

        submit_btn = Button(text="Submit", size_hint_y=None, height=50,
                            background_color=get_color_from_hex("#03A9F4"), background_normal='')
        submit_btn.bind(on_press=self.submit_driver_details)
        layout.add_widget(submit_btn)
        layout.add_widget(Label())

        scroll.add_widget(layout)
        main_layout.add_widget(scroll)
        self.add_widget(main_layout)

    def submit_driver_details(self, instance):
        driver_data = {field: self.inputs[field].text for field in self.inputs}
        driver_sheet.append_row(list(driver_data.values()))
        print("Driver details submitted")


class AmbulanceApp(App):
    def build(self):
        self.driver_name = ""
        sm = ScreenManager()
        sm.add_widget(LoginScreen(name="login"))
        sm.add_widget(DashboardScreen(name="dashboard"))
        sm.add_widget(RentScreen(name="rent"))
        sm.add_widget(MaintenanceScreen(name="maintenance"))
        sm.add_widget(DriverScreen(name="driver"))
        return sm


if __name__ == '__main__':
    AmbulanceApp().run()
