#!/bin/bash

unset LD_LIBRARY_PATH
export TF_ENABLE_ONEDNN_OPTS=0
# Check if a filename argument is provided
if [ -z "$1" ]; then
  echo "Usage: $0 <filename>"
  exit 1
fi

#노래 입력 경로, split 출력 경로
INPUT_DIR="./dataflow/music_original"
SPLIT_DIR="./dataflow/music_separated"
#입력 파일 이름
FILE=$1
SINGER=$2
LANGUAGE=$3
MODEL_NAME=$4

#입력 파일이 있나 확인. 없으면 에러메세지 출력 후 종료
if [ ! -f "$INPUT_DIR/$FILE" ]; then
  echo "File $INPUT_DIR/$FILE does not exist."
  exit 1
fi

#혹시 split 폴더 없으면 생성
mkdir -p "$SPLIT_DIR"

TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
#입력파일 경로
INPUT_FILE_PATH="$INPUT_DIR/$FILE"

#make_lyric으로 가사 추출하는 겸 노래 이름으로 앞으로 변수 사용
SONG_NAME=$(python lyrics_extract.py --language=$LANGUAGE --path=$INPUT_FILE_PATH | tee /dev/tty | grep "노래제목:" | awk -F ":" '{print $2}')
pid1=$!
#저장된 노래 이름 출력
echo "Lyrics saved:$SONG_NAME"
#노래 이름 이용해서 split한 노래도 저장함
SPLIT_SUBDIR="$SPLIT_DIR/$SONG_NAME"
echo $SPLIT_SUBDIR
#split_subdir이 없을때만 split 실행. 있으면 굳이 실행 안함
if [ ! -d "$SPLIT_SUBDIR" ]; then
  mkdir -p "$SPLIT_SUBDIR"

  # spleeter 실행
  echo "Running spleeter on $INPUT_FILE_PATH..."
  echo separate -p spleeter:2stems -o "$SPLIT_SUBDIR" "$INPUT_FILE_PATH" 
  spleeter separate -p spleeter:2stems -o "$SPLIT_SUBDIR" "$INPUT_FILE_PATH" 
  pid2=$!
  #spleeter 코드는 입력 파일 이름으로 subdirectory 만든 다음 그 아래 파일 저장함. 굳이 그럴 필요 없이 곡 이름 폴더 안에 있게 옮겨줌
  INPUT_BASENAME=$(basename "$INPUT_FILE_PATH" .m4a)
  echo $INPUT_BASENAME
  # 결과 파일 이동
  mv "$SPLIT_SUBDIR/$INPUT_BASENAME/"* "$SPLIT_SUBDIR/"
  # 빈 디렉토리 제거
  rmdir "$SPLIT_SUBDIR/$INPUT_BASENAME"

  # 제대로 안됐으면 에러메세지 출력 후 종료
  if [ $? -ne 0 ]; then
    echo "Spleeter failed to run."
    exit 1
  fi

  # 제대로 됐으면 어디 저장됐는지 말해줌
  echo "Separated files are saved in: $SPLIT_SUBDIR"
else
  # 이미 separate된 노래 있으면 굳이 안함
  echo "Music Separation was already doned"
  pid2=$!
fi


LYRICS_INPUT_PATH="./dataflow/lyrics_original/txt/$SONG_NAME.txt"
LYRICS_OUTPUT_PATH="./dataflow/lyrics_translated/$SONG_NAME/$SONG_NAME$TIMESTAMP.txt"
python lyrics_translation.py --language="$LANGUAGE" --input_path="$LYRICS_INPUT_PATH" --output_path="$LYRICS_OUTPUT_PATH" --model_name="$MODEL_NAME"
pid3=$!

STYLE_PATH="./dataflow/music_style/$SONG_NAME.txt"
GEN_PATH="./AICoverGen/generated_song/$SONG_NAME.mp3"
cd suno-api
python run.py
pid4=$!
cd ..
python suno-api/suno_download.py --input_path="$LYRICS_OUTPUT_PATH" --input_style="$STYLE_PATH" --song_name="$SONG_NAME" --output_path="$GEN_PATH"
pid5=$!

cd AICoverGen
IN_PATH="./generated_song/$SONG_NAME.mp3"
python src/main.py -i "$IN_PATH" -dir "$SINGER" -p 0
pid6=$!


fuser -k 3000/tcp
cd ..

wait $pid1
wait $pid2
wait $pid3
wait $pid4
wait $pid5
wait $pid6