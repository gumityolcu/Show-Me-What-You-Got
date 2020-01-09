import os
import sys
import select
import socket
import threading
import datetime
from socketFunctions import  *



def responseThreadSummoner(passResponseIP):
    threading.Thread(target=responseThread, args=(passResponseIP,), name='thread_function').start()
def responseThread(responseIP):
    s3 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s3.settimeout(0.05)
    s3.connect((responseIP,12355))
    s3.sendall(bytes("[" +userID +", "+hostIP+", "+ "response]", 'utf-8'))
    s3.close()
def listenUDPThread():
    s4.bind(("", 12355))
    while not isExit:
        data, addr = s4.recvfrom(1024)
        tempList2 = data.decode('utf-8').replace('\n', '')[:-1][1:].split(',',3)
        tempList2[0]= tempList2[0].replace(' ', '')
        tempList2[1]= tempList2[1].replace(' ', '')
        tempList2[2]= tempList2[2].replace(' ', '')
        responseCurrentTimeArray = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S').split(" ")[1].split(":")
        responseCurrentTime = int(responseCurrentTimeArray[0])*3600 + int(responseCurrentTimeArray[1])*60 + int(responseCurrentTimeArray[2])
        if tempList2[2] == 'announce' :
            if tempList2[1] in lastAnnounceTime:
                if (responseCurrentTime - lastAnnounceTime[tempList2[1]])>1:
                    userList[tempList2[0]] = tempList2[1]
                    passerIP = tempList2[1]
                    responseThreadSummoner(passerIP)
                lastAnnounceTime[tempList2[1]] = responseCurrentTime
            else :
                userList[tempList2[0]] = tempList2[1]
                passerIP = tempList2[1]
                responseThreadSummoner(passerIP)
                lastAnnounceTime[tempList2[1]] = responseCurrentTime
def listenThread():
    s.bind((hostIP, 12355))
    while not isExit:
        s.listen()
        clientsocket, adress = s.accept()
        tempList = clientsocket.recv(1024).decode('utf-8').replace('\n', '')[:-1][1:].split(',',3)
        tempList[0]= tempList[0].replace(' ', '')
        tempList[1]= tempList[1].replace(' ', '')
        tempList[2]= tempList[2].replace(' ', '')
        if tempList[2] == 'response':
            userList[tempList[0]] = tempList[1]
        if tempList[2] == 'message':
            tempList[3] = tempList[3].strip()
            if userList[tempList[0]] == tempList[1]:
                print(tempList[0]+": "+tempList[3])
        if tempList[2] == 'requestGame':
            if userList[tempList[0]] == tempList[1]:
                print("Game Request from "+ tempList[0] )
                char = input("Press 1 to select Warrior, 2 to select Mage, 3 to select Rogue: ")
                if char == "1":
                    charChoice = "warrior"
                elif char == "2":
                    charChoice = "mage"
                else :
                    charChoice = "rogue"
                enemyIP = tempList[1]
                enemyID = tempList[0]
                enemyType = tempList[3]
                nowType = charChoice
                myPosition = True
                tempTuple = (tempList[1], 12355)
                s5 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s5.connect(tempTuple)
                s5.sendall(bytes("[" +userID +","+hostIP+","+ "acceptGame," +charChoice+"]", 'utf-8'))
                s5.close()
                startGame(userID,nowType, hostIP,enemyID,enemyType,enemyIP,myPosition)

        if tempList[2] == "acceptGame":
            enemyIP = tempList[1]
            enemyID = tempList[0]
            enemyType = tempList[3]
            myPosition = False # im at right
            startGame(userID,myType, hostIP,enemyID,enemyType,enemyIP,myPosition)



s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s4 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
currentTimeArray = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S').split(" ")[1].split(":")
currentTime = int(currentTimeArray[0])*3600 + int(currentTimeArray[1])*60 + int(currentTimeArray[2])
lastTime = 0
lastAnnounceTime = {}
userList = {}
myPosition = False
enemyID = ""
enemyIP = ""
enemyType = ""
myType = ""
userID = ""
port = "12355"
isExit = False
hostIP = hostIP = os.popen('hostname -I').read().replace(" ", "").replace("\n"," ").strip()
pollObject = select.poll()
pollObject.register(sys.stdin.fileno(), select.POLLIN)
print("||2016400285 - 2016400249 - CMPE487 - Final Project||\n---------------------------\n")
userID = input("What is your username ?\n")
print("This program does not automatically announce you to other users when start!\nTo announce yourself and start playing please write -r!\nOn how to use program please write -h")
threading.Thread(target=listenThread, name='thread_function',daemon=True).start()
threading.Thread(target=listenUDPThread, name='thread_function2',daemon=True).start()
while not isExit:
    polledObject = pollObject.poll()
    try:
        polledElement = polledObject.pop()
    except :
        continue
    pollIndex, massage = polledElement
    if pollIndex == sys.stdin.fileno():
        message = sys.stdin.readline().rstrip()
        if message == '-l':
            for key,value in userList.items() :
                print(key)
        elif message == "-h":
            print("-g [username]: Will select the user to send a game request\n")
            print("-l: List all users currently available\n\n-r: Refreshes your user list and announces you\n")
            print("-m [username]: Will select the user to send message to. Write \"-m\" space and username you want to send message to.\nafter that program will expect you to write your message\n")
            print("-e: Exits the program")
        elif message == '-r':
            currentTimeArray = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S').split(" ")[1].split(":")
            currentTime = int(currentTimeArray[0])*3600 + int(currentTimeArray[1])*60 + int(currentTimeArray[2])
            if currentTime-lastTime > 60:
                userList ={}
                s2 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s2.settimeout(0.05)
                tempTuple = ("<broadcast>",12355)
                s2.bind(("",0))
                s2.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST,1)
                for i in range(3):
                    s2.sendto(bytes("[" + userID +", "+hostIP+", "+ "announce" +"]", 'utf-8'), tempTuple)
                s2.close()
                lastTime=currentTime
            else:
                print(str(60-(currentTime-lastTime))+" seconds remaining to refresh")
        elif message.split(" ", 1)[0] == '-m':
            try:
                messageName = message.split(" ",1)[1]
                messageText = input("to "+messageName+":")
            except:
                print("Faulty message instruction, write -h to help!")
            else:
                try:
                    messageIP = userList[messageName]
                except:
                    print("No such user!")
                else:
                    tempTuple = (messageIP, 12355)
                    s2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    s2.connect(tempTuple)
                    s2.sendall(bytes("[" +userID +", "+hostIP+", "+ "message, " +messageText+"]", 'utf-8'))
                    s2.close()
        elif message.split(" ", 1)[0] == '-g':
            try:
                requestName = message.split(" ",1)[1]
                char = input("Press 1 to select Warrior, 2 to select Mage, 3 to select Rogue: ")
            except:
                print("Faulty message instruction, write -h to help!")
            else:
                try:
                    requestIP = userList[requestName]
                except:
                    print("No such user!")
                else:
                    if char == "1":
                        charChoice = "warrior"
                    elif char == "2":
                        charChoice = "mage"
                    else :
                        charChoice = "rogue"
                    tempTuple = (requestIP, 12355)
                    myType = charChoice
                    s2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    s2.connect(tempTuple)
                    s2.sendall(bytes("[" +userID +","+hostIP+","+ "requestGame," +charChoice+"]", 'utf-8'))
                    s2.close()
        elif message == '-e':
            isExit = True
            s.close()
            s4.close()
            exit()
        else :
            print("Faulty instructions, write -h for help!")















