#!/usr/bin/env python3
import sys
import argparse
from colorama import Fore, Style, init

init(autoreset=True)

BANNER = f"""{Fore.CYAN}
  ██╗   ██╗██╗██████╗ ███████╗ ██████╗ ███████╗ ██████╗██████╗ ██╗██████╗ ███████╗
  ██║   ██║██║██╔══██╗██╔════╝██╔═══██╗██╔════╝██╔════╝██╔══██╗██║██╔══██╗██╔════╝
  ██║   ██║██║██║  ██║█████╗  ██║   ██║███████╗██║     ██████╔╝██║██████╔╝█████╗
  ╚██╗ ██╔╝██║██║  ██║██╔══╝  ██║   ██║╚════██║██║     ██╔══██╗██║██╔══██╗██╔══╝
   ╚████╔╝ ██║██████╔╝███████╗╚██████╔╝███████║╚██████╗██║  ██║██║██████╔╝███████╗
    ╚═══╝  ╚═╝╚═════╝ ╚══════╝ ╚═════╝ ╚══════╝ ╚═════╝╚═╝  ╚═╝╚═╝╚═════╝ ╚══════╝
{Style.RESET_ALL}
  {Fore.WHITE}AI-Powered Video Transcription Tool{Style.RESET_ALL}
  {Fore.GREEN}Supports: YouTube • Facebook • TikTok • Twitter/X • Instagram • Reddit • Twitch • +1000 more{Style.RESET_ALL}
"""

TASK_MENU_LABELS = [
    "Summarize the video",
    "Extract key points as bullet list",
    "Generate detailed notes",
    "Extract all action items / to-dos",
    "Translate transcript to another language",
    "Answer a specific question about the video",
    "Generate a blog post from the content",
    "Custom instruction",
]

TASK_INSTRUCTIONS = [
    "Please provide a comprehensive summary of the following transcript.",
    "Extract the most important key points from this transcript as a clean bullet list.",
    "Generate detailed, well-structured notes from this transcript suitable for study or reference.",
    "Extract every action item, task, or to-do mentioned in this transcript. Format as a numbered list.",
    "Translate the following transcript to Spanish (or another language if the user specifies).",
    "Answer questions about the following transcript. Please respond to any question the user has about this content.",
    "Write a well-structured, engaging blog post based on the content of this transcript.",
    None,
]


def check_first_run():
    from config import is_first_run
    if is_first_run():
        print(f"{Fore.YELLOW}")
        print("  ╔══════════════════════════════════════════════════════════╗")
        print("  ║  FIRST RUN CHECKLIST                                     ║")
        print("  ║                                                          ║")
        print("  ║  1. Edit .env and add your ANTHROPIC_API_KEY             ║")
        print("  ║     Get one at: https://console.anthropic.com/           ║")
        print("  ║                                                          ║")
        print("  ║  2. Optionally adjust WHISPER_MODEL in .env              ║")
        print("  ║     tiny/base/small/medium/large (default: base)         ║")
        print("  ╚══════════════════════════════════════════════════════════╝")
        print(Style.RESET_ALL)


def prompt_task() -> str:
    print(f"\n{Fore.CYAN}  [🤖] What would you like Claude to do with this transcript?{Style.RESET_ALL}")
    for i, label in enumerate(TASK_MENU_LABELS, 1):
        print(f"  {Fore.WHITE}{i}. {label}{Style.RESET_ALL}")
    print()

    while True:
        choice = input(f"{Fore.GREEN}> Choose (1-8) or type your own instruction: {Style.RESET_ALL}").strip()

        if choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(TASK_MENU_LABELS):
                if idx == 7:
                    instruction = input(f"{Fore.GREEN}> Enter your custom instruction: {Style.RESET_ALL}").strip()
                    return instruction
                else:
                    return TASK_INSTRUCTIONS[idx]
        elif choice:
            return choice

        print(f"{Fore.YELLOW}  Please enter a number 1-8 or type an instruction.{Style.RESET_ALL}")


def run_pipeline(url: str, task_instruction: str = None, confirm_long: bool = False, skip_scan: bool = False):
    from core.downloader import download_audio
    from core.scanner import scan_file
    from core.transcriber import transcribe
    from core.processor import process_transcript
    from utils import logger

    audio_path = None
    try:
        audio_path = download_audio(url, confirm_long=confirm_long)

        if not skip_scan:
            clean = scan_file(audio_path)
            if not clean:
                sys.exit(1)
        else:
            logger.warning("Virus scan skipped (--no-scan flag).")

        info = transcribe(audio_path, video_title=url.split("/")[-1] or "video")
        audio_path = None  # transcriber handles cleanup

        if task_instruction is None:
            task_instruction = prompt_task()

        process_transcript(info["text"], task_instruction, info["base_name"])

    except RuntimeError as e:
        from utils import logger
        logger.error(str(e))
        sys.exit(1)
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}  Interrupted.{Style.RESET_ALL}")
        sys.exit(0)


def interactive_mode():
    print(BANNER)
    check_first_run()

    from utils.file_manager import cleanup_stale_downloads
    cleanup_stale_downloads()

    while True:
        try:
            url = input(f"{Fore.GREEN}> Enter video URL: {Style.RESET_ALL}").strip()
        except KeyboardInterrupt:
            print(f"\n{Fore.CYAN}  Goodbye!{Style.RESET_ALL}")
            break

        if not url:
            continue

        run_pipeline(url)

        try:
            again = input(f"\n{Fore.GREEN}> Process another video? (y/n): {Style.RESET_ALL}").strip().lower()
        except KeyboardInterrupt:
            print(f"\n{Fore.CYAN}  Goodbye!{Style.RESET_ALL}")
            break

        if again != "y":
            print(f"{Fore.CYAN}  Goodbye!{Style.RESET_ALL}")
            break


def main():
    parser = argparse.ArgumentParser(description="VideoScribe — AI Video Transcription Tool")
    parser.add_argument("--url", help="Video URL to process")
    parser.add_argument("--task", help="Task instruction for Claude (e.g. 'summarize')")
    parser.add_argument("--whisper-model", help="Whisper model to use (tiny/base/small/medium/large)")
    parser.add_argument("--no-delete", action="store_true", help="Keep audio file after transcription")
    parser.add_argument("--no-scan", action="store_true", help="Skip virus scan")
    parser.add_argument("--confirm-long", action="store_true", help="Proceed even if video exceeds max duration")
    args = parser.parse_args()

    if args.whisper_model:
        import config
        config.WHISPER_MODEL = args.whisper_model

    if args.no_delete:
        import config
        config.AUTO_DELETE_AUDIO = False

    if args.url:
        print(BANNER)
        run_pipeline(
            args.url,
            task_instruction=args.task,
            confirm_long=args.confirm_long,
            skip_scan=args.no_scan,
        )
    else:
        interactive_mode()


if __name__ == "__main__":
    main()
