import json
import random
import tkinter as tk
from tkinter import simpledialog, messagebox

class Flashcard:
    # class constructor
    def __init__(self, question, choices, correct_answer, incorrect_attempts=0, correct_attempts=0):
        self.question = question
        self.choices = choices
        self.correct_answer = correct_answer
        self.incorrect_attempts = incorrect_attempts
        self.correct_attempts = correct_attempts

    # display question chen playing
    def ask_question(self):
        print(self.question)
        for idx, choice in enumerate(self.choices, 1):
            print(f"{idx}. {choice}")

        while True:
            try:
                # retrieve user choice and check if correct answer or not
                user_answer = int(input("Enter your answer (number): "))
                if 1 <= user_answer <= len(self.choices):
                    if self.choices[user_answer - 1] == self.correct_answer:
                        print("Correct!")
                        self.correct_attempts += 1
                    else:
                        print("Incorrect. The correct answer was:", self.correct_answer)
                        self.incorrect_attempts += 1
                    break
                # handle invalid input
                else:
                    print("Please enter a number between 1 and", len(self.choices))
            except ValueError:
                print("Invalid input. Please enter a number.")


    # convert flashcard into dictionary format for json storing
    def to_dict(self):
        return {
            "question": self.question,
            "choices": self.choices,
            "correct_answer": self.correct_answer,
            "incorrect_attempts": self.incorrect_attempts,
            "correct_attempts": self.correct_attempts
        }

# list all flashcards in the flashcard bank
def list_flashcards(flashcard_bank):
    for index, flashcard in enumerate(flashcard_bank, start=1):
        print(f"{index}. {flashcard.question}")

# edit flashcard
def edit_flashcard(flashcard):
    print("Current question: ", flashcard.question)
    # get new question input from the user
    new_question = input("Enter the new question (press enter if you want to keep the current)")
    if new_question:
        flashcard.question = new_question

    print("Current choices : ", ','.join(flashcard.choices))
    # get new choices input from the user
    new_choices = input("Enter the new answer choices, separated by a comma (press enter to keep the current choices) : ")
    if new_choices:
        flashcard.choices = [choice.strip() for choice in new_choices.split(',')]

    print("Current correct answer: ", flashcard.correct_answer)
    # get new correct answer input from the user
    new_answer = input("Enter the new correct answer (press enter to keep the current answer): ")
    if new_answer:
        flashcard.correct_answer = new_answer

# delete flashcard
def delete_flashcard(flashcard_bank, index):
    del flashcard_bank[index]

# let the user pick the flashcard
def choose_flashcard(flashcard_bank):
    list_flashcards(flashcard_bank)
    try:
        flashcard_index = int(input("Enter the number of the flashcard you'd like to play :"))
        if 0 <= flashcard_index < len(flashcard_bank):
            flashcard_bank[flashcard_index].ask_question()
            save_flashcards_to_file(flashcard_bank)
        else:
            print("Invalid index. Please enter a valid number.")
    except ValueError:
        print("Please enter a valid number")

