# Remote Cmd:
This project is a Python-based remote command execution tool that allows users to send commands to a remote client, execute them, and receive the output. It includes functionality for file transfer and remote email notification.

# How it works:
* Server: The server listens for incoming connections from clients. Once connected, it can send commands for execution and request file transfers.
* Client: The client receives commands and executes them in the local shell, sending back the output. It can also compress and send files as requested by the server.
* Email Notifications: Upon receiving files, the client compresses them into a ZIP file and sends an email notification with the ZIP file attached.

# What I learned:
* Socket programming and client-server communication
* Remote command execution and file transfer
* Sending emails with attachments and error handling
