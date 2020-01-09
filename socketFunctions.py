import socket
import datetime
from game import *
import threading

INTERVAL = 5
hostIP = ""
g = ""
run=True
def listenUDPThread():
    global run
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.bind((hostIP, PORT))
    except:
        pass
    while run:
        data, addr = s.recvfrom(1024)
        tempList = data.decode('utf-8').replace('\n', '')[:-1][1:].split(',', 8)
        tempList[0] = tempList[0].replace(' ', '')
        tempList[1] = tempList[1].replace(' ', '')
        tempList[2] = tempList[2].replace(' ', '')
        if tempList[2] == 'update':
            enemyHitState = int(tempList[3])
            px = int(tempList[4])
            py = int(tempList[5])
            vx = int(tempList[6])
            vy = int(tempList[7])
            if g.characters[1].frameCount - int(tempList[8]) > INTERVAL:
                px, py, vx, vy, enemyHitState = g.simulateForTime(px, py, vx, vy,
                                                                  g.characters[1].frameCount - int(tempList[8]),
                                                                  enemyHitState)
            g.characters[1].frameCount = int(tempList[8])
            g.update(px, py, vx, vy, enemyHitState)
            g.timeSinceLastPacket = 0
        elif tempList[2] == "ack":
            if int(tempList[3]) in g.sentDamagePacks:
                g.damageLock.acquire()
                g.sentDamagePacks.remove(int(tempList[3]))
                g.damageLock.release()
        elif tempList[2] == "damage":
            s2 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            myMessage = "[" + g.ownName + "," + hostIP + "," + "ack" + "," + tempList[3] + "]"
            s2.sendto(bytes(myMessage, 'utf-8'), (g.enemyIP, PORT))
            s2.close()
            if not int(tempList[3]) in g.ackedDamagePacks:
                g.characters[1].HP -= g.atomicDamage
                g.ackedDamagePacks.append(int(tempList[3]))
        elif tempList[2] == "ms":
            s3 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            myMessage = "[" + g.ownName + "," + hostIP + "," + "msAck" + "," + tempList[3] + "]"
            s3.sendto(bytes(myMessage, 'utf-8'), (g.enemyIP, PORT))
            s3.close()
        elif tempList[2] == "msAck":
            if g.waitingmsAck:
                if int(tempList[3]) == g.msPacketId:
                    timeDiff=datetime.datetime.now()-g.msPacketTime
                    g.ms = timeDiff.microseconds/2000
                    g.msWaitLock.acquire()
                    g.waitingmsAck = False
                    g.msWaitLock.release()

def startGame(player1, char1, ip1,player2,char2,ip2, position):
    global g
    global run
    run = True
    g = Game(player1, char1, ip1,player2,char2,ip2, position)
    hostIP =ip1
    threading.Thread(target=listenUDPThread, name='thread_function', daemon=True).start()
    g.run()
    run = False

