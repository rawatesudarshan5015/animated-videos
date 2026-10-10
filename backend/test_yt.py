import yt_dlp
import traceback

def test_download():
    MAX_VIDEO_DURATION = 300
    
    def duration_filter(info):
        duration = info.get('duration')
        if duration is None:
            duration = 0
        if duration > MAX_VIDEO_DURATION:
            return 'Video is too long'
        return None

    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'outtmpl': 'test_download.mp4',
        'noplaylist': True,
        'quiet': False,
        'match_filter': duration_filter
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download(['https://www.youtube.com/watch?v=jNQXAC9IVRw'])
    except Exception as e:
        print("ERROR:", str(e))
        traceback.print_exc()

if __name__ == '__main__':
    test_download()
