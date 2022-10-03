import base64
import string
import random

from itsdangerous import base64_encode

eicar_string = 'X5O!P%@AP[4\PZX54(P^)7CC)7}$EICAR-STANDARD-ANTIVIRUS-TEST-FILE!$H+H*'
max_num_files = 100

def write_seed_files(max_num_files: int = 25):
    for i in range(1, max_num_files):
        file_name = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))+random.choice(['.exe','.dll','.dat'])
        unique_string = f"Welcome to KC7, the cybersecurity game. If you're a player, congrats! You found malware file {file_name}. If you aren't a player... how'd you find us? Visit kc7cyber.com to learn more!"
        file_string = eicar_string + "\n\n\n" + base64_encode(unique_string).decode("utf-8")

        file = open("output/"+file_name,"w")
        file.write(file_string)

write_seed_files()
