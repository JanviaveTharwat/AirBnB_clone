#!/usr/bin/python3
"""Module for the entry point of the command interpreter."""
import cmd
import re
from shlex import split
from models import storage
from models.base_model import BaseModel
from models.user import User
from models.state import State
from models.city import City
from models.place import Place
from models.amenity import Amenity
from models.review import Review


class HBNBCommand(cmd.Cmd):
    """Contains the entry point of the command interpreter."""
    prompt = "(hbnb) "
    classes_names = {'BaseModel': BaseModel, 'User': User, 'Place': Place,
                     'State': State, 'City': City, 'Amenity': Amenity,
                     'Review': Review}
    types = {
             'number_rooms': int, 'number_bathrooms': int,
             'max_guest': int, 'price_by_night': int,
             'latitude': float, 'longitude': float
            }
    advancec_commands = ['all', 'count', 'show', 'destroy', 'update']

    def do_quit(self, args):
        """Quit command to exit the program."""
        return True

    def do_EOF(self, args):
        """Ending char handler."""
        print()
        return True

    def emptyline(self):
        """shouldn’t execute anything"""
        pass

    def do_create(self, args):
        """ Create an object of any class"""
        if not args:
            print("** class name missing **")
            return
        elif args not in HBNBCommand.classes_names:
            print("** class doesn't exist **")
            return
        new_object = HBNBCommand.classes_names[args]()
        storage.save()
        print(new_object.id)

    def do_show(self, args):
        """ Method to show an individual object """
        new_args = args.partition(" ")
        class_name = new_args[0]
        class_id = new_args[2]

        # guard against trailing args
        if class_id and ' ' in class_id:
            class_id = class_id.partition(' ')[0]

        if not class_name:
            print("** class name missing **")
            return

        if class_name not in HBNBCommand.classes_names:
            print("** class doesn't exist **")
            return

        if not class_id:
            print("** instance id missing **")
            return

        key = class_name + "." + class_id
        try:
            print(storage._FileStorage__objects[key])
        except KeyError:
            print("** no instance found **")

    def do_destroy(self, args):
        """ Destroys a specified object """
        new_args = args.partition(" ")
        class_name = new_args[0]
        class_id = new_args[2]

        if class_id and ' ' in class_id:
            class_id = class_id.partition(' ')[0]

        if not class_name:
            print("** class name missing **")
            return

        if class_name not in HBNBCommand.classes_names:
            print("** class doesn't exist **")
            return

        if not class_id:
            print("** instance id missing **")
            return

        key = class_name + "." + class_id

        try:
            del(storage.all()[key])
            storage.save()
        except KeyError:
            print("** no instance found **")

    def do_all(self, args):
        """ Shows all objects, or all objects of a class"""
        print_list = []

        if args:
            args = args.split(' ')[0]
            if args not in HBNBCommand.classes_names:
                print("** class doesn't exist **")
                return
            for key, val in storage.all().items():
                if key.split('.')[0] == args:
                    print_list.append(str(val))
        else:
            for key, val in storage.all().items():
                print_list.append(str(val))

        print(print_list)

    def do_update(self, args):
        """ Updates a certain object with new information """
        class_name = class_id = attribute_name = attribute_val = kwargs = ''

        args = args.partition(" ")
        if args[0]:
            class_name = args[0]
        else:
            print("** class name missing **")
            return
        if class_name not in HBNBCommand.classes_names:
            print("** class doesn't exist **")
            return

        # gets id from args
        args = args[2].partition(" ")
        if args[0]:
            class_id = args[0]
        else:
            print("** instance id missing **")
            return

        # generate the key
        key = class_name + "." + class_id

        # checks if key is present
        if key not in storage.all():
            print("** no instance found **")
            return

        # check if kwargs or args
        if '{' in args[2] and '}' in args[2] and type(eval(args[2])) is dict:
            kwargs = eval(args[2])
            args = []
            for key, val in kwargs.items():
                args.append(key)
                args.append(val)
        else:  # get args
            args = args[2]
            if args and args[0] == '\"':  # check for quoted arg
                second_quote = args.find('\"', 1)
                attribute_name = args[1:second_quote]
                args = args[second_quote + 1:]

            args = args.partition(' ')

            if not attribute_name and args[0] != ' ':
                attribute_name = args[0]
            if args[2] and args[2][0] == '\"':
                attribute_val = args[2][1:args[2].find('\"', 1)]

            if not attribute_val and args[2]:
                attribute_val = args[2].partition(' ')[0]

            data = [attribute_name, attribute_val]

        dict = storage.all()[key]

        for i, attribute_name in enumerate(data):
            # block only runs on even iterations
            if (i % 2 == 0):
                att_val = data[i + 1]  # following item is value
                if not attribute_name:  # check for att_name
                    print("** attribute name missing **")
                    return
                if not att_val:
                    print("** value missing **")
                    return
                # type cast as necessary
                if attribute_name in HBNBCommand.types:
                    att_val = HBNBCommand.types[attribute_name](att_val)

                # update dictionary
                dict.__dict__.update({attribute_name: att_val})

        storage.save()  # save updates to jason file

    def do_count(self, args):
        """Count current number of class instances"""
        count = 0
        for key, val in storage.all().items():
            if args == key.split('.')[0]:
                count += 1
        print(count)

    def precmd(self, line):
        """manuiplate commands for advanced command syntax.

        Usage: <class name>.<command>([<id> [<*args> or <**kwargs>]])
        (Brackets denote optional fields in usage example.)
        """
        id = ''
        args = ''

        # check commands conatains '.', '(', ')'
        if not ('.' in line and '(' in line and ')' in line):
            return line

        try:
            newline = line[:]

            # get <class name>
            _class = newline[:newline.find('.')]

            # get and validate <command>
            command = newline[newline.find('.') + 1:newline.find('(')]
            if command not in HBNBCommand.advancec_commands:
                raise Exception
            line = ' '.join([command, _class, id, args])

        except Exception as mess:
            pass
        finally:
            return line


if __name__ == '__main__':
    HBNBCommand().cmdloop()
