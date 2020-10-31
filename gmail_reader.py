# -*- coding: utf-8 -*-
"""gmail_reader.py
"""
from func import htmlToText, cleaning_raw_text, read_html_files, create_csv

import imaplib
import email
import re
import os
from os import listdir
from os.path import isfile, join

from email.header import decode_header
import pandas as pd
pd.set_option('display.max_colwidth', 100)


# here an instruction how to create password 
# for you app https://support.google.com/accounts/answer/185833
# account credentials
username = os.environ.get("USERNAME")
password = os.environ.get("PASSWORD")

# create an IMAP4 class with SSL 
imap = imaplib.IMAP4_SSL("imap.gmail.com")
# authenticate
imap.login(username, password)

status, messages = imap.select("INBOX")
# number of top emails to fetch
N = 206
# total number of emails
messages = int(messages[0])

from_list = []
subject_list = []
html_text_list = []
body_text_list = []
index_list = []

for i in range(messages, messages-N, -1):
    # fetch the email message by ID
    res, msg = imap.fetch(str(i), "(RFC822)")
    for response in msg:
        if isinstance(response, tuple):
            # parse a bytes email into a message object
            msg = email.message_from_bytes(response[1])
            # decode the email subject
            subject = decode_header(msg["Subject"])[0][0]
            if isinstance(subject, bytes):
                # if it's a bytes, decode to str
                subject = subject.decode()
            # email sender
            from_ = msg.get("From")
            
            # if the email message is multipart
            if msg.is_multipart():
                # iterate over email parts
                for part in msg.walk():
                    # extract content type of email
                    content_type = part.get_content_type()
                    content_disposition = str(part.get("Content-Disposition"))
                    try:
                        # get the email body
                        body = part.get_payload(decode=True).decode()
                    except:
                        pass
                    if content_type == "text/plain" and "attachment" not in content_disposition:
                        # print text/plain emails and skip attachments
                        # body_text_list.append(body)
                        print('test1')
                    elif "attachment" in content_disposition:
                        # download attachment
                        filename = part.get_filename()
                        if filename:
                            if not os.path.isdir(subject):
                                # make a folder for this email (named after the subject)
                                continue
                                # os.mkdir(f"from_gmail/{i}")
                            filepath = os.path.join(f"{i}", f"{i}")
                            # download attachment and save it
                            open(filepath, "wb").write(part.get_payload(decode=True))
            else:
                # extract content type of email
                content_type = msg.get_content_type()
                # get the email body
                body = msg.get_payload(decode=True).decode()
                if content_type == "text/plain":
                    # print only text email parts
                    # body_text_list.append(body)
                    print('test2')
            if content_type == "text/html":
                # if it's HTML, create a new HTML file and open it in browser

                filename = f"{i}.html"
                filepath = os.path.join("from_gmail/", filename)
                # write the file
                open(filepath, "w", encoding='utf-8').write(body)
                # open in the default browser
                # webbrowser.open(filepath)
                index_list.append(i)
                subject_list.append(subject)
                from_list.append(from_)
                
                html_text_list.append(body)
                body_text = htmlToText(body)
                body_text_list.append(body_text)
                print(i, (len(body)))
            # print("="*100)
                
imap.close()
imap.logout()

print(len(index_list))
print(len(from_list))
print(len(subject_list))
print(len(html_text_list))
print(len(body_text_list))

all_urls_list = []
MAX_URL_SIZE = 50
SITES = ('https://medium.com/', 'https://towardsdatascience.com')

