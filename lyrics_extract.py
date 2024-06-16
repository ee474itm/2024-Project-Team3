import requests
from bs4 import BeautifulSoup
import os
import urllib
import json
import requests
import json
import re
import hashlib
import base64
import argparse
import time
import hmac
import openai
openai.api_key = "sk-proj-vqb31qtd0Duat0wT1rSmT3BlbkFJTo7L3VYeryvQNaMd5mmP"
FILE_LIST = []
track_artistid = []
track_albumid = []
track_trackid = []
TIME = []
LYRICS = []
mm = []
ss = []
xx = []
def normalize_whitespace(text):
    # 여러 개의 공백 또는 줄바꿈을 하나의 공백으로 변환
    normalized_text = re.sub(r'\s+', ' ', text)
    # 앞뒤의 공백 제거
    normalized_text = normalized_text.strip()
    # 각 줄을 개행 문자로 구분하여 하나의 공백만 남도록 변환
    normalized_text = re.sub(r' (?=\n)', '', normalized_text)
    return normalized_text
def search_google(query):
    api_key = 'AIzaSyCbF96Cz4rPlo0gTcad7jtTs-73_619F0Q'
    cse_id = 'b3cde8e76f18049c7'
    url = f"https://www.googleapis.com/customsearch/v1?q={query}&key={api_key}&cx={cse_id}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    response = requests.get(url, headers=headers)
    return response.json()
def fetch_full_content(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        return "Failed to retrieve the web page."

    soup = BeautifulSoup(response.text, 'html.parser')

    # 다양한 태그에서 텍스트를 추출
    paragraphs = soup.find_all(['p', 'div', 'span'])

    # 추출한 텍스트를 합침
    full_text = "\n".join([para.get_text() for para in paragraphs if para.get_text().strip() != ""])
    
    if not full_text:
        return "No content found on the web page."
    
    return full_text
def fetch_youtube_details(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        return {"title": "Failed to retrieve the web page.", "description": ""}
    
    soup = BeautifulSoup(response.text, 'html.parser')

    # 제목 추출
    title_tag = soup.find("meta", property="og:title")
    if title_tag:
        title = title_tag["content"]
    else:
        title = "No title found."

    # 설명 추출
    description_tag = soup.find("meta", property="og:description")
    if description_tag:
        description = description_tag["content"]
    else:
        description = "No description found."

    return title + description
def extract_context(text, keyword, context_length=500):
    # 키워드 위치 찾기
    keyword_pos = text.find(keyword)
    if keyword_pos == -1:
        return ""
    
    # 키워드 주위 300자 추출
    start_pos = max(0, keyword_pos - context_length)
    end_pos = min(len(text), keyword_pos + len(keyword) + context_length)
    return text[start_pos:end_pos]

def find_korean_song_info(title, artist, album, search_text):
    # System 및 User prompt 설정
    system_prompt = f"""The song title is '{title}' by '{artist}'
    Translate this to the exact Korean title and artist name as registered in Bugs.
    정확한 이름만을 출력하고, input과 같은 format으로 제목$가수$앨범명만 출력해\n"""
    user_prompt = f"{title}${artist}${album}"
    
    # GPT-4 API 호출
    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": search_text + user_prompt}
        ]
    )
    # API 응답에서 필요한 정보 추출
    result = response.choices[0].message.content.strip()
    print(f'GPT로 얻은 한글 노래 정보: {result}')
    return result.split("$")

def recognize_song(file_path):
    access_key = 'fbb139e0c337cc3d6fdaf53ba468ae02'
    access_secret = 'fGoEyGawg0DbPXdYbdhB6B62Pu1xfgKTRO229GGN'
    requrl = 'http://identify-ap-southeast-1.acrcloud.com/v1/identify'

    http_method = "POST"
    http_uri = "/v1/identify"
    data_type = "audio"
    signature_version = "1"
    timestamp = str(time.time())

    string_to_sign = http_method + "\n" + http_uri + "\n" + access_key + "\n" + data_type + "\n" + signature_version + "\n" + timestamp

    sign = base64.b64encode(hmac.new(access_secret.encode(), string_to_sign.encode(), digestmod=hashlib.sha1).digest())

    sample_bytes = open(file_path, 'rb').read()

    files = [
        ('sample', ('sample', sample_bytes, 'audio/mpeg'))
    ]
    data = {
        'access_key': access_key,
        'sample_bytes': len(sample_bytes),
        'timestamp': timestamp,
        'signature': sign,
        'data_type': data_type,
        'signature_version': signature_version,
    }

    response = requests.post(requrl, files=files, data=data)
    response.encoding = 'utf-8'  # Ensure the response is decoded using utf-8
    result = response.json()

    if result['status']['code'] == 0:
        song_info = result['metadata']['music'][0]
        return (song_info['title'], song_info['artists'][0]['name'], song_info['album']['name'] if 'album' in song_info else 'N/A')

    else:
        return (None, None, None)
