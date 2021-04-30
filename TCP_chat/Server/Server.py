# -*- coding: utf-8 -*-
import socket
import threading
import time

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
UserConnect = {}

FistTime = time.time()

def Binding():
    global sock
    try:
        sock.bind(("0.0.0.0", 7000))
        print("listen: ", ("0.0.0.0", 7000))
    except:
        print("Can not binding port 7000")
        while True:
            try:
                port = int(input("New port: "))
                sock.bind(("0.0.0.0", port))
                print("listen: ", ("0.0.0.0", port))
                break
            except:
                print("Can not binding")



def CheckUserExist(name):
    global UserConnect
    for i in UserConnect:
        if i == name:
            return True
    return False

def SignUp(client, name):
    global UserConnect
    try:
        if CheckUserExist(name) == True:
            client.send(b"404")
            client.close()
        else:
            client.send(b'200')
            UserConnect[name] = client
    except:
        print("error SignUp(client, name)")

#data frame: send<=>source<=>destination<=>payload
def Forward(packet):
    global UserConnect
    try:
        if CheckUserExist(packet[2]) == True:
            mess = f"{packet[1]}<=>{packet[3]}"
            mess = bytes(mess, 'utf-8')
            UserConnect[packet[2]].send(mess)
        else:
            print(f"Can not send from {packet[1]} to {packet[2]}")
    except:
        print("error Forward(packet)")


def ForwardFile(mess):
    Header = mess[0:1024].decode("utf-8").split("#")
    global UserConnect
    try:
        if CheckUserExist(Header[2]) == True:
            UserConnect[Header[2]].send(mess)
    except:
        print("error ForwardFile")



def ReceiveFromClient():
    global sock

    while True:
        client, address = sock.accept()
        mess = client.recv(5120)
        print(f"Connect from address: {address}")

        if mess[0:1].decode("utf-8") == "f":
            threading.Thread(target=ForwardFile, args=(mess,)).start()
            continue

        data = mess.decode("utf-8").split("<=>")
        if data[0] == "signup":
            thread1 = threading.Thread(target=SignUp, args=(client, data[1],))
            thread1.start()
        elif data[0] == "send":
            thread2 = threading.Thread(target=Forward, args=(data,))
            thread2.start()


def UpdateUserConnect():
    global UserConnect, FistTime
    CurrentTime = time.time()
    if CurrentTime-FistTime > 3600:
        print("UpdateUserConnect()")
        DeleteUser = []

        for i in UserConnect:
            try:
                UserConnect[i].send(b"1")
                mess = UserConnect[i].recv(1024).decode("utf-8")
                if not mess:
                    DeleteUser.append(i)
            except:
                DeleteUser.append(i)
        
        for i in DeleteUser:
            del UserConnect[i]
        
        FistTime = time.time()
        


if __name__ == "__main__":
    
    Binding()
    sock.listen(50)

    threadRecv = threading.Thread(target=ReceiveFromClient)
    threadRecv.start()
    threadUpdate = threading.Thread(target=UpdateUserConnect)
    threadUpdate.start()

