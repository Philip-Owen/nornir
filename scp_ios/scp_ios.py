from nornir import InitNornir
from nornir.plugins.functions.text import print_result, print_title
from nornir.plugins.tasks.networking import netmiko_send_command, netmiko_file_transfer, netmiko_send_config

def scp_file(task):
    f_name = task.host.get('img')
    return task.run(task=netmiko_file_transfer, source_file=f_name, dest_file=f_name, direction='put')

def check_file_exists(task):
    img = task.host.get('img')
    return task.run(task=netmiko_send_command, command_string=f'dir flash:/{img}')

def set_boot_var(task):
    img = task.host.get('img')
    cmd = f'default boot system,boot system flash:{img}'
    cmd_list = cmd.split(',')
    return task.run(task=netmiko_send_config, config_commands=cmd_list)

def send_simple_cmd(task, cmd):
    return task.run(task=netmiko_send_command, use_timing=True,command_string=cmd)

def reload(task):
    send_simple_cmd(task, 'wr')
    send_simple_cmd(task, 'reload')
    send_simple_cmd(task, '\n')
    return ''

def main():
    nr = InitNornir(config_file="config.yml")
    ios = nr.inventory.groups['cisco-ios']['img']

    # Task: SCP file to device
    print_title(f'Sending {ios} via SCP')
    output = nr.run(scp_file)
    print_result(output)

    # Task: Check that file was installed 
    print_title(f'Verifying {ios} was installed')
    output = nr.run(check_file_exists)
    print_result(output)

    # Task: Set boot variable to new ios img
    print_title('Setting boot variable')
    output = nr.run(set_boot_var)
    print_result(output)

    # Task: Reload devices to install new img
    print_title('Reloading devices')
    output = nr.run(reload)
    print_result(output)

    print('Reloading...')

if __name__ == "__main__":
    main()


