import re
import time
import paramiko
from nix_functions import get_ip_addresses_from_url


class OwnSSH:
    def __init__(self, ip, username, password, keys_needed=False):
        self.ip = ip
        self.username = username
        self._password = password
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(
            hostname=self.ip,
            username=self.username,
            password=self._password,
            look_for_keys=keys_needed,
            allow_agent=keys_needed
        )
        self.ssh = client.invoke_shell()
        print(f'Connection to {self.ip} established.')

    is_root = False
    is_vtysh = False

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.ssh.close()

    def upgrade_to_root(self):
        self.ssh.send('\n')
        prompt = self.ssh.recv(5000).decode('utf-8')
        self.ssh.send('\nsudo -i\n')
        time.sleep(0.5)
        output = self.ssh.recv(5000).decode('utf-8')
        if 'password' in output:
            self.ssh.send(self._password + '\n')
            time.sleep(0.5)
            self.ssh.recv(5000)
            self.ssh.send('\n')
            time.sleep(0.5)
            prompt = self.ssh.recv(5000).decode('utf-8')
        if 'root' in prompt:
            self.is_root = True

    def enter_to_vtysh(self):
        self.ssh.send('vtysh\n')
        time.sleep(0.5)
        self.ssh.recv(5000)
        self.ssh.send('\n')
        time.sleep(0.5)
        self.ssh.recv(5000)
        self.is_vtysh = True

    def exit_from_vtysh(self):
        if self.is_vtysh:
            self.ssh.send('end\n')
            time.sleep(0.5)
            self.ssh.send('exit\n')
            time.sleep(0.5)
            self.ssh.recv(5000)
            self.is_vtysh = False
        else:
            print('You are not in FRR vtysh')

    def close(self):
        self.ssh.close()
        print(f'SSH connection to {self.ip} is closed.')

    def send_config_commands(self, commands, silent=False):
        if not isinstance(commands, list):
            commands = [commands]
        if self.is_vtysh:
            self.ssh.send('configure term\n')
            time.sleep(0.5)
            output = self.ssh.recv(5000).decode('utf-8')
            for command in commands:
                self.ssh.send(command + '\n')
                time.sleep(0.5)
                output += self.ssh.recv(5000).decode('utf-8')
            self.ssh.send('end\n')
            time.sleep(0.5)
            output += self.ssh.recv(5000).decode('utf-8')
            return output if not silent else None

    def write_config(self, silent=False):
        if self.is_vtysh:
            self.ssh.send('\nend\n')
            time.sleep(0.5)
            output = self.ssh.recv(5000)
            self.ssh.send('write memory\n')
            time.sleep(2)
            output += self.ssh.recv(5000)
            return output if not silent else None