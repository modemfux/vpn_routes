import json
import time
import paramiko
from funcs.nix_functions import get_ip_addresses_from_url
import logging


# Logging config
own_logger = logging.getLogger(__name__)
own_logger.setLevel(logging.INFO)
own_handler = logging.FileHandler('vpn_routes.log', mode='a')
own_format = logging.Formatter("%(asctime)s >> %(levelname)s: %(message)s")
own_handler.setFormatter(own_format)
own_logger.addHandler(own_handler)


class OwnSSH:
    def __init__(self, ip, username, password, keys_needed=False):
        self.ip = ip
        self.username = username
        self._password = password
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            client.connect(
                hostname=self.ip,
                username=self.username,
                password=self._password,
                look_for_keys=keys_needed,
                allow_agent=keys_needed,
                timeout=30.0
            )
            connection_state = True
        except TimeoutError as error:
            own_logger.error(f'Connection to {self.ip} is {error}')
            print(f'Connection to {self.ip} is {error}')
            connection_state = False
            raise TimeoutError
        except Exception as error:
            own_logger.error(f'Some error occured while connecting '
                             f'to {self.ip}. Error is: {error}'
                             )
            raise Exception(error)
        if connection_state:
            try:
                self.ssh = client.invoke_shell()
                print(f'Connection to {self.ip} established.')
            except Exception:
                own_logger.exception(f"There are some problems "
                                     f"with connection to {self.ip}. "
                                     "Check device's parameters."
                                     )

    def close(self):
        self.ssh.close()
        print(f'SSH connection to {self.ip} is closed.')

    # Global swithes for current state

    is_root = False
    is_vtysh = False

    # Context manager's function

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.ssh.close()
        print(f'SSH connection to {self.ip} is closed.')

    # Methods for interacting with Linux

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

    def exit_from_root(self):
        self.ssh.send('\n')
        time.sleep(0.5)
        output = self.ssh.recv(5000).decode('utf-8')
        if 'root@' in output:
            self.ssh.send('exit\n')
            time.sleep(0.5)
            self.ssh.recv(5000)
            self.is_root = False

    def enter_to_vtysh(self):
        self.ssh.send('vtysh\n')
        time.sleep(0.5)
        self.ssh.recv(5000)
        self.ssh.send('\n')
        time.sleep(0.5)
        self.ssh.recv(5000)
        self.is_vtysh = True

    def get_routes_from_urls(
        self,
        urls,
        nexthop,
        server='8.8.8.8',
        filename='vpn_routes.json',
        write_to_file=False
    ):
        if not isinstance(urls, list):
            urls = [urls]
        ip_list, url_dict = get_ip_addresses_from_url(
            urls,
            server,
            full_result=True
        )
        for url, addresses in url_dict.items():
            own_logger.info(f'For URL \'{url}\' were given those IPs: '
                            f'{", ".join(addresses)}'
                            )
        backup = 'previous_' + filename
        if write_to_file:
            with open(filename) as src, open(backup, 'w') as dst:
                try:
                    json_urls = json.load(src)
                    dst.write(json.dumps(json_urls))
                except Exception as error:
                    own_logger.error(
                        f'There were some error with file {filename}.'
                        f' Probably it was empty. Error: {error}'
                    )
            with open(filename, 'w') as dst:
                dst.write(json.dumps(url_dict))
        routes = [f'ip route {ip} 255.255.255.255 {nexthop} tag 65001'
                  for ip in ip_list
                  ]
        return routes

    # Methods for interacting with FRR

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
                own_logger.info(
                    f'Command {command} was executed on {self.ip}.'
                )
            self.ssh.send('end\n')
            time.sleep(0.5)
            output += self.ssh.recv(5000).decode('utf-8')
            return output if not silent else None

    def write_config(self, silent=False):
        if self.is_vtysh:
            self.ssh.send('\nend\n')
            time.sleep(0.5)
            output = self.ssh.recv(5000).decode('utf-8')
            self.ssh.send('write memory\n')
            time.sleep(2)
            output += self.ssh.recv(5000).decode('utf-8')
            own_logger.info(f'Configuration on {self.ip} saved.')
            return output if not silent else None
