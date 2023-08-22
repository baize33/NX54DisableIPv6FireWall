import re

import requests
import asyncio
import telnetlib3


async def telnet_login(host, port, password):
    reader, writer = await telnetlib3.open_connection(host, port)
    await asyncio.sleep(5)  # 使用异步sleep
    result = await reader.read(2000)
    if not result.strip(' ').endswith('<H3C_NX54>'):
        writer.write(password + '\n')  # 添加换行符
        await asyncio.sleep(1)  # 添加延迟
        result += await reader.read(2000)
    writer.write('debugshell\n')
    await asyncio.sleep(1)  # 添加延迟
    result += await reader.read(2000)
    cmd = "ip6tables -D FORWARD -j ACCEPT\nip6tables -I FORWARD -j ACCEPT\n"
    writer.write(cmd)
    await asyncio.sleep(1)  # 添加延迟
    result += await reader.read(2000)
    print("运行结果:")
    print(result)  # 解码结果

    await writer.drain()  # 确保所有数据都已发送
    writer.close()


def should_run(host, threshold):
    home_url = f"http://{host}/maintain_basic.asp?basicTab=1"
    pattern = r'runtime=" (\d+) 天 (\d+) 小时 (\d+) 分钟 (\d+) 秒 "'
    page = requests.get(home_url).text
    match = re.search(pattern, page)
    if match:
        days = int(match.group(1))
        hours = int(match.group(2))
        minutes = int(match.group(3))
        seconds = int(match.group(4))
        print(f"天: {days}, 小时: {hours}, 分钟: {minutes}, 秒: {seconds}")
        return minutes <= threshold
    else:
        print(page)
        return False


def main():
    # 服务器地址
    host = "192.168.124.1" 
    # 密码
    password = "(这里填密码)"
    # 最大分钟数，默认30分钟检测一次可自定义
    threshold = 30 
    #

    if not should_run(host, threshold):
        print(f"时间超过{threshold}min所以不运行")
        return
    print("时间到了, 运行一下")
    open_telnet_url = f"http://{host}/goform/aspForm?param=1&SET0=&CMD=Asp_SetTelnetDebug&GO=debug_status.asp&TCP_TIMEOUT_SYN_SENT_RCV=30&TCP_TIMEOUT_ESTABLISHED=1800&UDP_TIMEOUT=30&UDP_TIMEOUT_STREAM=160&ICMP_SEND_TIMEOUT=10&ACCEPT_SOURCE_ROUTE=0&NAT_TRANSFORM_MODE=1&CVMX_IPD=0&QOS_IP_BURST=0&QOS_IP_FIFO_LEN=256&IPQOS_CONGESTION=80&ACCEPT_INVALID_TCPACK=0&RMTELNETEN=0&HWNAT=0"
    requests.get(open_telnet_url)
    asyncio.run(telnet_login(host, port=15000, password=password))


if __name__ == "__main__":
    main()
