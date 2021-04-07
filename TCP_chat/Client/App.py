# -*- coding: utf-8 -*-
from tkinter import *
from tkinter import messagebox
from tkinter import Tk, Frame
from tkinter import Label, Button, Entry, Text
import socket
import threading

class ChatTCPApp():
    def __init__(self):
        self.root = Tk()
        self.root.title("TCP chat")
        
        self.__InputFrame = Frame(self.root)
        self.__OutputFrame = Frame(self.root)
        self.__ButtonFrame = Frame(self.root)
        self.__OutputFrame.grid(row=0, column=0)
        self.__InputFrame.grid(row=1, column=0)
        self.__ButtonFrame.grid(row=1, column=1)

        Button(self.__ButtonFrame, text="Send", command=lambda: self.SendMessage()).grid(row=1, column=0)
        Button(self.__ButtonFrame, text="Connect", command=lambda: self.Connect()).grid(row=0, column=0)

        Label(self.__InputFrame, text="Your name ").grid(row=0, column=0)
        Label(self.__InputFrame, text="Server ").grid(row=1, column=0)
        Label(self.__InputFrame, text="Port ").grid(row=2, column=0)
        Label(self.__InputFrame, text="Friend name ").grid(row=3, column=0)
        Label(self.__InputFrame, text="Message ").grid(row=4, column=1)

        self.__Name = Entry(self.__InputFrame)
        self.__Port = Entry(self.__InputFrame)
        self.__Server = Entry(self.__InputFrame)
        self.__Friend = Entry(self.__InputFrame)
        self.__Name.grid(row=0, column=1)
        self.__Port.grid(row=2, column=1)
        self.__Server.grid(row=1, column=1)
        self.__Friend.grid(row=3, column=1)

        self.__Message = Text(self.__OutputFrame, width=70, height=25, font=("Arial", 14))
        self.__MessageSend = Text(self.__InputFrame, width=50, height=4)
        self.__MessageSend.grid(row=4, column=2)
        self.__Message.grid(row=0, column=0)
        self.__Message.config(state=DISABLED)

        self.__sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def SendMessage(self):
        try:
            name = self.__Name.get()
            friend = self.__Friend.get()
            mess = self.__MessageSend.get("1.0", END)
            messsend = f"send<=>{name}<=>{friend}<=>{mess}"
            self.SendToServer(bytes(messsend, 'utf-8'))
            mess = f"YOU----# {mess}\n"
            self.__Message.config(state=NORMAL)
            self.__Message.insert(END, mess)
            self.__Message.config(state=DISABLED)

        except:
            messagebox.showerror(title="Send message", message="Message can't send!")

    def ReceiveMessage(self):
        try:
            port = int(self.__Port.get())
            server = self.__Server.get()
            name = self.__Name.get()
            connectmess = f"signup<=>{name}"
            self.__sock.connect((server, port))
            self.__sock.send(bytes(connectmess, 'utf-8'))

            while True:
                mess = self.__sock.recv(1024).decode("utf-8")

                if mess == "1":
                    self.__sock.send(b"1")
                    continue
                elif mess == "200":
                    messagebox.showinfo(title="Connect", message="Connected!")
                    continue
                elif mess == "404":
                    self.__sock.close()
                    self.__sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    messagebox.showerror(title="Connect", message="Can not connect!")
                    break
                else:
                    try:
                        mess = mess.split("<=>")
                        mess1 = f"{mess[0]}---#{mess[1]}\n"
                        self.__Message.config(state=NORMAL)
                        self.__Message.insert(END, mess1)
                        self.__Message.config(state=DISABLED)
                    except:
                        pass

        except:
            self.__sock.close()
            self.__sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            messagebox.showerror(title="Receive Message", message="Can not receive message!")

    def Connect(self):
        print("TCP Receive Message")
        thread = threading.Thread(target=self.ReceiveMessage)
        thread.start()

    def SendToServer(self, message):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        port = int(self.__Port.get())
        server = self.__Server.get()
        sock.connect((server, port))
        sock.send(message)







