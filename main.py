import serial #pyserail
import json
import turtle
import sys
import time
import os
import pytz

UTC = pytz.utc

IST = pytz.timezone('America/Chicago')

from datetime import datetime
from elasticsearch import Elasticsearch
es = Elasticsearch(['http://localhost:9200'], basic_auth=('elastic', 'changeme'))



dataExist = os.path.exists("data")
imagesExist = os.path.exists("images")
if not dataExist:
    os.mkdir("data")
if not imagesExist:
    os.mkdir("images")

ser = serial.Serial(
        port=sys.argv[1], \
        baudrate=115200, \
        #parity=serial.PARITY_ODD, \
        stopbits=serial.STOPBITS_ONE, \
        bytesize=serial.EIGHTBITS, \
        timeout=0)

t = turtle.Turtle()
wn=turtle.Screen()
wn.bgcolor("black")
wn.title("Wifi Finder")

def process_wifi_finder():


    print("connected to: " + ser.portstr)
    count = 1
    ser.write("auto scan\r".encode())
    buffer = ''
    wifilist = list()
    while True:
        buf = ser.readline()
        buf = buf.decode()
        buffer += buf

        if "\n" in buffer:
            if (buffer != "\n"):
                try:
                    data = json.loads(buffer.split("\n")[0])
                    if "scan" in data:
                        t.clear()
                        k = 0
                        t.speed(0)
                        wifilist = sorted(wifilist, key=lambda d: d['SSID'])
                        wifilist = sorted(wifilist, key=lambda d: d['signal'],  reverse=True)

                        timestr = time.strftime("%Y%m%d-%H%M%S")
                        style = ('Courier', 16, 'bold')
                        wn.title("Wifi Finder " + timestr)
                        t.penup()
                        t.goto(-87, -250)
                        t.pendown()
                        t.write(timestr, font=style)
                        style = ('Courier', 12, 'normal')
                        for wifi in wifilist:
                            wifi["time"] = timestr
                            with open("data\wifi_finder.json", "a") as outfile:
                                json.dump(wifi,outfile)

                            wifi["time"] =  datetime.now(IST)
                            resp = es.index(index="wifi-locator", id=wifi["MAC"] + "-" + timestr, document=wifi)
                            print(resp['result'])


                            if wifi["signal"] == 100:
                                t.color("white")
                            elif wifi["signal"] > 80:
                                t.color("green")
                            elif wifi["signal"] > 50:
                                t.color("orange")
                            else:
                                t.color("lightblue")

                            t.penup()
                            t.goto( -200, -200 + (20 * k) +( 200 - (wifi["signal"]*2)) )
                            t.pendown()
                            t.circle( 100 - wifi["signal"])
                            t.color("white")

                            t.write(wifi["SSID"] + " : " + wifi["delta"] + ":" \
                                    + str(wifi["signal"]) + "% " + wifi["Encryption"]\
                                    + " " + str(wifi["dBm"]), font=style)

                            k = k + 1
                        wifilist.clear()
                        ts = turtle.getscreen()
                        ts.getcanvas().postscript(file="images\\" + timestr+"_wifi_scan.eps")
                    else:
                        wifilist.append(data)
                    buffer = ''

                except json.JSONDecodeError as e:
                    do = ""

            buffer = ''

    ser.close()

if __name__ == '__main__':
    process_wifi_finder()
