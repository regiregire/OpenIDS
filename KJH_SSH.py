import paramiko
from scp import SCPClient, SCPException

ssh_client = None
def connect(ip, username, password):
    global ssh_client
    """Create SSH client session to remote server"""
    if ssh_client is None:
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_client.connect(ip, username=username, password=password)
    
    else:
        print("SSH client session exist.")
            
def disconnect():
    global ssh_client
    """Close SSH client session"""
    ssh_client.close()
    
def send_file(local_path, remote_path):
    global ssh_client
    """Send a single file to remote path"""
    try:
        with SCPClient(ssh_client.get_transport()) as scp:
            scp.put(local_path, remote_path, preserve_times=True)
    except SCPException:
        raise SCPException.message

def get_file(remote_path, local_path):
    global ssh_client
    """Get a single file from remote path"""
    try:
        with SCPClient(ssh_client.get_transport()) as scp:
            scp.get(remote_path, local_path)
    except SCPException:
        raise SCPException.message

def send_command(command):
    global ssh_client
    """Send a single command"""
    stdin, stdout, stderr = ssh_client.exec_command(command)


