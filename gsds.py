#! python3
# gsds.py - Timer and organizer for code learning.

import sys, time, json, shlex, threading, playsound3
from datetime import datetime
from pathlib import Path

# Global variables:
if getattr(sys, 'frozen', False):
    # From executable
    BASE_DIR = Path(sys.executable).parent
else:
    # From .py file
    BASE_DIR = Path(__file__).parent
SETTINGS_FILENAME = 'settings.json'
running_countdowns = []

def main():
    print(' Gold Digging Shovel '.center(50,'='))
    main_repl()

class Countdown:
    def __init__(self, seconds: int):
        self.running = False
        self.paused = False
        self.time_left = seconds
        self.time_paused = 0

    def count(self):
        # The actual timer function. Meant to be ran in a separate thread.
        self.running = True
        while self.running:
            while self.paused:
                time.sleep(1)
                self.time_paused += 1
            time.sleep(1)
            self.time_left -= 1
            if self.time_left <= 0:
                self.running = False
                print('Time out! Press Enter.')
                play_alarm()
    
    def start(self):
        # Use this to start the countdown in a separate thread.
        countdown_obj = threading.Thread(target=self.count)
        countdown_obj.start()

    def pause(self):
        self.paused = True

    def resume(self):
        self.paused = False

    def print_time(self):
        print(f'{timestamp()} Time left: {self.time_left}s')

    def cancel(self) -> int:
        # Resets the countdown to initial values. Use after start().
        global running_countdowns
        self.running = False
        self.paused = False
        running_countdowns.remove(self)
        return self.time_left

        
def main_repl():
    settings = load_settings()
    while True:
        print_actions('main', ['start','break','quit'])
        # Get input command:
        user_input = repl_input()
        # Start work timer:
        if user_input[0] in ('s', 'start'):
            if len(user_input) > 1:
                if not user_input[1].isnumeric():
                    print('Number of minutes should be a digit.')
                    continue
                else:
                    work_repl(int(user_input[1]))
                    continue
            else:
                work_repl(settings["default_max_session"])
                continue
        # Start break timer:
        elif user_input[0] in ('b', 'break'):
            if len(user_input) > 1:
                if not user_input[1].isnumeric():
                    print('Number of minutes should be a digit.')
                    continue
                else:
                    break_repl(int(user_input[1]))
                    continue
            else:
                break_repl(settings["default_break"])
                continue
        # Quit:
        elif user_input[0] in ('q', 'quit'):
            quit_shovel()

def work_repl(minutes):
    print('To be developed.')
    pass
"""
    global timer_flags, cd_time_left
    starttime = datetime.now()
    print(f'{timestamp()} Dig yourself out of a hole! {minutes} minutes.')
    print('''
p/pause   - pause session
t/time    - time left
s/save    - end session and save progress
c/cancel  - cancel session
    ''')
    # TODO: Start countdown
    while True:
        # Get input command:
        action = shlex.split(input('> '))
        action[0] = action[0].lower()
        # TODO: Pause timer:
        if action[0] in ('p', 'pause'):
            pass
        # TODO: Time left:
        elif action[0] in ('t', 'time'):
            pass
        # TODO: Save session:
        elif action[0] in ('s', 'save'):
            print('Logging sessions has yet to be implemented.')
            timer_flags['running'] = False
        # TODO: Stop timer:
        elif action[0] in ('c', 'cancel'):
            timer_flags['running'] = False
    
    # TODO: Play sound
""" # This is all huinya for now.

def break_repl(minutes:int) -> int:    # Returns elapsed time in seconds.
    global running_countdowns
    starttime = datetime.now()
    seconds = minutes * 60
    print(f'{timestamp()} Now take a break! {minutes} minutes.')
    print_actions('break', ['pause','time','cancel','quit'])
    cd = Countdown(seconds)
    running_countdowns.append(cd)
    cd.start()

    while cd.running:
        # Get input command:
        user_input = repl_input()
        if not user_input:
            continue
        if not cd.running:
            break
        # Pause timer:
        if user_input[0] in ('p', 'pause'):
            cd.pause()
            pause_repl('break', cd)
            if not cd.running:    # If canceled in the pause menu
                elapsed = seconds - cd.time_left
                return elapsed
        # Time left:
        elif user_input[0] in ('t', 'time'):
            cd.print_time()
        # Stop timer:
        elif user_input[0] in ('c', 'cancel'):
            cd.cancel()
            elapsed = seconds - cd.time_left
            return elapsed
        elif user_input[0] in ('q', 'quit'):
            quit_shovel()

    # Loop should end naturally only if the countdown reaches zero.
    assert cd.running == False
    assert cd.time_left <= 0
    return cd.time_left

def pause_repl(cd_type: str, cd): # Types: 'work', 'break'
    assert cd_type in ('work', 'break')
    print(f'{timestamp()} Paused. Time left: {cd.time_left}s')
    print_actions('break', ['resume','cancel','quit'])
    
    while cd.paused:
        user_input = repl_input()
        if not user_input:
            continue
        if user_input[0] in ('r', 'resume'):  # Unpause
            cd.resume()
            if cd_type == 'work':
                print(f'{timestamp()} Keep working!')
            elif cd_type == 'break':
                print(f'{timestamp()} Keep breaking!')
            return
        elif user_input[0] in ('s', 'save') and cd_type == 'work':
            # TODO: Implement saving
            return
        elif user_input[0] in ('c', 'cancel'):
            cd.cancel()
            return
        elif user_input[0] in ('q', 'quit'):
            quit_shovel()

def repl_input():
    # Turns input into a list of arguments.
    action = shlex.split(input('> '))
    action = [x.lower() for x in action]
    return action

def timestamp():
    date_time = '[' + datetime.now().strftime('%d.%m.%Y %H:%M') + ']'
    return date_time
    
def load_settings():
    global BASE_DIR, SETTINGS_FILENAME
    with open(BASE_DIR / SETTINGS_FILENAME) as json_f:
        json_text = json_f.read()
        settings = json.loads(json_text)
        return settings

def print_actions(name, commands):
    settings = load_settings()
    if 'start' in commands:
        print(f's/start <minutes> - start shoveling. Default: {settings["default_max_session"]} minutes')
    if 'break' in commands:
        print(f'b/break <minutes> - take a break. Default: {settings["default_break"]} minutes')
    if 'pause' in commands:
        print(f'p/pause           - pause {name} session')
    if 'resume' in commands:
        print(f'r/resume          - continue {name} session')
    if 'time' in commands:
        print(f't/time            - time left')
    if 'save' in commands:
        print(f's/save            - end session and save progress')
    if 'cancel' in commands:
        print(f'c/cancel          - stop {name} session')
    if 'quit' in commands:
        print(f'q/quit            - terminate Gold Digging Shovel')

def play_alarm():
    global BASE_DIR
    settings = load_settings()
    sound_path = BASE_DIR/settings["alarm_sound"]
    playsound3.playsound(sound_path)


def quit_shovel():
    global running_countdowns
    print('See ya!')
    for cd in running_countdowns:
        cd.paused = False
        cd.running = False
    sys.exit(0)

if __name__ == '__main__':
    main()