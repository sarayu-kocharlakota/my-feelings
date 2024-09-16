# TODO possibility to send or save data somewhere out of the app (email....)
# TODO change data font and make it visible


from functools import partial
from kivy.lang import Builder
from kivy.uix.screenmanager import Screen
from kivymd.app import MDApp
from tinydb import TinyDB, Query
from datetime import datetime
from kivy.properties import ObjectProperty
from kivymd.uix.label import MDLabel
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.button import MDIconButton, MDFillRoundFlatButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.textfield import MDTextField
from kivy.uix.popup import Popup

from kivymd.uix.filemanager import MDFileManager
from kivymd.toast import toast
from kivy.utils import platform




from kivy.core.window import Window
Window.softinput_mode = 'below_target'

feelings_db = TinyDB('feelings.json')


class TellMeMoreTweet(MDTextField):
    count = 0

    def insert_text(self, substring, from_undo=False):
        patch_name = [c for c in substring if self.count < 140]
        s = "".join(patch_name)

        if self.count < 140:
            self.count += 1
        return super().insert_text(s, from_undo=from_undo)


class HomeScreen(Screen):
    mood = ''
    additional_info = ObjectProperty(None)
    given_additional_info = ''
    first_reaction = ObjectProperty(None)
    send_data_button = ObjectProperty(None)
    data = ObjectProperty(None)

    def get_mood(self, selected_mood):
        if selected_mood == 'Happy' or selected_mood == 'Excited' or selected_mood == 'Feeling normal':
            self.first_reaction.text = f'[font=data/font/coffeeForBreakfast][color=#4CBB17]{selected_mood}? Great! Tell me more![/color][/font]'
        else:
            self.first_reaction.text = f'[font=data/font/coffeeForBreakfast][color=#4CBB17]{selected_mood}? Oh no! Tell me more![/color][/font]'
        self.mood = selected_mood
        self.send_data_button.disabled = False
        self.first_reaction.color = color=(206 / 255, 203 / 255, 203 / 255, 0.2)
        

    def reset_fields(self):
        self.mood = ''
        self.given_additional_info = ''
        self.first_reaction.text = ' '
        self.additional_info.text = ''
        self.send_data_button.disabled = True


    def send_data(self):
        now = datetime.now()
        dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
        date = dt_string[0:10]
        time = dt_string[10:]
        self.given_additional_info = self.additional_info.text.replace('\n',' ')
        feelings_db.insert({'date':f'{date}','time': f'{time}','mood':f'{self.mood}','additional info':f'{self.given_additional_info}'})
        self.reset_fields()   