# select flashcard based on incorrect to correct attempts ratio
def select_flashcard(flashcard_bank):
    # don't return anything if the flashcard bank is empty
    if not flashcard_bank:
        return None
    # calculate each flashcards incorrect attempts to correct attempt ratio and sort the flashcard bank accordingly (flashcards with the most incorrect attempts have the highest priority in the display of questions when the user is playing)
    flashcard_bank.sort(key=lambda x: (x.incorrect_attempts + 1) / (x.correct_attempts + 1), reverse=True)
    # return the chosen flashcard
    return random.choice(flashcard_bank[:max(3, len(flashcard_bank)// 2)])

# add a new flashcard in the bank
def add_flashcard():
    question = input('Enter the flashcard question : ')
    choices_input = input('Enter all choices separated by a comma: ')
    choices = [choice.strip() for choice in choices_input.split(',')]

    # separate each answers 
    while True:
        correct_answer = input('Enter the correct answer : ').strip()
        if correct_answer in choices:
            break
        else:
            print('The correct answer must be one of the choices. Please try again.')
    # create the new flashcard
    new_flashcard = Flashcard(question, choices, correct_answer)
    return new_flashcard

# load all flashcards from json file (if there are flashcards stored)
def load_flashcards_from_file(filename='flashcards.json'):
    try:
        with open(filename, 'r') as file:
            flashcards_data = json.load(file)
            return [Flashcard(**data) for data in flashcards_data]
    except FileNotFoundError:
        return [] 
    
# helper function to save the newly created/edited flashcards into the bank
def save_flashcards_to_file(flashcards, filename='flashcards.json'):
    with open(filename, 'w') as file:
        json.dump([flashcard.to_dict() for flashcard in flashcards], file, indent=4)

class FlashcardApp:
    def __init__(self, master):
        self.master = master
        master.title("Welcome to Wizzpy")

        # Set window size (width x height) and position (x_offset, y_offset)
        screen_width = master.winfo_screenwidth()
        screen_height = master.winfo_screenheight()
        width = 600
        height = 400
        x_offset = (screen_width - width) // 2
        y_offset = (screen_height - height) // 2
        master.geometry(f"{width}x{height}+{x_offset}+{y_offset}")

        self.flashcard_bank = load_flashcards_from_file()

        tk.Button(master, text="Add Flashcard", command=self.add_flashcard).pack()
        tk.Button(master, text="Review Flashcard", command=self.review_flashcard).pack()
        tk.Button(master, text="List Flashcards", command=lambda: self.list_flashcards(select_mode=False)).pack()
        tk.Button(master, text="Edit Flashcard", command=lambda: self.list_flashcards(edit_mode=True)).pack()
        tk.Button(master, text="Delete Flashcard", command=lambda: self.list_flashcards(delete_mode=True)).pack()

    def add_flashcard(self):
        question = simpledialog.askstring("Question", "Enter the flashcard question:")
        choices = simpledialog.askstring("Choices", "Enter all choices separated by a comma:")
        correct_answer = simpledialog.askstring("Correct Answer", "Enter the correct answer:")

        if question and choices and correct_answer:
            choices_list = [choice.strip() for choice in choices.split(',')]
            new_flashcard = Flashcard(question, choices_list, correct_answer)
            self.flashcard_bank.append(new_flashcard)
            save_flashcards_to_file(self.flashcard_bank)

    def review_flashcard(self):
        review_window = tk.Toplevel(self.master)
        review_window.title("Review Flashcards")

        tk.Button(review_window, text="Review Random Flashcard", command=self.review_random).pack()
        tk.Button(review_window, text="Select Flashcard to Review", command=lambda: self.list_flashcards(select_mode=True)).pack()

    def review_random(self):
        if not self.flashcard_bank:
            messagebox.showinfo("Info", "No flashcards available.")
            return
        random_flashcard = random.choice(self.flashcard_bank)
        self.show_flashcard(random_flashcard)

    def show_flashcard(self, flashcard):
        show_window = tk.Toplevel(self.master)
        show_window.title("Flashcard Review")
        tk.Label(show_window, text=flashcard.question).pack()

        for idx, choice in enumerate(flashcard.choices, start=1):
            choice_button = tk.Button(show_window, text=f"{idx}. {choice}", command=lambda c=choice: self.check_answer(flashcard, c, show_window))
            choice_button.pack()

    def check_answer(self, flashcard, user_choice, window):
        if user_choice == flashcard.correct_answer:
            flashcard.correct_attempts += 1
            messagebox.showinfo("Result", "Correct!")
        else:
            flashcard.incorrect_attempts += 1
            messagebox.showinfo("Result", f"Incorrect. The correct answer was: {flashcard.correct_answer}")
        save_flashcards_to_file(self.flashcard_bank)
        window.destroy()

    def edit_flashcard_gui(self, flashcard):
        new_question = simpledialog.askstring("Edit Question", "Enter new question:", initialvalue=flashcard.question)
        new_choices = simpledialog.askstring("Edit Choices", "Enter all choices separated by a comma:", initialvalue=', '.join(flashcard.choices))
        new_answer = simpledialog.askstring("Edit Correct Answer", "Enter the correct answer:", initialvalue=flashcard.correct_answer)

        if new_question:
            flashcard.question = new_question
        if new_choices:
            flashcard.choices = [choice.strip() for choice in new_choices.split(',')]
        if new_answer:
            flashcard.correct_answer = new_answer

        save_flashcards_to_file(self.flashcard_bank)

    def delete_flashcard_gui(self, index):
        del self.flashcard_bank[index]
        save_flashcards_to_file(self.flashcard_bank)
        messagebox.showinfo("Deleted", "Flashcard has been deleted.")

    def list_flashcards(self, select_mode=False, edit_mode=False, delete_mode=False):
        flashcards_info = "\n".join(f"{idx}. {fc.question}" for idx, fc in enumerate(self.flashcard_bank, start=1))
        index = simpledialog.askinteger("Select Flashcard", f"Enter the flashcard number:\n{flashcards_info}")

        if index and 0 < index <= len(self.flashcard_bank):
            if select_mode:
                self.show_flashcard(self.flashcard_bank[index - 1])
            elif edit_mode:
                self.edit_flashcard_gui(self.flashcard_bank[index - 1])
            elif delete_mode:
                self.delete_flashcard_gui(index - 1)
                
def main():
    ### GUI VERSION
    root = tk.Tk()
    app = FlashcardApp(root)
    root.mainloop()
