"""
Spam Bot using PyAutoGUI  --  Automated Message / Reminder Bot
----------------------------------------------------------------
Types a list of messages into whichever window has focus and presses
Enter after each one, repeating at a fixed interval.

Safety features (added on top of the basic GeeksforGeeks version):
  * Finite run: a maximum number of rounds instead of `while True`
  * Countdown so the user can click into the target window
  * PyAutoGUI FAILSAFE: move the mouse to the top-left corner to abort
  * Ctrl+C handling and a timestamped log file
  * Minimum delay between messages to avoid flooding

Usage examples:
  python spam_bot.py
  python spam_bot.py --rounds 3 --delay 10
  python spam_bot.py --messages "Drink water!" "Take a break!" --rounds 5
  python spam_bot.py --file messages.txt --rounds 2 --delay 15
"""

import argparse
import datetime
import sys
import time

import pyautogui

pyautogui.FAILSAFE = True   # move mouse to a screen corner to abort
pyautogui.PAUSE = 0.05      # small pause after every PyAutoGUI call

DEFAULT_MESSAGES = [
    "Reminder: Drink water!",
    "Reminder: Take medicine!",
    "Reminder: Take the dog for a walk!",
]
MIN_DELAY = 2      # seconds - lower values are rejected
MAX_ROUNDS = 100   # hard upper limit on repetitions
LOG_FILE = "spam_bot_log.txt"


def log(text: str) -> None:
    """Print a timestamped line and append it to the log file."""
    line = f"[{datetime.datetime.now():%Y-%m-%d %H:%M:%S}] {text}"
    print(line)
    with open(LOG_FILE, "a", encoding="utf-8") as fh:
        fh.write(line + "\n")


def load_messages(args) -> list:
    if args.file:
        with open(args.file, encoding="utf-8") as fh:
            msgs = [ln.strip() for ln in fh if ln.strip()]
        if msgs:
            return msgs
        sys.exit("The message file is empty.")
    return args.messages or DEFAULT_MESSAGES


def countdown(seconds: int) -> None:
    for s in range(seconds, 0, -1):
        print(f"Starting in {s}... click into the target window now", end="\r")
        time.sleep(1)
    print(" " * 60, end="\r")


def send(message: str, typing_interval: float) -> None:
    pyautogui.typewrite(message, interval=typing_interval)
    pyautogui.press("enter")


def run(messages, rounds, delay, start_wait, typing_interval) -> None:
    countdown(start_wait)
    log(f"Bot started: {len(messages)} message(s), {rounds} round(s), {delay}s delay")
    sent = 0
    try:
        for r in range(1, rounds + 1):
            for msg in messages:
                send(msg, typing_interval)
                sent += 1
                log(f"Round {r}/{rounds} sent #{sent}: {msg}")
                time.sleep(delay)
    except pyautogui.FailSafeException:
        log("FAILSAFE triggered (mouse in corner). Bot stopped.")
    except KeyboardInterrupt:
        log("Stopped by user (Ctrl+C).")
    else:
        log(f"Finished normally. Total messages sent: {sent}")


def main() -> None:
    p = argparse.ArgumentParser(description="Spam Bot using PyAutoGUI")
    p.add_argument("--messages", nargs="+", help="messages to type")
    p.add_argument("--file", help="text file with one message per line")
    p.add_argument("--rounds", type=int, default=2, help="repetitions of the list")
    p.add_argument("--delay", type=float, default=5, help="seconds between messages")
    p.add_argument("--start-wait", type=int, default=5, help="initial countdown (s)")
    p.add_argument("--typing-interval", type=float, default=0.02)
    args = p.parse_args()

    if not 1 <= args.rounds <= MAX_ROUNDS:
        sys.exit(f"--rounds must be between 1 and {MAX_ROUNDS}")
    if args.delay < MIN_DELAY:
        sys.exit(f"--delay must be at least {MIN_DELAY} seconds")

    run(load_messages(args), args.rounds, args.delay,
        args.start_wait, args.typing_interval)


if __name__ == "__main__":
    main()