class DataScreen(Screen):

    def get_day_data(self, date):
        Record = Query()
        b = feelings_db.search(Record.date == date)[0:6]
        return b

    def get_month_name(self, month):
        if month == '01':
            return 'January'
        elif month == '02':
            return 'February'
        elif month == '03':
            return 'March'
        elif month == '04':
            return 'April'
        elif month == '05':
            return 'May'
        elif month == '06':
            return 'June'
        elif month == '07':
            return 'July'
        elif month == '08':
            return 'August'
        elif month == '09':
            return 'September'
        elif month == '10':
            return 'October'
        elif month == '11':
            return 'November'
        elif month == '12':
            return 'December'
        else:
            return ''

    def check_amount_data_recorded(self):
        data_recorded_months = 0
        month = ''
        for record in feelings_db:
            if record['date'][3:5] != month:
                data_recorded_months += 1
                month = record['date'][3:5]
                if data_recorded_months > 2 :
                    return True
        return False

    def show_data_to_erase_dialog(self):
        close_button = MDFillRoundFlatButton(text='CLOSE', font_style='Button')
        dialog = MDDialog(
            text = 'Data is taking much space, it is suggested to erase them',
            buttons=[close_button]
        )
        dialog.open()
        close_button.bind(on_release=dialog.dismiss)

    def show_data(self):
        self.data.clear_widgets()
        if self.check_amount_data_recorded():
            self.show_data_to_erase_dialog()
        date = ''
        month = ''
        month_layout = MDBoxLayout(orientation='vertical',spacing=10, adaptive_height=True)
        
        for record in feelings_db:
            month_data_layout = MDGridLayout(cols=7, adaptive_height=True)
            month_label = MDLabel(halign='center',markup=True, font_style='Subtitle1')
            
            if month != record['date'][3:5]:
                month_name = self.get_month_name(record['date'][3:5])
                month_label.text = f'[font=data/font/coffeeForBreakfast]{month_name}[/font]'
                month = record['date'][3:5]
            
            if date != record['date']:
                day_entries = self.get_day_data(record['date'])
                text_date = record['date']
                month_data_layout.add_widget(MDLabel(markup=True, text=f'[font=data/font/coffeeForBreakfast]{text_date}[/font]'))
                buttons = []
                for i in range(0,len(day_entries)):
                    if day_entries[i]['mood'] == 'Feeling normal' or day_entries[i]['mood'] == 'Happy' or day_entries[i]['mood'] == 'Excited':
                        color = (0,1,0,1)
                    elif  day_entries[i]['mood'] == 'Sad' or  day_entries[i]['mood'] == 'Depressed':
                        color = (1,1,0,1)
                    else:
                        color = (1,0,0,1)
                    button = MDIconButton(icon='star',text_color=color,theme_text_color="Custom",)
                    buttons.append(button)

                for i in range(0, len(buttons)):
                    buttons[i].bind(on_release=partial(self.show_mood_info, day_entries[i]))

                for button in buttons:
                    month_data_layout.add_widget(button)
                
                date = record['date']
                month_layout.add_widget(month_label)
                month_layout.add_widget(month_data_layout)
            
            else:
                continue
      
        self.data.add_widget(month_layout)


    def show_mood_info(self,record, args):
        close_button = MDFillRoundFlatButton(text='CLOSE', pos_hint={'center_x':0.5, 'center_y':0.5},font_style='Button')
        box=MDBoxLayout(orientation='vertical', spacing=10, size_hint_x=1, adaptive_height=True)
        box.add_widget(MDLabel(text='time: ' + record['time'], adaptive_height=True))
        box.add_widget(MDLabel(text='mood: ' + record['mood'], adaptive_height=True))
        box.add_widget(MDLabel(text='additional info: ' + record['additional info'], adaptive_height=True))
        box.add_widget(close_button)
        dialog = MDDialog(
            type="custom",
            content_cls=box,
        )
        dialog.open()
        close_button.bind(on_release=dialog.dismiss)
    

    def show_erase_data_alert(self):
        erase_button = MDFillRoundFlatButton(text='ERASE', font_style='Button')
        cancel_button = MDFillRoundFlatButton(text='CANCEL', font_style='Button')

        dialog = MDDialog(
            text = 'Erase the entire database?',
            buttons=[erase_button, cancel_button]
        )
        dialog.open()

        erase_button.bind(on_press=self.erase_data)
        erase_button.bind(on_release=dialog.dismiss)
        cancel_button.bind(on_release=dialog.dismiss)


    def erase_data(self, args):
        feelings_db.truncate()
        self.show_data()



class MainWindow(Screen):
    pass


class FeelingsTrackerApp(MDApp):
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Window.bind(on_keyboard=self.events)
        self.manager_open = False
        self.file_manager = MDFileManager(
            exit_manager=self.exit_manager,
            select_path=self.select_path,
            #preview=True
        )
    
    
    def build(self):
        self.theme_cls.primary_palette = 'LightGreen'
        self.theme_cls.theme_style = "Dark"
        return Builder.load_file('manager.kv')
    

    def file_manager_open(self):
        PATH ="."
        if platform == "android":
          from android.permissions import request_permissions, Permission
          request_permissions([Permission.READ_EXTERNAL_STORAGE, Permission.WRITE_EXTERNAL_STORAGE])
          app_folder = os.path.dirname(os.path.abspath(__file__))
          PATH = "/storage/emulated/0" #app_folder
        self.file_manager.show(PATH)  # output manager to the screen
        self.manager_open = True

    def select_path(self, path):
        '''It will be called when you click on the file name
        or the catalog selection button.

        :type path: str;
        :param path: path to the selected directory or file;
        '''
        self.save_database_data(path)
        self.exit_manager()
        #toast(path)

    def exit_manager(self, *args):
        '''Called when the user reaches the root of the directory tree.'''

        self.manager_open = False
        self.file_manager.close()

    def events(self, instance, keyboard, keycode, text, modifiers):
        '''Called when buttons are pressed on the mobile device.'''

        if keyboard in (1001, 27):
            if self.manager_open:
                self.file_manager.back()
        return True

    def generate_text(self, records):
        text = ''
        for record in records:
            text += '\nDate: ' + record['date']
            text += '\nTime: ' + record['time']
            text += '\nMood: ' + record['mood']
            text += '\nAdditional info' + record['additional info']
            text += '\n-------------------------------------------\n'
        return text

    def save_database_data(self, path):
        records = feelings_db.all()
        text = self.generate_text(records)
        saved_records = open(f'{path}/records.txt','w+')
        saved_records.write(text)
        saved_records.close()


FeelingsTrackerApp().run()