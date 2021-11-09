# Copyright (C) 2021, Sebastián Reguera
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
import random

# Conditions
AT = "A"; PRESENT = "B"; ABSENT = "C"; CARRIED = "D"; SETQ = "E"; RESQ = "F"; ONEQ = "G"; CHANCE = "H"
# Actions
INVEN = "A"; GET = "B"; DROP = "C"; MESSAGE = "D"; SET = "E"; RESET = "F"; LET = "G"; SWAP = "H"
CREATE = "I"; DESTROY = "J"; GOTO = "K"; OK = "L"; DONE = "M"; DONEC = "N"; DESC = "O"; QUIT = "P"; END = "Q" 


messages = {
    1: "The door is shut fast.",
    2: "The door is open.",
    3: "It is already alight.",
    4: "With a grunt you manage to open the door.",
    5: "It is too stiff for you to open.",
    6: "You did it. Well done.",
    7: "You cannot get pass the door."
}

rooms = {
    1: "You are standing by a pothole.",
    2: "This is a vast cavern with passages leading east, south and west. A dim passsage slopes upwards behind you.",
    3: "This cave contains only a pool of oil.",
    4: "Here is a giant rusty door.",
    5: "You are in the western alcove.",
    6: "You are in the treasure cave."
}

connections = {
    1: {},
    2: {2: 3, 3: 4, 4: 5},
    3: {4: 2},
    4: {1: 2},
    5: {2: 2},
    6: {1: 4}
}

objects = {
    1: ("A lamp", 1),
    2: ("A lighted lamp", 0),
    3: ("A Ming vase", 5),
    4: ("A vase of oil", 0),
    5: ("A bar of gold", 6)
}

words = {
    "n": 1, "nort": 1,
    "e": 2, "east": 2,
    "s": 3, "sout": 3,
    "w": 4, "west": 4,
    "u": 5, "up":   5,
    "d": 6, "down": 6,
    "take": 13,
    "drop": 14,
    "vase": 15,
    "gold": 16,
    "door": 17,
    "open": 18,
    "lamp": 19,
    "ligh": 20,
    "fill": 21,
    "oil":  22,
    "inve": 23,
    "quit": 24,
    "look": 25
}

game_actions = [
    ([(AT, 4), (SETQ, 6)],    [(MESSAGE, 2), (DONEC,)]),
    ([(AT, 4), (RESQ, 6)],    [(MESSAGE, 1), (DONEC,)]),
    ([(AT, 1), (CARRIED, 5)], [(MESSAGE, 6), (END,)])
]

player_actions = [
    ((13, 19), [(PRESENT, 1)],          [(GET, 1), (OK,)]),                 # take lamp
    ((14, 19), [(PRESENT, 1)],          [(DROP, 1), (OK,)]),                # drop lamp
    ((13, 19), [(PRESENT, 2)],          [(GET, 2), (SET, 3), (OK,)]),       # take lit lamp
    ((14, 19), [(PRESENT, 2)],          [(DROP, 2), (RESET, 3), (OK,)]),    # drop lit lamp
    ((20,  0), [(CARRIED, 1)],          [(SWAP, 1), (SET, 3), (OK,)]),      # light lamp
    ((20,  0), [(PRESENT, 2)],          [(MESSAGE, 3), (DONE,)]),           # light lamp
    (( 6,  0), [(AT, 1)],               [(SET, 2), (GOTO, 2), (DESC,)]),    # down at 1
    (( 5,  0), [(AT, 2)],               [(RESET, 2), (GOTO, 1), (DESC,)]),  # up at 2
    ((13, 15), [(PRESENT, 3)],          [(GET, 3), (OK,)]),                 # take vase
    ((14, 15), [(PRESENT, 3)],          [(DROP, 3), (OK,)]),                # drop vase
    ((13, 16), [(PRESENT, 5)],          [(GET, 5), (OK,)]),                 # take gold
    ((14, 16), [(PRESENT, 5)],          [(DROP, 5), (OK,)]),                # drop gold
    ((21,  0), [(PRESENT, 3), (AT, 3)], [(SWAP, 3), (OK,)]),                # fill vase
    ((22,  0), [(AT, 4), (PRESENT, 4)], [(SWAP, 3), (SET, 5), (OK,)]),      # oil door
    ((18,  0), [(AT, 4), (SETQ, 5)],    [(MESSAGE, 4), (SET, 6), (DONE,)]), # open oiled door
    ((18,  0), [(AT, 4), (RESQ, 5)],    [(MESSAGE, 5), (DONE,)]),           # open non-oiled door
    (( 3,  0), [(AT, 4), (RESQ, 6)],    [(MESSAGE, 7), (DONE,)]),           # south when closed door
    (( 3,  0), [(AT, 4), (SETQ, 6)],    [(GOTO, 6), (DESC,)]),              # south when open door
    ((23,  0), [],                      [(INVEN,)]),                        # inven
    ((24,  0), [],                      [(QUIT,)]),                         # quit
    ((25,  0), [],                      [(DESC,)]),                         # look
]

class GotoDesc(Exception):
    pass

class GotoInput(Exception):
    pass

class GotoInputNG(Exception):
    pass

class GotoEnd(Exception):
    pass

