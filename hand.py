#!/usr/bin/env python3

from time import sleep

import irc.bot
import irc.strings
from irc.client import ip_numstr_to_quad, ip_quad_to_numstr

from led_driver import LEDDriver
from buttons import ButtonPoller

NICKNAME = "hand-bot"

class HandBot(irc.bot.SingleServerIRCBot):
    def __init__(self, channel, nickname, server, port=6667):
        irc.bot.SingleServerIRCBot.__init__(self, [(server, port)], nickname, nickname)
        self.channel = channel
        self.is_raised = False
        self.raised_nick = None
        self.user_queue = []

        self.led = LEDDriver()
        self.led.start()
        self.led.set_pattern("idle")

        self.buttons = ButtonPoller(self)
        self.buttons.start()

    def on_nicknameinuse(self, c, e):
        c.nick(c.get_nickname() + "_")

    def on_welcome(self, c, e):
        c.join(self.channel)

    def on_pubmsg(self, c, e):
        user = e.source.nick
        msg = e.arguments[0]
        self.do_command(user, msg)

    def button_0_pressed(self):
        self.next_action()

    def button_1_pressed(self):
        print("but 1")

    def next_action(self):
        if not self.is_raised:
            self.led.short_dim()
            return

        try:
            popped = self.user_queue.pop(0)
        except IndexError:
            popped = None

        if popped is not None:
            self.connection.privmsg(self.channel, f"{popped}: your turn is now complete. thank you!")

        if len(self.user_queue) == 0:
            self.set_state("idle")
        else:
            self.set_state("idle")
            sleep(1)
            self.set_state("raised")

    def set_state(self, state):

        if state == "raised":
            if self.is_raised:
                return

            self.is_raised = True
            self.led.set_pattern(state)
            return

        if state == "idle":
            if not self.is_raised:
                return

            self.is_raised = False
            self.led.set_pattern(state)
            return

        if state == "rainbow":
            if self.is_raised:
                return

            self.led.set_pattern(state)
            return

    def do_command(self, user, msg):
        c = self.connection

        msg = msg.strip()
        if msg == "!raise":
            if user in self.user_queue:
                c.privmsg(self.channel, f"{user}: you already raised your hand. wait your turn!")
                return
            else:
                self.set_state("raised")
                self.user_queue.append(user)
                position = self.user_queue.index(user)
                c.privmsg(self.channel, f"{user}: you raised your hand and you're in position {position}")
                return

        elif msg == "!lower":
            if user not in self.user_queue:
                c.privmsg(self.channel, f"{user}: your hand wasn't raised, silly!")
            else:
                self.user_queue.remove(user)
                c.privmsg(self.channel, f"{user}: you lowered your hand")

            if len(self.user_queue) == 0:
                self.set_state("idle")

        elif msg in ("!queue", "!waiting", "!status"):

            if len(self.user_queue) == 0:
                c.privmsg(self.channel, f"the queue is empty")
            else:
                c.privmsg(self.channel, f"the current queue: " + ", ".join(self.user_queue))
        elif msg == "!die":
            c.privmsg(self.channel, f"Goodbye cruel world!")
            self.die()
            sys.exit(-1)
        elif msg == "!love":
            c.privmsg(self.channel, f"Awwww, I love you too!")
        elif msg == "!rainbow":
            self.set_state("rainbow")
            c.privmsg(self.channel, f"Is it party time?")
        elif msg == "!rick":
            c.privmsg(self.channel, f"https://www.youtube.com/watch?v=dQw4w9WgXcQ")
        elif msg == "!help":
            c.privmsg(self.channel, f"I respond to the following commands:")
            c.privmsg(self.channel, f"  raise - raise your hand")
            c.privmsg(self.channel, f"  lower - lower your hand")
            c.privmsg(self.channel, f"  queue - show the current queue of people waiting")
            c.privmsg(self.channel, f"  love - show some love")
            c.privmsg(self.channel, f"  rick - how could we not?")

def main():
    try:
        bot = HandBot("#musicbrianz", NICKNAME, "irc.libera.chat", 6667)
        bot.start()
    except KeyboardInterrupt as err:
        bot.disconnect()
    finally:
        bot.disconnect()

if __name__ == "__main__":
    main()
