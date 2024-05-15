#!/usr/bin/env python3
from docopt import docopt, DocoptExit
from dotenv import load_dotenv

from stl.command.stl_command import StlCommand

import datetime

def main():
    load_dotenv()
    try:
        arguments = docopt(str(StlCommand.__doc__))
        if arguments.get('--interval', None) and arguments.get('--checkin', None) and arguments.get('--checkout', None):
            start_date = arguments.get('--checkin')
            end_date = arguments.get('--checkout')
            num_days = int(arguments.get('--interval'))

            start = datetime.datetime.strptime(start_date, '%Y-%m-%d')
            end = datetime.datetime.strptime(end_date, '%Y-%m-%d')

            sequences = []
            for i in range((end - start).days - num_days + 1):
                current_date = start + datetime.timedelta(days=i)
                sequence = [(current_date + datetime.timedelta(days=0)).strftime('%Y-%m-%d'), (current_date + datetime.timedelta(days=num_days)).strftime('%Y-%m-%d')]
                sequences.append(sequence)
            
            for sequence in sequences:
                arguments['--checkin'] = sequence[0]
                arguments['--checkout'] = sequence[1]
                if '--interval' in arguments:
                    del arguments['--interval']
                StlCommand(arguments).execute()
        else:
            StlCommand(arguments).execute()
    except DocoptExit as de:
        print(de)
        exit(1)


if __name__ == "__main__":
    main()
