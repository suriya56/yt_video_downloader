"""
Enhanced YouTube Video Downloader with proper format conversion via FFmpeg
"""

import yt_dlp
import os
import sys
import argparse
from typing import List, Dict, Optional

class Colors:
    """ANSI color codes for terminal output"""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_success(message: str) -> None:
    print(f"{Colors.OKGREEN}{message}{Colors.ENDC}")

def print_error(message: str) -> None:
    print(f"{Colors.FAIL}{message}{Colors.ENDC}")

def print_info(message: str) -> None:
    print(f"{Colors.OKBLUE}{message}{Colors.ENDC}")

def print_warning(message: str) -> None:
    print(f"{Colors.WARNING}{message}{Colors.ENDC}")

def print_banner() -> None:
    print(f"""
{Colors.HEADER}{Colors.BOLD}
╔══════════════════════════════════════════════════╗
║           YouTube Video Downloader               ║
║           (With Format Conversion)               ║
╚══════════════════════════════════════════════════╝
{Colors.ENDC}
""")

def progress_hook(d: Dict) -> None:
    if d['status'] == 'downloading':
        percent = d.get('_percent_str', 'N/A')
        speed = d.get('_speed_str', 'N/A')
        eta = d.get('_eta_str', 'N/A')
        print(f"\rProgress: {percent} | Speed: {speed} | ETA: {eta}", end='', flush=True)
    elif d['status'] == 'finished':
        print("\rDownload complete! Finalizing file...", end='', flush=True)

def check_ffmpeg() -> bool:
    """Check if FFmpeg is available in the system PATH"""
    try:
        yt_dlp.postprocessor.FFmpegPostProcessor().check_version()
        return True
    except Exception:
        return False

def get_available_formats(url: str) -> List[Dict]:
    """Get available formats for a video"""
    with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
        info = ydl.extract_info(url, download=False)
        return info.get('formats', [])

def download_video(
    url: str,
    output_path: str = './downloads',
    quality: str = 'best',
    format: str = 'mp4',
    audio_only: bool = False
) -> bool:
    """
    Download a YouTube video with specified quality and format
    
    Args:
        url: YouTube video URL
        output_path: Directory to save downloads
        quality: Video quality (best, worst, or specific resolution)
        format: Output format (mp4, webm, etc.)
        audio_only: Whether to download audio only
    
    Returns:
        bool: True if download succeeded, False otherwise
    """
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    
    has_ffmpeg = check_ffmpeg()
    if not has_ffmpeg:
        print_warning("\nWarning: FFmpeg not found. Some format conversions may not work properly.")
        print_warning("For best results, install FFmpeg and add it to your PATH.")
    
    ydl_opts = {
        'outtmpl': f'{output_path}/%(title)s.%(ext)s',
        'progress_hooks': [progress_hook],
        'quiet': True,
    }

    if audio_only:
        # Audio-only download options
        ydl_opts['format'] = 'bestaudio/best'
        if has_ffmpeg:
            ydl_opts['postprocessors'] = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': format if format in ['mp3', 'aac', 'flac', 'm4a', 'opus', 'vorbis', 'wav'] else 'mp3',
            }]
        else:
            print_warning("Downloading in original audio format (no FFmpeg for conversion)")
    else:
        # Video download options
        if format == 'mp4':
            # Native MP4 format (no conversion needed)
            format_filter = f'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best'
        else:
            # For other formats, we'll need to convert
            format_filter = 'bestvideo+bestaudio/best'
        
        if quality == 'best':
            ydl_opts['format'] = format_filter
        elif quality == 'worst':
            ydl_opts['format'] = 'worst'
        else:
            ydl_opts['format'] = f'{format_filter}[height<={quality[:-1]}]'
        
        # Add postprocessor for format conversion if needed
        if format != 'mp4' and has_ffmpeg:
            ydl_opts['postprocessors'] = [{
                'key': 'FFmpegVideoConvertor',
                'preferedformat': format,
            }]
        elif format != 'mp4' and not has_ffmpeg:
            print_warning(f"Cannot convert to {format} - FFmpeg not found. Downloading in original format.")
    
    try:
        print_info(f"\nDownloading: {url}")
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            if not info:
                print_error("Error: Could not extract video information")
                return False
            
            print_info(f"\nTitle: {info.get('title', 'Unknown')}")
            print_info(f"Duration: {info.get('duration', 'N/A')} seconds")
            print_info(f"Quality: {quality}")
            print_info(f"Requested Format: {format.upper()}")
            
            if 'entries' in info:
                print_info(f"Videos in playlist: {len(info['entries'])}")
            
            print("\nStarting download...")
            ydl.download([url])
            
            print_success("\nDownload complete!")
            print_info(f"Saved to: {output_path}")
            return True

    except yt_dlp.utils.DownloadError as e:
        print_error(f"\nDownload Error: {str(e)}")
    except yt_dlp.utils.ExtractorError as e:
        print_error(f"\nExtractor Error: {str(e)}")
    except Exception as e:
        print_error(f"\nUnexpected Error: {type(e).__name__}: {str(e)}")
    
    return False

def main() -> None:
    print_banner()
    
    parser = argparse.ArgumentParser(description='YouTube Video Downloader with Format Conversion')
    parser.add_argument('url', nargs='?', help='YouTube video or playlist URL')
    parser.add_argument('-o', '--output', default='./downloads',
                      help='Output directory (default: ./downloads)')
    parser.add_argument('-q', '--quality', default='best',
                      choices=['best', 'worst', '144p', '240p', '360p', '480p', 
                              '720p', '1080p', '1440p', '2160p'],
                      help='Video quality (default: best)')
    parser.add_argument('-f', '--format', default='mp4',
                      choices=['mp4', 'webm', 'flv', 'ogg', 'mkv', 'avi',
                              'mp3', 'aac', 'flac', 'm4a', 'wav'],
                      help='Output format (default: mp4)')
    parser.add_argument('-a', '--audio-only', action='store_true',
                      help='Download audio only')
    parser.add_argument('-l', '--list-formats', action='store_true',
                      help='List available formats for the video')
    
    args = parser.parse_args()
    
    if not args.url:
        args.url = input("Enter YouTube URL: ").strip()
        if not args.url:
            print_error("Error: No URL provided")
            sys.exit(1)
    
    if args.list_formats:
        try:
            formats = get_available_formats(args.url)
            print("\nAvailable Formats:")
            for f in sorted(formats, key=lambda x: x.get('height', 0)):
                ext = f.get('ext', '?')
                res = f.get('resolution', '?')
                note = f.get('format_note', '')
                print(f"ID: {f['format_id']} | {ext.upper()} | {res} | {note}")
            sys.exit(0)
        except Exception as e:
            print_error(f"Error listing formats: {str(e)}")
            sys.exit(1)
    
    success = download_video(
        args.url,
        args.output,
        args.quality,
        args.format,
        args.audio_only
    )
    
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()