def track_clear():
    track_albumid.clear()
    track_artistid.clear()
    track_trackid.clear()

def time_clear():
    xx.clear()
    ss.clear()
    mm.clear()
    LYRICS.clear()
    TIME.clear()

def lrc_maker(data, filename):
    TEXT = data['result']['lyrics']
    TEXT = TEXT.replace("＃", "\n")
    x = TEXT.count("|")
    if not os.path.exists(f'./dataflow/lyrics_original/lrc'):
        os.makedirs(f'./dataflow/lyrics_original/lrc')
    if not os.path.exists(f'./dataflow/lyrics_original/txt'):
        os.makedirs(f'./dataflow/lyrics_original/txt')
    with open(f'./dataflow/lyrics_original/lrc/{filename}.lrc', 'w', encoding='UTF8') as file:  # 덮어쓰기
        file.write(TEXT)
    TEXT = []
    with open(f'./dataflow/lyrics_original/lrc/{filename}.lrc', 'r', encoding='UTF8') as file:  # 한 줄씩 읽어오기
        for j in range(x):
            TEXT.append(file.readline().rstrip())
    for j in range(x):  # 시간과 가사 구분하기
        TIME.append(float(TEXT[j][:TEXT[j].rfind("|")]))
        LYRICS.append(TEXT[j][TEXT[j].rfind("|") + 1:])
    for j in range(x):
        xx.append(str(round(TIME[j] - int(TIME[j]), 2)))
        ss.append(f"{int(TIME[j]) % 60:02}")
        mm.append(f"{int(TIME[j]) // 60:02}")
    with open(f'./dataflow/lyrics_original/lrc/{filename}.lrc', 'w', encoding='UTF8') as file:  # 초기화
        file.write('')
    with open(f'./dataflow/lyrics_original/txt/{filename}.txt', 'w', encoding='UTF8') as file:  # 초기화
        file.write('')
    for j in range(x):
        with open(f'./dataflow/lyrics_original/lrc/{filename}.lrc', 'a', encoding='UTF8') as file:  # 최종
            file.write(f"[{mm[j]}:{ss[j]}{xx[j][1:]}]{LYRICS[j]}\n")
        with open(f'./dataflow/lyrics_original/txt/{filename}.txt', 'a', encoding='UTF8') as file:  # 최종
            file.write(f"{LYRICS[j]}\n")
    time_clear()
    track_clear()
    print(f"{filename}.lrc 파일을 가져왔습니다.")
    print(f"노래제목:{filename}")
    return True

def lrc_delete(filename):
    track_clear()
    os.remove(f'{filename}.lrc')
    print(f"{filename}은(는) 싱크가사를 지원하지 않습니다.")
    return False

def fetch_lyrics(title, artist, album):
    # 벅스에서 검색
    soup_artist = BeautifulSoup(requests.get(f'https://music.bugs.co.kr/search/artist?q={artist}').text, 'html.parser')
    soup_album = BeautifulSoup(requests.get(f'https://music.bugs.co.kr/search/album?q={artist} {album}').text, 'html.parser')
    soup_track = BeautifulSoup(requests.get(f'https://music.bugs.co.kr/search/track?q={artist} {title}').text, 'html.parser')

    if soup_artist.select('#container > section > div > ul > li:nth-of-type(1) > figure > figcaption > a.artistTitle'):
        artist_id = soup_artist.select_one('#container > section > div > ul > li:nth-of-type(1) > figure > figcaption > a.artistTitle')['href'][32:-25]
    else:
        print(f"{title}에 대한 검색 결과가 없습니다.")
        return
    if soup_album.select('#container > section > div > ul > li:nth-of-type(1) > figure'):
        for id in soup_album.select('#container > section > div > ul > li:nth-of-type(1) > figure'):  # 앨범검색 결과
            album_artistid = id['artistid']
            #print(album_artistid)
            album_albumid = id['albumid']
    else:
        print("%s에 대한 검색 결과가 없습니다."%album)

    track_artistid = []
    track_albumid = []
    track_trackid = []
    #print(soup_track)
    for id in soup_track.find_all("tr"):
        if id.get('artistid'):
            track_artistid.append(id.get('artistid'))
        if id.get('albumid'):
            track_albumid.append(id.get('albumid'))
        if id.get('trackid'):
            track_trackid.append(id.get('trackid'))
    #print(artist_id)
    #print(album_artistid)
    #print(track_artistid)
    if artist_id in track_artistid:
        n = track_artistid.index(artist_id)
        urllib.request.urlretrieve(f'http://api.bugs.co.kr/3/tracks/{track_trackid[n]}/lyrics?&api_key=b2de0fbe3380408bace96a5d1a76f800', f"./dataflow/lyrics_original/lrc/{title}.lrc")
        if not os.path.exists(f'./dataflow/lyrics_original'):  
            os.makedirs(f'./dataflow/lyrics_original')
        with open(f'./dataflow/lyrics_original/lrc/{title}.lrc', encoding='UTF8') as json_file:
            data = json.load(json_file)
        if data['result'] is not None:  # 싱크 가사 있을 때
            if "|" in data['result']['lyrics']:  # time이 있을 때
                lrc_maker(data, title)
            else:  # time이 없을 때
                lrc_delete(title)
        else:  # 싱크 가사 없을 때
            lrc_delete(title)
    else:
        print(f"{title}에 대한 검색 결과가 없습니다.")
        track_clear()
