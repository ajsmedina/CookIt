import RPi.GPIO as GPIO
import pygame
import analog
import time
import random

#=================================
# CookIt! Co-operative Cooking Game
# By Anton Medina
#=================================

GPIO.setmode(GPIO.BCM)

#===
# Input/Output setup for EveOne Board
#===
GPIO.setup(22, GPIO.IN)
GPIO.setup(24, GPIO.IN)
GPIO.setup(25, GPIO.IN)
GPIO.setup(04, GPIO.OUT)
GPIO.setup(17, GPIO.OUT)
GPIO.setup(18, GPIO.OUT)

pygame.init()

#===
# Names of stations for characters to interact with
#===
playerBStations = ["Send", "Trash", "Cut", "Cut", "Cut", "Prep", "Prep", "Prep", "Collect"]
playerAStations = ["Collect", "Cook", "Cook", "Cook", "Lettuce", "Tomato", "Meat", "Trash", "Send"]

size=[650,500]
black = [0,0,0]
white = [255,255,255]

font=pygame.font.Font(None,20)
pygame.display.set_caption("Cook It!")

screen=pygame.display.set_mode(size)

#===
# Gets the on-screen position of the player based on the position of their pot
# player: the id of the player to read position
# @return: player position
#===
def getPlayerPosition(player):
    return min(int(float(analog.read(player,0))/825.0 *9), 9)

#===
# Draws the names of the cooking stations
#===
def drawCookStations():
        for i in range (0, len(playerBStations)):
            screen.blit(font.render(playerBStations[i],1,white),(50+60*i,250))
            screen.blit(font.render(playerAStations[i],1,white),(50+60*i,450))
                                                                                
        for i in range (0, 3):
            drawIcon(cut[2-i], 170+60*i,260)
            screen.blit(font.render(str(cutTime[2-i]),1,white),(180+60*i,260))
            
            drawOrder(plates[2-i], 350+60*i,260)

            drawIcon(cook[2-i], 110+60*i,460)
            screen.blit(font.render(str(cookTime[2-i]),1,white),(120+60*i,460))

            
        drawIcon(collectB, 50+60*8,260)
        drawIcon(collectA, 50,460)

#===
# Draws the order and patience of each customer
#===
def drawCustomers():            
    for i in range (0, 5):
        if(orderTime[i]>0):
            drawOrder(orders[i],20+80*i,50)
            screen.blit(font.render(str(orderTime[i]),1,white),(40+80*i,50))
        
#===
# Draws the players in their positions
#===
def drawPlayers():
        pygame.draw.circle(screen,[0,255,255],[540-60*getPlayerPosition(0),200], 20, 2)
        pygame.draw.circle(screen,[255,0,255],[540-60*getPlayerPosition(1),400], 20, 2)
    
#===
# Draws what each character is holding
#===
def drawInventory():
        drawIcon(inventoryB, 550,120)
        drawIcon(inventoryA, 550,360)
        screen.blit(font.render("Carrying: ",1,white),(520,100))
        screen.blit(font.render("Carrying: ",1,white),(520,350))

#===
# Draws the icon of the ingredient.
# iconID: the id of the ingredient
# x: the x value of the icon
# y: the y value of the icon
#===
def drawIcon(iconID, x, y):
    y+=15
    if(iconID==1):
        pygame.draw.rect(screen,[255,150,150],([x-15,y-10],[20,20]))
    elif(iconID==2):
        pygame.draw.circle(screen,[255,150,150],[x,y], 10)
    elif(iconID==3):
        pygame.draw.circle(screen,[150,100,60],[x,y], 10)
    elif(iconID==4):
        pygame.draw.circle(screen,[50,30,30],[x,y], 10)
    elif(iconID==5):
        pygame.draw.circle(screen,[0,225,0],[x,y], 10, 2)
    elif(iconID==6):
        pygame.draw.circle(screen,[0,255,0],[x,y], 10)
    elif(iconID==7):
        pygame.draw.circle(screen,[225,0,0],[x,y], 10, 2)
    elif(iconID==8):
        pygame.draw.circle(screen,[225,0,0],[x,y], 10)


#===
# Draws the ingredients that make up the order
# ordr: the string of ingredients to draw
# x: the x position to draw it on
# y: the y position to draw it on
#===
def drawOrder(ordr, x, y):
    for i in range(0,len(ordr)):
        drawIcon(int(ordr[i]),x+10*i,y)
    
#===
# Shifts the orders after an order is finished
# start: the order index to start shifting from
#===
def shiftOrders(start):
    for i in range(start, 4):
        orders[i]=orders[i+1]
        orderTime[i]=orderTime[i+1]

    orders[4]=""
    orderTime[4]=0

