import random 
from string import Template

from copy import deepcopy

# This file contains helper functions for converting LogicPuzzle 
# hints into human readable (ish) text.
grammar_dict = {
    "suspect": {
        "weapon": {
            "is": "{ent1} was the {cat1} with the {ent2}",
            "not": "{ent1} was not the {cat1} with the {ent2}",
            "hour": {
                "before": {
                    "step": 1,
                    "timed": "{ent1} was there {amount} hours before the {ent2}",
                    "untimed": "{ent1} was there at least 1 hour before the {ent2}",
                },
                "or": "Either {ent1} or the {ent2} was there at {is_ent}",
            },
        },
        "hour": {
            "is": "{ent1} was there at {ent2}",
            "not": "{ent1} not was there at {ent2}",
        },
        "weapon": {
            "or": "Either {ent1} or the suspect there at {ent1} had the {is_ent}"
        },
    },
    "weapon": {
        "suspect": {
            "is": "The {ent1} was with {ent2}",
            "not": "The {ent1} not was with {ent2}",
            "hour": {
                "before": {
                    "step": 1,
                    "timed": "The {ent1} was there {amount} hours before {ent2}",
                    "untimed": "The {ent1} was there at least 1 hour before {ent2}",
                },
                "or": "Either the {ent1} or  {ent2} was there  at  {is_ent}",
            },
        },
        "hour": {
            "is": "The {ent1} was there at {ent2}",
            "not": "The {ent1} not was there at {ent2}",
            "suspect": {"or": "{is_ent} either had the {ent1} or was there at {ent2}"},
        },
    },
    "hour": {
        "suspect": {
            "is": "{ent1} was when {ent2} was there",
            "not": "{ent1} is not when {ent2} was there",
            "weapon": {
                "or": "The {is_ent} was either there at {ent1} or was with {ent2}"
            },
        },
        "weapon": {
            "is": "{ent1} was when the {ent2} was there",
            "not": "{ent1} is not when the {ent2} was there",
            "suspect": {"or": "{is_ent} was either there at {ent1} or had the {ent2}"},
        },
    },
}

def toTemplate(str):
    return Template(str.replace("{", "${"))

def is_to_english(attributes, grammar_dict = {}):
    cat1 = attributes[0].title 
    ent1 = attributes[1]
    cat2 = attributes[2].title
    ent2 = attributes[3]

    if (
        cat1 in grammar_dict
        and cat2 in grammar_dict[cat1]
        and "is" in grammar_dict[cat1][cat2]
    ):
        template = grammar_dict[cat1][cat2]["is"]
        if isinstance(template, list): 
            template = template[0]
    
    else:
        template = "The {cat1} {ent1} is the {cat2} {ent2}"
    template = toTemplate(template)

    return template.safe_substitute(cat1=cat1, cat2 = cat2, ent1=ent1, ent2=ent2) 


def not_to_english(attributes, grammar_dict={}):
    attributes = attributes[0]["is"]
    cat1 = attributes[0].title 
    ent1 = attributes[1]
    cat2 = attributes[2].title 
    ent2 = attributes[3]

    if cat1 in grammar_dict and cat2 in grammar_dict[cat1] and "not" in grammar_dict[cat1][cat2]:
        template = grammar_dict[cat1][cat2]["not"]
        if isinstance(template, list): 
            template = template[0]
    else: 
        template = "The {cat1} {ent1} was not the {cat2} {ent2}"

    template = toTemplate(template) 
    return template.safe_substitute(cat1=cat1, cat2=cat2, ent1=ent1, ent2=ent2) 

def before_to_english(attributes,  grammar_dict = {}):
    cat1 = attributes[0].title
    ent1 = attributes[1]
    cat2 = attributes[2].title
    ent2 = attributes[3]

    if (
        cat1 in grammar_dict
        and cat2 in grammar_dict[cat1]
        and "not" in grammar_dict[cat1][cat2]
    ):
        template = grammar_dict[cat1][cat2]["not"]
    else:
        template = "The {cat1} {ent1} was not the {cat2} {ent2}"

    return template.format(cat1=cat1, cat2=cat2, ent1=ent1, ent2=ent2)


