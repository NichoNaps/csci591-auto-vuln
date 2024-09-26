import random
import string


# TODO save inputs to list
# Driver for email generation
def cfg_driver():
    # Generate sender and recipients
    add_1 = generate_address(10)
    add_2 = generate_address(10)
    # Set length of email body
    body_len = 1000
    # Build email string
    ret_val = helo_host(10, False, False) + \
              mail_from(add_1) + rcpt_to(add_2) + \
              "To: " + "\"" + generate_string(10, False, True) + "\"" + " <" + add_2 + ">" + "\n" + \
              "From: " + "\"" + generate_string(10, False, True) + "\"" + " <" + add_1 + ">" + "\n" + \
              "Subject: " + generate_string(10, False, True) + \
              generate_string(body_len, True, True) + "."
    print(ret_val)
    return ret_val


# HELO message
def helo_host(length, ws_flag, punc_flag):
    host_name = generate_string(length, ws_flag, punc_flag)
    return "HELO " + host_name + "\n"


# MAIL FROM:
def mail_from(address):
    return "MAIL FROM:<" + address + ">" + "\n"


# RCPT TO:
def rcpt_to(address):
    return "RCPT TO:<" + address + ">" + "\n"


# Generates a random string of defined length.
# ws_flag sets if whitespace characters are present
# punc_flag sets if punctuation is present
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
    # Build string
    random_string = "".join(random.choice(characters) for _ in range(length))
    return random_string


# Email address generator
# Lengths are set to the longest possible tld
def generate_address(usr_length):
    # longest domain is 24 characters long total
    domain = generate_string(random.randint(1, 21), False, False)
    user = generate_string(random.randint(1, usr_length), False, False)
    return user + "@" + domain + ".com"


cfg_driver()
