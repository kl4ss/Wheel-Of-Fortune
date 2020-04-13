import random
import os
import turtle
from threading import Timer

# Fixed Variables:
BASE_DIR = os.getcwd()
NUMBER_OF_PLAYERS = 3
PUZZLE_DEFAULT =  "GET THE FRUSTRATION OUT OF YOUR SYSTEM"
VOWELS = ["A", "E", "I", "O", "U"]
# FONT = "Calibri"
FONT = "Century Gothic"
# BACKGROUND_COLOR = "#ffc4e4"
BACKGROUND_COLOR = "#40e0d0"

# Screen Set Up
window = turtle.Screen()
window.title("Wheel Of Fortune")
window.setup(width=1.0, height=1.0)
turtle.bgcolor(BACKGROUND_COLOR)
turtle.speed(0)
turtle.penup()

# Write Welcome
turtle.pencolor("white")
turtle.setpos(0, 350)
turtle.write("WHEEL OF FORTUNE", align="center", font=(FONT, 30, "bold"))
turtle.penup()
turtle.hideturtle()


# Application Functions
def load_phrases(file):
    phrases = []
    phrases_file = open(file=file, mode="r")
    for line in phrases_file:
        line = line.rstrip("\n")
        if line != "":
            phrases.append(line)
    return phrases

def is_a_vowel(alphabet):
    return alphabet.upper() in VOWELS

def findnth(haystack, needle, n):
    parts = haystack.split(needle, n+1)
    if len(parts)<=n+1:
        return -1
    return len(haystack)-len(parts[-1])-len(needle)


# Objects For Wheel Of Fortune
class Game:
    def __init__(self):
        self.players = []
        self.phrases = load_phrases(os.path.join(BASE_DIR, "WofFPhrases.txt"))
        self.wheel = Wheel(radius=250)
        self.puzzle = None
        self.current_player_number = 1

    def find_player(self, player_number):
        for player in self.players:
            if player.player_number == player_number:
                return player

    def game_results(self):
        for player in self.players:
            print("Player {0}: {1} - ${2}".format(player.player_number, player.name, player.money))
    
    def next_player(self):
        if self.current_player_number == NUMBER_OF_PLAYERS: 
            self.current_player_number = 1
        else:
            self.current_player_number += 1
    
    def play(self):
        self.puzzle = Puzzle(random.choice(self.phrases))
        while not self.puzzle.is_solved():
            player = self.find_player(self.current_player_number)
            self.puzzle.display()
            print()
            self.game_results()
            print("\n{}'s Turn\n".format(player.name))
            print("\nSpinning The Wheel...\n")
            outcome = self.wheel.spin()

            if outcome == "Bankrupt":
                print("\n{} got bankrupt!\n".format(player.name))
                player.money = 0
                self.next_player()
            elif outcome == "Lose A Turn":
                print("\n{} loses a turn!\n".format(player.name))
                self.next_player()
            else:
                print("${}".format(outcome))
                # Start Passive Timer
                t = Timer(10.0, print, ['Sorry, times up!'])
                t.start()
                letter = ""
                valid_input = False
                while not valid_input:
                    letter = input("Guess a letter, you have 10 seconds: ")
                    if t.is_alive():
                        if letter == "":
                            print("Letter cannot be empty!")
                        elif len(letter) > 1:
                            print("You entered more than one letters.")
                        else:
                            if letter.isalpha():
                                if letter in self.puzzle.list_form:
                                    print("{} already found in the puzzle!".format(letter))
                                else:   
                                    # If letter is vowel deduct $250
                                    if is_a_vowel(letter):
                                        if outcome == "Free Play":
                                            print("{0} used Free Play for the vowel '{1}'".format(player.name, letter.upper()))
                                            valid_input = True
                                        else:
                                            if player.money < 250:
                                                print("Not enough money to buy a vowel.")
                                            else:
                                                print("{0} bought the vowel '{1}'".format(player.name, letter.upper()))
                                                player.money -= 250
                                                valid_input = True
                                    else:
                                        valid_input = True
                            else:
                                print("Please enter a valid alphabet!")
                    else:
                        valid_input = True
                t.cancel()
                
                # Check if passive timer exceeded 10 seconds
                if t.is_alive():
                    del t # Delete the timer instance for memory management
                    if self.puzzle.check(letter):
                        number_of_letters = self.puzzle.count_letters(letter)
                        print("You've guessed it! There are {0} '{1}'(s)".format(number_of_letters, letter))
                        if not outcome == "Free Play" and not is_a_vowel(letter):
                            player.money += (number_of_letters * outcome)
                        self.puzzle.fill_letter(letter)
                        self.puzzle.display()
                        self.game_results()
                        if not self.puzzle.is_solved():
                            valid_input = False
                            want_to_solve = ""
                            while not valid_input:
                                want_to_solve = input("\nWould you like to solve the puzzle ? (Y/N): ")
                                if want_to_solve == "Y" or want_to_solve == "N":
                                    valid_input = True
                                else:
                                    print("Please enter only 'Y' or 'N'.")
                            if want_to_solve == "Y":
                                solve_attempt = input("Solve the puzzle: ")
                                self.puzzle.solve(solve_attempt)
                                if self.puzzle.is_solved():
                                    self.puzzle.list_form = list(self.puzzle.phrase)
                                    self.puzzle.display()
                                    print("Congratulations! {} solved the puzzle!".format(player.name))
                                    for p in self.players:
                                        if p != player:
                                            p.money = 0
                                else:
                                    print("Sorry {}, your answer is incorrect!".format(player.name))
                                    self.next_player()
                    else:
                        print("\nSorry the puzzle does not contain the letter {}.\n".format(letter.upper()))
                        if not outcome == "Free Play":
                            self.next_player()
                else:
                    del t # Delete the timer instance for memory management
                    self.next_player()
        print("\nFinal Results")
        self.game_results()

    def setup(self):
        print("\nPlayers, please enter your name.\n")
        for count in range(NUMBER_OF_PLAYERS):
            player_number = count + 1
            valid_input = False
            name = ""
            while not valid_input:
                print("Player {}:".format(player_number))
                name = input("Enter a name: ")
                if name != "":
                    valid_input = True
                else:
                    print("Name cannot be empty!")
            self.players.append(Player(name, player_number))

    def start(self):
        print("Welcome To Wheel Of Fortune!")
        self.setup()
        self.play()
        

