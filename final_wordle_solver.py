'''
Written by Joseph Ma
8/16/22
'''
import pandas as pd
import random as r
import math as m

GRAY = "\033[2;48;5;243m\033[38;5;255m"
YELLOW = "\033[2;48;5;3m\033[38;5;248m"
GREEN = "\033[2;48;5;10m\033[38;5;248m"
RESET = "\033[2;48;5;10m\033[0m"

#this function returns a colored string to display our guess hints
def show_our_guess(guess, hints):
  colored_string = ""
  for i in range(len(guess)):
    if(hints[i] == "G"):
      colored_string += GREEN + guess[i]
    elif(hints[i] == "Y"):
      colored_string += YELLOW + guess[i]
    else:
      colored_string += GRAY + guess[i]
  return colored_string

#this function extracts a dataframe of words of desired lengths
def get_words(i, file):
  df = pd.read_csv(file)
  #extract the words of the desired length
  df_filtered = df[df["Word"].str.len() == i]

  #create a list of list of seperated letters
  data = []
  for x in range(len(df_filtered)):
    word = df_filtered.values[x][0]
    word_list = list(word)
    word_list.insert(0, word)
    data.append(word_list)

  #create a data frame with column consisting of letters in each word
  len_word = i   #number of letters
  column_vals = ["Word"]
  for x in range(len_word):
    column_vals.append("letter_" + str(x + 1))

  letters = pd.DataFrame(data, columns=column_vals)
  return letters

#this function prints out our guesses so far
def print_guess_list(guess_list):
  if(len(guess_list) != 0):
    print("GUESSES SO FAR")
    print("---------------------------")
    for i in range(len(guess_list)):
      print(guess_list[i])
      print(RESET  + "---------------------------")

#this function ensures that the feedback entered by the user is valid
def check_feedback(invalid, feedback, guess_length):
  while(len(feedback) != guess_length or invalid):
    print("Please enter the correct number of hints/valid hints")
    feedback = input("Enter the hints:")
    feedback = feedback.upper()
    invalid = False
    for l in feedback:
      if (l != "G" and l != "Y" and l != "W"):
        invalid = True
  return feedback

