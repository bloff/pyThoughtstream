#!/usr/bin/env python

path_prefix = '/home/bruno/Repositories/Programming/pyThoughtstream/'

import time

import wx

import serial
from serial.serialutil import SerialException

import pyttsx

import threading

import pygame
pygame.mixer.init()

import os

from serial.tools import list_ports


def serial_ports():
    """
    Returns a generator for all available serial ports
    """
    if os.name == 'nt':
        # windows
        for i in range(256):
            try:
                s = serial.Serial(i)
                s.close()
                yield 'COM' + str(i + 1)
            except serial.SerialException:
                pass
    else:
        # unix
        for port in list_ports.comports():
            yield port[0]


class Thoughtstream(wx.Frame):

    def __init__(self,parent,title):
        # configure the serial connections (the parameters differs on the device you are connecting to)
        wx.Frame.__init__(self,parent,title=title,size=(800,600))

        # bind events
        self.Bind(wx.EVT_CLOSE, self.OnClose)

        #toolbar
        self.bitmap_usb = wx.Bitmap(path_prefix+'img/usb.png')
        self.bitmap_connect = wx.Bitmap(path_prefix+'img/connect.png')
        self.bitmap_connect_green = wx.Bitmap(path_prefix+'img/connect_green.png')
        self.bitmap_no_data = wx.Bitmap(path_prefix+'img/no_data.png')
        self.bitmap_data = wx.Bitmap(path_prefix+'img/data.png')
        self.bitmap_tts_on = wx.Bitmap(path_prefix+'img/tts_on.png')
        self.bitmap_tts_off = wx.Bitmap(path_prefix+'img/tts_off.png')
        self.bitmap_quit = wx.Bitmap(path_prefix+'img/quit.png')




        self.toolbar = self.CreateToolBar()
        self.toolbar.AddLabelTool(1, 'Select Port', self.bitmap_usb,  shortHelp="Select Serial Port", longHelp="Change serial port the Thoughtstream USB is connected to.")
        self.Bind(wx.EVT_TOOL, self.on_select_port_button, id=1)
        self.toolbar.AddLabelTool(2, 'Connect', self.bitmap_connect, shortHelp="Connect/Disconnect")
        self.Bind(wx.EVT_TOOL, self.on_connect_button, id=2)
        self.toolbar.AddLabelTool(3, 'Data/No Data', self.bitmap_no_data, shortHelp="Signals incomming data.")
        # self.toolbar.AddLabelTool(4, 'Sound On/Off', self.bitmap_tts_off, shortHelp="Toggles audio feedback.")
        # self.Bind(wx.EVT_TOOL, self.on_toggle_tts_button, id=4)
        self.toolbar.AddLabelTool(5, 'Sound On/Off (2)', self.bitmap_tts_off, shortHelp="Toggles audio feedback (method 2).")
        self.Bind(wx.EVT_TOOL, self.on_toggle_tts_button2, id=5)

        self.toolbar.AddLabelTool(10, 'Quit', self.bitmap_quit, shortHelp="Quit")
        self.Bind(wx.EVT_TOOL, self.on_qt_button, id=10)

        accel_tbl = wx.AcceleratorTable([(wx.ACCEL_CTRL,  ord('Q'), 10 )])
        self.SetAcceleratorTable(accel_tbl)


        # self.toolbar.AddLabelTool(3, 'Quit', wx.Bitmap(path_prefix+'img/quit.png'))
        # self.Bind(wx.EVT_TOOL, self.open_connection, id=3)
        self.toolbar.Realize()


        # Prepare panel and resistance label
        panel = wx.Panel(self)
        self.resistance_label = wx.StaticText(panel, label="1000.0", pos=(0, 10))
        font = self.resistance_label.GetFont()
        font.SetPointSize(270)
        font.SetFamily(wx.FONTFAMILY_MODERN)
        self.resistance_label.SetFont(font);

        #setup timer
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.update, self.timer)
        self.timer.Start(1000)

        self.Show(True)


        self.address = "/dev/ttyUSB0" # Default address
        self.serialport = None
        self.adc_value = 200
        self.resistance_value  = 10000
        self.avg_resistance = 0
        self.avg_resistance_last = 0
        self.probe_error = False
        self.low_battery = False
        self.new_data = False
        self.recalculation_occurred = False
        self.success = False

        self.tts = False
        self.tts2 = False
        self.time_last = time.time()

        self.load_config_file()

        self.open_connection()
        self.update_connect_icon()

        self.Maximize()



    def load_config_file(self):
        None

    def select_port_dlg(self):
        choices = list(serial_ports())
        dlg = wx.SingleChoiceDialog(self, "Please choose the serial port the Thoughtstream USB is connected to.", "Choose Port", choices, wx.CHOICEDLG_STYLE)
        if dlg.ShowModal() == wx.ID_OK:
            self.address = dlg.GetStringSelection()
#            print 'You selected: %s\n' % dlg.GetStringSelection()
        dlg.Destroy()


    def on_qt_button(self, event):
        self.Close()


    def on_select_port_button(self, event):
        if self.serial_port_is_connected():
            self.close_connection()
        self.select_port_dlg()
        self.open_connection()
        self.update_connect_icon()

    def on_connect_button(self, event):
        if self.serial_port_is_connected():
            self.close_connection()
        else:
            self.open_connection()
        self.update_connect_icon()

    def on_toggle_tts_button(self, event):
        self.tts = not self.tts
        if self.tts:
            self.toolbar.SetToolNormalBitmap(4, self.bitmap_tts_on)
        else:
            self.toolbar.SetToolNormalBitmap(4, self.bitmap_tts_off)

    def on_toggle_tts_button2(self, event):
        self.tts2 = not self.tts2
        if self.tts2:
            self.toolbar.SetToolNormalBitmap(5, self.bitmap_tts_on)
        else:
            self.toolbar.SetToolNormalBitmap(5, self.bitmap_tts_off)


    def serial_port_is_connected(self):
        return self.serialport is not None and self.serialport.isOpen()

    def update_connect_icon(self):
        if self.serial_port_is_connected():
            self.toolbar.SetToolNormalBitmap(2, self.bitmap_connect_green)
