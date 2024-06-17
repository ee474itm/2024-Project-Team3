import openai
import json
import random
import os
import argparse

openai.api_key = 'your_api_key'

system_prompt = f"""You are a lyricist and translator who translates lyrics.
You must translate the lyrics of the {{original}} song provided to {{translated}}.
In this case, the number of syllables of words that are translated to sing along to the beat of the song must be similar. 
It's okay to paraphrase or modify the meaning, so try translating it with the number of syllables as the top priority.
Let's think step by step. First, interpret the overall meaning of these Korean lyrics.
Second, based on the interpretation of the Korean lyrics, select key English words that convey the emotions and message of the lyrics.
Third, to make english lyrics similar to korean, find English words that have similar meanings to the selected key words and also sound similar to the original Korean words.
Finally, using interpreted overall meaning and found key word, make english lyrics
You SHOULD output final lyrics after ##Final lyrics## form"""

def get_response(language, input_path, example_num=5, model_name='gpt-4o'):
    if os.path.exists(input_path):
        with open(input_path, 'r', encoding='utf-8') as f:
            lyrics = f.read()
    else:
        raise ValueError("input path 잘못됨")

    example = []
    filename = './dataflow/few_example_data/cot_' + language[0][:3] + '2' + language[1][:3] + '.jsonl'
    with open(filename, 'r', encoding='utf-8') as f:
        count = sum([1 for line in f])
    if count < example_num:
        raise ValueError("example의 개수가 준비된 데이터 개수보다 많음")

    with open(filename, 'r', encoding='utf-8') as f:
        idx = random.sample(range(count), example_num)
        i = 0
        for line in f:
            data = json.loads(line)
            if i in idx:
                example.append(data['messages'][1])
                example.append(data['messages'][2])
            i += 1
    """with open('../basic_pitch_output/vocals_basic_pitch.csv', 'r') as file:
        lines = file.readlines()
    lyrics = "MIDI information:\n" + "".join(lines) + "\noriginal lyrics:\n" + lyrics"""
    messages = [{"role": "system", "content": system_prompt.format(original=language[0], translated=language[1])}] + \
               example + \
                [{"role": "user", "content":lyrics}]
    response = openai.chat.completions.create(
        model=model_name,
        messages=messages
    )
    return response

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Translate lyrics using OpenAI GPT model')
    parser.add_argument('--language', type=str, required=True, help='Comma-separated language pair, e.g., "kor,eng"')
    parser.add_argument('--input_path', type=str, required=True, help='Path to the input lyrics file')
    parser.add_argument('--output_path', type=str, required=True, help='Path to save the GPT response')
    parser.add_argument('--model_name', type=str, default='gpt-4o', help='Name of the GPT model to use')
    parser.add_argument('--example_num', type=int, default=3, help='Number of examples')

    args = parser.parse_args()
    language_pair = args.language.split(',')
    if len(language_pair) != 2:
        raise ValueError("Invalid language format. Use 'lang1,lang2' format")
    print('가사 번역 시작...')
    response = get_response(language_pair, args.input_path, example_num=args.example_num, model_name=args.model_name)
    
    # Save response to the output file
    if not os.path.exists(f'./dataflow/lyrics_translated'):
        os.makedirs(f'./dataflow/lyrics_translated')
    if not os.path.exists("/".join(args.output_path.split('/')[:-1])):
        os.makedirs("/".join(args.output_path.split('/')[:-1]))
    with open(args.output_path, 'w', encoding='utf-8') as f:
        f.write(response.choices[0].message.content.strip().split('Final lyrics##')[1])
    
    print(f"Translation saved to {args.output_path}")
