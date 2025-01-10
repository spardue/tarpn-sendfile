#!/usr/bin/python
import telnetlib
import time
import argparse

def parse_config_file(filename):
    config_dict = {}

    with open(filename, "r") as file:
        for line in file:
            # Strip whitespace and ignore empty lines
            line = line.strip()
            if not line or line.startswith("#"):  # Ignore blank lines and comments
                continue

            # Split the line at the first '=' into key and value
            if ":" in line:
                key, value = line.split(":", 1)  # Split only at the first '='
                config_dict[key.strip()] = value.strip()

    return config_dict

nodeConfig = parse_config_file("/home/pi/node.ini")

CALL_SIGN = nodeConfig['local-op-callsign']
PASSWORD = 'p'

def sendCommand(tn, cmd, wait=1):
    cmd = cmd.encode() + b"\r\n"
    tn.write(cmd)
    time.sleep(wait)
    response = tn.read_very_eager()
    return response

def connect(tn):
    sendCommand(tn, CALL_SIGN)
    sendCommand(tn, PASSWORD)
    sendCommand(tn, "") # flush buffer?
    time.sleep(1)


def sendBBSMessage(tn, call, subject, body):
    sendCommand(tn, "BBS")
    sendCommand(tn, f"SP {call}")
    sendCommand(tn, subject)
    response = sendCommand(tn, f"{body}\r\n/ex")

def telnet_to_bpq(args):
    HOST = "localhost"
    PORT = 8011

    try:
        # Connect to the Telnet server
        tn = telnetlib.Telnet(HOST, PORT, timeout=5)
        print(f"Connected to {HOST}:{PORT}")
        time.sleep(1)  # Allow server to initialize
        connect(tn)
        with open(args.file, "r") as file:
            content = file.read().strip()
        response = sendBBSMessage(tn, args.to, args.subject , content)
        print(response)
        tn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract parameters from the command line for an amateur radio message.")

    # Define the required arguments
    parser.add_argument("--to", required=True, help="Amateur radio call sign of the recipient")
    parser.add_argument("--subject", required=True, help="Short subject for the message")
    parser.add_argument("--file", required=True, help="Path of the file to send")

    # Parse arguments
    args = parser.parse_args()

    # Print the extracted values
    print(f"To: {args.to}")
    print(f"Subject: {args.subject}")
    print(f"File: {args.file}")


    telnet_to_bpq(args)

