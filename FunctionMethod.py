import random
import string


# TODO save inputs to list

def cfg_driver():
    add_1 = generate_address(10)
    add_2 = generate_address(10)
    body_len = 1000
    ret_val = helo_host(10, False, False) + \
              mail_from(add_1) + rcpt_to(add_2) + \
              "To: " + "\"" + generate_string(10, False, True) + "\"" + " <" + add_2 + ">" + "\n" + \
              "From: " + "\"" + generate_string(10, False, True) + "\"" + " <" + add_1 + ">" + "\n" + \
              "Subject: " + generate_string(10, False, True) + \
              generate_string(body_len, True, True) + "."
    print(ret_val)
    return ret_val


def helo_host(length, ws_flag, punc_flag):
    host_name = generate_string(length, ws_flag, punc_flag)
    return "HELO " + host_name + "\n"


def mail_from(address):
    return "MAIL FROM:<" + address + ">" + "\n"


def rcpt_to(address):
    return "RCPT TO:<" + address + ">" + "\n"


def generate_string(length, ws_flag, punc_flag):
    # Digits and letters
    if ws_flag == False and punc_flag == False:
        characters = string.digits + string.ascii_letters
    # Digits letters and punctuation
    elif ws_flag == False and punc_flag == True:
        characters = string.digits + string.ascii_letters + string.punctuation
    # Digits letters and whitespace
    elif ws_flag == True and punc_flag == False:
        characters = string.digits + string.ascii_letters + string.whitespace
    # All possible
    else:
        characters = string.printable
    random_string = "".join(random.choice(characters) for _ in range(length))
    return random_string


def generate_address(usr_length):
    # longest domain is 24 characters long total
    domain = generate_string(random.randint(1, 21), False, False)
    user = generate_string(random.randint(1, usr_length), False, False)
    return user + "@" + domain + ".com"


cfg_driver()
