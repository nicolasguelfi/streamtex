# Read URL from a file
url_file = os.path.join("static", "videos", "youtube_urls.txt")
with open(url_file) as f:
    youtube_url = f.readline().strip()
stx.st_video(youtube_url)
