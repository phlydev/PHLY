import yt_dlp as youtube_dl
import os


def download_video(url, output_path):
    ydl_opts = {
        'format': 'best',
        'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
        'quiet': True,  # Unterdrückt Fortschrittsmeldungen
        'no_warnings': True,  # Unterdrückt Warnungen
    }

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])


if __name__ == "__main__":
    video_url = input("Enter the URL of the video:  ")
    output_directory = "C:\\YOURDIRECTORY"

    # Überprüfen, ob das Verzeichnis existiert, und erstellen, falls nicht
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    download_video(video_url, output_directory)

    # Verhindert, dass sich das Skript sofort schließt
    input("Download completed. Press Enter to finish.")
