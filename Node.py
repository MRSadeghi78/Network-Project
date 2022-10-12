import _thread
import socket
import threading
import time
from ForwardingTableEntry import ForwardingTableEntry
from Neighbor import Neighbor


print_lock = threading.Lock()


def safe_print(*a, **b):
    """Thread safe print function"""
    with print_lock:
        print(*a, **b)


def print_forwarding_table(forwarding_table):
    safe_print('{')
    for i in forwarding_table:
        safe_print('\tnode', i, '->', forwarding_table[i])
    safe_print('}')


def send_command(connection, command):
    connection.send(command.encode('ascii'))


def receive_command(connection, source_node, neighbor_node):
    while True:
        command = connection.recv(1024)
        command_str = command.decode('ascii')
        command_lines = command_str.splitlines()
        if command_lines[0] == 'update forwarding table':
            source_node.update_forwarding_table(neighbor_node)
        elif command_lines[0] == 'add node':
            source_node.add_node_to_forwarding_table(int(command_lines[1]))
        elif command_lines[0] == 'reset forwarding table':
            source_node.reset_forwarding_table()
        elif command_lines[0] == 'delete node':
            source_node.delete_node(int(command_lines[1]))


class Node:
    def __init__(self, node_number):
        super().__init__()
        self.number = node_number
        self.neighbors = {}
        self.forwarding_table = {node_number: ForwardingTableEntry(0, None)}
        # self.forwarding_table_lock = threading.Lock()

    def __str__(self):
        return str(self.number)

    def tell_neighbors_forwarding_table_is_changed(self):
        command = 'update forwarding table'
        for neighbor_number in self.neighbors:
            _thread.start_new_thread(send_command, (self.neighbors[neighbor_number].connection, command,))

    def update_forwarding_table(self, changed_neighbor):
        forwarding_table_is_changed = False
        for node in self.forwarding_table:
            new_distance = self.neighbors[changed_neighbor.number].link_cost + changed_neighbor.forwarding_table[node].distance
            if new_distance < self.forwarding_table[node].distance:
                self.forwarding_table[node].next_node = changed_neighbor.number
                self.forwarding_table[node].distance = new_distance
                forwarding_table_is_changed = True
        if forwarding_table_is_changed:
            self.tell_neighbors_forwarding_table_is_changed()

    def add_node_to_forwarding_table(self, new_node_number):
        if new_node_number not in self.forwarding_table:
            self.forwarding_table[new_node_number] = ForwardingTableEntry(float('inf'), None)
            command = 'add node\n' + str(new_node_number) + '\n'
            for neighbor_number in self.neighbors:
                _thread.start_new_thread(send_command, (self.neighbors[neighbor_number].connection, command,))

    def add_neighbor_request_socket(self, new_neighbor, link_cost):
        soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        port = int(str(self.number) + str(new_neighbor.number))
        port_dest = int(str(new_neighbor.number) + str(self.number))
        soc.bind(('localhost', port))
        soc.connect(('localhost', port_dest))
        self.neighbors[new_neighbor.number] = Neighbor(link_cost, soc)
        _thread.start_new_thread(receive_command, (soc, self, new_neighbor,))
        for node_number in list(new_neighbor.forwarding_table):
            self.add_node_to_forwarding_table(node_number)
        while True:
            all_nodes_added_to_neighbor = True
            for node_number in self.forwarding_table:
                if node_number not in new_neighbor.forwarding_table:
                    all_nodes_added_to_neighbor = False
                    time.sleep(0.1)
                    break
            if all_nodes_added_to_neighbor:
                break
        self.update_forwarding_table(new_neighbor)

    def add_neighbor_accept_socket(self, new_neighbor, link_cost):
        soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        port = int(str(self.number) + str(new_neighbor.number))
        soc.bind(('localhost', port))
        soc.listen(10)
        connection, address = soc.accept()
        self.neighbors[new_neighbor.number] = Neighbor(link_cost, connection)
        _thread.start_new_thread(receive_command, (connection, self, new_neighbor,))
        for node_number in list(new_neighbor.forwarding_table):
            self.add_node_to_forwarding_table(node_number)
        while True:
            all_nodes_added_to_neighbor = True
            for node_number in self.forwarding_table:
                if node_number not in new_neighbor.forwarding_table:
                    all_nodes_added_to_neighbor = False
                    time.sleep(0.1)
                    break
            if all_nodes_added_to_neighbor:
                break
        self.update_forwarding_table(new_neighbor)

    def reset_forwarding_table(self):
        forwarding_table_already_reset = True
        for node in self.forwarding_table:
            if self.forwarding_table[node].distance != float('inf'):
                self.forwarding_table[node].next_node = None
                self.forwarding_table[node].distance = float('inf')
                forwarding_table_already_reset = False
        self.forwarding_table[self.number].distance = 0
        return forwarding_table_already_reset

    def edit_link_cost(self, neighbor, new_link_cost):
        self.neighbors[neighbor.number].link_cost = new_link_cost
        forwarding_table_already_reset = self.reset_forwarding_table()
        if not forwarding_table_already_reset:
            command = 'reset forwarding table\n'
            for neighbor_number in self.neighbors:
                _thread.start_new_thread(send_command, (self.neighbors[neighbor_number].connection, command,))
        self.update_forwarding_table(neighbor)

    def delete_node(self, node_number):
        if node_number in self.forwarding_table:
            del self.forwarding_table[node_number]
            if node_number in self.neighbors:
                self.neighbors[node_number].link_cost = float('inf')
            command = 'delete node\n' + str(node_number) + '\n'
            for neighbor_number in self.neighbors:
                _thread.start_new_thread(send_command, (self.neighbors[neighbor_number].connection, command,))
