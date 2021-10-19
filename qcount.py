import os, json, io
from typing import Tuple, Union

def load(*,file:str="save.json") -> Tuple[list,list]:
    '''Loads the questions and completed questions in the specified file, defaults to `save.json`.
        
        Returns a tuple: `(questions,completed)`'''
    if file == "":
        file = "save.json"
    if os.path.isfile(file):
        with open(file) as f:
            data = json.load(f)
            f.close()
        return data['questions'], data['completed']
    else:
        return None

def save(questions:list,completed:list,*,file:str="save.json") -> None:
    '''Saves the questions and completed questions in the specified file, defaults to `save.json`.'''
    data = {
        'questions':questions,
        'completed':completed,
    }
    with open(file=file, mode='w') as f:
        json.dump(data, f)
        f.close()

def parse_input(inp):
    '''Parses the input to a list of numbers. Gets every other number in the range if any of `["even", "odd", "evens", "odds"]` is next.'''
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