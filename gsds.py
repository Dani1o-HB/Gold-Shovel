#! python3
# TODO: Log work sessions to a database.

import sys, time, json, shlex, threading, playsound3, sqlite3
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
DB_FILENAME = 'gsds.db'
running_countdowns = []

def main():
    print(' Gold Digging Shovel '.center(50,'='))
    init_db()
    main_repl(default_action='start')

class Countdown:
    def __init__(self, seconds: int, cd_type: 'str'):
        assert cd_type in ('work', 'break')
        self.running = False
        self.paused = False
        self.time_left = seconds
        self.time_paused = 0
        self.cd_type = cd_type

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
                if self.cd_type == 'work':
                    print('Good work! Watcha been doing, champ?')
                else:
                    print('Time\'s up! Press Enter.')
                play_alarm(self.cd_type)
    
    def start(self):
        # Use this to start the countdown in a separate thread.
        countdown_obj = threading.Thread(target=self.count)
        countdown_obj.start()

    def pause(self):
        self.paused = True

    def resume(self):
        self.paused = False

    def print_time(self):
        return t_convert(self.time_left)

    def cancel(self) -> int:
        # Resets the countdown to initial values. Use after start().
        global running_countdowns
        self.running = False
        self.paused = False
        running_countdowns.remove(self)
        return self.time_left

        
def main_repl(default_action = None):
    settings = load_settings()
    actions_list = ['start','break','quit']
    while True:
        print_actions('main', actions_list, default_action=default_action)
        # Get input command:
        user_input = repl_input()
        if not user_input:
            if default_action:
                user_input = [default_action]
            else:
                continue
        # Start work timer:
        if user_input[0] in ('s', 'start'):
            if len(user_input) > 1:
                if not user_input[1].isnumeric():
                    print('Number of minutes should be a digit.')
                    continue
                else:
                    running_repl('work', int(user_input[1]))
                    continue
            else:
                running_repl('work', settings["default_max_session"])
                continue
        # Start break timer:
        elif user_input[0] in ('b', 'break'):
            if len(user_input) > 1:
                if not user_input[1].isnumeric():
                    print('Number of minutes should be a digit.')
                    continue
                else:
                    running_repl('break', int(user_input[1]))
                    continue
            else:
                running_repl('break', settings["default_break"])
                continue
        # Quit:
        elif user_input[0] in ('q', 'quit'):
            quit_shovel()

def running_repl(cd_type: str, minutes:int) -> int:    # Returns elapsed time in seconds.
    global running_countdowns
    default_action = 'pause'
    start_time = time.time()
    assert cd_type in ('work', 'break')
    seconds = minutes * 60

    if cd_type == 'work':
        print(f'{timestamp()} Dig yourself out of the shit! {minutes} minutes.')
    elif cd_type == 'break':
        print(f'{timestamp()} Now take a break! {minutes} minutes.')
    actions = ['pause','time','cancel','quit']
    if cd_type == 'work':
        actions.insert(2, 'save')
    print_actions(cd_type, actions, default_action=default_action)
    cd = Countdown(seconds, cd_type)
    running_countdowns.append(cd)
    cd.start()

    while cd.running:
        # Get input command:
        user_input = input('> ')
        if not cd.running: # Countdown ended.
            break
        if not user_input:
            if default_action:
                user_input = [default_action]
            else:
                continue
        else:
            user_input = repl_input(user_input)
        # Pause timer:
        if user_input[0] in ('p', 'pause'):
            cd.pause()
            user_input = pause_repl(cd_type, cd)
            if user_input[0] in ('r', 'resume'):
                continue
        # Time left:
        if user_input[0] in ('t', 'time'):
            print(f'{timestamp()} Time left: {cd.print_time()}')
        # End session and save progress:
        elif cd_type == 'work' and user_input[0] in ('s', 'save'):
            cd.cancel()
            elapsed = seconds - cd.time_left
            comment = input('Going so soon? Anyway, watcha been doing?\n')
            if not comment:
                comment = f'{t_convert(elapsed)} work session.'
            save_session(int(start_time), elapsed, int(time.time()), comment)
            return elapsed
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
    elapsed = seconds
    # Logging progress.
    if cd_type == 'work':
        comment = user_input[:200].strip()
        if not comment:
            comment = f'{t_convert(elapsed)} work session.'
        save_session(int(start_time), elapsed, int(time.time()), comment)
    return elapsed