def get_song_summary(name):
    system_prompt = f"""Provide a brief description of the sone in less than 120 characters. It must obtain tempo, inst, style of vocal (gender, pitch)"""
    example = [{"role": "user", "content": "버즈-가시"},
               {"role": "assistant", "content": "100-110 BPM, bright and cheerful feel. synths, crisp drums, and subtle funky guitar. Clear, joyful female vocals."},
               {"role": "user", "content": "태연-weekend"},
               {"role": "assistant", "content": "70-80 BPM, emotional feel. Features acoustic/electric guitars, drums, bass, and piano. Sweet, heartbroken male vocals."}]
    messages = [{"role": "system", "content": system_prompt}] + \
               example + \
                [{"role": "user", "content":name}]
    print(messages)
    response = openai.chat.completions.create(
        model='gpt-4o',
        messages=messages
    )
    
    summary = response.choices[0].message.content.strip()
    
    return summary[:120]  # Ensuring the summary is within 120 characters

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fetch lyrics and create lrc file for a given song.")
    #parser.add_argument('--song_name', type=str, required=True, help='Song name')
    parser.add_argument('--language', type=str, required=True, help='language. e.g. kor, eng, jap')
    parser.add_argument('--path', type=str, required=True, help='language. e.g. kor, eng, jap')
    args = parser.parse_args()
    path = f'{args.path}'
    #path = './dataflow/music_input/kor/각자의밤.m4a'
    #path = f'./dataflow/music_input/{args.language}/{args.song_name}.m4a'

    if not os.path.isfile(path):
        print(f"File not found: {path}")
        exit(1)

    title, artist, album = recognize_song(path)
    os.system(f'echo "ACRCloud api로 찾은 노래 정보: 제목:{title}, 가수:{artist}, 앨범:{album}"')

    if 'kor' == args.language[:3]:
        os.system(f'echo "한국 음원사이트 기준 음원 정보 검색..."')
        search_text = search_google(title + ', ' + artist + ', ' + album +', 한국어')
        search_url = [search_text['items'][i]['link'] for i in range(len(search_text['items']))]
        search_lst = [fetch_youtube_details(search_url[i]) if 'youtube' in search_url[i] else fetch_full_content(search_url[i]) for i in range(len(search_url))]
        search_lst = list(map(normalize_whitespace, search_lst))
        search_lst = [extract_context(search_lst[i], title, context_length=500) + extract_context(search_lst[i], artist, context_length=500) + extract_context(search_lst[i], album, context_length=500) for i in range(len(search_lst))]
        #search_lst = [fetch_youtube_details(search_url[i]) if 'youtube' in search_url[i] else fetch_full_content(search_url[0])]
        title, artist, album = find_korean_song_info(title, artist, album, " ".join(search_lst))
        print(f'GPT로 찾은 노래 정보: 제목:{title}, 가수:{artist}, 앨범:{album}')
    if title and artist and album:
        if os.path.exists(f'./dataflow/lyrics_original/lrc/{title}.lrc'):
            print("Lyrics already made")
            print(f"노래제목:{title}")
        else:
            fetch_lyrics(title, artist, album)
    else:
        print("Metadata not found or incomplete in the provided file.")
    if not os.path.exists(f'./dataflow/music_style/{title}.txt'):
        with open(f'./dataflow/music_style/{title}.txt', 'w', encoding='UTF8') as file:  # 초기화
            file.write(get_song_summary(f'{artist}-{title}'))