#this function runs the main solver
def run_solver():
  cont = True
  list_of_conditions = []   #will hold our list of conditions to evaluate
  guess_list = []       #will hold our list of guesses to display
  guess_length = 0

  while(cont):
    print_guess_list(guess_list)
    guess = input("Enter your guess: ")
    if guess_length == 0:
      guess_length = len(guess)
      while(guess_length < 4 or guess_length > 11):
        print("Invalid number of characters")
        guess = input("Enter your guess: ")
      if guess_length != 5:
        file_name = "all_words.txt"
      else:
        file_name = "allowed_words.txt"
      df = get_words(guess_length, file_name)    #retrieve dataframe of words
      filtered = get_words(guess_length, file_name)    #retrieve dataframe of words
      green_index = [0] * guess_length      #array indicates which letters have been guessed correctly
      data_conditions = [df["letter_1"] == df["letter_1"]] * len(green_index)  
    else:
      while(len(guess) != guess_length):
        print("Please ensure the number of characters in your guess is " + str(guess_length))
        guess = input("Enter your guess: ")
    guess = guess.lower()     #disregard whether letters are capitalized or not
    print("\nG for green, Y for yellow, W for grey (wrong)")
    feedback = input("eg. for a five letter word GYWWW  --> Enter the hints: ")
    feedback = feedback.upper()
    invalid = False
    for l in feedback:
      if (l != "G" and l != "Y" and l != "W"):
            invalid = True
    feedback = check_feedback(invalid, feedback, guess_length)

    
    #CONDITION EVALUATION
    yellow_letter = []      #checks for the case in which we have a yellow letter but repeated  for example PILLS 
    green_letter = []
    grey_letter = []

    print(guess)
    print(feedback)
    guess_list.append(show_our_guess(guess, feedback))

    #Green CONDITIONS
    condition_created = False
    for i in range(len(feedback)):
      if(feedback[i] == "G"):
        green_letter.append(guess[i])
        if(condition_created == False):
          conditions_green = df["letter_" + str(i + 1)] == guess[i]             #checks if that letter is in that spot
          condition_created = True
        else:
          conditions_green = conditions_green & (df["letter_" + str(i + 1)] == guess[i])    #IMPORTANT: need brackets because & takes precdence
    if(condition_created == False):
      conditions_green = df["letter_1"] == df["letter_1"]     #create arbritrary True statements since we are ANDing them at the end anyways

    #Yellow CONDITIONS
    condition_created = False
    for i in range(len(feedback)):
      if(feedback[i] == "Y"):
        yellow_letter.append(guess[i])    

        if(condition_created == False):
          conditions_yellow = df["Word"].str.contains(guess[i]) & (df["letter_" + str(i + 1)] != guess[i])      #checks if that letter is included in the word AND is not in that position
          condition_created = True
        else:
          conditions_yellow = conditions_yellow & (df["Word"].str.contains(guess[i]) & (df["letter_" + str(i + 1)] != guess[i]))
    if(condition_created == False):
      conditions_yellow = df["letter_1"] == df["letter_1"]     #create arbritray True statements since we are ANDing them at the end anyways

    #Grey CONDITIONS
    condition_created = False
    for i in range(len(feedback)):
      if(feedback[i] == "W"):
        grey_letter.append(guess[i])
        if(guess[i] not in yellow_letter and guess[i] not in green_letter):
          #ONLY apply the grey condition-(letter does not appear in the word) if that letter has not been marked yellow or green
          if(condition_created == False):
            conditions_grey = ~df["Word"].str.contains(guess[i])
            condition_created = True
          else:
            conditions_grey = conditions_grey & (~df["Word"].str.contains(guess[i]))      #checks if that letter is not included in the word
        else:
          #IF that letter has been marked yellow or green somewhere- we can only deduce that letter is NOT in that spot
          #example: PILLS- if first L is yellow and second L is grey, we can only deduce second L is not in the spot of the fourth letter
          if(condition_created == False):
            conditions_grey = df["letter_" + str(i + 1)] != guess[i]
            condition_created = True
          else:
            conditions_grey = conditions_grey & (df["letter_" + str(i + 1)] != guess[i])

    if(condition_created == False):
      conditions_grey = df["letter_1"] == df["letter_1"]     #create arbritray True statements since we are ANDing them at the end anyways
    
    #CONDITION COUNT GREEN + YELLOW
    condition_created = False
    #check word count according to yellow letter list- for example in PILLS- if the first L is yellow and second is not, we know there must be at least 1 L in the word + number of green L's
    green_yellow_letters = green_letter + yellow_letter

    unique_gy_letters = list(set(green_yellow_letters))
    for letter in unique_gy_letters:
      count = yellow_letter.count(letter) + green_letter.count(letter)    #see how many times that letter was colored yellow and green
      if(letter not in grey_letter):
        #the letter has to appear AT LEAST the number of times it has been green + yellow
        if(condition_created == False):
          conditions_repeat = df["Word"].str.count(letter) >= count
          condition_created = True
        else:
          conditions_repeat = conditions_repeat & (df["Word"].str.count(letter) >= count)
      else:
        #the letter has to appear EXACTLY the number of times it has been green + yellow
        if(condition_created == False):
          conditions_repeat = df["Word"].str.count(letter) == count
          condition_created = True
        else:
          conditions_repeat = conditions_repeat & (df["Word"].str.count(letter) == count)

    if(condition_created == False):
      conditions_repeat = df["letter_1"] == df["letter_1"]     #create arbritray True statements since we are ANDing them at the end anyways

    list_of_conditions.append(conditions_green & conditions_grey & conditions_yellow & conditions_repeat)
    
    #Bitwise AND all our previously accumulated conditions
    for i in range(len(list_of_conditions)):
      if(i == 0):
        final_condition = list_of_conditions[0]
      else:
        final_condition = final_condition & list_of_conditions[i]
    filtered = df[final_condition]


    num_left = len(filtered)
    if num_left == 0:
      print("\nNO POSSIBLE ANSWERS\n")
      print("There are no words that fit your conditions.")
    else:
      for l in range(len(feedback)):
        if(green_index[l] == 0):
        #we should check if that column has uncertainty
          if (filtered['letter_' + str(l + 1)].values == filtered['letter_' + str(l + 1)].values[0]).all():
            green_index[l] = 1
      print("\n" + str(num_left) + " POSSIBLE ANSWERS")
      print("----------------------------------------------------")
      print(filtered)
      print("----------------------------------------------------")
    
    letters_of_interest = []
    check_letters = []
    for j in range(len(green_index)):
      if(green_index[j] == 0):
        #this position in the word is currently uncertain and not green
        #find the most frequently appearing uncertain letters in each position
        letters_of_interest.append(filtered["letter_" + str(j + 1)].value_counts().index.tolist()[:26]) #len(green_index)
      else:
        letters_of_interest.append([])  #otherwise append an empty list to that position

    #prioritize the letters based on the most frequently appearing in each index
    for j in range(len(green_index)):
      for k in range(len(green_index)):
        if(len(letters_of_interest[k]) >= j + 1):
          check_letters.append(letters_of_interest[k][j])

    #eliminate duplicates but keep the order
    priority_letters = []
    for j in range(len(check_letters)):
      if(check_letters[j] not in priority_letters):
        priority_letters.append(check_letters[j])

    index_ctr = 0
    optimized = False
    check_conditions = df["letter_1"] == df["letter_1"]
    for j in range(len(data_conditions)):
      check_conditions = check_conditions & data_conditions[j]

    filtered_df = df[check_conditions]

    num_priority = len(green_index) - sum(green_index)    #this tells us how many uncertain columns we have
    print("LETTERS TO ELIMINATE: ")
    print(priority_letters)
    priority_letters = check_letters    #testing
    assigned = False
    while(len(filtered_df) > 1 and optimized == False and len(priority_letters[index_ctr: index_ctr + num_priority]) > 0):
      letters_set = set(priority_letters[index_ctr: index_ctr + num_priority])
      df_set = filtered_df["Word"].apply(set)
      for j in range(len(df_set)):
        df_set[df_set.index[j]] = len(df_set[df_set.index[j]].intersection(letters_set))
      if df_set.max() == len(green_index):
        optimized = True   #we have words that match the first n letters
      filtered_df = filtered_df[df_set == df_set.max()]

      if(len(filtered_df) != 1 and len(filtered_df) != 0):
        if (len(filtered_df) != 1):
          word_guess = filtered_df.values[r.randint(0, len(filtered_df) - 1)][0]
          assigned = True
        elif (len(filtered_df) != 0):
          word_guess = filtered_df.values[0][0]
          assigned = True
      index_ctr += num_priority

    if(assigned):    
      for j in range(len(word_guess)):
        #add the conditions such that we will not repeatedly guess the same letter in the same position
        data_conditions[j] = data_conditions[j] & (df["letter_" + str(j + 1)] != word_guess[j])
      print("Suggested guess: " + str(word_guess))
    else:
      print("No suggested guesses")

    #USER INPUT TO continue or not
    answer = input("Continue (y/n): ")
    while(answer.upper() != "Y" and answer.upper() != "N"):
      print("Please enter y or n!")
      answer = input("Continue (y/n): ")
    if(answer.upper() == "Y"):
      cont = True
    else:
      cont = False

if __name__ == "__main__":
    print("Final Wordle Solver by Joseph Ma")
    new_game = True
    while(new_game):
      run_solver()
      ans = input("Would you like to try a new game? (y/n): ")
      while(ans.upper() != 'Y' and ans.upper() != 'N'):
        print("Please enter y or n")
        ans = input("Would you like to try a new game? (y/n): ")
      if(ans.upper() == "Y"):
        new_game = True
      else:
        new_game = False
