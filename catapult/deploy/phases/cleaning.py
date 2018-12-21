from os import system


def phase(paths, storage, _, __, ssh, logger):
    command_template = 'ls -1t {releases_path}' \
                       ' | tail -n +{keep_releases}' \
                       " | sed 's#/##' |" \
                       ' xargs -I ! rm -rf {releases_path}/!'

    keep_releases = int(storage.get('config.deploy.keep_releases')) + 1

    remote_command = command_template.format(
        releases_path=paths.get('remote.releases_folder'),
        keep_releases=keep_releases,
    )

    ssh.execute_on_hosts(remote_command)

    local_command = command_template.format(
        releases_path=paths.get('local.releases_folder'),
        keep_releases=keep_releases,
    )

    system(local_command)

    logger.success('old releases removed')