for text_with_urls in html_text_list:
    urls = re.findall(r"""(?i)\b((?:https?:(?:/{1,3}|[a-z0-9%])|[a-z0-9.\-]+[.](?:com|net|org|edu|gov|mil|aero|asia|biz|cat|coop|info|int|jobs|mobi|museum|name|post|pro|tel|travel|xxx|ac|ad|ae|af|ag|ai|al|am|an|ao|aq|ar|as|at|au|aw|ax|az|ba|bb|bd|be|bf|bg|bh|bi|bj|bm|bn|bo|br|bs|bt|bv|bw|by|bz|ca|cc|cd|cf|cg|ch|ci|ck|cl|cm|cn|co|cr|cs|cu|cv|cx|cy|cz|dd|de|dj|dk|dm|do|dz|ec|ee|eg|eh|er|es|et|eu|fi|fj|fk|fm|fo|fr|ga|gb|gd|ge|gf|gg|gh|gi|gl|gm|gn|gp|gq|gr|gs|gt|gu|gw|gy|hk|hm|hn|hr|ht|hu|id|ie|il|im|in|io|iq|ir|is|it|je|jm|jo|jp|ke|kg|kh|ki|km|kn|kp|kr|kw|ky|kz|la|lb|lc|li|lk|lr|ls|lt|lu|lv|ly|ma|mc|md|me|mg|mh|mk|ml|mm|mn|mo|mp|mq|mr|ms|mt|mu|mv|mw|mx|my|mz|na|nc|ne|nf|ng|ni|nl|no|np|nr|nu|nz|om|pa|pe|pf|pg|ph|pk|pl|pm|pn|pr|ps|pt|pw|py|qa|re|ro|rs|ru|rw|sa|sb|sc|sd|se|sg|sh|si|sj|Ja|sk|sl|sm|sn|so|sr|ss|st|su|sv|sx|sy|sz|tc|td|tf|tg|th|tj|tk|tl|tm|tn|to|tp|tr|tt|tv|tw|tz|ua|ug|uk|us|uy|uz|va|vc|ve|vg|vi|vn|vu|wf|ws|ye|yt|yu|za|zm|zw)/)(?:[^\s()<>{}\[\]]+|\([^\s()]*?\([^\s()]+\)[^\s()]*?\)|\([^\s]+?\))+(?:\([^\s()]*?\([^\s()]+\)[^\s()]*?\)|\([^\s]+?\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’])|(?:(?<!@)[a-z0-9]+(?:[.\-][a-z0-9]+)*[.](?:com|net|org|edu|gov|mil|aero|asia|biz|cat|coop|info|int|jobs|mobi|museum|name|post|pro|tel|travel|xxx|ac|ad|ae|af|ag|ai|al|am|an|ao|aq|ar|as|at|au|aw|ax|az|ba|bb|bd|be|bf|bg|bh|bi|bj|bm|bn|bo|br|bs|bt|bv|bw|by|bz|ca|cc|cd|cf|cg|ch|ci|ck|cl|cm|cn|co|cr|cs|cu|cv|cx|cy|cz|dd|de|dj|dk|dm|do|dz|ec|ee|eg|eh|er|es|et|eu|fi|fj|fk|fm|fo|fr|ga|gb|gd|ge|gf|gg|gh|gi|gl|gm|gn|gp|gq|gr|gs|gt|gu|gw|gy|hk|hm|hn|hr|ht|hu|id|ie|il|im|in|io|iq|ir|is|it|je|jm|jo|jp|ke|kg|kh|ki|km|kn|kp|kr|kw|ky|kz|la|lb|lc|li|lk|lr|ls|lt|lu|lv|ly|ma|mc|md|me|mg|mh|mk|ml|mm|mn|mo|mp|mq|mr|ms|mt|mu|mv|mw|mx|my|mz|na|nc|ne|nf|ng|ni|nl|no|np|nr|nu|nz|om|pa|pe|pf|pg|ph|pk|pl|pm|pn|pr|ps|pt|pw|py|qa|re|ro|rs|ru|rw|sa|sb|sc|sd|se|sg|sh|si|sj|Ja|sk|sl|sm|sn|so|sr|ss|st|su|sv|sx|sy|sz|tc|td|tf|tg|th|tj|tk|tl|tm|tn|to|tp|tr|tt|tv|tw|tz|ua|ug|uk|us|uy|uz|va|vc|ve|vg|vi|vn|vu|wf|ws|ye|yt|yu|za|zm|zw)\b/?(?!@)))""", text_with_urls)
    url_list = []
    for url in urls:
        url = re.sub('\?source.+', '', url)
        if url.startswith(SITES) and len(url) > MAX_URL_SIZE:
            url_list.append(url)
        # else:
        #     False
        all_urls_list.append(url_list)

links = [u for url in all_urls_list for u in url]
print(len(links))
unique_links = set(links)
print(len(unique_links))

df = pd.DataFrame({'index': index_list, 'from':from_list, 'subject':subject_list, 'html_text_list':html_text_list, 'body_text_list':body_text_list})

html_list = []

for html_ in df.body_text_list:
    html_list.append(cleaning_raw_text(html_))

path = os.path.abspath('from_gmail/')
all_files = [f for f in listdir(path) if isfile(join(path, f)) and f.endswith(".html")]

# Commented out IPython magic to ensure Python compatibility.
path_and_files = [path + "/" + f for f in all_files]
read_html_files(path=path_and_files) # instead of path_and_files

all_filenames_without_html = []

for filename in all_files:
    pattern = ".html"
    filename = re.sub(pattern, '', filename)
    all_filenames_without_html.append(filename)

columns = ['txt']
series = pd.DataFrame(html_list, index=None, columns=columns)
frames = [series]
data = pd.concat(frames)

data['from'] = df['from']
data['subject'] = df['subject']
data['body_text'] = df['body_text_list']

# Delete first symbol \t in the string
cleaned_dt_list = []
for dt in data.txt:
    dt = ''.join(str(dt).split('\t', 1))
    dt = ''.join(str(dt).split('\n', 1))
    cleaned_dt_list.append(dt)
data.txt = cleaned_dt_list
print(data)
create_csv(data, 'data')
