#!/usr/bin/python3

#TODO:
#   - Implement auxiliary recipes
#       - Implement serve with
#   How to handle auxiliary recipes?
#
#   When parsing, add everything after the first "Serves" to a new Recipe
#       (This should effectively just call itself recursively as many times as necessary)
#   Store the new recipe in a self.auxiliaries dict with {name:recipe}.
#   Copy over all variables from the calling recipe to the auxiliary
#   When reaching a "serve with", call the appropriate auxiliary from the auxiliaries dict
#   Execute it, and add all the objects in its first mixing bowl to the main first mixing bowl

# A Chef interpreter in Python.
import sys, os, re
from random import shuffle

# The main paragraphs of a Chef program
paragraphs = ["name", "comments", "ingredients", "method"]

regexes = {
"from":"([\w\s]+) from",
"to":"([\w\s]+) to",
"into":"([\w\s]+) into",
"bowl":".*(\d+)[\S+ ]*mixing bowl",
"dish":".*the (\d+)*[\S+ ]*baking dish"
}

# Some of these are ambiguous wet/dry measures
#   TODO: Come up with a better way of handling these.
dry_measures = ['g', 'kg', 'pinch', 'pinches', 'cup', 'cups', 'teaspoon', 'teaspoons', 'level teaspoons', 'tablespoon', 'tablespoons']

# These indicate explicit unicode characters.
#   TODO: Store these as ints, differentiate between wet/dry with int/floats
wet_measures = ['ml', 'l', 'dash', 'dashes']

# These make an ambiguous measure dry
measure_specifiers = ['heaped', 'level']

# Some shitty error handler I probably won't use
def parse_error(line, message=""):

    print("Error on line %d" % line)
    print(message)
    sys.exit(-1)