class Wheel:
    def __init__(self,  radius):
        self.radius = radius
        self.sectors = [550, 800, 300, 700, 900, 500, 5000, 'Bankrupt',
                        300, 500, 450, 500, 800, 'Lose A Turn', 700, 'Free Play',
                        650, 'Bankrupt', 600, 500, 350, 600, 500, 400]
        self.colors = ['#d40ae1', '#ffa700', '#32d0ff', '#ff4141', '#fdff0d', '#5cc30c', '#dedede', '#000000', 
                       '#ffa700', '#5cc30c', '#ff79bc', '#d40ae1', '#ff4141', '#ffffff', '#32d0ff', '#009619',
                       '#d40ae1', '#000000', '#ff79bc', '#5cc30c', '#32d0ff', '#ff4141', '#ff79bc', '#fdff0d']
        self.current_sector = 0
        self.arrow_turtle = turtle.Turtle()
        self.arrow_turtle.speed(0)
        self.arrow_turtle.hideturtle()
        self.render()

    def render(self, center=(0, 80)):
        wheel_turtle = turtle.Turtle()
        wheel_turtle.speed(0)

        wheel_text_turtle = turtle.Turtle()
        wheel_text_turtle.speed(0)
        wheel_text_turtle.penup()

        slice_angle = 360 / len(self.sectors)
        heading, position = 90, (center[0] + self.radius, center[1])

        for count, color in enumerate(self.colors):
            wheel_turtle.color(color)
            wheel_turtle.penup()
            wheel_turtle.goto(position)
            wheel_turtle.setheading(heading)
            wheel_turtle.pendown()
            wheel_turtle.begin_fill()

            # Fix Alignment Of Text (Need To Hard Code)
            if count == 0:
                wheel_text_turtle.setposition(position[0] - 40, position[1]+20)
            elif count == 1:
                wheel_text_turtle.setposition(position[0] - 45, position[1]+15)
            elif count == 2:
                wheel_text_turtle.setposition(position[0] - 50, position[1]+10)
            elif count == 3:
                wheel_text_turtle.setposition(position[0] - 50, position[1])
            elif count == 4:
                wheel_text_turtle.setposition(position[0] - 50, position[1]-10)    
            elif count == 5:
                wheel_text_turtle.setposition(position[0] - 50, position[1]-20)    
            elif count == 6:
                wheel_text_turtle.setposition(position[0] - 45, position[1]-30)
            elif count == 7:
                wheel_text_turtle.setposition(position[0] - 55, position[1]-35)
            elif count == 8:
                wheel_text_turtle.setposition(position[0] - 30, position[1]-40)
            elif count == 9:
                wheel_text_turtle.setposition(position[0] - 20, position[1]-45)    
            elif count == 10:
                wheel_text_turtle.setposition(position[0] - 10, position[1]-45)    
            elif count == 11:
                wheel_text_turtle.setposition(position[0], position[1]-45)
            elif count == 12:
                wheel_text_turtle.setposition(position[0] + 10, position[1]-40)
            elif count == 13:
                wheel_text_turtle.setposition(position[0] + 10, position[1]-30)
            elif count == 14:
                wheel_text_turtle.setposition(position[0] + 25, position[1]-25)
            elif count == 15:
                wheel_text_turtle.setposition(position[0] + 10, position[1]-10)    
            elif count == 16:
                wheel_text_turtle.setposition(position[0] + 20, position[1]-10)    
            elif count == 17:
                wheel_text_turtle.setposition(position[0] + 5, position[1])  
            elif count == 18:
                wheel_text_turtle.setposition(position[0] + 15, position[1]+10)
            elif count == 19:
                wheel_text_turtle.setposition(position[0] + 10, position[1]+20)
            elif count == 20:
                wheel_text_turtle.setposition(position[0] + 5, position[1]+20)
            elif count == 21:
                wheel_text_turtle.setposition(position[0] - 5, position[1]+25)    
            elif count == 22:
                wheel_text_turtle.setposition(position[0] - 20, position[1]+30)    
            elif count == 23:
                wheel_text_turtle.setposition(position[0] - 30, position[1]+30)  
            else:
                wheel_text_turtle.setposition(position[0], position[1])

            wheel_text_turtle.pencolor("black")
            if isinstance(self.sectors[count], int):
                wheel_text_turtle.write("${}".format(self.sectors[count]), font=(FONT, 10, "bold"))
            else:
                if self.sectors[count] == "Bankrupt" or self.sectors[count] == "Free Play":
                     wheel_text_turtle.pencolor("white")
                wheel_text_turtle.write(self.sectors[count], font=(FONT, 10, "bold"))

            wheel_turtle.circle(self.radius, extent=slice_angle)
            heading, position = wheel_turtle.heading(), wheel_turtle.position()
            wheel_turtle.penup()
            wheel_text_turtle.penup()
            wheel_turtle.goto(center)
            wheel_turtle.end_fill()
    
        wheel_turtle.hideturtle()
        wheel_text_turtle.hideturtle()
    
        # Render Arrow
        self.arrow_turtle.goto(center)
        self.arrow_turtle.left(0.5*slice_angle)
        self.arrow_turtle.color("#6e6e6e")
        self.arrow_turtle.pensize(10)
        self.arrow_turtle.pendown()
        self.arrow_turtle.forward(self.radius - 75)
        self.arrow_turtle.penup()
        self.arrow_turtle.hideturtle()


    def spin(self):
        index = random.randrange(0, len(self.sectors))
        self.spin_to(index)
        return self.sectors[index] 

    def spin_to(self, target, center=(0,80)):
        slice_angle = 360 / len(self.sectors)
        if target < self.current_sector:
            number_of_rotations = (len(self.sectors) - self.current_sector) + target
            current = self.current_sector
            for count in range(number_of_rotations):
                current += 1
                self.arrow_turtle.reset()
                self.arrow_turtle.speed(0)
                self.arrow_turtle.penup()
                self.arrow_turtle.goto(center)
                self.arrow_turtle.left((0.5*slice_angle) + (current%24)*slice_angle)
                self.arrow_turtle.color("#6e6e6e")
                self.arrow_turtle.pensize(10)
                self.arrow_turtle.pendown()
                self.arrow_turtle.forward(self.radius - 75)
                self.arrow_turtle.penup()
                self.arrow_turtle.hideturtle()
            
        for count in range(self.current_sector, target+1):
            self.arrow_turtle.reset()
            self.arrow_turtle.penup()
            self.arrow_turtle.goto(center)
            self.arrow_turtle.left((0.5*slice_angle) + count*slice_angle)
            self.arrow_turtle.color("#6e6e6e")
            self.arrow_turtle.pensize(10)
            self.arrow_turtle.pendown()
            self.arrow_turtle.forward(self.radius - 75)
            self.arrow_turtle.penup()
            self.arrow_turtle.hideturtle()
        self.current_sector = target

