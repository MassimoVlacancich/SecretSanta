from random import randint
from random import shuffle
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage

test_mode = True

def read_filecontent(filename):
    with open(filename, 'r') as content_file:
        content = content_file.read()
    return content

def send_email(recipient, person_name=''):
    import smtplib
    user = 'musarra.babbo.natale.segreto@gmail.com'
    pwd = 'uewcmlbwwscrsaob'

    msg = MIMEMultipart('alternative')
    subject = 'Babbo Natale Segreto - TEST' if test_mode else 'Babbo Natale Segreto'
    msg['Subject'] = subject
    msg['From'] = user
    msg['To'] = recipient

    text = ''
    template_name = 'test_template.html' if test_mode else 'template.html'
    html = read_filecontent(template_name)
    if not test_mode:
        html = html.replace('COPPIA_ID', person_name)
    # print(html)

    if test_mode:
        fp = open('test.gif', 'rb')
        msg_image = MIMEImage(fp.read())
        fp.close()
    else:
        # Pick a random GIF from the library.
        gif_number = randint(1, 12)
        gif_name = str(gif_number) + '.gif'

        # Attach Image
        fp = open('GIFS/' + gif_name, 'rb')
        msg_image = MIMEImage(fp.read())
        fp.close()

    part1 = MIMEText(text, 'plain')
    part2 = MIMEText(html, 'html')

    # Define the image's ID as referenced above
    msg_image.add_header('Content-ID', '<image1>')
    
    msg.attach(part1)
    msg.attach(part2)
    msg.attach(msg_image)

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.ehlo()
        server.starttls()
        server.login(user, pwd)
        server.sendmail(user, recipient, msg.as_string())
        server.close()
        print('successfully sent the mail to: ' + recipient)
    except Exception as e:
        print("failed to send mail")
        print(e)


everyone = [
    {"name": "max",       "family": "red",   "email": "massimovlacancich@gmail.com",    "lastyearTo": "simone"   },
    {"name": "ignazio",   "family": "red",   "email": "ignaziomusarra@gmail.com",       "lastyearTo": "camillo"  },
    {"name": "loredana",  "family": "red",   "email": "lorymarty67@libero.it",          "lastyearTo": "claudio"  },
    {"name": "roberta",   "family": "red",   "email": "robertamusarra@gmail.com",       "lastyearTo": "sabrina"  },
    {"name": "riccardo",  "family": "red",   "email": "riccardoschiliro.rs@gmail.com",  "lastyearTo": "sergio"   },
    {"name": "silvia",    "family": "red",   "email": "musarrasilvia@gmail.com",        "lastyearTo": "franco"   },
    {"name": "franco",    "family": "green", "email": "francomusarra@libero.it",        "lastyearTo": "riccardo" },
    {"name": "flavia",    "family": "green", "email": "flaviarosso@libero.it",          "lastyearTo": "max"      },
    {"name": "sabrina",   "family": "green", "email": "musarrasabrina@gmail.com",       "lastyearTo": "alessia"  },
    {"name": "camillo",   "family": "green", "email": "scalaa@yahoo.com",               "lastyearTo": "silvia"   },
    {"name": "sergio",    "family": "blue",  "email": "musarrotti@gmail.com",           "lastyearTo": "ignazio"  },
    {"name": "luisa",     "family": "blue",  "email": "luisa.arrotti@gmail.com",        "lastyearTo": "loredana" },
    {"name": "simone",    "family": "blue",  "email": "simonemusarra96@gmail.com",      "lastyearTo": "roberta"  },
    {"name": "alessia",   "family": "blue",  "email": "alemusa98@gmail.com",            "lastyearTo": "antonella"},
    {"name": "claudio",   "family": "pink",  "email": "cmus29@gmail.com",               "lastyearTo": "flavia"   },
    {"name": "antonella", "family": "pink",  "email": "brusa123451@gmail.com",          "lastyearTo": "luisa"    },
] 

debug = True

def run_test():
    # send all emails
    print('-----')
    print('Sending test email')
    print('-----')
    for person in everyone:
        print('Sending test email to: ' + person['name'] + ' -@:  ' + person['email'])
        send_email(person['email']) 

def run_secret_santa():

    # Shuffle the list of people.
    shuffle(everyone)

    # Initialize people
    for person in everyone:
        person['giftFrom'] = None
        person['giftingTo'] = None

    total_people = len(everyone)

    # Ensure that everyone makes a gift to someone else
    for person in everyone:

        # If already making a gift, skip.
        if person['giftingTo'] is not None:
            continue

        while person['giftingTo'] is None:

            random_person_idx = randint(0, total_people - 1)
            random_person = everyone[random_person_idx]

            # Try again if this random person already has a gift.
            if random_person['giftFrom'] is not None:
                continue

            # Only gift to this person if this person is not gifting to you.
            if random_person['giftingTo'] == person['name']:
                continue

            # Skip if already gifted to this person last year.
            if random_person['name'] == person['lastyearTo']:
                continue

            # Skip if same person or part of same family
            if person['name'] == random_person['name'] or person['family'] == random_person['family']:
                continue

            person['giftingTo'] = random_person['name']
            random_person['giftFrom'] = person['name']

            if debug:
                print(' --> ' + person['name'] + ' is gitfing to ' + random_person['name'])

    print('-----')
    print('Done')
    print('-----')

    for person in everyone:
        if person['giftFrom'] is None or person['giftingTo'] is None:
            print(' *** ')
            print(' * Issue! * - ' + str(person))
            print(' *** ')
        else:
            if debug:
                print(person['name'] + ' RICEVE DA: ' + person['giftFrom'] + ' REGALA A: ' + person['giftingTo'])


    # send all emails
    print('-----')
    print('Sending email')
    print('-----')
    if not debug:
        for person in everyone:
            print('Sending email to: ' + person['name'] + ' -@:  ' + person['email'])
            send_email(person['email'], person['giftingTo']) 


if test_mode:
    run_test()
else:
    run_secret_santa()