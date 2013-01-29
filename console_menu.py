import collections
import copy
import time
import pdb

class ConsoleMenu(object):
    def __init__(self, menu_text, menu_prompt='', menu_items = None):
        self.menu_text = menu_text
        if menu_prompt:
            self.menu_prompt = menu_prompt
        else:
            self.menu_prompt = 'Choice: '
        self.menu_items = {}
        if menu_items:
            for command, text in menu_items:
                self.add_menu_item(command, text)
        # when we create a child, builtin commands gets extended with a back option        
        self.builtin_commands = {'q' : (self.quit, 'quit')}
        self.parent = None

    def __call__(self):
        '''Allows a ConsoleMenu to be a command for a menu item (nested menus)'''
        return self.run_menu()

    def quit(self):
        def do_nothing():
            pass
        return do_nothing

    def run_menu(self):
        valid_input = False
        while not valid_input:
            self._display()
            valid_input, user_choice = self._get_user_input()
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
        self._verify_menu_item(item_number, command, text)
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
        valid_items = list(self.builtin_commands) + str_items
        try:
            user_input = raw_input(self.menu_prompt)
            user_input = user_input.strip()
        except EOFError:
            # pressing ctrl-d generates EOFError
            user_input = 'q'
        valid_input = user_input in valid_items
        if not valid_input:
            print
            print '**************************************************'
            print 'Error: invalid input, please try again'
            print '**************************************************'
            time.sleep(1)
        return valid_input, user_input
    
    def _verify_menu_items_type(self, menu_items):
        if not menu_items:
            return
        elif not isinstance(menu_items, collections.Sequence):
            msg = 'menu_items argument to ConsoleMenu constructor must be a sequence'
        for i, item in enumerate(menu_items):
            if not isinstance(item, collections.Sequence):
                msg = 'Menu item #%d passed to ConsoleMenu constructor is not a sequence.  Offending item is: %s' % (i, str(item))
                raise ValueError(msg)
            
    def _verify_menu_item(self, item_number, command, text):
        if not callable(command):
            msg = 'Command for menu item #%d is not callable.  Offending item is: %s' % (item_number, str((command, text)))
            raise ValueError(msg)
        if type(text) != str:
            msg = 'Text for menu item #%d is not a string.  Offending item is: %s' % (item_number, str((command, text)))
            raise ValueError(msg)
    
    
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