class Puzzle:
    def __init__(self, phrase):
        self.list_form = []
        self.turtles = []
        self.phrase = phrase
        self.solved = False
        self.generate_list_form()

    def count_letters(self, alphabet):
        count = 0
        for letter in self.phrase:
            if letter == alphabet.upper():
                count += 1
        return count

    def check(self, alphabet):
        return alphabet.upper() in self.phrase
    
    def display(self):
        self.render()
        print("".join(self.list_form))

    def fill_letter(self, alphabet):
        for count, letter in enumerate(self.phrase):
            if alphabet.upper() == letter:
                self.list_form[count] = letter
        if "".join(self.list_form) == self.phrase:
            self.solved = True

    def is_solved(self):
        return self.solved

    def generate_list_form(self):
        for character in self.phrase:
            if character == " ":
                self.list_form.append(" ")
            else:
                self.list_form.append("_")
    
    def render(self):
        x_pos, y_pos = -650, -200
        space_count =  0
        for count, character in enumerate(self.list_form):
            if character == " ":
                # Bring over long words into next row
                space_count += 1
                next_space = findnth(self.phrase," ",space_count)
                word = ""
                if next_space == -1:
                    word = self.phrase[findnth(self.phrase," ",space_count-1):]
                else:
                    word = self.phrase[findnth(self.phrase," ",space_count-1):next_space]
                if x_pos + (len(word) * 50) + 30 >= 650:
                    x_pos = -650
                    y_pos -= 60
                if x_pos > -650:
                    x_pos += 30
            else:
                letter_turtle = turtle.Turtle()
                letter_turtle.speed(0)
                letter_turtle.penup()
                letter_turtle.goto(x_pos, y_pos)
                letter_turtle.color("black")
                letter_turtle.pensize(5)
                letter_turtle.pendown()
                letter_turtle.forward(40)
                letter_turtle.right(90)
                letter_turtle.forward(40)
                letter_turtle.right(90)
                letter_turtle.forward(40)
                letter_turtle.right(90)
                letter_turtle.forward(40)
                letter_turtle.right(90)
                letter_turtle.penup()
                if character.isalpha():
                    letter_turtle.forward(20)
                    letter_turtle.right(90)
                    letter_turtle.forward(35)
                    letter_turtle.color("black")
                    letter_turtle.write(character, align="center", font=(FONT, 20, "bold"))
                    letter_turtle.hideturtle()
                letter_turtle.hideturtle()
                self.turtles.append(letter_turtle)
                x_pos += 50
            if x_pos >= 650:
                x_pos = -650
                y_pos -= 60
        # for letter in self.list_form:
        #     letter_turtle = turtle.Turtle 

        # pass

    def solve(self, phrase):
        if self.phrase == phrase.upper():
            self.solved = True

class Player:
    def __init__(self, name, player_number):
        self.name = name
        self.money = 0
        self.player_number = player_number
        self.round_amounts = []

if __name__ == "__main__":
    game = Game()
    game.start()