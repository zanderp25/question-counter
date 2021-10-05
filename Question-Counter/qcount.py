# Question Counter for Homework

import os, json

def load():
    if os.path.isfile("save.json"):
        with open("save.json") as f:
            data = json.load(f)
            f.close()
        return data
    else:
        return None

def save(questions,completed, filename="save.json"):
    data = {
        'questions':questions,
        'completed':completed,
    }
    with open(filename,'w') as f:
        json.dump(data,f)
        f.close()

def parse_input(inp):
    for i in [";", ",", " ", "&"]:
        inp = inp.replace(i, "|")
    inp = inp.split("|")
    identifiers = ["even", "odd", "evens", "odds"]
    questions = []
    for i in range(len(inp)):
        if inp[i] in identifiers + ['']:
            continue
        elif '-' in inp[i]:
            ii = inp[i].split('-')
            if len(ii) > 2:
                raise SyntaxError("Invalid input")
            if not i+1 >= len(inp):
                ident = True if inp[i+1] in identifiers else False
            else:
                ident = False
            questions += [x for x in range(int(ii[0]), int(ii[1])+1, 2 if ident else 1)]
        elif inp[i].isdigit:
            questions += [int(inp[i])]
        else:
            raise SyntaxError("Invalid input " + str(inp[i]))
    return questions

def menu(inp):
    global completed
    if inp == "":
        return True
    elif inp == "a":
        add = [*parse_input(input("Enter questions to add: "))]
        for item in add:
            if not item in completed and item in questions:
                completed += [item]
        return False
    elif inp == "e":
        completed = parse_input(input("Enter completed questions: "))
        return False
    elif inp == "r":
        completed = []
        return False
    elif inp == "s":
        f = input("Enter filename (leave blank for 'save.json'): ")
        save(questions, completed, f if f != '' else 'save.json')
        return False
    elif inp == "q":
        exit()
    else:
        return False

completed = []

def main():
    global question
    global completed

    for question in questions + ['\rEnd of questions']:
        if question in completed:
            continue
        os.system('clear')
        print(f"Question {question}:")
        print(f"  {len(questions)} questions total.")
        print(f"  {len(questions) - len(completed)} questions remaining.")
        print(f"  {len(completed)} questions completed.")
        print("")
        print("  a - Add to completed")
        print("  e - Edit completed questions")
        print("  r - Reset completed questions")
        print("  s - Save")
        print("  q - Quit")
        print("")
        print("  Press enter to continue.") if len(completed) != len(questions) else print("  Press enter to quit.")
        if not menu(input("")):
            main()
            return
        else:
            completed.append(question)

if __name__ == "__main__":
    if os.path.isfile("save.json"):
        data = load()
        questions = data['questions']
        completed = data['completed']
    else:
        questions = parse_input(input("Input the questions that need to be completed. > "))
    main()
