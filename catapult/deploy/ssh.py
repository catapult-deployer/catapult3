import paramiko
from catapult.library.exceptions import SshException


class Ssh:
    def __init__(self, user, key_file, hosts, logger):
        connections = {}
        for host in hosts:
            try:
                connection = paramiko.SSHClient()
                connection.set_missing_host_key_policy(paramiko.AutoAddPolicy())

                connection.connect(host, username=user, key_filename=key_file)

                connections[host] = connection
            except Exception as error:
                raise SshException(
                    'An error "{}" has occurred while establishing a connection to the server "{}"'.format(error, host)
                )

        self.connections = connections
        self.logger = logger

    def close(self):
        for host, connection in self.connections.items():
            try:
                connection.close()
            except Exception as error:
                raise SshException(
                    'An error "{}" has occurred while closing a connection with server "{}"'.format(error, host)
                )

    def execute_on_hosts(self, command):
        result = {}

        for host, connection in self.connections.items():
            result[host] = self.execute_on_host(host, command)

        return result

    def execute_on_host(self, host, command):
        try:
            connection = self.connections[host]

            stdin, stdout, stderr = connection.exec_command(command, get_pty=True)

            stdout_return_line = None
            for line in iter(stdout.readline, ''):
                # take only last line for return
                stdout_return_line = line.strip('\n\r')

                self.logger.success(stdout_return_line, host)

            for line in iter(stderr.readline, ''):
                self.logger.error(line.strip('\n\r'), host)

            if stdout.channel.recv_exit_status() != 0:
                raise SshException(
                    'An error has occurred while execution command "{}" on host "{}"'.format(command, host)
                )

            return stdout_return_line
        except Exception as error:
            raise SshException('Remote execution error "{}"'.format(error))

    def move_on_hosts(self, local_path, remote_path):
        for host, connection in self.connections.items():
            self.move_on_host(host, local_path, remote_path)

    def move_on_host(self, host, local_path, remote_path):
        try:
            connection = self.connections[host]

            sftp = connection.open_sftp()
            result = sftp.put(local_path, remote_path)

            self.logger.success(result, host)
        except Exception as error:
            self.logger.error(error, host)