#===
# Checks whether or not the current served plate is a valid order.
# If it is, gain points based on how happy the customer is.
# plateServed: the string of ingredients on the current plate
# @return: points gained
#===
def checkValidOrder(plateServed):
    addPoints = 0
    
    for i in range(0, 5):
        if(checkOrderString(plateServed,orders[i]) and orders[i]!=0):
            addPoints=orderTime[i]/15
            shiftOrders(i)
            break
        
    return addPoints

#===
# Check if two ingredient strings are equal by comparing if they have the same
# amount of meat, lettuce, and tomato
# plateServed: the ingredient string of the plate being served
# orderTarget: the ingredient string of the customer order being checked
# @return: true if they match, false if they don't
#===
def checkOrderString(plateServed, orderTarget):
    serveIngredients = [0,0,0]
    orderIngredients = [0,0,0]
    same = False
    
    if(len(plateServed)==len(orderTarget)):
        for i in range(0,len(plateServed)):
            if(plateServed[i]=="3"):
                serveIngredients[0]+=1
            elif(plateServed[i]=="6"):
                serveIngredients[1]+=1
            elif(plateServed[i]=="8"):
                serveIngredients[2]+=1
                
            if(orderTarget[i]=="3"):
                orderIngredients [0]+=1
            elif(orderTarget[i]=="6"):
                orderIngredients [1]+=1
            elif(orderTarget[i]=="8"):
                orderIngredients [2]+=1
        if(serveIngredients[0] == orderIngredients [0] and
            serveIngredients[1] == orderIngredients [1] and
            serveIngredients[2] == orderIngredients [2]):
            same = True

    return same

#===
# Randomly generate an order for a customer.
#===
def makeOrder():
    orderID=-1
    order = "3" #Include meat by default
    for i in range(0, 2):
        select = random.randint(0,4)
        #Add nothing if 0
        if(select==1):
            order+="3"
        elif(select==2):
            order+="6"
        elif(select==3):
            order+="8"

    for i in range(0,5):
        if(orderTime[i]==0):
            orderID = i
            break
        
    if(orderID>=0):
        orders[orderID] = order
        orderTime[orderID] = max(2500-points, 1000)

#===
# Display lights on EveOne board according to number of lives
#===
def displayLightLives(lives):
    GPIO.output(4,lives==2)
    GPIO.output(18,lives>=1)
    GPIO.output(17,lives>=0)
    
#===
# Display the main menu for the player
#===
def displayMainMenu():
    screen.fill(black)

    screen.blit(font.render("Cook It!",15,white),(100,100))
    screen.blit(font.render("Press the red button to start!",2,white),(100,300))

    pygame.display.flip()

#===
# Display a game over message when the player loses
#===
def displayGameOver(points):
    screen.fill(black)
    screen.blit(font.render("Game OVER! Points: "+str(points),1,white),(10,10)) 
    pygame.display.flip()

    #WAIT FOR INPUT

#===
# Updates the screen every iteration and draws the game
# lives: number of lives the players have
#===
def updateScreen(lives)

    screen.fill(black)

    screen.blit(font.render("Points: "+str(points),1,white),(10,10))
    drawCookStations()
    drawInventory()
    drawPlayers()
    drawCustomers()
    displayLightLives(lives)

    pygame.display.flip()

