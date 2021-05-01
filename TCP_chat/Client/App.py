# -*- coding: utf-8 -*-
from tkinter import *
from tkinter.ttk import *
from tkinter import messagebox
from tkinter import Tk, Frame, filedialog
from tkinter import Label, Button, Entry, Text
import socket
import threading
import os
import asyncio

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

        Button(self.__ButtonFrame, text="Send", command=lambda: self.SendMessage()).grid(row=2, column=0)
        Button(self.__ButtonFrame, text="Connect", command=lambda: self.__ThreadingConnect()).grid(row=0, column=0)
        Button(self.__ButtonFrame, text="Attach file", command=lambda: self.__ThreadAttachFile()).grid(row=1, column=0)

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

        self.__Process = Progressbar(self.__InputFrame, orient = HORIZONTAL, length = 100, mode = 'determinate')
        self.__Process.grid(row=1, column=2)
        self.__Process['value'] = 0
        self.root.update_idletasks()

        self.__sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__FileAttach = dict()

    def SendMessage(self):
        loop = asyncio.new_event_loop()
        try:
            name = self.__Name.get()
            friend = self.__Friend.get()
            mess = self.__MessageSend.get("1.0", END)
            messsend = f"send<=>{name}<=>{friend}<=>{mess}"

            loop.run_until_complete(self.SendToServer(bytes(messsend, 'utf-8')))

            mess = f"YOU----# {mess}\n"
            self.__Message.config(state=NORMAL)
            self.__Message.insert(END, mess)
            self.__Message.config(state=DISABLED)

        except:
            messagebox.showerror(title="Send message", message="Message can't send!")
        

    async def ReceiveMessage(self):
        loop = asyncio.get_event_loop()

        try:
            try:
                port = int(self.__Port.get())
                server = self.__Server.get()
                name = self.__Name.get()
                connectmess = f"signup<=>{name}"
                await loop.sock_connect(self.__sock, (server, port))
                await loop.sock_sendall(self.__sock, bytes(connectmess, 'utf-8'))

            except:
                self.__sock.close()
                self.__sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                messagebox.showerror(title="Connect", message="Can not connect!")
                return

            while True:
                mess = await loop.sock_recv(self.__sock, 4096)
                
                if mess[0:1].decode("utf-8") == 'f':
                    try:
                        MesssageAttachFile = mess.decode("utf-8").split("#")
                        self.__FileAttach[u""+MesssageAttachFile[-1]] = open(u""+MesssageAttachFile[-1], mode="wb")
                        continue
                    except:
                        await loop.create_task(self.ReceiveFile(mess))
                        continue
                
                mess = mess.decode("utf-8")
                if mess == "1":
                    await loop.sock_sendall(self.__sock, bytes("1", "utf-8"))
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
        loop = asyncio.new_event_loop()
        loop.run_until_complete(self.ReceiveMessage())
        

    def __ThreadingConnect(self):
        thread = threading.Thread(target=self.Connect)
        thread.daemon = True
        thread.start()

    async def SendToServer(self, message):
        loop = asyncio.get_event_loop()
        port = int(self.__Port.get())
        server = self.__Server.get()
        socksend = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        await loop.sock_connect(socksend, (server, port))
        await loop.sock_sendall(socksend, message)

        socksend.shutdown(socket.SHUT_RDWR)
        socksend.close()
        await asyncio.sleep(0.002)
        
    
    def AttachFileFuc(self):
        messagebox.showwarning(title="Attach file", message="Your filename must be in ASCII format !")
        loop = asyncio.new_event_loop()
        loop.run_until_complete(self.AttachFile())

    def __ThreadAttachFile(self):
        thread = threading.Thread(target=self.AttachFileFuc)
        thread.daemon = True
        thread.start()

    async def AttachFile(self):
        loop = asyncio.get_event_loop()

        try:
            path = filedialog.askopenfilename(title="Select a file to send")
            filename = os.path.basename(path)
            size = os.path.getsize(path)
            size_have_send = 0

            with open(u""+path, mode="rb") as f:

                name = self.__Name.get()
                friend = self.__Friend.get()
                
                filename = f"{name}-{filename}"

                Flag = 1

                Header = f"f#{name}#{friend}#"

                data = f.read(3072)
                await loop.create_task(self.SendToServer(bytes(f"{Header}{filename}", "utf-8")))
                
                while data:
                    nextdata = f.read(3072)
                    if not nextdata:
                        Flag = 0
                        size_have_send = size
                    else:
                        size_have_send += 3072

                    MessageHeader = f"{Header}{Flag}#{filename}#"
                    if len(MessageHeader) < 1024:
                        space = (1024-len(MessageHeader))*"$"
                        MessageHeader = f"{MessageHeader}{space}"
                        
                    mess = bytes(f"{MessageHeader}", "utf-8")+data
                    await loop.create_task(self.SendToServer(mess))
                    data = nextdata

                    self.__Process['value'] = int((size_have_send/size)*100)
                    self.root.update_idletasks()
            
            self.__Message.config(state=NORMAL)
            self.__Message.insert(END, f"You--->{filename}\n")
            self.__Message.config(state=DISABLED)

        except:
            messagebox.showerror(title="Attach file", message="Can not Attach file because no MyID or friendID!")
        finally:
            self.__Process['value'] = 0
            self.root.update_idletasks()


    async def ReceiveFile(self, mess):
        Header = mess[0:1024].decode("utf-8")
        data = mess[1024:]
        Header = Header.split("#")
        self.__FileAttach[u""+Header[-2]].write(data)

        if Header[-3] == "0":
            self.__FileAttach[u""+Header[-2]].close()
            del self.__FileAttach[u""+Header[-2]]

            self.__Message.config(state=NORMAL)
            self.__Message.insert(END, f"{Header[1]}--->{Header[-2]}\n")
            self.__Message.config(state=DISABLED)