class Adventure:

    def __init__(self, rooms, connections, messages, objects, words, game_actions, player_actions):
        self.rooms = rooms
        self.connections = connections
        self.messages = messages
        self.objects = objects
        self.words = words
        self.game_actions = game_actions
        self.player_actions = player_actions
        self.flags = { fn: 0 for fn in range(1, 11) }
        self.counters = { cn: 0 for cn in range(1, 6) }
        self.room = 1
        self.object_pos = { on: pos for (on, (odesc, pos)) in objects.items() }
        self.verb = 0
        self.noun = 0
    
    def run(self):
        try:
            while True:
                try:
                    self.turn()
                except GotoDesc:
                    pass
        except GotoEnd:
            pass
    
    def turn(self):
        if not self.flags[2]:
            self.desc()
        else:
            if self.counters[2]:
                self.counters[2] -= 1
            if self.flags[3]:
                self.desc()
            else:
                print("It is dark. Better get some light or you may be in trouble.")
            if self.counters[3]:
                self.counters[3] -= 1
        gt = True
        while True:
            try:
                self.input(gt)
                gt = True
            except GotoInput:
                gt = True
            except GotoInputNG:
                gt = False

    def desc(self):
        print(rooms[self.room])
        here = [on for (on, pos) in self.object_pos.items() if pos == self.room]
        if here:
            print("There is also: " + ", ".join(self.objects[on][0] for on in here))

    def input(self, game=True):
        if game:
            self.game_turn()
        if self.counters[1]:
            self.counters[1] -= 1
        if self.counters[4]:
            self.counters[4] -= 1
        phrase = input("> ")
        self.parse(phrase)
        if self.verb == 0:
            print("Pardon?")
            raise GotoDesc()
        if self.verb in self.connections[self.room]:
            self.room = self.connections[self.room][self.verb]
            raise GotoDesc()
        done = self.player_turn()
        if not done:
            if self.verb < 13:
                print("You can't go that way.")
            else:
                print("You can't.")
            raise GotoDesc()

    def game_turn(self):
        for rule in self.game_actions:
            (conditions, actions) = rule
            if self.match(conditions):
                self.exec(actions)

    def player_turn(self):
        for rule in self.player_actions:
            self.exec_rule(rule)
        return False

    def exec_rule(self, rule):
        ((verb, noun), conditions, actions) = rule
        if verb == self.verb and (noun == self.noun or noun == 0) and self.match(conditions):
            self.exec(actions)

    def match(self, conditions):
        return all([self.eval_cond(cond) for cond in conditions])

    def eval_cond(self, condition):
        (op, val) = condition
        if op == AT:
            return self.room == val
        elif op == PRESENT:
            return self.object_pos[val] == self.room or self.object_pos[val] == -1
        elif op == ABSENT:
            return self.object_pos[val] != self.room and self.object_pos[val] > 0
        elif op == CARRIED:
            return self.object_pos[val] == -1
        elif op == SETQ:
            return self.flags[val] != 0
        elif op == RESQ:
            return self.flags[val] == 0
        elif op == ONEQ:
            return self.counters[val] == 1
        elif op == CHANCE:
            return random.randint(0, 100) < val
        else:
            print("Invalid condition " + condition)
            raise GotoEnd()

    def exec(self, actions):
        for action in actions:
            self.exec_action(action)
    
    def exec_action(self, action):
        op = action[0]
        val = action[1] if len(action) > 1 else 0

        if op == INVEN:
            carried = [on for (on, pos) in self.object_pos.items() if pos == -1]
            if carried:
                print("You are holding: " + ", ".join(self.objects[on][0] for on in carried))
            else:
                print("You are holding: " + "nothing.")
            raise GotoDesc()
        elif op == GET:
            if self.flags[1] >= 5:
                print("You cannot carry more.")
                raise GotoDesc()
            elif self.object_pos[val] == -1:
                print("You already have it.")
                raise GotoDesc()
            else:
                self.object_pos[val] = -1
                self.flags[1] += 1
        elif op == DROP:
            if self.object_pos[val] == -1:
                self.object_pos[val] = self.room
                self.flags[1] -= 1
            else:
                print("You don't have " + objects[val][1])
                raise GotoDesc()
        elif op == MESSAGE:
            print(self.messages[val])
        elif op == SET:
            self.flags[val] = 1
        elif op == RESET:
            self.flags[val] = 0
        elif op == LET:
            self.counters[val] = action[2]
        elif op == SWAP:
            self.object_pos[val], self.object_pos[val+1] = self.object_pos[val+1], self.object_pos[val]
        elif op == CREATE:
            if self.object_pos[val] == -1:
                self.flags[1] -= 1
            self.object_pos[val] = self.room
        elif op == DESTROY:
            if self.object_pos[val] == -1:
                self.flags[1] -= 1
            self.object_pos[val] = 0
        elif op == GOTO:
            self.room = val
        elif op == OK:
            print("Okay.")
            raise GotoInput()
        elif op == DONE:
            raise GotoInput()
        elif op == DONEC:
            raise GotoInputNG()
        elif op == DESC:
            raise GotoDesc()
        elif op == QUIT:
            q = input("Are you sure? ")
            if q != "y":
                raise GotoDesc()
            else:
                raise GotoEnd()
        elif op == END:
            raise GotoEnd()
        else:
            pass

    def parse(self, phrase):
        keywords = [self.words[w[:4]] for w in phrase.split() if w[:4] in self.words]
        self.verb = keywords[0] if len(keywords) > 0 else 0
        self.noun = keywords[1] if len(keywords) > 1 else 0

if __name__ == "__main__":
    Adventure(
        rooms,
        connections,
        messages,
        objects,
        words,
        game_actions,
        player_actions
    ).run()
