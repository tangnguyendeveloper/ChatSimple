# -*- coding: utf-8 -*-
from tkinter import *
from tkinter import messagebox
from tkinter import Tk, Frame
from tkinter import Label, Button, Entry, Text
import socket
import threading

class ChatUDPApp():
    def __init__(self):
        self.root = Tk()
        self.root.title("UDP chat")
        
        self.__InputFrame = Frame(self.root)
        self.__OutputFrame = Frame(self.root)
        self.__ButtonFrame = Frame(self.root)
        self.__OutputFrame.grid(row=0, column=0)
        self.__InputFrame.grid(row=1, column=0)
        self.__ButtonFrame.grid(row=1, column=1)

        Button(self.__ButtonFrame, text="Send", command=lambda: self.SendMessage()).grid(row=1, column=0)
        Button(self.__ButtonFrame, text="Connect", command=lambda: self.Connect()).grid(row=0, column=0)

        Label(self.__InputFrame, text="Your port ").grid(row=0, column=0)
        Label(self.__InputFrame, text="Host destination ").grid(row=1, column=0)
        Label(self.__InputFrame, text="Port destination ").grid(row=2, column=0)
        Label(self.__InputFrame, text="Message ").grid(row=3, column=1)

        self.__Port = Entry(self.__InputFrame)
        self.__PortDes = Entry(self.__InputFrame)
        self.__HostDes = Entry(self.__InputFrame)
        self.__Port.grid(row=0, column=1)
        self.__PortDes.grid(row=2, column=1)
        self.__HostDes.grid(row=1, column=1)

        self.__Message = Text(self.__OutputFrame, width=70, height=25, font=("Arial", 14))
        self.__MessageSend = Text(self.__InputFrame, width=50, height=4)
        self.__MessageSend.grid(row=3, column=2)
        self.__Message.grid(row=0, column=0)
        self.__Message.config(state=DISABLED)

        self.__sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def SendMessage(self):
        #sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            host = self.__HostDes.get()
            port = int(self.__PortDes.get())
            mess = self.__MessageSend.get("1.0", END)
            mess_byte = bytes(mess, 'utf-8')
            self.__sock.sendto(mess_byte, (host, port))
            mess = f"YOU----# {mess}\n"
            self.__Message.config(state=NORMAL)
            self.__Message.insert(END, mess)
            self.__Message.config(state=DISABLED)

        except:
            messagebox.showerror(title="Send message", message="Message can't send!")

    def ReceiveMessage(self):
        #sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            port = int(self.__Port.get())
            self.__sock.bind(("0.0.0.0", port))

            while True:
                mess, address = self.__sock.recvfrom(1024)
                mess = mess.decode("utf-8")
                mess = f"{address}----# {mess}\n"
                self.__Message.config(state=NORMAL)
                self.__Message.insert(END, mess)
                self.__Message.config(state=DISABLED)

        except:
            messagebox.showerror(title="Receive Message", message="Can not receive message!")

    def Connect(self):
        print("UDP Receive Message")
        thread = threading.Thread(target=self.ReceiveMessage)
        thread.start()






