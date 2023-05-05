from vpn_routes.funcs.classes import OwnSSH
from vpn_routes.funcs.main_functions import get_remote_device_data


def main():
    nexthop, device = get_remote_device_data()
    urls = input(
        'Введите необходимые URL'
        ' (если их несколько, то разделите запятой): ')
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
