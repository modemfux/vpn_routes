import re
import subprocess
import os


def is_ip_address(ip):
    if not isinstance(ip, str):
        ip = str(ip)
    sp = ip.split('.')
    check_dict = {
        'four_octets': len(sp) == 4,
        'all_digits': all(map(lambda x: x.isdigit(), sp))
    }
    if check_dict['all_digits']:
        check_dict['correct_numbers'] = all(
            map(lambda x: int(x) in range(0, 256), sp)
        )
    else:
        check_dict['correct_numbers'] = False
    return all(check_dict.values())


def get_from_nix(command):
    result = subprocess.run(
        command,
        shell=True,
        stdout=subprocess.PIPE,
        encoding='utf-8'
    )
    return result.stdout.strip()


def get_from_windows(command):
    result = subprocess.run(
        command,
        shell=True,
        stdout=subprocess.PIPE,
        encoding='cp1251'
    ).stdout
    return result.encode().decode('utf-8').strip()


def get_a_record_from_server(url, server='8.8.8.8'):
    if not is_ip_address(server):
        raise TypeError(f"Incorrect server's IP: {server}")
    request_dict = {
        'dig': f'dig @{server} {url} +short',
        'nsl': f'nslookup -type=A {url} {server}'
    }
    if os.name == 'nt':
        reg_ip = r'((?:\d+[.]){3}\d+)'
        output = get_from_windows(request_dict['nsl'])
        ip_list = [ip.group(1) for ip in list(re.finditer(reg_ip, output))[1:]]
    elif os.name == 'posix':
        if get_from_nix('which dig'):
            output = get_from_nix(request_dict['dig'])
            ip_list = [ip for ip in output.split('\n')]
        else:
            reg_ip = r'Address: (\d+[.]\d+[.]\d+[.]\d+)'
            output = get_from_nix(request_dict['nsl'])
            ip_list = [ip.group(1) for ip in re.finditer(reg_ip, output)]
    return {url: ip_list}


def get_ip_addresses_from_url(url_list, server='8.8.8.8', full_result=False):
    if not is_ip_address(server):
        raise TypeError(f"Incorrect server's IP: {server}")
    if not isinstance(url_list, list):
        raise TypeError(f"Incorrect URLs list: {server}")
    result_dict = {}
    for url in url_list:
        result_dict.update(get_a_record_from_server(url, server))
    mid_list = []
    for ips in result_dict.values():
        mid_list += ips
    result = sorted(list(set(mid_list)))
    return result if not full_result else (result, result_dict)


def work_with_script_folder():
    os_type = os.name
    match os_type:
        case 'nt':
            home_dir = os.getenv('HOMEDRIVE') + os.getenv('HOMEPATH') + '\\'
        case 'posix':
            home_dir = os.getenv('HOME') + '/'
    if home_dir and os.path.exists(home_dir):
        routes_dir = home_dir + '.vpn_routes'
        if not os.path.exists(routes_dir):
            os.mkdir(routes_dir)
        return routes_dir