def before_to_english(attributes, grammar_dict={}):
    cat1 = attributes[0].title
    ent1 = attributes[1]
    cat2 = attributes[2].title
    ent2 = attributes[3]

    num_cat = attributes[4].title

    timed = len(attributes) == 6
    if timed:
        amount  = attributes[5] 
    else: 
        amount = -1 

    if cat1 in grammar_dict and cat2 in grammar_dict[cat1] and num_cat in grammar_dict[cat1][cat2] and  "before" in grammar_dict[cat1][cat2][num_cat]:
        template_info = grammar_dict[cat1][cat2][num_cat]["before"]
        if isinstance(template_info, list): 
            template_info = template[0]
        step = attributes[4].increment
    else:
        template_info = None 
        step = attributes[4].increment

    if not timed:
        if not template_info is None:
            template = template_info["untimed"]
        else:

            template = "The {cat1} {ent1} is at least {step} {num_cat} before the {cat2} {ent2}"
        template = toTemplate(template) 
        return template.safe_substitute(cat1= cat1, cat2=cat2, num_cat=num_cat, step=step, ent1=ent1, ent2=ent2 )
    else:
        amount = amount * step
        if not template_info is None:
            template = template_info["timed"]
        else:
            
            template = "The {cat1} {ent1} is {amount} {num_cat}s before the {cat2} {ent2}"
        template = toTemplate(template) 
        return template.safe_substitute(cat1= cat1, cat2=cat2, num_cat=num_cat, step=step, ent1=ent1, ent2=ent2, amount=amount )

        template = (
            "The {cat1} {ent1} is {amount} {num_cat}s before the {cat2} {ent2}"
        )
        return template.format(
            cat1=cat1,
            cat2=cat2,
            num_cat=num_cat,
            step=step,
            ent1=ent1,
            ent2=ent2,
            amount=amount,
        )


def simple_or_to_english(attributes, grammar_dict={}):
    cat1 = attributes[0].title
    ent1 = attributes[1]
    cat2 = attributes[2].title
    ent2 = attributes[3]

    is_cat = attributes[4].title
    is_ent = attributes[5]

    if cat1 in grammar_dict and cat2 in grammar_dict[cat1] and is_cat in grammar_dict[cat1][cat2] and "or" in grammar_dict[cat1][cat2][is_cat]:
        template =  grammar_dict[cat1][cat2][is_cat]["or"]
        if isinstance(template, list): 
            template = template[0]
    else:
        template = (
            "Either the {cat1} {ent1} or the {cat2} {ent2} is the {is_cat} {is_ent}"
        )

    template = toTemplate(template) 
    return template.safe_substitute(cat1=cat1, cat2=cat2, ent1=ent1, ent2=ent2, is_cat=is_cat, is_ent=is_ent)


def compound_or_to_english(attributes, grammar_dict={}):
    hint1 = attributes[0]
    hint2 = attributes[1]

    text1 = hint_to_english(hint1, grammar_dict=grammar_dict)
    text2 = hint_to_english(hint2, grammar_dict=grammar_dict)
    text1 = text1[0].lower() + text1[1:]
    text2 = text2[0].lower() + text2[1:]

    s = "Either {} or {}".format(text1, text2)
    return s


def hint_to_english(hint, grammar_dict={}):
    kind = next(iter(hint))
    if kind == "is":
        return is_to_english(hint[kind], grammar_dict=grammar_dict)
    elif kind == "not":
        return not_to_english(hint[kind], grammar_dict=grammar_dict)
    elif kind == "before":
        return before_to_english(hint[kind], grammar_dict=grammar_dict)
    elif kind == "simple_or":
        return simple_or_to_english(hint[kind], grammar_dict=grammar_dict)
    elif kind == "compound_or":
        return compound_or_to_english(hint[kind], grammar_dict=grammar_dict)
    else:
        return "NOT IMPLEMENTED YET"


