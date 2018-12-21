import math
from operator import itemgetter
from catapult.modules.library import calculate_total_weight


class ServerNode:
    def __init__(self, host, capacity):
        self.host = host
        self.capacity = capacity
        self.next_node = None
        self.works = []

    def is_allow_weight(self, weight):
        if weight <= self.capacity:
            return True

        return False

    def minus_weight(self, weight):
        self.capacity -= weight

    def set_next(self, next_node):
        self.next_node = next_node

    def get_next(self):
        return self.next_node

    def get_host(self):
        return self.host

    def append_work(self, work):
        self.works.append(work)

    def get_works(self):
        return self.works


def get_circled_linked_list(servers, point):
    last_node = None
    first_node = None

    for server in servers:
        capacity = math.ceil(server["weight"] * point)

        if capacity < 3:
            capacity = 3

        node = ServerNode(server["host"], capacity)

        if not first_node:
            first_node = node

        if last_node:
            last_node.set_next(node)

        last_node = node

    last_node.set_next(first_node)

    return first_node


def fill_balancing_nodes(works, server_node):
    works = sorted(works, key=itemgetter('weight'), reverse=True)

    current_node = server_node

    for work in works:
        while True:
            if current_node.is_allow_weight(work['weight']):
                current_node.append_work(work)
                current_node.minus_weight(work['weight'])
                current_node = current_node.get_next()
                break

            current_node = current_node.get_next()


def get_balancing(server_node):
    balancing = {}

    current_node = server_node
    first_node_host = current_node.get_host()
    is_first_iteration = True
    while True:
        if first_node_host == current_node.get_host() and not is_first_iteration:
            break

        balancing[current_node.get_host()] = current_node.get_works()
        current_node = current_node.get_next()

        is_first_iteration = False

    return balancing


def balanced_by_host(elements, servers):
    balancing_weight = calculate_total_weight(elements)
    servers_weight = calculate_total_weight(servers)

    point = math.ceil(balancing_weight / float(servers_weight))

    server_node = get_circled_linked_list(servers, point)
    fill_balancing_nodes(elements, server_node)

    return get_balancing(server_node)
