
from os import system
import pygame as pg
import numpy as np

## TO DO (not in any particular order) - complete by 02/19/25:
## 1. determine how to arrange words/letters randomly without isolating individual letters/making it impossible to construct remaining words
## 2. figure out how to save progress on a given game in case she wants to come back to it later
## 3. implement word/topic selection, likely using ChatGPT API (?)
## 4. port game to an iOS friendly language/developing environment
## -----side bar, 4 might be very difficult. I believe Unity is capable of iOS development, but I haven't used it in a while.
## 5. different difficulty levels?
## 6. general setup & visuals, home screen, etc.
## 7. OPTIONAL, kinda: implement network connectivity so we can play together? or perhaps just so it can be a web app before iOS.

## board object since i'm assuming we'll have multiple (?) at once
class Board:

    pg.font.init()

    ## CLASS VARIABLES ##
    board = np.empty([8,6],dtype=str) ## going to be letters
    letter_locs = np.empty([8,6],dtype=tuple)
    all_words = []
    GAME_FONT = pg.font.SysFont('arial', 50)
    ## CLASS VARIABLES ## 

    def __init__(self, screen):
        
        ## asset loading
        fpath = "./dat/strands1.txt"
        text = open(fpath)
        for line in text.readlines():
            words = line.split(", ")
            self.all_words.append(words)
                   
        ## 8 rows x 6 columns (48 total letters)
        
        for i in range(8):
            ## Changes which row the squares are drawn on.
            rowCoord = 200 + (i*60)
            
            for j in range(6):
                colCoord = 20 + (j*60)
                ## Draw rectangles at an interval of 60 pixels, starting at 20 (to allow whitespace)
                pg.draw.rect(screen, "red", pg.Rect(colCoord,rowCoord, 50, 50), border_radius=15)
                self.letter_locs[i][j] = (colCoord, rowCoord)
                pg.display.flip()
                
    def fillBoard(self):
        ## to start
        next_position = np.random.choice(self.letter_locs[:][1])
        ## Algorithm for placing letters
        for words in self.all_words:
            gameTitle = words[0]
            
            for word in words:
                if word == gameTitle:
                    continue
                elif word == words[1]:
                    spangram = word
                
                for letter in word:
                    
                    text_surface = self.GAME_FONT.render(letter, False, (0, 0, 0))
                    next_position = self.detNextLetterPos(next_position, letter, word, spangram)
                    Strands.screen.blit(text_surface, next_position)
                    pg.display.flip()

    

    def checkGrid(self, pos):
        ## helper method for detNextLetterPos()
        ## takes pos input as board coords ([8,6]) and checks all adjacent squares'
        open_squares = []
        print("meow")
        try:
            ## check left edge
            for i in range(-1,2):
                square = self.board[pos[0]-1][pos[1]-i]
                if square == '':
                    open_squares.append(square)
                    print(open_squares)
        except IndexError:
            pass
            ## put this in a loop
    def detNextLetterPos(self, currLetterPos, letter, word, spangram):
        ## figure out where to place the next letter to ensure no islands
        try:
            self.checkGrid(currLetterPos)
        except:
            pass
        
        return currLetterPos
        
## put the game in a class for cleanliness
## not sure if it's really necessary

class Strands:
    
    ## CLASS VARIABLES
    screen = pg.display.set_mode((400, 867))
    running = True
    ## CLASS VARIABLES

    def update():
        return

    def envSetup(self): 
        self.screen.fill("pink")
        pg.display.set_caption("Strands")

        print("setup complete")
    
    def eventHandler(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.running = False
                
    ## core loop
    def run(self):
        
        self.envSetup() ## redundant for now
        board = Board(self.screen)
        board.fillBoard()
        
        while self.running:
            
            self.eventHandler()
            pg.display.flip()
            
        pg.quit()

def main():
    
    pg.init()
    
    game = Strands()
    game.run()

if __name__ == main():
    main()
