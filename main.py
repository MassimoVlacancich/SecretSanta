import os
import sys
from datetime import datetime
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from random import randint
from random import shuffle

from dotenv import load_dotenv
from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse

test_mode = True # Only sends emails to all to check receipts, does not run matches
test_only_me = True
debug = True # prints matches but does not send final email
do_calls = True
calls_file_path = "calls.txt"

recording_url_audio1 = "https://secretsanta-9207.twil.io/recording1.mp3" # "https://raw.githubusercontent.com/MassimoVlacancich/SecretSanta/master/audio/recording1.mp3"
recording_url_audio2 = "https://secretsanta-9207.twil.io/recording2.mp3" # "https://raw.githubusercontent.com/MassimoVlacancich/SecretSanta/master/audio/recording2.mp3"

# Load secrets

# Load environment variables
if not os.path.exists(".env"):
    sys.exit("❌ Missing .env file. Please create it with your Twilio credentials.")

load_dotenv()

# Retrieve credentials
account_sid = os.getenv("TWILIO_ACCOUNT_SID")
auth_token = os.getenv("TWILIO_AUTH_TOKEN")
twilio_number = os.getenv("TWILIO_PHONE_NUMBER")

# Verify they exist
if do_calls and not all([account_sid, auth_token, twilio_number]):
    sys.exit("❌ Missing one or more Twilio credentials in .env (SID, token, or phone number).")

if do_calls:
    client = Client(account_sid, auth_token)

def read_filecontent(filename):
    with open(filename, 'r') as content_file:
        content = content_file.read()
    return content

def call(recipient_name, recipient_number, gift_to_name):
    message = """
    <Response>
        <Pause length="1"/>
        <Say voice="Giorgio" language="it-IT" loop="2">
            Ciao! Sono priorio contento di sentirti oggi! <break time="200ms"/>
            Sei a <emphasis> Briancone </emphasis>? Ma che bello bello bello bello! <break time="200ms"/>
            Un abbraccio a Ludmilla detta Liucy
        </Say>
    </Response>
    """

    audio_message = f"""
    <Response>
        <Play>{recording_url_audio1}</Play>
    </Response>
    """

    response = VoiceResponse()
    # response.pause(length=1)
    response.play(recording_url_audio1)
    # response.say(gift_to_name, voice="alice", language="it-IT", loop=2)
    # response.play(recording_url_audio2)

    try:
        call_result = client.calls.create(
            from_=twilio_number,
            to=recipient_number,
            twiml=message,
            record=True
        )
        print(f"📞 Call triggered successfully! SID: {call_result.sid}")

        # Append call info in CSV format: datetime,recipient_name,call_sid
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(calls_file_path, "a") as f:
            f.write(f"{timestamp},{recipient_name},{recipient_number},{call_result.sid}\n")


    except Exception as e:
        print(f"❌ Failed to place call: {e}")

def log_recordings():
    with open(calls_file_path, "r") as f:
        lines = f.readlines()

    for line in lines:
        line = line.strip()
        if not line:
            continue

        try:
            timestamp, recipient_name, recipient_number, call_sid = line.split(",")
        except ValueError:
            print(f"⚠️ Skipping invalid line: {line}")
            continue

        # Fetch recordings for this Call SID
        recs = client.recordings.list(call_sid=call_sid)
        if not recs:
            print(f"⚠️ No recordings found for Call SID: {call_sid}")
            continue

        # Log each recording URL
        for rec in recs:
            recording_url = f"https://api.twilio.com/2010-04-01/Accounts/{account_sid}/Recordings/{rec.sid}.mp3"
            print(f"{timestamp}, {recipient_name}, {recording_url}")

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
    {"name": "max",       "family": "red",   "email": "massimovlacancich@gmail.com",    "lastyearTo": "luisa"    },
    {"name": "ignazio",   "family": "red",   "email": "ignaziomusarra@gmail.com",       "lastyearTo": "sabrina"  },
    {"name": "loredana",  "family": "red",   "email": "lorymarty67@libero.it",          "lastyearTo": "sergio"   },
    {"name": "roberta",   "family": "red",   "email": "robertamusarra@gmail.com",       "lastyearTo": "simone"   },
    {"name": "riccardo",  "family": "red",   "email": "riccardoschiliro.rs@gmail.com",  "lastyearTo": "flavia"   },
    {"name": "silvia",    "family": "red",   "email": "musarrasilvia@gmail.com",        "lastyearTo": "camillo"  },
    {"name": "franco",    "family": "green", "email": "francomusarra@libero.it",        "lastyearTo": "claudio"  },
    {"name": "flavia",    "family": "green", "email": "flaviarosso@libero.it",          "lastyearTo": "roberta"  },
    {"name": "sabrina",   "family": "green", "email": "musarrasabrina@gmail.com",       "lastyearTo": "riccardo" },
    {"name": "camillo",   "family": "green", "email": "scalaa@yahoo.com",               "lastyearTo": "max"      },
    {"name": "sergio",    "family": "blue",  "email": "musarrotti@gmail.com",           "lastyearTo": "antonella"},
    {"name": "luisa",     "family": "blue",  "email": "luisa.arrotti@gmail.com",        "lastyearTo": "ignazio"  },
    {"name": "simone",    "family": "blue",  "email": "simonemusarra96@gmail.com",      "lastyearTo": "loredana" },
    {"name": "alessia",   "family": "blue",  "email": "alemusa98@gmail.com",            "lastyearTo": "silvia"   },
    {"name": "claudio",   "family": "pink",  "email": "cmus29@gmail.com",               "lastyearTo": "alessia"  },
    {"name": "antonella", "family": "pink",  "email": "brusa123451@gmail.com",          "lastyearTo": "franco"   },
]

def run_test():
    # send all emails
    print('-----')
    print('Sending test email')
    print('-----')
    for person in everyone:
        print('Sending test email to: ' + person['name'] + ' -@:  ' + person['email'])
        send_email(person['email'])

def run_test_on_me():
    send_email("massimovlacancich@gmail.com")

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
    if test_only_me:
        if do_calls:
            call("silvia", "+393386761258", "luisa")
            log_recordings()
        else:
            run_test_on_me()
    else:
        run_test()
else:
    run_secret_santa()