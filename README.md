## VPN Routes

Used to add new static routes to FRR installed on VPS via establishing SSH connection.

### CodeClimate Maintainability
[![Maintainability](https://api.codeclimate.com/v1/badges/28d1e9241153acdaa00d/maintainability)](https://codeclimate.com/github/modemfux/vpn_routes/maintainability)

#### Usage example
```
08:42 $ make main
poetry run python -m vpn_routes.main
Не хватает параметра ip. Введите его: 192.0.2.10
Для адреса 195.2.93.231 есть сохраненные данные: Пользователь modemfux, nexthop 192.0.2.1.
Хотите воспользоваться ими?[Y/n]: n
Не хватает параметра username. Введите его: modemfux
Не хватает параметра password. Введите его:
Не хватает адреса nexthop. Введите его: 192.0.2.1
Введите необходимые URL (если их несколько, то разделите запятой): rutracker.org
Connection to 192.0.2.10 established.
configure term
sample-srv01(config)# ip route 104.21.72.173 255.255.255.255 192.0.2.1 tag 65001
sample-srv01(config)# ip route 172.67.187.38 255.255.255.255 192.0.2.1 tag 65001
sample-srv01(config)# end
sample-srv01#

sample-srv01# end
sample-srv01# write memory
Note: this version of vtysh never writes vtysh.conf
Building Configuration...
Integrated configuration saved to /etc/frr/frr.conf
[OK]
amst-mfuxx-srv01#
SSH connection to 192.0.2.10 is closed.
```
