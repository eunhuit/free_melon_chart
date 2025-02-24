from bs4 import BeautifulSoup
from pytubefix import YouTube
import base64, requests, os, time, random, datetime


def get_spotify_access_token(client_id, client_secret):
    auth_url = "https://accounts.spotify.com/api/token"
    auth_header = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
    auth_data = {"grant_type": "client_credentials"}
    auth_response = requests.post(auth_url, headers={"Authorization": f"Basic {auth_header}"}, data=auth_data)
    return auth_response.json()["access_token"]


def get_album_cover(access_token, title, artist):
    search_url = f"https://api.spotify.com/v1/search?q=track:{title}%20artist:{artist}&type=track&limit=1"
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(search_url, headers=headers)
    data = response.json()

    if data["tracks"]["items"]:
        images = data["tracks"]["items"][0]["album"]["images"]
        if images:
            return images[0]["url"]
    return "None"  # 이미지를 찾을 수 없을 때 "None" 반환


def get_melon_chart():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'}
    url = 'https://www.melon.com/chart/'
    response = requests.get(url, headers=headers)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, 'html.parser')
    chart = []

    song_rows = soup.select('#frm > div > table > tbody > tr')

    for row in song_rows:
        try:
            title = row.select_one('div.rank01 > span > a').text.strip()
            artist = row.select_one('div.rank02 > a').text.strip()
            chart.append((title, artist))
        except AttributeError as e:
            print(f"요소를 찾지 못해 해당 행을 건너뜁니다. 오류: {e}")
            continue

    return chart


def get_melon_chart_with_spotify_covers(client_id, client_secret):
    access_token = get_spotify_access_token(client_id, client_secret)
    melon_chart = get_melon_chart()
    chart_with_covers = []

    for title, artist in melon_chart:
        cover_url = get_album_cover(access_token, title, artist)
        chart_with_covers.append(f"{title}^{artist}^{cover_url}")

    return chart_with_covers


def save_to_file(filename, data):
    with open(filename, "w", encoding="utf-8") as file:
        file.write("\n".join(data))
    print(f"결과가 '{filename}' 파일에 저장되었습니다.")

def get_youtube_link(title, artist):
    query = f"{title} {artist} lyrics"
    url = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        text = response.text
        start_index = text.find('/watch?v=')
        if start_index != -1:
            end_index = text.find('\\', start_index)
            if end_index != -1:
                extracted_substring = text[start_index:end_index]
                full_link = f"https://www.youtube.com{extracted_substring}"
                try:
                    yt = YouTube(full_link)
                    duration = yt.length  # 동영상 길이(초)

                    if duration > 1800:  # 30분 = 1800초
                        print(f"{title} - {artist}: Skipped (Too long)")
                        return None

                    print(f"{title} - {artist}: Link found")
                    return full_link
                except Exception as e:
                    print(f"{title} - {artist}: Error (Pytube): {e}")
                    return None

        print(f"{title} - {artist}: No link found")
        return None

    except requests.exceptions.RequestException as e:
        print(f"Request Error: {e}")
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None

def download_youtube_audio(url, file_number, output_path='assets'):
    try:
        yt = YouTube(url)
        audio = yt.streams.filter(only_audio=True).first()

        if not os.path.exists(output_path):
            os.makedirs(output_path)

        new_file = os.path.join(output_path, f"{file_number}.mp3")
        
        # 파일이 이미 존재하면 삭제
        if os.path.exists(new_file):
            os.remove(new_file)
            print(f"기존 파일 삭제: {new_file}")

        out_file = audio.download(output_path=output_path)
        os.rename(out_file, new_file)

        print(f"다운로드 완료: {new_file}")
    except Exception as e:
        print(f"오류 발생: {str(e)}")

def read_songs_from_file(filename="melon.txt"):
    songs = []
    try:
        with open(filename, "r", encoding="utf-8") as file:
            for index, line in enumerate(file, start=1):
                parts = line.strip().split("^")
                if len(parts) == 3:
                    displayName, artist, cover = map(str.strip, parts)
                    songs.append({
                        "path": f"assets/{index}.mp3",
                        "displayName": displayName,
                        "cover": cover,
                        "artist": artist
                    })
                    print(f"곡 추가됨: {displayName} - {artist}")
                else:
                    print(f"잘못된 형식의 줄 발견 (라인 {index}): {line.strip()}")
    except FileNotFoundError:
        print(f"파일을 찾을 수 없습니다: {filename}")
    return songs


def generate_js_code(songs):
    now = datetime.datetime.now()
    formatted_date = now.strftime("%Y년 %m월 %d일 %H시 %M분")
    js_code = f"const time = '마지막 업데이트: {formatted_date}';\n" 
    js_code += 'document.getElementById("time").innerHTML = time;\n'
    js_code += "const songs = [\n"
    for song in songs:
        js_code += f"""    {{
        path: '{song["path"]}',
        displayName: '{song["displayName"]}',
        cover: '{song["cover"]}',
        artist: '{song["artist"]}',
    }},\n"""
    js_code += "];"
    return js_code

client_id = "2028ab41c830455d9add09c86804d830"
client_secret = "8c049cc951ee467f92fc103ab94de616"

chart_data = get_melon_chart_with_spotify_covers(client_id, client_secret)

## 결과를 메모장 파일로 저장 (덮어쓰기)
#filename = "melon.txt"
#if os.path.exists(filename):
#    print(f"'{filename}' 파일이 이미 존재합니다. 덮어쓰기를 진행합니다.")
#save_to_file(filename, chart_data)

## melon.txt 파일 읽기 및 melon_links.txt 파일 생성
#with open('melon.txt', 'r', encoding='utf-8') as f_in, open('melon_links.txt', 'w', encoding='utf-8') as f_out:
#    for line in f_in:
#        parts = line.strip().split('^')
#        if len(parts) >= 2:
#            title, artist = parts[0], parts[1]
#            link = get_youtube_link(title, artist)
#            if link:
#                f_out.write(f"{link}\n")
#
#            # 요청 간 딜레이 추가
#            time.sleep(random.uniform(1, 3))

## melon_links.txt 파일 읽기 및 mp3 다운로드
#with open('melon_links.txt', 'r', encoding='utf-8') as f:
#    for i, line in enumerate(f, 1):
#        url = line.strip()
#        if url:  # 빈 줄이 아닐 경우에만 다운로드
#            download_youtube_audio(url, file_number=i)

songs = read_songs_from_file()
js_code = generate_js_code(songs)

with open("songs_data.js", "w", encoding="utf-8") as js_file:
    js_file.write(js_code)

print("songs_data.js 파일이 생성되었습니다.")

