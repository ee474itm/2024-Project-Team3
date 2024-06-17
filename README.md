# 2024-Project-Team3
## Team member
20190330 Song junyeong(Leader)\
20190422 Yoon sunmoon\
20190516 Lee chanryeol

## Summay of project
### Adoptation of music
The model is divided into six stages.
1. Extracting song information: Using ACRCcloud and GPT API 
2. Original lyrics extraction: Website crawling
3. Separate input music file: Use Spletter
4. Lyrics Translation: Based on GPT-4o model
5. Create music: Use suno.ai or ACEStudio
   1. If suno.ai, use api so end-to-end
   2. If ACEStudio, use translated lyrics and separated music, allocate syllables into note manually(example results are 가시_ACE)
6. Voice conversion: Use AICoverGen 
## How to run code

1. Install libraries using requirements.txt
2. In lyrics_extract.py, and lyrics_translation.py, write your gpt api key in "your_api_key"
3. Input mp3 (or m4a) file in dataflow/music_original
4. Input voice model in AICoverGen/rvc_model
5. sh [Adopting.sh](http://adopting.sh/) {file_name} {artist_name} {language pair} {model}
    1. file_name: name of mp3(mp4) file in dataflow/music_original
    2. artist_name: name of voice model to conversion
    3. language pair: original language, translating language pair, only three characters (ex. kor,eng)
    4. model: GPT-api model (ex. gpt-4o, gpt-4, gpt-3.5-turbo)

ex) sh [Adopting.sh](http://Adopting.sh) weekend.m4a Taeyeon kor,eng gpt-4o