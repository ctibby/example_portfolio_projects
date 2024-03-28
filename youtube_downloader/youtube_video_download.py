from pytube import YouTube
from sys import argv

# Could use to enter youtube path in termial after file "python3 youtube_video_dowloader.py "filepath""
# link = argv[1]

ytlinks = open('youtube_links.txt', 'r')

for i in ytlinks.readlines():
    link = i
    yt = YouTube(link)

    print(link)
    print("Title: ", yt.title)
    print("Views: ", yt.views)

    yd = yt.streams.get_highest_resolution()

    yd.download()