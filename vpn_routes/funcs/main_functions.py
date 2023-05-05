from cryptography.fernet import Fernet
from vpn_routes.funcs.nix_functions import work_with_script_folder
from getpass import getpass
import yaml
import os


def decrypt_password(key, encrypted_password):
    decryptor = Fernet(key)
    return decryptor.decrypt(encrypted_password).decode()


def encrypt_password(raw_password):
    key = Fernet.generate_key()
    encryptor = Fernet(key)
    encrypted_password = encryptor.encrypt(raw_password.encode())
    return key.decode(), encrypted_password.decode()


def get_remote_device_data(device={}):
    # Get known routers informations
    memory_file = work_with_script_folder() + '/known_routers.yaml'
    if os.path.exists(memory_file):
        with open(memory_file) as src:
            known_routers = yaml.safe_load(src)
    else:
        known_routers = {}

    if not device.get('ip'):
        ip = input('Не хватает параметра ip. Введите его: ')
        device['ip'] = ip

    if known_routers.get(ip):
        nexthop = known_routers[ip]['nexthop']
        user = known_routers[ip]['username']
        key = known_routers[ip]['key']
        password = decrypt_password(key, known_routers[ip]['password'])
        print(f'Для адреса {ip} есть сохраненные данные: '
              f'Пользователь {user}, nexthop {nexthop}.')
        choice = input('Хотите воспользоваться ими?[Y/n]: ').lower()
        if choice in ['', 'y']:
            device['username'] = user
            device['password'] = password
            return nexthop, device
    else:
        known_routers[ip] = {}
        username = input('Не хватает параметра username. Введите его: ')
        password = getpass('Не хватает параметра password. Введите его: ')
        nexthop = input('Не хватает адреса nexthop. Введите его: ')
        device['username'] = username
        device['password'] = password
        known_routers[ip]['username'] = username
        known_routers[ip]['nexthop'] = nexthop
        key, enc_pass = encrypt_password(password)
        known_routers[ip]['key'] = key
        known_routers[ip]['password'] = enc_pass
        with open(memory_file, 'w') as dst:
            yaml.safe_dump(known_routers, dst)
        return nexthop, device
