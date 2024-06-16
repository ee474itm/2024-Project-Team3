import time
import requests
import subprocess
import argparse
import os
import signal
import shutil
# replace your vercel domain
base_url = 'http://localhost:3000'


def custom_generate_audio(payload):
    url = f"{base_url}/api/custom_generate"
    response = requests.post(url, json=payload, headers={'Content-Type': 'application/json'})
    return response.json()


def extend_audio(payload):
    url = f"{base_url}/api/extend_audio"
    response = requests.post(url, json=payload, headers={'Content-Type': 'application/json'})
    return response.json()

def generate_audio_by_prompt(payload):
    url = f"{base_url}/api/generate"
    response = requests.post(url, json=payload, headers={'Content-Type': 'application/json'})
    return response.json()


def get_audio_information(audio_ids):
    url = f"{base_url}/api/get?ids={audio_ids}"
    response = requests.get(url)
    return response.json()


def get_quota_information():
    url = f"{base_url}/api/get_limit"
    response = requests.get(url)
    return response.json()

def get_clip(clip_id):
    url = f"{base_url}/api/clip?id={clip_id}"
    response = requests.get(url)
    return response.json()

def generate_whole_song(clip_id):
    payloyd = {"clip_id": clip_id}
    url = f"{base_url}/api/concat"
    response = requests.post(url, json=payload)
    return response.json()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="")
    parser.add_argument('--input_path', type=str, required=True, help='')
    parser.add_argument('--input_style', type=str, required=True, help='')
    parser.add_argument('--song_name', type=str, required=True, help='')
    parser.add_argument('--output_path', type=str, required=True, help='')
    args = parser.parse_args()
    print(1)
    time.sleep(10)

    f1 = open(args.input_path, 'r')
    lyrics = f1.read()
    f1.close()

    f2 = open(args.input_style,'r')
    tag = f2.read()
    f2.close()

    data = custom_generate_audio({
        "prompt": lyrics,
        "tags": tag,
        "title": f"{args.song_name}_suno",
        "make_instrumental": False,
        "wait_audio": True
    })

    ids = f"{data[0]['id']},{data[1]['id']}"
    print(f"ids: {ids}")

    for _ in range(60):
        data = get_audio_information(ids)
        if data[0]["status"] == 'streaming':
            print(f"{data[0]['id']} ==> {data[0]['audio_url']}")
            print(f"{data[1]['id']} ==> {data[1]['audio_url']}")
            break
        # sleep 5s
        time.sleep(5)
    time.sleep(300)
    c = f"wget https://cdn1.suno.ai/{data[1]['id']}.mp3"
    os.system(c)
    os.rename(f"{data[1]['id']}.mp3",f"{args.song_name}_suno.mp3")
    shutil.move(f'{args.song_name}_suno.mp3',args.output_path)