#===
# Main iteration loop
#===
try:
    while 1:
                
        ticks = 0
        oldticks = 0

        inventoryA = 0
        inventoryB = 0
        collectA = 0
        collectB = 0

        plates = ["", "", ""]
	
	buttonDown = [False, False, False]
        orders = ["", "", "", "", ""]
        orderTime = [0, 0, 0, 0, 0]
        cut = [0,0,0]
        cutTime = [0,0,0]
        cook = [0,0,0]
        cookTime = [0,0,0]

        orderDelay=400

        points = 0
        lives = 3

        while 1:
            displayMainMenu()
            if(GPIO.input(17)==1):
                break
    
        while 1:
            ticks = pygame.time.get_ticks()

            if(ticks-oldticks>=50): #Counters decrease every 50 ticks
                oldticks=ticks

		#Countdown for adding a new order to the list
                if(orderDelay==1):
                    makeOrder()
                    orderDelay=300
                if(orderDelay>0):
                    orderDelay-=1

		#Decreases the countdown for cutting/cooking
                for i in range(0,3):
                    if(cutTime[i]==1 and cut[i]!=0):
                        cut[i]+=1
                    if(cutTime[i]>0):
                        cutTime[i]-=1
                    if(cookTime[i]==1):
                        cook[i]+=1 #Cook an uncooked burger or burn a cooked burger
                        if(cook[i]==3):
                            cookTime[i]=150
                    if(cookTime[i]>0):
                        cookTime[i]-=1

		#Removes a failed order
                if(orderTime[0]==0):
                    lives-=1
                    shiftOrders(0)
                    makeOrder()

		#Decrease countdown for current orders
                for i in range(0,5):
                     if(orderTime[i]>0):
                         orderTime[i]-=1

	    #Refreshes the buttons as "lifted" if they are not pressed.
            if(GPIO.input(25)==0):
                buttonDown[1] = False
                
            if(GPIO.input(24)==0):
                buttonDown[0] = False

            if(GPIO.input(22)==0):
                buttonDown[2] = False

		
            #CODE FOR BOTTOM PLAYER (COOK)       
	    #Checks for button 1. Must be lifted before this event will trigger again
            if(GPIO.input(25)==1 and buttonDown[1]==False):
                buttonDown[1]=True

		#If the player is at a cook station
                if (getPlayerPosition(1)>=5 and getPlayerPosition(1)<=7):
                    if(inventoryA==2):
                        cook[getPlayerPosition(1)-5] = inventoryA
                        cookTime[getPlayerPosition(1)-5]=150
                        inventoryA = 0
                    elif(inventoryA==0 and cook[getPlayerPosition(1)-5]>2):
                        inventoryA = cook[getPlayerPosition(1)-5]
                        cook[getPlayerPosition(1)-5] = 0
                        cookTime[getPlayerPosition(1)-5] = 0
                        lights[i-5].ChangeDutyCycle(0)

		#If the player's inventory is empty (picking up ingredients/collect)
                elif(inventoryA==0):
                    if(getPlayerPosition(1)==4):
                        inventoryA=5
                    elif(getPlayerPosition(1)==3):
                        inventoryA=7
                    elif(getPlayerPosition(1)==2):
                        inventoryA=1
                    elif(getPlayerPosition(1)==8):
                        inventoryA=collectA
                        collectA=0

		#If the player's inventory is not empty (trash/send)
                else:
                    if(getPlayerPosition(1)==1):
                        inventoryA=0
                    elif(getPlayerPosition(1)==0 and collectB==0):
                        collectB=inventoryA
                        inventoryA=0
                   
            #CODE FOR TOP PLAYER (CUT)       
	    #Checks for button 0. Must be lifted before this event will trigger again

            if(GPIO.input(24)==1 and buttonDown[0]==False):
                buttonDown[0]=True
                
		#If the player is at a cut station

                if (getPlayerPosition(0)>=4 and getPlayerPosition(0)<=6):
                    if(inventoryB==1 or inventoryB == 5 or inventoryB == 7):
                        cut[getPlayerPosition(0)-4] = inventoryB
                        cutTime[getPlayerPosition(0)-4]=100
                        inventoryB = 0
                    elif(inventoryB==0 and cut[getPlayerPosition(0)-4]!=0 and cutTime[getPlayerPosition(0)-4]==0):
                        inventoryB = cut[getPlayerPosition(0)-4]
                        cut[getPlayerPosition(0)-4] = 0

		#If the player is at a collect with empty inventory
                elif(inventoryB==0 and getPlayerPosition(0)==0):
                        inventoryB=collectB
                        collectB=0

		#If the player's inventory is not empty (trash/send/plates)
                else:
                    if (getPlayerPosition(0)>=1 and getPlayerPosition(0)<=3):
                        plates[getPlayerPosition(0)-1] += str(inventoryB)
                        inventoryB=0
                    elif(getPlayerPosition(0)==7):
                        inventoryB=0
                    elif(getPlayerPosition(0)==8 and collectA==0):
                        collectA=inventoryB
                        inventoryB=0

	    #CODE FOR SERVING ORDER (TOP PLAYER)
	    #Checks for button 2. Must be lifted before this event will trigger again
	    #If player is at a plate, serves the plate

            if(GPIO.input(22)==1  and buttonDown[2]==False):
                if (getPlayerPosition(0)>=1 and getPlayerPosition(0)<=3):
                    points += checkValidOrder(plates[getPlayerPosition(0)-1])
                    plates[getPlayerPosition(0)-1]=""


            if(lives<0):
                break
            
	    updateScreen(lives)
            
        displayGameOver(points)
     
except KeyboardInterrupt:
	pass
    
GPIO.cleanup()
pygame.quit () 