def pause_repl(cd_type: str, cd): # Types: 'work', 'break'
    assert cd_type in ('work', 'break')
    default_action = 'resume'
    actions = ['resume','cancel','quit']
    if cd_type == 'work':
        actions.insert(1, 'save')
    print(f'{timestamp()} Paused. Time left: {cd.print_time()}')
    print_actions(cd_type, actions, default_action=default_action)

    while cd.paused:
        user_input = repl_input()
        if not user_input:
            if default_action:
                user_input = [default_action]
            else:
                continue
        if user_input[0] in ('r', 'resume'):  # Unpause
            cd.resume()
            if cd_type == 'work':
                print(f'{timestamp()} Keep working!')
            elif cd_type == 'break':
                print(f'{timestamp()} Keep breaking!')
            return user_input
        elif user_input[0] in ('s', 'save') and cd_type == 'work':
            return user_input
        elif user_input[0] in ('c', 'cancel', 'q', 'quit'):
            return user_input


def repl_input(user_input=None):
    # Turns input into a list of arguments.
    if user_input == None:
        user_input = input('> ')
    action = shlex.split(user_input)
    action = [x.lower() for x in action]
    return action

def timestamp():
    date_time = '[' + datetime.now().strftime('%d.%m.%Y %H:%M') + ']'
    return date_time

def t_convert(seconds: int) -> str:
    # Formats seconds into hours, minutes and seconds string.
    minutes = seconds // 60
    seconds -= minutes * 60
    hours = minutes // 60
    minutes -= hours * 60
    output = ''
    if hours:
        output += str(hours)+'h '
    if minutes:
        output += str(minutes)+'m '
    if seconds:
        output += str(seconds)+'s'
    return output
    
def load_settings():
    global BASE_DIR, SETTINGS_FILENAME
    with open(BASE_DIR / SETTINGS_FILENAME) as json_f:
        json_text = json_f.read()
        settings = json.loads(json_text)
        return settings

def print_actions(cd_type, actions, default_action = None):
    settings = load_settings()
    actions_dict = {
        'start':  f's/start <minutes> - start shoveling. Default: {settings["default_max_session"]} minutes',
        'break':  f'b/break <minutes> - take a break. Default: {settings["default_break"]} minutes',
        'pause':  f'p/pause           - pause {cd_type} session',
        'resume': f'r/resume          - continue {cd_type} session',
        'time':   f't/time            - time left',
        'save':   f's/save            - end session and save progress',
        'cancel': f'c/cancel          - stop {cd_type} session',
        'quit':   f'q/quit            - terminate Gold Digging Shovel'
        }
    for action in actions:
        if action == default_action: 
            print('>', end='')
        else:
            print(' ', end='')
        print(actions_dict[action])

def play_alarm(cd_type):
    assert cd_type in ('work', 'break')
    global BASE_DIR
    settings = load_settings()
    sound_path = BASE_DIR/settings[f"alarm_sound_{cd_type}"]
    playsound3.playsound(sound_path)

def init_db():
    global BASE_DIR, DB_FILENAME
    with sqlite3.connect(BASE_DIR/DB_FILENAME) as conn:
        conn.execute("CREATE TABLE IF NOT EXISTS sessions (id INTEGER PRIMARY KEY AUTOINCREMENT, "\
            "start_time INTEGER, duration_sec INTEGER, end_time INTEGER, comment TEXT) STRICT")

def save_session(start_time: int, duration_sec: int, end_time: int, comment: str):
    global BASE_DIR, DB_FILENAME
    with sqlite3.connect(BASE_DIR/DB_FILENAME) as conn:
        conn.execute("INSERT INTO sessions (start_time, duration_sec, end_time, comment) VALUES (?,?,?,?)",
                     (start_time, duration_sec, end_time, comment))
    
def ask_comment():
    print('Good work! Watcha been doing, champ?')

def quit_shovel():
    global running_countdowns
    print('See ya!')
    for cd in running_countdowns:
        cd.paused = False
        cd.running = False
    sys.exit(0)

if __name__ == '__main__':
    main()