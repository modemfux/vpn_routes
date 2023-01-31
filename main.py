from funcs.classes import OwnSSH
from getpass import getpass


def main(nexthop='', device={}):
    device_params = ['ip', 'username', 'password']
    for param in device_params:
        if not device.get(param):
            if param == 'password':
                device[param] = getpass(f'Не хватает параметра {param}.'
                                        ' Введите его: ')
            else:
                device[param] = input(f'Не хватает параметра {param}.'
                                      ' Введите его: ')
    while not nexthop:
        nexthop = input('Не хватает адреса nexthop. Введите его: ')
    urls = input(
        'Введите необходимые URL'
        ' (если их несколько, то разделите запятой): '
    )
    url_list = [url.strip() for url in urls.split(',')]

    with OwnSSH(**device) as ssh:
        config = ssh.get_routes_from_urls(url_list, nexthop)
        ssh.upgrade_to_root()
        ssh.enter_to_vtysh()
        print(ssh.send_config_commands(config))
        print(ssh.write_config())
        ssh.exit_from_vtysh()
        ssh.exit_from_root()


if __name__ == '__main__':
    main()