def serialized_hint_grammar(hint):
    hint = deepcopy(hint)
    kind = next(iter(hint))

    attributes = hint[kind]
    if kind == "not":
        attributes = attributes[0]["is"]

    if kind == "is" or kind == "not":

        cat1 = attributes[0].title
        ent1 = attributes[1]
        cat2 = attributes[2].title
        ent2 = attributes[3]

        hint[kind] = [cat1, ent1, cat2, ent2]
    elif kind == "before":
        cat1 = attributes[0].title
        ent1 = attributes[1]
        cat2 = attributes[2].title
        ent2 = attributes[3]

        num_cat = attributes[4].title

        timed = len(attributes) == 6

        if timed:
            hint[kind] = [cat1, ent1, cat2, ent2, num_cat, attributes[5]]
        else:
            hint[kind] = [cat1, ent1, cat2, ent2, num_cat]
    elif kind == "simple_or":
        cat1 = attributes[0].title
        ent1 = attributes[1]
        cat2 = attributes[2].title
        ent2 = attributes[3]

        is_cat = attributes[4].title
        is_ent = attributes[5]

        hint[kind] = [cat1, ent1, cat2, ent2, is_cat, is_ent]
    elif kind == "compound_or":
        hint1 = attributes[0]
        hint2 = attributes[1]

        hint1 = serialized_hint_grammar(hint1)
        hint2 = serialized_hint_grammar(hint2)

        hint[kind] = [hint1, hint2]
    return hint


def get_category_with_title(categories, title):
    for category in categories:
        if category.title == title:
            return category
    return None


def deserialized_hint_grammar(hint, categories):
    print(hint)
    hint = deepcopy(hint)
    kind = next(iter(hint))

    attributes = hint[kind]

    if kind == "is" or kind == "not" or kind == "before" or kind == "simple_or":
        cat1 = get_category_with_title(categories, attributes[0])
        ent1 = attributes[1]
        cat2 = get_category_with_title(categories, attributes[2])
        ent2 = attributes[3]

        if kind == "is":
            hint[kind] = [cat1, ent1, cat2, ent2]
        elif kind == "not":
            hint[kind] = [{"is": [cat1, ent1, cat2, ent2]}]
        elif kind == "before" or kind == "simple_or":
            cat3 = get_category_with_title(categories, attributes[4])
            if kind == "before":
                timed = len(attributes) == 6

                if timed:
                    hint[kind] = [cat1, ent1, cat2, ent2, cat3, attributes[5]]
                else:
                    hint[kind] = [cat1, ent1, cat2, ent2, cat3]
            elif kind == "simple_or":
                is_ent = attributes[5]

                hint[kind] = [cat1, ent1, cat2, ent2, cat3, is_ent]
    elif kind == "compound_or":
        hint1 = attributes[0]
        hint2 = attributes[1]

        hint1 = deserialized_hint_grammar(hint1, categories)
        hint2 = deserialized_hint_grammar(hint2, categories)

        hint[kind] = [hint1, hint2]
    return hint

#random.seed(42)
# suspects = Category("suspect", ["Ms. Scarlet", "Ms. White", "Col Mustard", "Prof Plum"], False)
# weapons = Category("weapon", ["Knife", "Rope", "Candle Stick", "Wrench"], False)
# rooms = Category("room", ["Ball room", "Living Room", "Kitchen", "Study"], False)
# time = Category("hour", ["1:00 pm", "2:00 pm", "3:00 pm", "4:00 pm"], True)

# puzzle = Puzzle([suspects, weapons, time])
# if __name__ == "__main__":
#     """is_hint = generate_hint(puzzle)
#     print(is_hint)
#     print(hint_to_english(is_hint))
#     print("")

#     compond_or_hint = generate_hint(puzzle)
#     print(hint_to_english(compond_or_hint))
#     print("")

#     before_hint = generate_hint(puzzle)
#     print(before_hint)
#     print(hint_to_english(before_hint))
#     print("")

#     hint = generate_hint(puzzle)
#     hint = generate_hint(puzzle)

#     not_hint = generate_hint(puzzle)
#     print(not_hint)
#     print(hint_to_english(not_hint))
#     print("")

#     hint = generate_hint(puzzle)
#     hint = generate_hint(puzzle)
#     hint = generate_hint(puzzle)
#     hint = generate_hint(puzzle)
#     hint = generate_hint(puzzle)
#     hint = generate_hint(puzzle)
#     hint = generate_hint(puzzle)
#     hint = generate_hint(puzzle)

#     simple_or_hint = generate_hint(puzzle)
#     print(simple_or_hint)
#     print(hint_to_english(simple_or_hint))
#     print("")"""

#     for i in range(10):
#         hint = generate_hint(puzzle)
#         print(hint_to_english(hint, grammar_dict=grammar_dict))
