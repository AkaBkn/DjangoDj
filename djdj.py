import gtk
import appindicator
import subprocess
import os
import signal
from ConfigParser import ConfigParser
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SETTINGS_FILE = 'settings.ini'

class DjDj(object):
    server = None
    custom_commands = []
    custom_runserver_command = ''

    def __init__(self):
        self.read_settings()

        self.orig_path = os.getcwd()

        ind = appindicator.Indicator ("DjangDj", "djdj-icon", appindicator.CATEGORY_APPLICATION_STATUS)
        
        ind.set_status (appindicator.STATUS_ACTIVE)
        #ind.set_attention_icon ("indicator-messages-new")

        ind.set_menu(self.create_menu())
        
        gtk.main()

    def read_settings(self):
        #f = open()
        c = ConfigParser()
        c.read(SETTINGS_FILE)

        for section in c.sections():
            for option in c.options(section):
                if section == 'general':
                    if option == 'django_project_path':
                        self.django_path = c.get(section, option)
                    elif option == 'custom_runserver_command':
                        self.custom_runserver_command = c.get(section, option)
                        
                elif section == 'commands':
                    self.custom_commands.append((option, c.get(section, option)))

        

    def create_menu(self):
        gtk_menu = gtk.Menu()

        menu = [
            ['--'], 
            ['Run Server', self.run_server],
            ['--'],
            ['About', self.about],
            ['--'],
            ['Exit', self.exit],
        ]

        for m in self.custom_commands:
            menu_item = gtk.MenuItem(m[0])
            menu_item.connect("activate", self.run_management_command, m[1])
            menu_item.show()
            gtk_menu.append(menu_item)

        for m in menu:
            if m[0] is not '--':
                menu_item = gtk.MenuItem(m[0])
                menu_item.connect("activate", m[1])
            else:
                menu_item = gtk.SeparatorMenuItem()

            menu_item.show()
            gtk_menu.append(menu_item)

        return gtk_menu

    def run_server(self, item):
        if not self.server:
            os.chdir(self.django_path)

            if self.custom_runserver_command:
                cmd = self.custom_runserver_command.split()
            else:
                cmd = ['./manage.py', 'runserver']

            self.server = subprocess.Popen(cmd, shell=True)

            logger.info('Server started with process id: %d' % self.server.pid)
            
            os.chdir(self.orig_path)
            item.set_label('Stop Server')
            
        else:
            self.server.kill()
            #os.killpg(os.getpgid(self.server.pid), signal.SIGTERM)
            self.server = None
            item.set_label('Run Server')

    def run_management_command(self, item, command):
        os.chdir(self.django_path)
        subprocess.Popen(['./manage.py', command ])
        os.chdir(self.orig_path)

    def about(self, item):
        w = self.create_window('About')
        l = gtk.Label('This software was created by Dominic Fischer <pirate.owns@gmail.com>')
        l.show()
        self.box.pack_start(l, True, True, 10)
        b = gtk.Button('Close')
        b.connect('clicked', self.close_window)
        b.show()
        self.box.pack_start(b, False, False, 0)
        w.show()

    def create_window(self, title='DjangoDj'):
        w = gtk.Window(gtk.WINDOW_TOPLEVEL)
        w.set_title(title)
        w.set_position(gtk.WIN_POS_CENTER_ALWAYS)
        
        b = gtk.VBox(False, 10)
        b.show()
        w.add(b)
        
        self.window = w
        self.box = b
        return w

    def close_window(self, widget):
        self.window.destroy()

    def exit(self, item):
        gtk.main_quit()

if __name__ == "__main__":
   dj = DjDj()
