import os
import pygame as pg
import numpy as np

## TO DO (not in any particular order) - complete by 02/19/25:
## 1. determine how to arrange words/letters randomly without isolating individual letters/making it impossible to construct remaining words
## 2. figure out how to save progress on a given game in case she wants to come back to it later
## 3. implement word/topic selection, likely using ChatGPT API (?)
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
    ## CLASS VARIABLES ## 

    def __init__(self, screen, GAME_FONT):
        
        ## asset loading
        fpath = "./dat/text/strands1.txt" 
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
            game_title = words[0]
            spangram = words[1]
            for word in words:
                if word == game_title:

                    title_text = Strands.GAME_FONT.render(game_title, True, (0,0,0))
                    x_loc = (Strands.screen.get_width() / len(game_title)) + 30 ## this is pretty jank lol & doesn't scale that well but it's fine for now

                    Strands.screen.blit(title_text, (x_loc,50,0,0))

                elif word == spangram:
                    continue
                
                for letter in word:
                    
                    text_surface = Strands.GAME_FONT.render(letter, False, (0, 0, 0))
                    next_position = self.detNextLetterPos(next_position, letter, word, spangram)
                    Strands.screen.blit(text_surface, next_position)
                    pg.display.flip()

    

    def checkGrid(self, pos):
        ## helper method for detNextLetterPos()
        ## takes pos input as board coords ([8,6]) and checks all adjacent squares'
        open_squares = []
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
    GAME_FONT = pg.font.SysFont('arial', 50, bold=True)
    pictures = {}
    screen = pg.display.set_mode((400, 867))
    running = True
    start = False
    ## CLASS VARIABLES

    def update():
        return

    def setup(self): 

        self.screen.fill("pink")
        pg.display.set_caption("Strands")

        title_text = self.GAME_FONT.render('STRANDS', True, (135, 20, 0))
        
        ## dictionary of all text i want on main screen to make it a little easier to place them all w/o a bunch of lines?
        ## idk of that'll work
        
        menu_text = {'I love you :)': (110, 150, 0, 0),'START': (150,600,0,0), 'SETTINGS': (115,700,0,0)} # ... etc
        home_screen_font = pg.font.SysFont('forte', 35) ## editing fonts (GAME_FONT) is dogshit in pygame so I just made a new one
        
        ## title text, if hasn't clicked start, board display otherwise
        if not self.start:
            
            self.screen.blit(self.pictures['heart.png'], (40,250,0,0))
            self.screen.blit(self.pictures['kiera1.jpeg'], (140,315,0,0))
            self.screen.blit(title_text, (100, 50, 0, 0))
            
            for text in menu_text:
                txt_surface = home_screen_font.render(text, True, (135, 20, 0))
                self.screen.blit(txt_surface,menu_text[text])

            return menu_text
                
        else:

            board = Board(self.screen, self.GAME_FONT)
            board.fillBoard()

            return board
       
    def loadAssets(self):
        
        directory = "./dat/pictures"

        for filename in os.listdir(directory):
            
            filepath = os.path.join(directory, filename)
            image = pg.image.load(filepath).convert_alpha()
            width, height = image.get_size()
            sf = 0.25
            
            image = pg.transform.scale(image, (width*sf, height*sf))
            self.pictures[filename] = image
    
    def eventHandler(self, text): ## probably a little jank to have text as an argument here but i don't think this needs to be super clean

        for event in pg.event.get():
            
            if event.type == pg.QUIT:
                self.running = False
                
            if event.type == pg.MOUSEBUTTONDOWN:

                mouse_pos = pg.mouse.get_pos()
                if not self.start:
                    ## check if on the start button/do other detection for buttons
                    start_loc = text['START']
                    settings_loc = text['SETTINGS']

                    if ((mouse_pos[0] >= start_loc[0] and mouse_pos[0] <= start_loc[0] + 80) 
                    and (mouse_pos[1] >= start_loc[1] and mouse_pos[1] <= start_loc[1]+30)):

                        self.start = True
                        self.setup()

                    elif mouse_pos:
                        pass
                        # settings

                else:
                    ## game board interaction handling
                    pass
                
                
    ## core loop
    def run(self):
        
        self.loadAssets()
        text = self.setup() ## setup returns a dictionary w/ title text & their respective locations. 
                            ## helpful for checking if buttons have been pressed; see eventHandler()
        while self.running:

            self.eventHandler(text)
            pg.display.flip()
            
        pg.quit()

def main():
    
    pg.init()
    
    game = Strands()
    game.run()

if __name__ == main():
    main()
