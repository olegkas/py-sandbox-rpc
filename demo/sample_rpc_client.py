import subprocess
from sandbox_rpc.client import rpc
from sandbox_rpc.common import RpcBaseException
import logging
import os

rpc.config(
    service="http://0.0.0.0:4321/rpc",
    keep_alive=True,
    return_stdout=True,
    return_stderr=True
)


fmt = "Host name is '{}'"


@rpc
def get_host_name():
    logging.info("std stream redirect test")
    print("std print redirect test")
    # sys.exit("Something is wrong, exiting!!!")
    # os.exit(100)

    with open("/etc/hosts") as f:
        print(f.read())

    hostname = subprocess.check_output("hostname", shell=False).decode()
    return fmt.format(hostname.strip())


@rpc
def get_etc_hosts():
    with open("/etc/hosts") as f:
        return f.read()


try:
    print(get_host_name())
    print(get_etc_hosts())
    # print(test_funcs.hello_world())
    # print(test_funcs.greeting("Morning", "Jim", "Johnson"))
    # print(test_funcs.execute("printenv"))
    # print(test_funcs.hello_f("Morning", "Jim", "Johnson"))
except RpcBaseException as e:
    e.print_traceback()
except Exception as e:
    logging.exception(e)



