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
timer_flags = {"running": False, "paused": False}
cd_time_left = 0

def main():
    print(' Gold Digging Shovel '.center(50,'='))
    start_repl()

def start_repl():
    settings = load_settings()
    while True:
        print(f'''
s/start <minutes> - start shoveling. Default: {settings["default_max_session"]}
b/break <minutes> - start break. Default: {settings["default_break"]}   
q/quit            - terminate Gold Digging Shovel 
          ''')  # TODO: implement print_actions()
        # Get input command:
        user_input = repl_input()
        # Start work timer:
        if user_input[0] in ('s', 'start'):
            if len(user_input) > 1:
                if not user_input[1].isnumeric():
                    print('Number of minutes should be a digit.')
                    continue
                else:
                    work_timer(int(user_input[1]))
                    continue
            else:
                work_timer(settings["default_max_session"])
                continue
        # Start break timer:
        elif user_input[0] in ('b', 'break'):
            if len(user_input) > 1:
                if not user_input[1].isnumeric():
                    print('Number of minutes should be a digit.')
                    continue
                else:
                    break_timer(int(user_input[1]))
                    continue
            else:
                break_timer(settings["default_break"])
                continue
        # Quit:
        elif user_input[0] in ('q', 'quit'):
            quit_shovel()

def work_timer(minutes):
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

def break_timer(minutes):    # Returns elapsed time.
    global timer_flags, cd_time_left
    seconds = minutes * 60
    starttime = datetime.now()
    print(f'{timestamp()} Now take a break! {minutes} minutes.')
    print('''
p/pause   - pause break
t/time    - time left
c/cancel  - stop break
q/quit    - terminate program.
    ''')  # TODO: implement print_actions()

    # Starting countdown thread:
    countdown_obj = threading.Thread(target=countdown, args=[seconds])
    timer_flags['running'] = True
    countdown_obj.start()

    while timer_flags['running']:
        # Get input command:
        user_input = repl_input()
        if not user_input:
            continue
        if not timer_flags['running']:
            break
        # Pause timer:
        if user_input[0] in ('p', 'pause'):
            timer_flags['paused'] = True
            time_left = cd_pause('break')
            if time_left is not None:    # If canceled in the pause menu
                elapsed = seconds - time_left
                return elapsed
        # Time left:
        elif user_input[0] in ('t', 'time'):
            print(f'{timestamp()} Time left: {cd_time_left}s')
        # Stop timer:
        elif user_input[0] in ('c', 'cancel'):
            time_left = cd_cancel_reset()
            elapsed = seconds - time_left
            return elapsed
        elif user_input[0] in ('q', 'quit'):
            quit_shovel()

    # Loop should end naturally only if the countdown reaches zero.
    assert cd_cancel_reset() == 0
    return seconds
        
def countdown(seconds):
    # The actual timer function. Meant to be ran in a separate thread.
    # Use cd_cancel_reset() to reset values to default after usage.
    global timer_flags, cd_time_left, BASE_DIR
    settings = load_settings()
    cd_time_left = seconds
    paused = 0
    while timer_flags['running']:
        while timer_flags['paused']:
            time.sleep(1)
            paused += 1
        time.sleep(1)
        if cd_time_left > 0:
            cd_time_left -= 1
        else:
            timer_flags['running'] = False
            print('Time out! Press Enter.')
            playsound3.playsound(BASE_DIR/settings["alarm_sound"])

def cd_cancel_reset():
    # Resets the countdown to initial values. Use after countodwn().
    global timer_flags, cd_time_left
    timer_flags['paused'] = False
    timer_flags['running'] = False
    time_left = cd_time_left
    return time_left

def cd_pause(repl_type): # Types: 'work', 'break'
    print(f'''
{timestamp()} Paused. Time left: {cd_time_left}s
r/resume   - continue break
c/cancel   - stop break
q/quit     - terminate program.
    ''') # TODO: implement print_actions()
    while timer_flags['paused']:
        user_input = repl_input()
        if not user_input:
            continue
        if user_input[0] in ('r', 'resume'):  # Unpause
            timer_flags['paused'] = False
            print(f'{timestamp()} Keep breaking!')
            return None
        elif user_input[0] in ('s', 'save') and repl_type == 'work':
            # TODO: Implement saving
            pass
        elif user_input[0] in ('c', 'cancel'):  # Cancel
            time_left = cd_cancel_reset()
            return time_left
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

def print_actions(actions_list):
    # TODO
    pass

def quit_shovel():
    print('See ya!')
    cd_cancel_reset()
    sys.exit(0)

if __name__ == '__main__':
    main()