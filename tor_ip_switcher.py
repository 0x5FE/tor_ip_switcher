#!/usr/bin/env python3
"""
tor_switcher.py reloaded and refactored by Rupe to work with toriptables2.py.
tor_ip_switcher.py is a light GUI interface for issuing NEWNYM signals over TOR's control port.
Useful for making any DoS attack look like a DDoS attack.
"""

import tkinter as tk
from tkinter import messagebox
from tkinter.scrolledtext import ScrolledText
from time import localtime, sleep
import random
import urllib.request
import json
from stem import Signal
from stem.control import Controller

class Switcher(tk.Tk):

    def __init__(self):
        super().__init__()
        self.resizable(0, 0)
        self.title(".o0O| TOR IP Switcher |O0o.")

        self.host = tk.StringVar()
        self.port = tk.IntVar()
        self.passwd = tk.StringVar()
        self.time = tk.DoubleVar()

        self.host.set('localhost')
        self.port.set(9051)
        self.passwd.set('')
        self.time.set(30)

        tk.Label(self, text='Host:').grid(row=1, column=1, sticky=tk.E)
        tk.Label(self, text='Port:').grid(row=2, column=1, sticky=tk.E)
        tk.Label(self, text='Password:').grid(row=3, column=1, sticky=tk.E)
        tk.Label(self, text='Interval:').grid(row=4, column=1, sticky=tk.E)

        tk.Entry(self, textvariable=self.host).grid(row=1, column=2, columnspan=2)
        tk.Entry(self, textvariable=self.port).grid(row=2, column=2, columnspan=2)
        tk.Entry(self, textvariable=self.passwd, show='*').grid(
            row=3, column=2, columnspan=2)
        tk.Entry(self, textvariable=self.time).grid(row=4, column=2, columnspan=2)

        tk.Button(self, text='Start', command=self.start).grid(row=5, column=2)
        tk.Button(self, text='Stop', command=self.stop).grid(row=5, column=3)

        self.output = ScrolledText(
            self,
            foreground="white",
            background="black",
            highlightcolor="white",
            highlightbackground="purple",
            wrap=tk.WORD,
            height=8,
            width=40)
        self.output.grid(row=1, column=4, rowspan=5, padx=4, pady=4)

        self.controller = None

    def start(self):
        self.write('TOR Switcher starting.')
        self.ident = random.random()
        self.controller = Controller.from_port(port=self.port.get())
        try:
            self.controller.authenticate(password=self.passwd.get())
            self.newnym()
        except Exception as ex:
            self.write('Authentication failed: %s' % str(ex))
            self.controller.close()
            self.controller = None

    def stop(self):
        if self.controller:
            self.controller.close()
        try:
            self.write('TOR Switcher stopping.')
        except:
            pass
        self.ident = random.random()

    def write(self, message):
        t = localtime()
        try:
            self.output.insert(tk.END,
                               '[%02i:%02i:%02i] %s\n' % (t[3], t[4], t[5], message))
            self.output.yview(tk.MOVETO, 1.0)
        except:
            print('[%02i:%02i:%02i] %s\n' % (t[3], t[4], t[5], message))

    def error(self):
        messagebox.showerror('TOR IP Switcher', 'Tor daemon not running!')

    def newnym(self):
        key = self.ident
        interval = self.time.get()

        while key == self.ident and self.controller:
            try:
                self.controller.signal(Signal.NEWNYM)
                sleep(1)  # Wait a second for the new IP to take effect
                with urllib.request.urlopen('https://ifconfig.me') as response:
                    my_new_ident = response.read().decode()
                    self.write('Your IP is %s' % (my_new_ident))
            except Exception as ex:
                self.write('There was an error: %s.' % (ex))
                key = self.ident + 1
                self.write('Quitting.')

if __name__ == '__main__':
    mw = Switcher()
    mw.mainloop()
    mw.stop()
