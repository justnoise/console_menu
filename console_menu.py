# Copyright (C) 2013 by Brendan Cox

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import collections
import copy
import time


class ConsoleMenu(object):
    def __init__(self, menu_text, menu_prompt='', menu_items = None):
        self.menu_text = menu_text
        if menu_prompt:
            self.menu_prompt = menu_prompt
        else:
            self.menu_prompt = 'Choice: '
        self.menu_items = {}
        if menu_items:
            for item, text in menu_items:
                self.add_menu_item(item, text)
        # when we create a child, builtin commands gets extended with a back option
        self.builtin_commands = {'q': (self.quit, 'quit')}
        self.parent = None

    def __call__(self):
        '''Allows a ConsoleMenu to be a command for a menu item (nested menus)'''
        return self.run_menu()

    def quit(self):
        return lambda: None

    def run_menu(self):
        user_choice = None
        while not user_choice:
            self._display()
            user_choice = self._get_user_input()
        if user_choice not in self.builtin_commands:
            user_choice = int(user_choice)

        all_commands = copy.copy(self.builtin_commands)
        all_commands.update(self.menu_items)
        command = all_commands[user_choice][0]
        if isinstance(command, ConsoleMenu):
            return command()
        else:
            return command

    def add_menu_item(self, command, text):
        item_number = len(self.menu_items) + 1
        self.menu_items[item_number] = (command, text)
        if isinstance(command, ConsoleMenu):
            command.parent = self
            command.builtin_commands['b'] = (self, 'back')

    def _display(self):
        print
        print '--------------------------------------------------'
        print self.menu_text
        print '--------------------------------------------------'
        all_menu_items = copy.copy(self.menu_items)
        all_menu_items.update(self.builtin_commands)
        for item_selector, item in sorted(all_menu_items.items()):
            # no back option if we're not a child menu
            if item_selector == 'b' and not self.parent:
                continue
            text = item[1]
            print '  %s) %s' % (str(item_selector),  text)

    def _get_user_input(self):
        str_items = [str(i) for i in self.menu_items.keys()]
        valid_items = list(self.builtin_commands.keys()) + str_items
        try:
            user_input = raw_input(self.menu_prompt)
            user_input = user_input.strip()
        except EOFError:
            # pressing ctrl-d generates EOFError
            user_input = 'q'
        if user_input not in valid_items:
            print
            print '**************************************************'
            print 'Error: invalid input, please try again'
            print '**************************************************'
            time.sleep(1)
            user_input = None
        return user_input


if __name__ == '__main__':
    def say_hello():
        print 'hello'

    def make_printer(printthis):
        def _():
            print printthis
        return _

    items = [(say_hello, 'Item 1'),
             (say_hello, 'Item 2 does nothing'),
             (say_hello, 'Item 3 does about as much as item 2'),
             (say_hello, 'Item 4 dont do much'),
             (say_hello, 'Item 5 is another menu')]
    menu = ConsoleMenu('Please choose a useless option', menu_items=items)
    another_menu = ConsoleMenu('Please choose another useless option')
    another_menu.add_menu_item(make_printer('one'), 'Item One')
    another_menu.add_menu_item(make_printer('two'), 'Item Two')
    another_menu.add_menu_item(make_printer('three'), 'Item Three')
    menu.add_menu_item(another_menu, 'Do sub menu')
    action = menu.run_menu()
    action()

    items = [('foo', 'gimmie foo'),
             ('bar', 'gimmie bar'),
             ('baz', 'gimmie baz')]
    menu = ConsoleMenu('Please choose something... anything!', menu_items=items)
    action = menu.run_menu()
    print 'you chose:', action
