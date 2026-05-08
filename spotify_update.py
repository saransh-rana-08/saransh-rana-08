import os
import re
import requests
import base64

CLIENT_ID = os.environ["SPOTIFY_CLIENT_ID"]
CLIENT_SECRET = os.environ["SPOTIFY_CLIENT_SECRET"]
REFRESH_TOKEN = os.environ["SPOTIFY_REFRESH_TOKEN"]


def get_access_token():
    """Exchange the refresh token for a short-lived access token."""
    auth = base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode()
    response = requests.post(
        "https://accounts.spotify.com/api/token",
        data={"grant_type": "refresh_token", "refresh_token": REFRESH_TOKEN},
        headers={"Authorization": f"Basic {auth}"},
    )
    response.raise_for_status()
    return response.json()["access_token"]


def get_now_playing(token):
    """Fetch the currently playing track, if any."""
    response = requests.get(
        "https://api.spotify.com/v1/me/player/currently-playing",
        headers={"Authorization": f"Bearer {token}"},
    )
    if response.status_code == 200:
        data = response.json()
        item = data.get("item")
        if item:
            return {
                "name": item["name"],
                "artist": ", ".join(a["name"] for a in item["artists"]),
                "url": item["external_urls"]["spotify"],
                "album_art": item["album"]["images"][0]["url"] if item["album"]["images"] else None,
                "is_playing": data.get("is_playing", False),
            }
    return None


def get_recently_played(token):
    """Fallback: fetch the most recently played track."""
    response = requests.get(
        "https://api.spotify.com/v1/me/player/recently-played?limit=1",
        headers={"Authorization": f"Bearer {token}"},
    )
    if response.status_code == 200:
        items = response.json().get("items", [])
        if items:
            track = items[0]["track"]
            return {
                "name": track["name"],
                "artist": ", ".join(a["name"] for a in track["artists"]),
                "url": track["external_urls"]["spotify"],
                "album_art": track["album"]["images"][0]["url"] if track["album"]["images"] else None,
                "is_playing": False,
            }
    return None


def update_readme(content):
    """Replace the content between the Spotify markers in README.md."""
    with open("README.md", "r", encoding="utf-8") as f:
        readme = f.read()

    pattern = r"<!-- SPOTIFY:START -->.*?<!-- SPOTIFY:END -->"
    replacement = f"<!-- SPOTIFY:START -->\n{content}\n<!-- SPOTIFY:END -->"
    updated = re.sub(pattern, replacement, readme, flags=re.DOTALL)

    with open("README.md", "w", encoding="utf-8") as f:
        f.write(updated)


def main():
    token = get_access_token()

    track = get_now_playing(token)
    if not track:
        track = get_recently_played(token)

    if track:
        emoji = "🎵" if track["is_playing"] else "🎧"
        status = "**Now Playing**" if track["is_playing"] else "**Last Played**"
        content = (
            f"{emoji} {status}: "
            f"[{track['name']}]({track['url']}) "
            f"*by {track['artist']}*"
        )
    else:
        content = "🔇 *Not listening to anything right now.*"

    update_readme(content)
    print(f"README updated: {content}")


if __name__ == "__main__":
    main()
