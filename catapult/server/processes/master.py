import tempfile
import logging
from time import sleep
from multiprocessing import Queue, Process, active_children
from catapult.server.processes.worker import worker
from catapult.server.processes.writer import writer
from catapult.server.processes.server import server
from catapult.server.library import get_ws_url
from catapult.server.killer import GracefulKiller, GracefulKillerException
from catapult.server.repository import Repository

processes = []


def master(config, services, deploy):
    sqlite_path = '{}/base.sqlite'.format(tempfile.mkdtemp())
    logging.info('use path "{}" for sqlite'.format(sqlite_path))

    deploy_queue = Queue()
    write_queue = Queue()

    repository = Repository(sqlite_path)
    repository.initialize()

    workers = config['server']['workers']
    ws_template = get_ws_url(
        config['server']['host'],
        config['server']['port']
    )

    logging.info('run {} deploy workers'.format(workers))
    for _ in range(0, workers):
        arguments = (
            deploy,
            deploy_queue,
            write_queue,
            ws_template
        )
        start_process(worker, arguments)

    logging.info('run writer process')
    start_process(writer, (
        repository,
        write_queue,
    ))

    logging.info('run server process')
    start_process(server, (
        config,
        services,
        repository,
        deploy_queue,
        write_queue,
    ))

    killer = GracefulKiller()

    try:
        while len(processes) > 0:
            for index, structure in enumerate(processes):
                process = structure['process']
                target = structure['target']

                if not process.is_alive():
                    logging.error('process "{}" dying, try ro restart'.format(target.__name__))
                    restart_process(index)

            sleep(1)

            if killer.is_killed:
                break
    except GracefulKillerException:
        logging.info('master process shutting down')

    active_children()


def start_process(target, arguments):
    process = Process(target=target, args=arguments)
    process.daemon = False
    process.start()

    processes.append({
        'process': process,
        'target': target,
        'arguments': arguments
    })


def restart_process(index):
    structure = processes[index]

    process = Process(
        target=structure['target'],
        args=structure['arguments']
    )
    process.daemon = False
    process.start()

    structure['process'] = process
