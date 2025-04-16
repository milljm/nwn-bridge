#!/usr/bin/env python3
"""
Connect to a NWN's SQlite database, and pool/watch for trigger
events to supply to an LLM, and return the LLMs response.
"""
import os
import sys
import argparse
import subprocess
import threading

try:
    # pylint: disable=multiple-imports
    import sqlite3, ollama
except ModuleNotFoundError as e:
    print(f'Failed to import required modules. {e}\n'
          'Perhaps you need to activate your environment? Or create one using:\n\n'
          '\tconda create -n nwn-bridge python sqlite3 ollama ollama-python\n'
          '\tconda activate nwn-bridge')
    sys.exit(1)

class Ollama():
    """
    Responsible for Ollama calls, and server startup
    """
    def __init__(self, args):
        self.args = args
        self.ollama_client = ollama.Client()

    @staticmethod
    def start_ollama_server():
        """ Starts the Ollama server """
        try:
            # Use subprocess.Popen for non-blocking execution
            process = subprocess.Popen(['ollama', 'serve'],
                                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            def log_output(stream):
                """Logs output from the server process."""
                for line in iter(stream.readline, b''):  # Read lines until EOF
                    print(line.decode('utf-8').strip())

            # Start threads to handle stdout and stderr
            stdout_thread = threading.Thread(target=log_output, args=(process.stdout,))
            stderr_thread = threading.Thread(target=log_output, args=(process.stderr,))
            stdout_thread.daemon = True
            stderr_thread.daemon = True
            stdout_thread.start()
            stderr_thread.start()

            return process

        except FileNotFoundError:
            print("Error: 'ollama' command not found. Make sure Ollama is installed and"
                  " in your PATH.")
            return None
        # pylint: disable=broad-exception-caught
        except Exception as e:
            print(f"An error occurred while starting Ollama server: {e}")
            return None

class SQLite():
    """
    SQLite handler

    syntax:
        sql = SQLite('/path/to/database')

    usage:
        data = sql.fetch('NWN_TAG')
        sql.write('NWN_TAG', data)
    """
    def __init__(self, args):
        self.db = sqlite3.connect(args.database)
        self.client = ollama.Client()
        self.cursor = self.db.cursor()

    def get_data(self, cursor)->object:
        """ determine data type """
        return

    def fetch(self, nwn_tag)->object:
        return self.db

    def write(self, nwn_tag, data):
        return None

def verify_args(args):
    """ verify arguments are correct """
    if not os.path.exists(args.database) or not os.access(args.database, os.W_OK):
        print(f'{args.database} does not exist, or is not read/writable')
    return args

def parse_args(argv):
    """ parse arguments """
    about = """A tool which bridges Neverwinter Nights EE <--> SQLite <--> LLM"""
    epilog = f"""
example:
  ./{os.path.basename(__file__)} gemma3:latest /path/to/triggers.json /path/to/mygame.sqlite3
    """
    parser = argparse.ArgumentParser(description=f'{about}',
                                     epilog=f'{epilog}',
                                     formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('llm', help='name of LLM model (as it appears with: `ollama list`)')
    parser.add_argument('triggers', help='path to json control triggers file (see README.md)')
    parser.add_argument('database', help='path to NWN SQLite database')
    parser.add_argument('-s', '--server', nargs=1, help='ollama server address'
                        ' (leave empty to launch local server)')
    return verify_args(parser.parse_args(argv))

if __name__ == '__main__':
    args = parse_args(sys.argv[1:])
    print(args)
