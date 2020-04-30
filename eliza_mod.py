#!/usr/bin/env python

"""
**Eliza** is a pattern-matching automated psychiatrist.  Given a set of rules
in the form of input/output patterns, Eliza will attempt to recognize user input
phrases and generate relevant psychobabble responses.

Each rule is specified by an input pattern and a list of output patterns.  A
pattern is a sentence consisting of space-separated words and variables.  Input
pattern variables come in two forms: single variables and segment variables;
single variables (which take the form `?x`) match a single word, while segment
variables (which take the form `?*x`) can match a phrase.  Output pattern
variables are only single variables.  The variable names contained in an input
pattern should be the same as those in the corresponding output pattern, and
each segment variable `?*x` in an input pattern corresponds to the single
variable `?x` in the output pattern.

The conversation proceeds by reading a sentence from the user, searching through
the rules to find an input pattern that matches, replacing variables in the
output pattern, and printing the results to the user.

For examples of using this scheme, see the following programs:

- [Eliza](examples/eliza/eliza.html)
- [Automated technical support system](examples/eliza/support.html)

This implementation is inspired by Chapter 5 of "Paradigms of Artificial
Intelligence Programming" by Peter Norvig.
"""

import random
import string
import re
import nltk

# nltk.download('wordnet')
# nltk.download('stopwords')

from nltk.stem import PorterStemmer
from nltk.stem import WordNetLemmatizer 
from nltk.corpus import stopwords

stop_words = set(stopwords.words('english'))
ps = PorterStemmer()
lemmatizer = WordNetLemmatizer()

## Talking to the computer

def interact(inputs, rules, word_group, default_responses):
    """Have a conversation with a user."""
    # Read a line, process it, and print the results until no input remains.
    # while True:
    try:
        # to simplify matching.
        inputs = remove_punct(inputs)       # remove punctuation
        inputs = remove_article(inputs)     # remove article
        if not inputs:
            # continue
            pass
    except:
        # break
        pass
    return respond(rules, inputs, word_group, default_responses)

def prepare_input(inputs, word_group):
    # inputs = [w for w in inputs if not w in stop_words]     # remove stopword
    # inputs = [ps.stem(x) for x in inputs]                   # stemming
    inputs = [lemmatizer.lemmatize(x, pos = "n") for x in inputs]      # lemma nouns
    inputs = [lemmatizer.lemmatize(x, pos = "v") for x in inputs]      # lemma verb
    inputs = [x.upper() for x in inputs]

    word_group = [[y.upper() for y in x] for x in word_group]
    for n, x in enumerate(inputs):
        for y in word_group:
            if x in y:
                inputs[n] = y[0]
    # print(inputs)

    return inputs

def respond(rules, inputs, word_group, default_responses):
    """Respond to an input sentence according to the given rules."""

    inputs = inputs.split() # match_pattern expects a list of tokens
    inputs = prepare_input(inputs, word_group)

    # Look through rules and find input patterns that matches the input.
    matching_rules = []
    for pattern, transforms in rules:
        pattern = pattern.split()
        replacements = match_pattern(pattern, inputs)
        if replacements:
            matching_rules.append((transforms, replacements))
    # print(matching_rules)

    # When rules are found, choose one and one of its responses at random.
    # If no rule applies, we use the default rule.
    if matching_rules:
        # responses, replacements = random.choice(matching_rules)
        responses, replacements = matching_rules[0] # select highest relationship
        response = random.choice(responses)
    else:
        replacements = {}
        response = random.choice(default_responses)

    # Replace the variables in the output pattern with the values matched from
    # the input string.
    for variable, replacement in replacements.items():
        replacement = ' '.join(switch_viewpoint(replacement))
        if replacement:
            response = response.replace('?' + variable, replacement)
    
    return response
    

## Pattern matching

