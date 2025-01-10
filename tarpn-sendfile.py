#!/usr/bin/python
import telnetlib
import time
import argparse
import os
import json
import base64
import glob

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

def sendFile(tn, call, filename, body):
    msg = {}

    body = base64.b85encode(body).decode('ascii')

    msg['filename'] = filename
    msg['body'] = body
    jsonMsg = json.dumps(msg)
    msg = f"@!#{jsonMsg}"
    sendBBSMessage(tn, call, "tarpn-sendfile", msg)

def telnet_to_bpq(args):
    HOST = "localhost"
    PORT = 8011

    try:
        # Connect to the Telnet server
        tn = telnetlib.Telnet(HOST, PORT, timeout=5)
        print(f"Connected to {HOST}:{PORT}")
        time.sleep(1)  # Allow server to initialize
        connect(tn)
        with open(args.file, "rb") as file:
            content = file.read().strip()
        head, tail = os.path.split(args.file)
        response = sendFile(tn, args.to, tail, content)
        print(response)
        tn.close()
    except Exception as e:
        print(f"Error: {e}")

def process_mes_files():
    # Input and output directory paths
    input_dir = '/home/pi/bpq/Mail'
    output_dir = '/home/pi/tarpn-sendfile-inbox'
    
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Get all .mes files in the input directory
    mes_files = glob.glob(os.path.join(input_dir, '*.mes'))
    
    for mes_file in mes_files:
        try:
            with open(mes_file, 'r') as f:
                content = f.read().strip()
                
                # Check if the file starts with @!#
                if not content.startswith('@!#'):
                    continue
                
                # Extract the JSON part (remove the @!# prefix)
                json_str = content[3:]
                
                try:
                    # Parse the JSON data
                    data = json.loads(json_str)
                    
                    # Extract filename and encoded body
                    output_filename = data.get('filename')
                    encoded_body = data.get('body')
                    
                    if not output_filename or not encoded_body:
                        print(f"Missing required fields in {mes_file}")
                        continue
                    
                    # Create full output path
                    output_path = os.path.join(output_dir, output_filename)
                    
                    # Decode the base85 content
                    try:
                        decoded_content = base64.b85decode(encoded_body)
                        
                        # Write the decoded content to the output file
                        with open(output_path, 'wb') as out_file:
                            out_file.write(decoded_content)
                            
                        print(f"Successfully processed {mes_file} -> {output_path}")
                        
                    except Exception as e:
                        print(f"Error decoding base85 content in {mes_file}: {str(e)}")
                        
                except json.JSONDecodeError as e:
                    print(f"Invalid JSON format in {mes_file}: {str(e)}")
                    
        except Exception as e:
            print(f"Error processing file {mes_file}: {str(e)}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract parameters from the command line for an amateur radio message.")

    # Define the required arguments
    parser.add_argument("--to", required=False, help="Amateur radio call sign of the recipient")
    parser.add_argument("--file", required=False, help="Path of the file to send")
    parser.add_argument("--sync", action='store_true', required=False, help="Download files from BBS messages into the inbox")


    # Parse arguments
    args = parser.parse_args()

    # Print the extracted values


    if args.to and args.file:
        print(f"To: {args.to}")
        print(f"File: {args.file}")
        telnet_to_bpq(args)
    elif args.sync:
        process_mes_files()
    else:
        print("Try -h")

