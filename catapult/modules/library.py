from random import shuffle
from catapult.modules.constants import BOT_MIRRORING, BOT_BALANCING


def calculate_total_weight(items):
    weight = 0
    for item in items:
        weight += item["weight"]

    return weight


def get_balancing_demons(demons):
    balancing = []
    for demon in demons:
        if demon['type'] != BOT_BALANCING:
            continue

        for _id in range(0, demon['instances']):
            copiend = demon.copy()
            copiend['name'] = '{}-{}'.format(copiend['name'], _id)

            balancing.append(copiend)

    shuffle(balancing)

    return balancing


def get_mirroring_demons(demons):
    mirroring = []
    for demon in demons:
        if demon['type'] != BOT_MIRRORING:
            continue

        mirroring.append(demon)

    return mirroring


def get_balancing_applications(applications):
    balancing = []
    for application in applications:
        if application['type'] != BOT_BALANCING:
            continue

        balancing.append(application)

    shuffle(balancing)

    return balancing


def get_mirroring_applications(applications):
    mirroring = []
    for application in applications:
        if application['type'] != BOT_MIRRORING:
            continue

        mirroring.append(application)

    return mirroring


def get_applications_by_type(applications, server_type):
    result = []
    for application in applications:
        if application['server'] != server_type:
            continue

        result.append(application)

    return result
