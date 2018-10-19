import json
import requests
import time
import urllib
import os
import youtube_dl

TOKEN = '700462758:AAGTGgDfsMCgDlXBwG5y965w7jHVHoxVGAE'
URL = "https://api.telegram.org/bot{}/".format(TOKEN)

YDL_OPTS = {
    'format': 'bestaudio/best',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
    'outtmpl': '%(id)s.%(ext)s',
}

def get_url(url):
    response = requests.get(url)
    content = response.content.decode("utf8")
    return content


def get_json_from_url(url):
    content = get_url(url)
    js = json.loads(content)
    return js


def get_updates(offset=None):
    url = URL + "getUpdates?timeout=100"
    if offset:
        url += "&offset={}".format(offset)
    js = get_json_from_url(url)
    return js


def get_last_update_id(updates):
    update_ids = []
    for update in updates["result"]:
        update_ids.append(int(update["update_id"]))
    return max(update_ids)


def download_all(updates):
    for update in updates["result"]:
        text = update["message"]["text"]
        chat = update["message"]["chat"]["id"]
        print(text)
        if r'/start' in text:
            send_message("Welcome to YouTube MP3 downloader chat bot! "
                         "Share any youtube link here and the downloaded mp3 file will be sent to you.",
                chat)
            continue
        with youtube_dl.YoutubeDL(YDL_OPTS) as ydl:
            try:
                result = ydl.extract_info(text)
                send_message("Downloaded {}. Sending it to you...".format(result['title']), chat)
                send_file = "{}.mp3".format(result['id'])
                if os.path.exists(send_file):
                    s = send_audio(send_file, chat)
                if s['ok']: 
                    os.remove(send_file)
                else:
                    send_message("Sending failed! :(", chat)
            except:
                send_message("Send me a valid URL and I will download it for you. "
                    "Dont send me junk!", chat)

def get_last_chat_id_and_text(updates):
    num_updates = len(updates["result"])
    last_update = num_updates - 1
    text = updates["result"][last_update]["message"]["text"]
    chat_id = updates["result"][last_update]["message"]["chat"]["id"]
    return (text, chat_id)


def send_message(text, chat_id):
    text = urllib.parse.quote_plus(text)
    url = URL + "sendMessage?text={}&chat_id={}".format(text, chat_id)
    get_url(url)

def send_audio(filepath, chat_id):
    print("Sending the file: {}".format(filepath))
    url = URL + "sendAudio?chat_id={}".format(chat_id)
    files = {'audio': open(filepath, 'rb')}
    r = requests.post(url, files=files)
    return json.loads(r.text)

def main():
    last_update_id = None
    while True:
        updates = get_updates(last_update_id)
        if len(updates["result"]) > 0:
            last_update_id = get_last_update_id(updates) + 1
            download_all(updates)
        time.sleep(0.5)


if __name__ == '__main__':
    main()