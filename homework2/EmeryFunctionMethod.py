import random
import string
from harness import Harness


class RandEmail:
    # Constructor for random email object. Access generation line by line via email_array
    def __init__(self, num_recipients, body_length):
        self.addresses = []
        # Generate random list of recipients
        for _ in range(num_recipients + 1):
            self.addresses.append(generate_address(5))
        self.num_recipients = num_recipients
        self.body_length = body_length
        self.helo = helo_host(10, False, False)
        self.mail_from = mail_from(self.addresses[0])
        self.rcpt_to = rcpt_to(self.addresses[1])
        self.data = "DATA"
        self.body_to = "To: " + "\"" + generate_string(10, False, True) + "\"" + " <" + self.addresses[1] + ">"
        self.body_from = "From: " + "\"" + generate_string(10, False, True) + "\"" + " <" + self.addresses[0] + ">"
        self.body_subject = "Subject: " + generate_string(10, False, True)
        self.body_body = generate_string(self.body_length, True, True)
        self.body_term = "."
        self.email_array = []
        self.email_array.append(self.helo)
        self.email_array.append(self.mail_from)
        # Append all recipients
        for x in range(len(self.addresses) - 1):
            x += 1
            self.rcpt_to = rcpt_to(self.addresses[x])
            self.email_array.append(self.rcpt_to)
        self.email_array.append(self.data)
        self.email_array.append(self.body_to)
        self.email_array.append(self.body_from)
        self.email_array.append(self.body_subject)
        self.email_array.append(self.body_body)
        self.email_array.append(self.body_term)
        # self.email_array.append("QUIT")


# TODO save inputs to list
# Driver for email generation


def cfg_driver():
    # Generate sender and recipients
    add_1 = generate_address(5)
    add_2 = generate_address(5)
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
    return "HELO " + host_name


# MAIL FROM:
def mail_from(address):
    return "MAIL FROM:<" + address + ">"


# RCPT TO:
def rcpt_to(address):
    return "RCPT TO:<" + address + ">"


def delete_items(lst, n):
    for x in range(n):

        if (len(lst) == 0):
            return
        
        lst.pop(random.randint(0, len(lst)-1))

def dupe_items(lst, n):
    for x in range(n):
        idx = random.randint(0, len(lst)-1)

        lst.insert(random.randint(0, len(lst)-1), lst[idx])

def re_order(lst, n):
    for x in range(n):
        item = lst.pop(random.randint(0, len(lst)-1))
        lst.insert(random.randint(0, len(lst)-1), item)

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
        characters = string.digits + string.ascii_letters + string.whitespace.replace('\r', '').replace('\n', '')
    # All possible
    else:
        characters = string.printable.replace('\r', '')
    # Build string
    random_string = "".join(random.choice(characters) for _ in range(length))
    return random_string


# Email address generator
# Lengths are set to the longest possible tld
def generate_address(usr_length):
    # longest domain is 24 characters long total
    domain = generate_string(random.randint(1, 5), False, False)
    user = generate_string(random.randint(1, usr_length), False, False)
    return user + "@" + domain + ".com"


harness = Harness()


tests = []
for x in range(1000):

    # make multiple emails
    allInputs = []
    for y in range(random.randint(1, 200)):
        inputs = RandEmail(random.randint(1, 5), random.randint(1, 250)).email_array
        re_order(inputs, random.randint(0, 2))
        dupe_items(inputs, random.randint(0, 2)) # This causes a loooooooot of the same crash in print_list
        delete_items(inputs, random.randint(0, 2))

        allInputs.extend(inputs)

    allInputs.append("QUIT")
    
    tests.append(allInputs)

harness.runBatch(tests, silent=True)

