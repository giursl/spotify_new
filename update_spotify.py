import os
import requests
import base64

cid = os.getenv("SPOTIFY_CLIENT_ID")
csec = os.getenv("SPOTIFY_CLIENT_SECRET")
rtoken = os.getenv("SPOTIFY_REFRESH_TOKEN")

# Obter novo Access Token
res = requests.post("https://accounts.spotify.com/api/token", data={
    "grant_type": "refresh_token",
    "refresh_token": rtoken,
    "client_id": cid,
    "client_secret": csec
}).json()

token = res.get("access_token")
track_name = "Nada a tocar"
artist_name = "Offline"
cover_url = ""
progress_ms = 0
duration_ms = 1
is_playing = False

if token:
    headers = {"Authorization": f"Bearer {token}"}
    track_res = requests.get("https://api.spotify.com/v1/me/player/currently-playing", headers=headers)
    
    if track_res.status_code == 200 and track_res.text:
        data = track_res.json()
        if data and data.get("item"):
            is_playing = data.get("is_playing", False)
            item = data["item"]
            track_name = item["name"]
            artist_name = ", ".join([artist["name"] for artist in item["artists"]])
            cover_url = item["album"]["images"][0]["url"] if item["album"]["images"] else ""
            progress_ms = data.get("progress_ms", 0)
            duration_ms = item["duration_ms"]

img_base64 = ""
if cover_url:
    try:
        img_data = requests.get(cover_url).content
        img_base64 = f"data:image/jpeg;base64,{base64.b64encode(img_data).decode()}"
    except:
        pass

progress_percent = int((progress_ms / duration_ms) * 100) if duration_ms > 0 else 0

def format_time(ms):
    seconds = int(ms / 1000)
    minutes = seconds // 60
    secs = seconds % 60
    return f"{minutes}:{secs:02d}"

current_time = format_time(progress_ms)
status_label = "NOW PLAYING" if is_playing else "LAST PLAYED"

image_tag = f'<image x="16" y="16" width="120" height="120" preserveAspectRatio="xMidYMid slice" href="{img_base64}" rx="4"/>' if img_base64 else ''

svg_content = f"""<svg width="460" height="152" viewBox="0 0 460 152" fill="none" xmlns="http://www.w3.org/2000/svg">
  <style>
    .bg {{ fill: #181818; }}
    .title {{ fill: #ffffff; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif; font-size: 16px; font-weight: 700; }}
    .artist {{ fill: #b3b3b3; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif; font-size: 13px; font-weight: 400; }}
    .status {{ fill: #1db954; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif; font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; }}
    .time {{ fill: #a7a7a7; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif; font-size: 11px; }}
  </style>
  <rect width="460" height="152" rx="8" class="bg" />
  
  <rect x="16" y="16" width="120" height="120" rx="4" fill="#282828" />
  {image_tag}

  <text x="152" y="50" class="title">{track_name[:32] + ("..." if len(track_name) > 32 else "")}</text>
  <text x="152" y="72" class="artist">{artist_name[:35] + ("..." if len(artist_name) > 35 else "")}</text>
  
  <g transform="translate(152, 92)">
    <path fill="#1db954" d="M12 0C5.4 0 0 5.4 0 12s5.4 12 12 12 12-5.4 12-12S18.66 0 12 0zm5.521 17.34c-.24.359-.66.48-1.021.24-2.82-1.74-6.36-2.101-10.561-1.141-.418.122-.779-.179-.899-.539-.12-.421.18-.78.54-.9 4.56-1.021 8.52-.6 11.64 1.32.42.18.479.659.301 1.02zm1.44-3.3c-.301.42-.841.6-1.262.3-3.239-1.98-8.159-2.58-11.939-1.38-.479.12-1.02-.12-1.14-.6-.12-.48.12-1.021.6-1.141C9.6 9.9 15 10.561 18.72 12.84c.361.181.54.78.241 1.2zm.12-3.36C15.24 8.4 8.82 8.16 5.16 9.301c-.6.179-1.2-.181-1.38-.721-.18-.601.18-1.2.72-1.381 4.26-1.26 11.28-1.02 15.721 1.621.539.3.719 1.02.419 1.56-.299.421-1.02.599-1.559.3z"/>
    <text x="26" y="15" class="status">{status_label}</text>
  </g>

  <rect x="152" y="122" width="260" height="4" rx="2" fill="#404040" />
  <rect x="152" y="122" width="{int(260 * (progress_percent / 100))}" height="4" rx="2" fill="#1db954" />
  
  <text x="152" y="143" class="time">{current_time}</text>
  <text x="412" y="143" text-anchor="end" class="time">-{format_time(duration_ms - progress_ms)}</text>
</svg>"""

with open("spotify.svg", "w", encoding="utf-8") as f:
    f.write(svg_content)