#            self.toolbar.SetToolLabel(2,"Connected to port: %r" % (self.address,))
        else:
            self.toolbar.SetToolNormalBitmap(2, self.bitmap_connect)
            self.toolbar.SetToolNormalBitmap(3, self.bitmap_no_data)
#            self.toolbar.SetToolLabel(2,"Disconnected")

        # self.toolbar.Realize()



    def on_quit_button(self, event):
        None

    def close_connection(self):
        self.serialport.close()



    def open_connection(self):

        try:
            if self.serialport is None:
                self.serialport = serial.Serial(
                    port=self.address,
                    baudrate=19200,
                    parity=serial.PARITY_NONE,
                    stopbits=serial.STOPBITS_ONE,
                    bytesize=serial.EIGHTBITS
                )
            else:
                self.serialport.port = self.address
                self.serialport.open()
        except SerialException:
            print "Failed to connect to serial port %s" % (self.address,)

    def getbyte(self):
        return ord(self.serialport.read(1))

    def getvalues(self):
        if self.getbyte() != 0xa3 or self.getbyte() != 0x5b or self.getbyte() != 8:
            self.success = False
            return

        value_byte1 = self.getbyte()
        value_byte2 = self.getbyte()

        self.adc_value = (value_byte1 << 8) + value_byte2
        self.resistance_value = (7700010000 / self.adc_value )  -  470000

        bits = self.getbyte()
        self.probe_error = (bits & 1) != 0
        self.low_battery = (bits & 2) != 0
        self.new_data = (bits & 4) != 0
        self.recalculation_occurred = (bits & 8) != 0

        checksum_byte1 = self.getbyte()
        checksum_byte2 = self.getbyte()
        checksum = (checksum_byte1<<8)+checksum_byte2
        self.success = 0xa3+0x5b+0x8+value_byte1+value_byte2+bits == checksum

    def OnClose(self, event):
        if self.serialport is not None:
            self.serialport.close()
        self.Destroy()


    def update(self, event):
        if not self.    serial_port_is_connected():
            self.resistance_label.SetLabel("Conn.")
        elif self.serialport.inWaiting() > 0:
            self.toolbar.SetToolNormalBitmap(3, self.bitmap_data)

            avg_resistance=0
            count = 0
            while self.serialport.inWaiting() > 0:
                self.getvalues()
                avg_resistance += self.resistance_value
                count += 1
            assert(count != 0)
            avg_resistance /= count
            val = avg_resistance / 100
            valf = val / 10.0
            lbl = "%s%.1f" % ("  " if val < 10000 else "", valf)
            self.avg_resistance = avg_resistance
            self.resistance_label.SetLabel(lbl)
            self.audio_feedback()
        else:
            self.toolbar.SetToolNormalBitmap(3, self.bitmap_no_data)

    def play_up(self):
        pygame.mixer.music.load(path_prefix+"snd/up.wav")
        pygame.mixer.music.play()

    def play_down(self):
        pygame.mixer.music.load(path_prefix+"snd/down.wav")
        pygame.mixer.music.play()

    def play_warning(self):
        pygame.mixer.music.load(path_prefix+"snd/warn.wav")
        pygame.mixer.music.play()


    def audio_feedback(self):
        if self.tts:
            if self.avg_resistance > self.avg_resistance_last:
                self.play_up()
            else:
                self.play_down()
            self.avg_resistance_last = self.avg_resistance


            time_current = time.time()
            if time_current - self.time_last >= 60:
                val = self.avg_resistance / 10000
                tts_say("%d" % (val,))
                self.time_last = time_current
        elif self.tts2:
            val = self.avg_resistance / 1000
            if val < 100:
                time_interval = 1
            else:
                time_interval = 1 + val / 100
            # time_interval = 1
            time_current = time.time()

            if self.avg_resistance < self.avg_resistance_last - 4000:
                self.play_warning()
                self.avg_resistance_last = self.avg_resistance
            elif time_current - self.time_last >= time_interval:
                self.time_last = time_current

                if self.avg_resistance > self.avg_resistance_last:
                    self.play_up()
                else:
                    self.play_down()
                self.avg_resistance_last = self.avg_resistance





    pass

def tts_say(text):
    t = threading.Thread(target=tts_say_, args =(text,))
    t.daemon = True
    t.start()

def tts_say_(text):
    # print "%r --- %r" % (arg1, text)
    tts_engine = pyttsx.init()
    tts_engine.say(text)
    tts_engine.runAndWait()

class ThoughtstreamApp():
    def build(self):
        ts = Thoughtstream()

#        Clock.schedule_interval(ts.update, 1.0 / 60.0)
        return ts


if __name__ == '__main__':
   app = wx.App(False)  # Create a new app, don't redirect stdout/stderr to a window.
   frame = Thoughtstream(None, "Thoughtstream USB") # A Frame is a top-level window.
   app.MainLoop()
