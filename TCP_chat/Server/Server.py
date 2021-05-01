# -*- coding: utf-8 -*-
import socket
import time
import asyncio

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

async def SignUp(client, name):
    global UserConnect
    loop = asyncio.get_event_loop()

    try:
        if CheckUserExist(name) == True:
            await loop.sock_sendall(client, b"404")
            client.close()
        else:
            await loop.sock_sendall(client, b"200")
            UserConnect[name] = client
    except:
        print("error SignUp(client, name)")
    

#data frame: send<=>source<=>destination<=>payload
async def Forward(packet):
    global UserConnect
    loop = asyncio.get_event_loop()

    data = ""
    for i in range(3, len(packet)):
        data += f"<=>{packet[i]}"

    try:
        if CheckUserExist(packet[2]) == True:
            mess = f"{packet[1]}{data}"
            mess = bytes(mess, 'utf-8')
            await loop.sock_sendall(UserConnect[packet[2]], mess)
        else:
            print(f"Can not send from {packet[1]} to {packet[2]}")
    except:
        print("error Forward(packet)")
    


async def ForwardFile(mess):
    loop = asyncio.get_event_loop()
    Header = mess[0:1024].decode("utf-8").split("#")
    global UserConnect
    try:
        if CheckUserExist(Header[2]) == True:
            await loop.sock_sendall(UserConnect[Header[2]], mess)
    except:
        print("error ForwardFile")
    

async def ReceiveFromClient(client, address):
    loop = asyncio.get_event_loop()

    mess = (await loop.sock_recv(client, 4096))
    print(f"Connect from address: {address}")

    if mess[0:1].decode("utf-8") == "f":
        await loop.create_task(ForwardFile(mess))
        client.close()
        return

    data = mess.decode("utf-8").split("<=>")
    if data[0] == "signup":
        await loop.create_task(SignUp(client, data[1]))
    elif data[0] == "send":
        await loop.create_task(Forward(data))
        client.close()
    

async def AcceptClient():
    global sock

    loop = asyncio.get_event_loop()

    while True:
        client, address = await loop.sock_accept(sock)
        await loop.create_task(ReceiveFromClient(client, address))


async def UpdateUserConnect():
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

async def main():
    global sock

    Binding()
    sock.listen()
    sock.setblocking(False)

    TaskAccept = asyncio.create_task(AcceptClient())
    TaskClean = asyncio.create_task(UpdateUserConnect())
    
    await TaskAccept


if __name__ == "__main__":
    
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
