import yt_dlp
import os
import sys

def list_formats(url):
    """List all available formats for a YouTube video"""
    ydl_opts = {
        'listformats': True,
        'quiet': False,
    }
    
    try:
        print(f"Listing available formats for: {url}")
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        return True
    except Exception as e:
        print(f"Error listing formats: {str(e)}")
        return False

def download_with_format(url, format_id, output_path='./downloads'):
    """Download a YouTube video with a specific format ID"""
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    
    ydl_opts = {
        'format': format_id,
        'outtmpl': f'{output_path}/%(title)s.%(ext)s',
    }
    
    try:
        print(f"Downloading format {format_id} from: {url}")
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        print("Download complete!")
        return True
    except Exception as e:
        print(f"Download error: {str(e)}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Please provide a YouTube URL")
        url = input("Enter YouTube URL: ").strip()
    else:
        url = sys.argv[1]
    
    # First list available formats
    if list_formats(url):
        format_id = input("\nEnter the format code you want to download (e.g., 22 for 720p if available): ").strip()
        
        if format_id:
            download_with_format(url, format_id)
        else:
            print("No format selected. Exiting.")
    else:
        print("Failed to list formats. Exiting.")