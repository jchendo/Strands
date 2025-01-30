import os
import random
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
                   
        ## 8 rows x 6 columns (48 total letters)
        
        for i in range(8):
            ## Changes which row the squares are drawn on.
            rowCoord = 200 + (i*60)
            
            for j in range(6):
                colCoord = 20 + (j*60)
                ## Draw rectangles at an interval of 60 pixels, starting at 20 (to allow whitespace)
                pg.draw.rect(screen, self.color, pg.Rect(colCoord,rowCoord, 50, 50), border_radius=15)
                self.letter_locs[i][j] = (colCoord+20, rowCoord+15)
    
    def colorBoard(self,screen,squares=[],color='red', found_words=[]):

        if squares == [] and color=='red':

            for i in range(8):
                ## Changes which row the squares are drawn on.
                rowCoord = 200 + (i*60)
            
                for j in range(6):
                    colCoord = 20 + (j*60)
                    location = self.letter_locs[i][j]
                    letter = self.board[i][j]
                    text_surface = Strands.BOARD_FONT.render(letter, True, (0,0,0))
                    
                    if (i,j) in found_words:
                        pg.draw.rect(screen, 'yellow', pg.Rect(colCoord,rowCoord, 50, 50), border_radius=15)
                        Strands.screen.blit(text_surface, location)
                    else:
                        
                        ## Draw rectangles at an interval of 60 pixels, starting at 20 (to allow whitespace)
                        pg.draw.rect(screen, color, pg.Rect(colCoord,rowCoord, 50, 50), border_radius=15)
                        Strands.screen.blit(text_surface, location)

        else:

            for i in range(len(squares)):
                
                loc = squares[i]
                try:
                    location = self.letter_locs[loc]
                    letter = self.board[loc]
                    text_surface = Strands.BOARD_FONT.render(letter, True, (0,0,0))
                    pg.draw.rect(screen, color, pg.Rect(location[0]-20, location[1]-15, 50, 50), border_radius=15)
                    Strands.screen.blit(text_surface, location)
                except:
                    pass
                
    def fillBoard(self, words):
        ## to start
        curr_position = (np.random.randint(0,8), np.random.randint(0,6)) ## board pos
        self.board = np.empty((8,6), dtype='str')
        
        ## Algorithm for placing letters
        word_locs = {}
        start = time.time()
        game_title = words[0]
        spangram = words[1]
        words[len(words)-1] = words[len(words)-1].rstrip() ## white space at the end of .txt lines
        #self.board[curr_position] = words[1][0]
        
        for word in words:

            if word == game_title:

                title_text = Strands.GAME_FONT.render(game_title, True, (0,0,0))
                x_loc = (Strands.screen.get_width() / len(game_title)) + 30 ## this is pretty jank lol & doesn't scale that well but it's fine for now

                Strands.screen.blit(title_text, (x_loc,50,0,0))
                continue
            else:
                word_locs[word] = []

            for letter in word:
                text_surface =  Strands.BOARD_FONT.render(letter, True, (0, 0, 0))
                open_spots = self.openGridSquares(curr_position, open=True) ## this function runs assuming curr_position is a placed letter

                ## rewrite this loop (for pos in open_spots, if self.areEmptyConnected... etc)
                
                for pos in open_spots:
                    if self.areEmptyConnected(pos, start):
                        curr_position = pos
                        self.board[curr_position] = letter
                        break
                    
                word_locs[word].append(curr_position)
                Strands.screen.blit(text_surface, self.letter_locs[curr_position])
        print(word_locs) 
        
        return word_locs

    def openGridSquares(self, curr_position, open=True): ## returns list of open grid squares surrounding the given curr_position
        open_square_loc = []

        if open:

            try:

                for i in range(-1,2): ## has to have values -1, 0, 1 in order to get the rows above, equal, and below currLetterPos
                    if (curr_position[0] - i) >= 8 or (curr_position[0] - i) < 0:
                        continue
                    for j in range(-1,2): ## same logic for columns
                        if (curr_position[1] - j) >= 6 or (curr_position[1] - j) < 0:
                            continue
                        if self.board[(curr_position[0]-i,curr_position[1]-j)] == '':
                            open_square_loc.append((curr_position[0]-i, curr_position[1]-j))
            
                if len(open_square_loc) != 0:
                    return open_square_loc
                else:

                    return [(-1,-1)]
            except:

                return [(-1,-1)]

        else: ## just returns all adjacent squares 
            for i in range(-1,2): ## has to have values -1, 0, 1 in order to get the rows above, equal, and below currLetterPos
                    if (curr_position[0] - i) >= 8 or (curr_position[0] - i) < 0:
                        continue
                    for j in range(-1,2): ## same logic for columns
                        if (curr_position[1] - j) >= 6 or (curr_position[1] - j) < 0:
                            continue
                        open_square_loc.append((curr_position[0]-i, curr_position[1]-j))
            return open_square_loc

    def areEmptyConnected(self, letter_loc, start): ## boolean return function that says whether or not all empty squares would be connected if a certain letter is placed
        visited = np.zeros((8,6))
        #self.board[letter_loc] = ''
        visited[letter_loc] = 1
        adjacents = self.openGridSquares(letter_loc)
        #print(f'Adjacents: {adjacents}')

        filled_visited = self.boardFloodSearch(adjacents, visited)
        print(filled_visited)
        
        if time.time() - start >= 3:
            return True
        
        for x in range(8):
            for y in range(6):
                print(f'Board: {self.board[x][y]}\nPosition: {(x,y)}\nVisited: {filled_visited[x][y]}\n')
                if self.board[x][y] == '' and filled_visited[x][y] == 0:
                    #self.board[letter_loc] = ''
                    return False
        #self.board[letter_loc] = ''
        return True
        
    def boardFloodSearch(self, adjacents, visited):
        try:
            for square in adjacents:
                if visited[square] == 1:
                    continue
                else:
                    visited[square] = 1
                    new_adjacents = self.openGridSquares(square)
                    self.boardFloodSearch(new_adjacents, visited)
        except:
            return visited
        return visited

    def checkBoard(self):

        open_squares = []
        for i in range(8):
            for j in range(6):
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
    word_path = []
    word_locs = {}
    all_words = []
    found_words = []
    running = True
    start = True
    level_select = False
    page_num = 1
    settings = False
    ## CLASS VARIABLES

    def update(self, event):
        ## just updating screen for now
        if not self.start:
            self.screen.fill('pink')
            self.setup()
            if self.settings: ## this whole thing is a little jank & so laggy but it works for now
                pgw.update(event)

        else:
            
            if len(self.found_words) == 48:
                start = False
                print('You win!')

            if self.word_path in self.word_locs.values():
                    
                    #print(f'Congrats, you found the word {value}.')
                    self.board.colorBoard(self.screen, squares=self.word_path, color='yellow')
                    self.found_words.extend(self.word_path)
                    self.word_path = []
                    #time.sleep(10)
            else:
                    self.board.colorBoard(self.screen, squares=self.word_path, color=self.board.color, found_words=self.found_words)
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
        if not self.start and not self.level_select:

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
        elif self.level_select:       
            text = 'Level Select'
            ## (60 * page_num) per page (60 * page_num) + 60
            lower_range = 60 * self.page_num
            upper_range = lower_range + 60
            x_coord = 35
            y_coord = 140
            title_surface = self.GAME_FONT.render(text, True, 'red')
            self.screen.blit(title_surface, (80, 50))
            for i in range(lower_range, upper_range):
                level_num = i+1
                level_num_surface = self.BOARD_FONT.render(str(level_num), True, (0,0,0))
                text_surface = self.BOARD_FONT.render(text, True, (0,0,0))
                pg.draw.rect(self.screen, 'lightpink', pg.Rect(x_coord, y_coord, 50, 50), border_radius=15)
                self.screen.blit(level_num_surface, (x_coord+15,y_coord+10))
                if level_num % 5 == 0:
                    y_coord += 55
                    x_coord = 35
                else:
                    x_coord += 70
                

        elif self.start:
           
            self.screen.fill("pink") ## gets rid of all hearts & other stuff
            self.channel.fadeout(4000)

            self.board = Board(self.screen, self.GAME_FONT, self.BOARD_FONT)
            words = self.all_words[3]
            self.word_locs = self.board.fillBoard(words)

            return self.board
       
    def loadAssets(self):
        
        directory = "./dat"
        progress = 0
        dir_length = len(os.listdir(directory + '/pictures')) + len(os.listdir(directory + '/sounds'))
        
        fpath = "./dat/text/strands.txt" 
        text = open(fpath)
        
        
        for line in text.readlines():
            words = line.split(", ")
            self.all_words.append(words)

        for filename in os.listdir(directory + '/pictures'): ## images
            
            filepath = os.path.join(directory + '/pictures', filename)
            image = pg.image.load(filepath).convert_alpha()
            width, height = image.get_size()
            sf = 0.25
            
            image = pg.transform.scale(image, (width*sf, height*sf))
            self.pictures[filename] = image

            # progress bar 
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

                        self.level_select = True
                        self.setup()

                    elif ((mouse_pos[0] >= settings_loc[0] and mouse_pos[0] <= settings_loc[0] + 150) 
                    and (mouse_pos[1] >= settings_loc[1] and mouse_pos[1] <= settings_loc[1]+30)):

                        self.settings = True
                        self.setup()
                        # settings

                else: ## game board interaction handling

                    for i in range(8):
                        loc_list = self.board.letter_locs[i]
                        for j in range(6):
                            loc = self.board.letter_locs[i][j]

                            if ((mouse_pos[0] -  loc[0] > -25 and mouse_pos[0] - loc[0] <= 25) 
                            and (mouse_pos[1] -  loc[1] < 35 and mouse_pos[1] - loc[1] >= -15)):
                                
                                if (i,j) not in self.found_words:

                                    if (i,j) in self.word_path:
                                        self.word_path.remove((i,j))
                                        self.word_path.clear()
                                        self.board.color = 'red'
                                        self.board.colorBoard(self.screen)
                                    elif len(self.word_path) == 0:
                                        self.word_path.append((i,j))
                                        self.board.color = 'darkred'
                                    elif (i,j) in self.board.openGridSquares(self.word_path[len(self.word_path)-1], open=False):
                                        self.word_path.append((i,j))
                                        self.board.color = 'darkred'
                                    else:
                                        self.board.color = 'red'
                                else:
                                    continue
                                
                            

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