def match_pattern(pattern, inputs, bindings=None):
    """
    Determine if the input string matches the given pattern.

    Expects pattern and input to be lists of tokens, where each token is a word
    or a variable.

    Returns a dictionary containing the bindings of variables in the input
    pattern to values in the input string, or False when the input doesn't match
    the pattern.
    """

    # Check to see if matching failed before we got here.
    if bindings is False:
        return False
    
    # When the pattern and the input are identical, we have a match, and
    # no more bindings need to be found.
    if pattern == inputs:
        return bindings

    bindings = bindings or {}

    # Match input and pattern according to their types.
    if is_segment(pattern):
        token = pattern[0] # segment variable is the first token
        var = token[2:] # segment variable is of the form ?*x
        return match_segment(var, pattern[1:], inputs, bindings)
    elif is_variable(pattern):
        var = pattern[1:] # single variables are of the form ?foo
        return match_variable(var, [inputs], bindings)
    elif contains_tokens(pattern) and contains_tokens(inputs):
        # Recurse:
        # try to match the first tokens of both pattern and input.  The bindings
        # that result are used to match the remainder of both lists.
        return match_pattern(pattern[1:],
                             inputs[1:],
                             match_pattern(pattern[0], inputs[0], bindings))
    else:
        return False


def match_segment(var, pattern, inputs, bindings, start=0):
    """
    Match the segment variable against the input.

    pattern and input should be lists of tokens.

    Looks for a substring of input that begins at start and is immediately
    followed by the first word in pattern.  If such a substring exists,
    matching continues recursively and the resulting bindings are returned;
    otherwise returns False.
    """

    # If there are no words in pattern following var, we can just match var
    # to the remainder of the input.
    if not pattern:
        return match_variable(var, inputs, bindings)

    # Get the segment boundary word and look for the first occurrence in
    # the input starting from index start.
    word = pattern[0]
    try:
        pos = start + inputs[start:].index(word)
    except ValueError:
        # When the boundary word doesn't appear in the input, no match.
        return False

    # Match the located substring to the segment variable and recursively
    # pattern match using the resulting bindings.
    var_match = match_variable(var, inputs[:pos], dict(bindings))
    match = match_pattern(pattern, inputs[pos:], var_match)

    # If pattern matching fails with this substring, try a longer one.
    if not match:
        return match_segment(var, pattern, inputs, bindings, start + 1)
    
    return match


def match_variable(var, replacement, bindings):
    """Bind the input to the variable and update the bindings."""
    binding = bindings.get(var)
    if not binding:
        # The variable isn't yet bound.
        bindings.update({var: replacement})
        return bindings
    if replacement == bindings[var]:
        # The variable is already bound to that input.
        return bindings

    # The variable is already bound, but not to that input--fail.
    return False


## Pattern matching utilities

def contains_tokens(pattern):
    """Test if pattern is a list of subpatterns."""
    return type(pattern) is list and len(pattern) > 0


def is_variable(pattern):
    """Test if pattern is a single variable."""
    return (type(pattern) is str
            and pattern[0] == '?'
            and len(pattern) > 1
            and pattern[1] != '*'
            and pattern[1] in string.ascii_letters
            and ' ' not in pattern)


def is_segment(pattern):
    """Test if pattern begins with a segment variable."""
    return (type(pattern) is list
            and pattern
            and len(pattern[0]) > 2
            and pattern[0][0] == '?'
            and pattern[0][1] == '*'
            and pattern[0][2] in string.ascii_letters
            and ' ' not in pattern[0])


## Translating user input

def replace(word, replacements):
    """Replace word with rep if (word, rep) occurs in replacements."""
    for old, new in replacements:
        if word == old:
            return new
    return word


def switch_viewpoint(words):
    """Swap some common pronouns for interacting with a robot."""
    replacements = [('I', 'YOU'),
                    ('YOU', 'I'),
                    ('ME', 'YOU'),
                    ('MY', 'YOUR'),
                    ('AM', 'ARE'),
                    ('ARE', 'AM')]
    return [replace(word, replacements) for word in words]

def remove_article(string):
    string = re.sub("(\s+)(a|an|the)(\s+)", " ", string)
    string = re.sub("(\A)(a|an|the)(\s+)", "", string)
    return string

def remove_punct(string):
    """Remove common punctuation marks."""
    if string.endswith('?'):
        string = string[:-1]
    return (string.replace(',', '')
            .replace('.', '')
            .replace(';', '')
            .replace('!', ''))
