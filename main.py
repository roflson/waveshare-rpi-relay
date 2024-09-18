import os
import sys
import time

#These mappings come from the waveshare board itself, it has the pin/relay mappings next to the jumpers on the board.
pin_mapping = {
    'tv_blind': {
        'down': 16,
        'up': 13
    },
    'other_blind': {
        'up': 6,
        'down': 5
    }
}

def check_channel(channel_id):
    path = f"/sys/class/gpio/gpio{channel_id}"
    return os.path.isdir(path)

def enable_relay(channel_id):
    channel_root = f"/sys/class/gpio/gpio{channel_id}"
    with open(channel_root+"/value", 'w') as f:
        f.write('1')

def disable_relay(channel_id):
    channel_root = f"/sys/class/gpio/gpio{channel_id}"
    with open(channel_root+"/value", 'w') as f:
        f.write('0')

#Relay gets briefly enabled 
def enable_channel(channel_id):
    root = f"/sys/class/gpio"
    channel_root = f"{root}/gpio{channel_id}"
    with open(root+"/export", 'w') as f:
        f.write(str(channel_id))
    time.sleep(0.5)
    with open(channel_root+"/active_low", 'w') as f:
        f.write('1')
    with open(channel_root+"/direction", 'w') as f:
        f.write('out')
    disable_relay(channel_id)

def opposite_direction(direction):
    if direction == 'up':
        return 'down'
    else:
        return 'up'

class Command:
    def __init__(self, direction, enable_duration):
        self.direction = direction
        self.enable_duration = enable_duration

    def run(self, blind):
        channel = blind[self.direction]
        opposite_channel = blind[opposite_direction(self.direction)]
        enable_relay(channel)
        time.sleep(self.enable_duration)
        disable_relay(channel)
        enable_relay(opposite_channel)
        time.sleep(0.5)
        disable_relay(opposite_channel)
        
        
class Scenario:
    def __init__(self, blind, commands):
        self.blind = blind
        self.commands = commands

    def get_commands(self):
        return self.commands

    def run(self):
        for command in self.commands:
            command.run(self.blind)
            time.sleep(1)

commands = {
    'full_raise': Command('up', 120),
    'full_lower': Command('down', 120),
    'lower_75': Command('down', 60)
}
            
scenarios = {
    'raise_other_blind': Scenario(pin_mapping['other_blind'], [commands['full_raise']]),
    'other_blind_daytime': Scenario(pin_mapping['other_blind'], [commands['full_raise'], commands['lower_75']])
}
            
if __name__ == "__main__":
    for blind in pin_mapping.values():
        for direction in blind.values():
            if not check_channel(direction):
                enable_channel(direction)

    scenario_name = sys.argv[1]
    if scenario_name not in scenarios:
        raise ValueError('Invalid scenario')
    scenarios[scenario_name].run()
