import os
import time
import pygame as pg
import numpy as np
import threading

from pygame.mixer import music
import pygame_widgets as pgw ##  type: ignore
from pygame_widgets.slider import Slider # type: ignore

## TO DO (not in any particular order) - complete by 02/19/25:
## 1. determine how to arrange words/letters randomly without isolating individual letters/making it impossible to construct remaining words
## 2. figure out how to save progress on a given game in case she wants to come back to it later
## 3. implement word/topic selection, likely using ChatGPT API (?)
## 5. different difficulty levels?
## 6. general setup & visuals, home screen, etc.
## 7. OPTIONAL, kinda: implement network connectivity so we can play together? or perhaps just so it can be a web app before iOS.

## board object since i'm assuming we'll have multiple (?) at once
class Board:

    #pg.font.init()

    ## CLASS VARIABLES ##
    board = np.empty([8,6],dtype=str) ## going to be letters
    color = "red"
    letter_locs = np.empty([8,6],dtype=tuple)
    all_words = []
    ## CLASS VARIABLES ## 

    def __init__(self, screen, GAME_FONT, BOARD_FONT):
        
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
                pg.draw.rect(screen, self.color, pg.Rect(colCoord,rowCoord, 50, 50), border_radius=15)
                self.letter_locs[i][j] = (colCoord+20, rowCoord+15)
    
    def colorBoard(self,screen,squares=[]):

        if squares == []:

            for i in range(8):
                ## Changes which row the squares are drawn on.
                rowCoord = 200 + (i*60)
            
                for j in range(6):
                    colCoord = 20 + (j*60)
                    ## Draw rectangles at an interval of 60 pixels, starting at 20 (to allow whitespace)
                    pg.draw.rect(screen, self.color, pg.Rect(colCoord,rowCoord, 50, 50), border_radius=15)

        else:
            for i in squares:
                try:
                    location = self.letter_locs[i]
                    letter = self.board[i]
                    text_surface = Strands.BOARD_FONT.render(letter, True, (0,0,0))
                    pg.draw.rect(screen, self.color, pg.Rect(location[0]-20, location[1]-15, 50, 50), border_radius=15)
                    Strands.screen.blit(text_surface, location)
                except:
                    print(i)
                
    def fillBoard(self):
        ## to start
        curr_position = (np.random.randint(0,9), np.random.randint(0,7)) ## board pos
        ## Algorithm for placing letters
        word_locs = {}
        start = time.time()
        for words in self.all_words:
            game_title = words[0]
            spangram = words[1]
            for word in words:
                word_locs[word] = []
                
                
                #self.colorBoard(Strands.screen)

                if word == game_title:

                    title_text = Strands.GAME_FONT.render(game_title, True, (0,0,0))
                    x_loc = (Strands.screen.get_width() / len(game_title)) + 30 ## this is pretty jank lol & doesn't scale that well but it's fine for now

                    Strands.screen.blit(title_text, (x_loc,50,0,0))
                    continue
                
                for letter in word:

                    text_surface =  Strands.BOARD_FONT.render(letter, True, (0, 0, 0))
                    next_position = self.openGridSquares(curr_position)[0]
                    word_locs[word].append(next_position)
                   
                    while not self.areEmptyConnected(next_position, start) and not self.checkBoard():
                        
                        open_spots = self.openGridSquares(curr_position)
                        if open_spots == [(0,0)]:
                            open_spots = self.checkBoard()[1] ## will hopefully prevent islands by identifying open areas & filling them
                        next_position = open_spots[np.random.choice(len(open_spots))]
                        
                    curr_position = next_position
                    ## the below line throws an error for now due to areEmptyConnected() not being implemented yet
                    self.board[curr_position] = letter
                    
                    Strands.screen.blit(text_surface, self.letter_locs[curr_position])
                
                #time.sleep(0.12)
                #self.color = np.random.choice(['blue', 'red', 'yellow', 'orange', 'green', 'purple', 'brown'], replace=False)
                #self.colorBoard(Strands.screen,squares=word_locs[word])

    def openGridSquares(self, curr_position): ## returns list of open grid squares surrounding the given curr_position
        open_square_loc = []

        try:

            for i in range(-1,2): ## has to have values -1, 0, 1 in order to get the rows above, equal, and below currLetterPos
                if (curr_position[0] - i) >= 8 or (curr_position[0] - i) < 0:
                    continue
                for j in range(-1,2): ## same logic for columns
                    if (curr_position[1] - j) >= 6 or (curr_position[1] - j) < 0:
                        continue
                    if self.board[curr_position[0]-i][curr_position[1]-j] == '':
                        open_square_loc.append((curr_position[0]-i, curr_position[1]-j))
            
            if len(open_square_loc) != 0:
                return open_square_loc
            else:

                return [(0,0)]
        except:

            return [(0,0)]

    def areEmptyConnected(self, letter_loc,start): ## boolean return function that says whether or not all empty squares would be connected if a certain letter is placed
        
        ## identify if once a letter is placed, all empty spots are connected

        #self.board[letter_loc] = ''
        positions = self.openGridSquares(letter_loc)
        path = [letter_loc]

        for pos in positions:
            
            elapsed = time.time() - start

            if elapsed >= 5:
                self.board[letter_loc] = ''
                return True ## exit in case of issue

            next_pos = self.openGridSquares(pos)
            common = set(next_pos) & set(path) ## checks to see if any values are in common between path & positions -- important to not backtrack
            
            if len(next_pos) > 0 and pos not in common:
                positions = next_pos ## pseudo recursion, essentially just finds the first path that allows all white squares to be connected
                path.append(pos)

            else:
                if self.checkBoard()[0]:
                    return True
                self.board[letter_loc] = ''
                return False

    def checkBoard(self):

        open_squares = []
        for i in range(len(self.board[0])):
            for j in range(len(self.board[1])):
                if self.board[i][j] == '':
                    open_squares.append((i,j))
        if len(open_squares) == 0:
            return True, [(0,0)] ## if the board is full, return True & send 0,0
        return False, open_squares ## else show me the open squares!!!!    


