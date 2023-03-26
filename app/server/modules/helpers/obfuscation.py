## A collection of function used to obfuscate a Command and Control (C2) process


import base64
import random
import string

def random_rot_obfuscate_string(input_string:str) -> str:
    # Choose a random shift value between 1 and 25
    shift =  13#random.randint(1, 25)
    
    # Initialize an empty string to hold the obfuscated output
    obfuscated_string = ''
    
    # Loop over each character in the input string
    for char in input_string:
        # Check if the character is a letter
        if char.isalpha():
            # Determine the offset based on the character's case
            if char.isupper():
                offset = ord('A')
            else:
                offset = ord('a')
            
            # Apply the ROT shift and append the obfuscated character
            obfuscated_char = chr(((ord(char) - offset + shift) % 26) + offset)
            obfuscated_string += obfuscated_char
        else:
            # Append non-letter characters without obfuscating them
            obfuscated_string += char
    
    return obfuscated_string


def base64_encode_string(input_string:str) -> str:
    """base64 encode the command"""
    # Convert the input string to bytes
    input_bytes = input_string.encode('utf-8')
    
    # Encode the bytes as base64
    encoded_bytes = base64.b64encode(input_bytes)
    
    # Convert the encoded bytes back to a string
    encoded_string = encoded_bytes.decode('utf-8')
    
    return "C:\Windows\System32\powershell.exe -Nop -ExecutionPolicy bypass -enc {encoded_string}"



def variable_obfuscation(input_string:str) -> str:
    obfuscated = ""
    var_count = 1
    for word in input_string.split():
        if len(word) > 2:
            var_name = ''.join(random.choice(string.ascii_letters) for i in range(random.randint(5,10)))
            obfuscated += "${}='".format(var_name) + word + "';"
            obfuscated += "$a=${};".format(var_name)
            var_count += 1
        else:
            obfuscated += word + " "
    return obfuscated



def reverse_string(input_string:str) -> str:
    """Rever the command"""
    # Use slicing to reverse the string
    reversed_string = input_string[::-1]
    
    return reversed_string


def obfuscate_string(function_names:list, command:str) -> str:
    """
    Takes a list of function names, and a string input
    runs the corresponsing functions against the input
    return: obfusated string
    """
    functions = {
        'rot': random_rot_obfuscate_string,
        'base64': base64_encode_string,
        'var_obsfuscate': variable_obfuscation,
        'reverse': reverse_string
    }
    for name in function_names:
        if name in functions:
             command = functions[name](command)
        else:
            print("Function {} not found!".format(name))

    return command


# print(obfuscate_string(["base64", "rot", "reverse"], "my name is simeon"))