# Honestly ingredients and bowls should probably be put in their own classes and stuff.
#   Whatever.
class Recipe:

    # Method for auxiliary recipes to pass bowls back to the calling chef.
    #   This will definitely for sure get used eventually, I promise.
    def passback(self):

        if self.bowls[0] is not None:
            return self.bowls[0]
        else:
            return []


    # Get the mixing bowl from the command string with regex
    def get_bowl(self, string):

        bowl = re.findall(regexes["bowl"], string)

        # If no bowl was specified, default to bowl 0
        bowl = 0 if bowl == [] else int(bowl[0])-1

        # Probably a good time to make sure there are enough bowls.
        if bowl > len(self.bowls)-1:
            self.bowls.append([])


        return bowl

    # Get the baking dish index from a command string
    def get_dish(self, string):

        dish = re.findall(regexes["dish"], string)

        # If no dish was specified, default to dish 0
        dish = int(dish[0])-1 if not dish == [''] else 0

        # Probably a good time to make sure there are enough dishes.
        if dish > len(self.dishes)-1:
            self.dishes.append([])

        return dish


    # Put an ingredient on top of a mixing bowl
    def put(self, cstring):

        bowl = self.get_bowl(cstring)

        # Get the value of the ingredient
        ingredient = re.findall(regexes['into'], cstring)[0]
        value = self.ingredients[ingredient]

        # Get out some extra bowls if you need to
        while len(self.bowls) < (bowl):
            self.bowls.append([[]])

        # Prepend value to bowl.
        self.bowls[bowl] = [value] + self.bowls[bowl]


    # Copy the contents of a mixing bowl to a baking dish for output
    def pour(self, cstring):

        bowl = self.get_bowl(cstring)
        dish = self.get_dish(cstring)

        self.dishes[dish] = self.bowls[bowl] + self.dishes[dish]


    # Liquefy either ingredients or the contents of mixing bowls into unicode
    def liquefy(self, cstring):

        # If we're just liquefying a single ingredient..
        if not "mixing bowl" in cstring:
            self.ingredients[cstring] = chr(int(self.ingredients[cstring]))
            return

        # Otherwise liquefy the whole bowl
        bowl = self.get_bowl(cstring)

        # Convert any integer (wet) ingredients in the bowl to unicode, and
        #   print any numbers (dry measures) as-is.
        self.bowls[bowl] = [chr(int(elem)) if not type(elem) is str else elem for elem in self.bowls[bowl] ]


    # Serve the output of some baking dishes
    # TODO: Handle serve with
    def serves(self, cstring):

        if 'with' not in cstring:
            print("Serving")

            num_dishes = int(cstring)

            for n in range(num_dishes):
                # print(self.dishes)
                self.dishes[n] = [str(x) for x in self.dishes[n]]
                print(' '.join(self.dishes[n]))

        # Invoke a sous recipe
        else:

            # This is my great implementation of sous recipes.
            pass


    # Read a value from STDIN
    def take(self, cstring):

        # Get the ingredient to populate
        ingredient = re.findall(regexes["from"], cstring)[0]

        # Keep looping until the user manages to type in a number
        while value is None:

            # Read something from the input.
            #   Make sure not to show a prompt, guessing whether the program's hanging
            #   or waiting for input keeps users on their toes.
            value = input("")

            # Validate user input, make sure it's a float
            try:
                value = float(value)
            except ValueError:
                print("Invalid value entered. Enter a numeric value.\n")

        self.ingredients[ingredient] = value


    # Pop the top value in the mixing bowl into the specified ingredient
    def fold(self, cstring):

        ingredient = re.findall(regexes["into"], cstring)[0]

        bowl = self.get_bowl(cstring)

        self.ingredients[ingredient] = self.bowls[bowl].pop(0)


    # Add the value of an ingredient to the value on top of a mixing bowl, and
    #   stores the value on top of that mixing bowl.
    def add(self, cstring):

        bowl = self.get_bowl(cstring)

        # 'Add dry ingredients' adds ALL the dry ingredients, so have some logic for that
        if "dry ingredients" in cstring:
            #Add all dry ingredients and put the result on the bowl
            temp = 0

            # Build a list of all the dry ingredients by selecting out only floats
            temp = [self.ingredients[key] for key in self.ingredients.keys() if type(self.ingredients[key]) is float]

            self.bowls[bowl] = [sum(temp)] + self.bowls[bowl]

        # If no bowl is specified, then the entire command string is just the ingredient.
        if 'bowl' not in cstring:
            ingredient = cstring
        else:
            ingredient = re.findall(regexes["to"], cstring)[0]

        value = self.ingredients[ingredient]

        # Prepend a value that's the top value plus the ingredient
        # self.bowls[bowl] = [self.bowls[bowl][0] + value] + self.bowls[bowl]

        # Increment the top value by the amount to add
        self.bowls[bowl][0] += value


    # Remove the value of an ingredient from the value on top of a mixing bowl, and
    #   stores the value on top of that mixing bowl.
    def remove(self, cstring):

        bowl = self.get_bowl(cstring)

        # If 'from' a bowl is specified, get the ingredient differently.
        if "from" in cstring:
            ingredient = re.findall(regexes["from"], cstring)[0]
        else:
            ingredient = cstring

        value = self.ingredients[ingredient]

        # Prepend a value that's the top value plus the ingredient
        # self.bowls[bowl] = [self.bowls[bowl][0] - value] + self.bowls[bowl]
        self.bowls[bowl][0] -= value


    # Multiply the value of an ingredient with the value on top of a mixing bowl, and
    #   stores the value on top of that mixing bowl.
    def combine(self, cstring):

        bowl = self.get_bowl(cstring)

        if "into" in cstring:
            ingredient = re.findall(regexes["into"], cstring)[0]
        else:
            ingredient = cstring

        value = self.ingredients[ingredient]

        # Prepend a value that's the top value plus the ingredient
        # self.bowls[bowl] = [self.bowls[bowl][0] * value] + self.bowls[bowl]
        self.bowls[bowl][0] *= value


    # Divide the value on top of a mixing bowl by the value of an ingredient, and
    #   stores the value on top of that mixing bowl.
    def divide(self, cstring):

        bowl = self.get_bowl(cstring)

        if "into" in cstring:
            ingredient = re.findall(regexes["into"], cstring)[0]
        else:
            ingredient = cstring


        value = self.ingredients[ingredient]

        # Prepend a value that's the top value plus the ingredient
        # self.bowls[bowl] = [self.bowls[bowl][0] / value] + self.bowls[bowl]
        self.bowls[bowl][0] = self.bowls[bowl][0] / value


    # Roll the ingredients in the mixing bowl. Shifts the top ingredient down
    #   by stir_by, and moves the first stir_by ingredients up one.
    def stir(self, cstring):

        # Get which bowl to stir
        if 'the' in cstring:
            bowl = self.get_bowl(cstring)
        else:
            bowl = 0

        # Get the number of elements to stir it by
        if 'minutes' in cstring:

            # Get number of elements to stir by
            stir_by = re.findall("(\d*) minutes", cstring)[0]

        # If no minutes are specified, stir by the value in the ingredient
        else:
            ingredient = re.findall(regexes["into"], cstring)[0]
            stir_by = self.ingredients[ingredient]

        # Set stir_by to be no greater than the length of the bowl
        stir_by = stir_by if stir_by < (len(self.bowls[bowl])-1) else (len(self.bowls[bowl])-1)

        # In case someone gets cheeky and tries to call it on an empty list...
        if stir_by < 0:
            stir_by = 0

        # Shift all elements up by stir_by and put the top element in the stir_by place
        _i = self.bowls[bowl][0]
        for i in range(stir_by):
            self.bowls[bowl][i] = self.bowls[bowl][i+1]
        self.bowls[bowl][stir_by] = _i


    # Randomly reorder ingredients in bowl
    def mix(self, cstring):

        if "bowl" in cstring:
            bowl = self.get_bowl(cstring)
        else:
            bowl = 0

        shuffle(self.bowls[bowl])


    # Immediately exit the current recipe
    def refrigerate(self, cstring=None):

        if cstring is not None:
            hours = re.findall("(\d*) hours", cstring)[0]
            self.serve(hours)

        self.passback()


    # Remove everything from a bowl
    def clean(self, cstring):

        bowl = self.get_bowl(cstring)

        self.bowls[bowl] = []


    # Dict of commands. Maps command strings to the function
    commands = \
        {"Put": put,
        "Pour": pour,
        "Liquefy": liquefy,
        "Serves": serves,
        "Take": take,
        "Fold": fold,
        "Add": add,
        "Remove": remove,
        "Combine": combine,
        "Divide": divide,
        "Stir": stir,
        "Mix": mix,
        "Refrigerate": refrigerate,
        "Clean": clean,
        "Set": 0 # Set isn't handled by a function, but my flow control needs it to be a key.
        }


    # Recipe constructor
    def __init__(self, lines):

        self.bowls = [[]]
        self.dishes = [[]]
        self.commandlist = list()
        self.ingredients = dict()

        # Read the input lines of text and parse them
        self.parse(lines)


    # Parse the text to construct the Recipe
    # TODO: Handle reading sous recipes.
    def parse(self, lines):

        section = 0
        line_num = 0

        for _l in range(len(lines)):
            line = lines[_l]
            line_num += 1

            # First, read the recipe name.
            # TODO: Validate name beyond just checking for a period. Maybe.
            if paragraphs[section] == "name":
                section += 1
                recipename = line

                # Validate name ends in a period.
                # if not recipename[-2] == '.':
                #     print(recipename[-2])
                #     parse_error(line_num, "Invalid recipe name.")

                continue


            # Enter ingredients section parsing
            if line == "Ingredients.\n":

                section += 1
                continue


            # Enter method section parsing
            elif line == "Method.\n":

                section += 1
                continue


            # If we're in the ingredients section...
            if paragraphs[section] == "ingredients":
                if line == '\n':
                    continue

                # Break up line into words
                ingredient = line[:-1].split(' ')

                # Build a dictionary mapping object names to their respective objects.
                value = ingredient[0]

                # If it's an uninitialized variable, just make an empty entry in the dict
                if len(ingredient) == 1:
                    key = value
                    self.ingredients[key] = ''


                # These indicate an ingredient is dry, and just add an extra word.
                elif ingredient[1] in measure_specifiers:

                    # Need to handle these separately because of the extra word
                    key = ' '.join(ingredient[3:])
                    self.ingredients[key] = float(value)


                # Store dry measures as floats
                elif ingredient[1] in dry_measures:
                    key = ' '.join(ingredient[2:])
                    self.ingredients[key] = float(value)


                # Store wet measures as strings
                elif ingredient[1] in wet_measures:
                    key = ' '.join(ingredient[2:])
                    self.ingredients[key] = chr(int(value))

                # Catchall
                else:
                    key = ' '.join(ingredient[1:])
                    self.ingredients[key] = float(value)


            # If we're in the method section...
            # Parse commands as delimited by periods OR newlines.
            # Generate a list of all the commands
            if paragraphs[section] == "method":

                # Ignore newlines. TODO: This might be a bad call if I want a newline
                #   to specify where the recipe ends and the sous recipe starts.
                if line == '\n':
                    continue

                # If multiple commands are on one line, split them by period
                _commands = line[:-1].split('.')

                for _c in _commands:
                    if len(_c) == 0:
                        continue
                    if _c[0] == ' ':
                        _c = _c[1:]
                    self.commandlist.append(_c)

            # If you hit a "Serves", the remainder are auxiliary recipes
            # if "Serves" in line:
            #     return


    # Cook the dish
    def cook(self):

        # print("Cooking...")
        # print(self.ingredients)

        loop_indices = []

        # Run through commandlist here, executing the commands
        i = 0

        # print(self.commandlist)

        # Do this in a while loop so we can mess with i as a program counter
        #   for flow control. Everyone loves GOTOs.
        while i < len(self.commandlist):

            command = self.commandlist[i]

            # print("\nExecuting: [%s] " % command)
            c_split = command.split(maxsplit=1)


            # Please don't judge me for any of the following code.
            #
            # Any of these evaluating to True indicate the command has something to do with flow control
            if c_split[0] not in self.commands.keys() or "until" in command or "Set aside" in command:

                ################ ENTERING LOOP ################
                # TODO: Really, this should go last and just be an 'else'.
                #   Putting the start condition before the end conditions ruins
                #   the Feng Shui of the code though.

                if 'until' not in c_split[1].split() and not c_split[0] == 'Set':
                    verb = c_split[0]

                    # Get the ingredient name - counter will be self.ingredients.ingredient
                    # Just don't worry about this line tbh
                    loop_ingredient = ' '.join(c_split[1].split(maxsplit=1)[1:])

                    # Store the index of the current command as the loop index to return to when we hit an 'until'
                    loop_indices.append([i, verb, loop_ingredient])


                ################## EXITING LOOP ###############
                # If command is 'set aside', break out of the current loop.
                elif "Set aside" in command:

                    # Iterate until you hit the end of the innermost loop
                    while 'until' not in self.commandlist[i]:
                        i += 1

                    i += 1

                    # Remove the loop ingredient from the list of indices to
                    #   show we're no longer looping over it.
                    loop_indices.pop()

                    continue


                # This command indicates the end of a loop.
                elif 'until' in c_split[1]:

                    # This would be bad - means we're exiting a loop we never entered
                    if loop_indices == []:
                        parse_error(i, "'Until' without an opening loop") # Panic

                    # If the verb that started the loop doesn't appear in 'verbed',
                    # then this until statement doesn't correspond to the innermost loop.
                    # This should never really happen, but in case it does, let's handle it.
                    if loop_indices[-1][1].lower() not in c_split[1].split()[-1]:
                        parse_error(i, "Outer loop closed before inner")


                    # If the loop counter isn't 0, then loop
                    if not self.ingredients[loop_indices[-1][2]] == 0:

                        # Decrement the ingredient
                        #   being used as a loop counter if it appears in the command.
                        # If the word 'the' appears, it'll be as part of 'the [ingredient]'
                        if loop_indices[-1][2] in c_split[1]:

                            # Decrement ingredient
                            self.ingredients[loop_indices[-1][2]] -= 1

                            # Check to see if counter is 0 after decrementing.
                            # If so, exit the loop.
                            if (self.ingredients[loop_indices[-1][2]]) == 0:

                                i += 1
                                loop_indices.pop()

                                continue

                        # If we've made it this far, the loop counter is nonzero
                        #   and we're ready to restart the loop.
                        # Reset program counter to the beginning of the loop
                        i = loop_indices[-1][0]


                    # If the loop ingredient IS 0, we're ready to exit this loop.
                    #   Remove the values of the last list element from the loop variables,
                    #   continue on with life.
                    elif self.ingredients[loop_indices[-1][2]] == 0:
                        print("Loop index for %s is %d, should be zero" % (loop_indices[-1][2], self.ingredients[loop_indices[-1][2]]))
                        loop_indices.pop(-1)
                        i += 1
                        continue

                i += 1
                continue

            # This is a little janky but refrigerate can be invoked as one word.
            if c_split[0] == 'Refrigerate' and len(c_split) == 1:
                self.commands['Refrigerate']
                # TODO: This should actually end the recipe.
                i += 1
                continue

            # Call the appropriate command
            self.commands[c_split[0]](self, c_split[1])

            i += 1


if __name__=="__main__":
    if len(sys.argv) != 2 or not os.path.exists(sys.argv[1]):
        print("Please specify a valid Chef script to execute.")
        sys.exit()

    filename = sys.argv[1]
    # print("Executing %s" % filename)

    cfile = open(sys.argv[1])
    recipe = Recipe(cfile.readlines())
    recipe.cook()