class Strands:
    
    ## INITS
    pg.mixer.init()
    pg.font.init()
    ## CLASS VARIABLES
    GAME_FONT = pg.font.SysFont('arial', 50, bold=True)
    BOARD_FONT = pg.font.SysFont('arial', 25)
    pictures = {}
    songs = {}
    title_screen_song = 'Honey.mp3'
    music_volume = 0
    channel = pg.mixer.Channel(0)
    screen = pg.display.set_mode((400, 867))
    volume_slider = pgw.slider.Slider(screen, 250, 50, 100, 25, min=0, max=99, initial = music_volume * 100)
    running = True
    start = False
    settings = False
    ## CLASS VARIABLES

    def update(self, event):
        ## just updating screen for now
        if not self.start:
            self.screen.fill('pink')
            self.setup()
            if self.settings: ## this whole thing is a little jank & so laggy but it works for now
                pgw.update(event)
        pg.display.update()

    def spawnHearts(self):
        ## animates the hearts that appear on the homescreen
        sf = 0.05
        num_hearts = 50 ## number to appear on screen at once
        heart = self.pictures['heart.png']
        width, height = heart.get_size()
        heart = pg.transform.scale(heart, (width*sf, height*sf))

        heart_locs = []

        for i in range(num_hearts):
           x_coords = np.random.randint(0, self.screen.get_width(), size=num_hearts)
           y_coords = np.random.randint(-1000, 0, size=num_hearts) ## spawns some outside the screen to stagger the waterfall
           heart_locs.append([x_coords[i], y_coords[i]])
            
        while not self.start:
            pg.time.delay(20)
            self.animateHearts(heart,heart_locs)
                  
    def animateHearts(self, heart,heart_locs):
        
        y_coord = 0

        for i in range(len(heart_locs)):
            
            self.screen.blit(heart, heart_locs[i])
            heart_locs[i][1] += 1
            heart_locs[i][0] += np.random.uniform(-0.33, 0.15) + 0.33

            if heart_locs[i][0] >= self.screen.get_width():
                heart_locs[i][0] = -15

            if heart_locs[i][1] >= self.screen.get_height():
                heart_locs[i] = [np.random.randint(0, self.screen.get_width()),np.random.randint(-1000, -25)]

        return

    def setup(self): 
        
        pg.display.set_caption("Strands")

        title_text = self.GAME_FONT.render('STRANDS', True, (135, 20, 0))
        
        ## dictionary of all text i want on main screen to make it a little easier to place them all w/o a bunch of lines?
        
        menu_text = {'I love you :)': (110, 150, 0, 0),'START': (150,600,0,0), 'SETTINGS': (115,700,0,0)} # ... etc
        home_screen_font = pg.font.SysFont('forte', 35) ## editing fonts (GAME_FONT) is dogshit in pygame so I just made a new one
        
        if not self.channel.get_busy():
            self.channel.set_volume(self.music_volume)
            self.channel.play(self.songs[self.title_screen_song])
        
        ## title text, if hasn't clicked start, board display otherwise
        if not self.start:

            if not self.settings: ## different setup for settings menu vs. just reg homescreen
                self.screen.blit(self.pictures['heart.png'], (40,250,0,0))
                self.screen.blit(self.pictures['kiera1.jpeg'], (140,315,0,0))
                self.screen.blit(title_text, (100, 50, 0, 0))
            
                for text in menu_text:
                    txt_surface = home_screen_font.render(text, True, (135, 20, 0))
                    self.screen.blit(txt_surface,menu_text[text])

                return menu_text

            else:
                # settings
                self.screen.blit(pg.transform.scale(self.pictures['back_button.png'], (64,64)), (0,0,0,0))
                self.music_volume = self.volume_slider.getValue() / 100
                self.channel.set_volume(self.music_volume)
                          
        else:
           
            self.screen.fill("pink") ## gets rid of all hearts & other stuff
            self.channel.fadeout(4000)

            board = Board(self.screen, self.GAME_FONT, self.BOARD_FONT)
            board.fillBoard()

            return board
       
    def loadAssets(self):
        
        directory = "./dat"
        progress = 0
        dir_length = len(os.listdir(directory + '/pictures')) + len(os.listdir(directory + '/sounds'))

        for filename in os.listdir(directory + '/pictures'): ## images
            
            filepath = os.path.join(directory + '/pictures', filename)
            image = pg.image.load(filepath).convert_alpha()
            width, height = image.get_size()
            sf = 0.25
            
            image = pg.transform.scale(image, (width*sf, height*sf))
            self.pictures[filename] = image

            progress += 1
            percent = float(progress / dir_length) 
            loading_bar = pg.Surface((350*percent, 30))
            loading_outline = pg.Surface((360*percent, 40))
            loading_bar.fill('white')
            loading_outline.fill('pink')

            self.screen.blit(loading_outline, (15, 745))
            self.screen.blit(loading_bar, (20, 750))
            pg.display.flip()

            time.sleep(0.01)
    
        for filename in os.listdir(directory + '/sounds'):

            filepath = os.path.join(directory + '/sounds', filename)
            song = pg.mixer.Sound(filepath)
            self.songs[filename] = song

            progress += 1
            percent = float(progress / dir_length)
            loading_bar = pg.Surface((350*percent, 30))
            loading_outline = pg.Surface((360*percent, 40))
            loading_bar.fill('white')
            loading_outline.fill('pink')

            self.screen.blit(loading_outline, (15, 745))
            self.screen.blit(loading_bar, (20, 750))
            pg.display.flip()

            time.sleep(0.01)

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

                    if self.settings:
                            
                        if ((mouse_pos[0] >= 0 and mouse_pos[0] <= 64) 
                        and (mouse_pos[1] >= 0 and mouse_pos[1] <= 64)):

                            self.settings = False
                            self.setup()

                    if ((mouse_pos[0] >= start_loc[0] and mouse_pos[0] <= start_loc[0] + 80) 
                    and (mouse_pos[1] >= start_loc[1] and mouse_pos[1] <= start_loc[1]+30)):

                        self.start = True
                        self.setup()

                    elif ((mouse_pos[0] >= settings_loc[0] and mouse_pos[0] <= settings_loc[0] + 150) 
                    and (mouse_pos[1] >= settings_loc[1] and mouse_pos[1] <= settings_loc[1]+30)):

                        self.settings = True
                        self.setup()
                        # settings

                else:
                    ## game board interaction handling
                    pass

            return event
                           
    ## core loop
    def run(self):
        
        self.loadAssets()
        text = self.setup() ## setup returns a dictionary w/ title text & their respective locations. 
                            ## helpful for checking if buttons have been pressed; see eventHandler()
        thread = threading.Thread(target=self.spawnHearts, daemon=True)
        thread.start()
        
        while self.running:

            event = self.eventHandler(text)
            self.update(event)
            
        pg.quit()

def main():
    
    pg.init()
    
    game = Strands()
    game.run()

if __name__ == main():
    main()
