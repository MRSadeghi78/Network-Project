import _thread

from Node import Node


def accept_connection_link(node1, node2, link_cost):
    node1.add_neighbor_accept_socket(node2, link_cost)


def edit_link(node1, node2, link_cost):
    node1.edit_link_cost(node2, link_cost)


def print_forwarding_table(forwarding_table):
    print('{')
    for i in forwarding_table:
        print('\tnode', i, '->', forwarding_table[i])
    print('}')


def Main():
    nodes = {}
    while True:
        command = input('\nEnter your command:\n')
        if command == 'add node':
            node_number = int(input('Enter node number: '))
            nodes[node_number] = Node(node_number)
            print('node', node_number, 'added.')
        elif command == 'add link':
            first_node = int(input('Enter first node: '))
            second_node = int(input('Enter second node: '))
            link_cost = int(input('Enter link cost: '))
            _thread.start_new_thread(accept_connection_link, (nodes[first_node], nodes[second_node], link_cost,))
            nodes[second_node].add_neighbor_request_socket(nodes[first_node], link_cost)
        elif command == 'edit link':
            first_node = int(input('Enter first node: '))
            second_node = int(input('Enter second node: '))
            link_cost = int(input('Enter link cost: '))
            _thread.start_new_thread(edit_link, (nodes[first_node], nodes[second_node], link_cost, ))
            nodes[second_node].edit_link_cost(nodes[first_node], link_cost)
        elif command == 'del node':
            removing_node = int(input('Enter node number: '))
            nodes[removing_node].delete_node(removing_node)
            # del nodes[removing_node]
        elif command == 'del link':
            first_node = int(input('Enter first node: '))
            second_node = int(input('Enter second node: '))
            link_cost = float('inf')
            _thread.start_new_thread(edit_link, (nodes[first_node], nodes[second_node], link_cost,))
            nodes[second_node].edit_link_cost(nodes[first_node], link_cost)
        elif command == 'print ft':  # print forwarding table
            node_number = int(input('Enter node number: '))
            for neighbor in nodes[node_number].neighbors:
                nodes[node_number].update_forwarding_table(nodes[neighbor])
            print_forwarding_table(nodes[node_number].forwarding_table)
        elif command == 'update fts':  # update all forwarding tables
            for node in nodes:
                for neighbor in nodes[node].neighbors:
                    nodes[node].update_forwarding_table(nodes[neighbor])
        elif command == 'print path':
            source_node = int(input('Enter source node: '))
            destination_node = int(input('Enter destination node: '))
            print(source_node, end=' ')
            current_node = nodes[source_node]
            while current_node.forwarding_table[destination_node].next_node is not None:
                current_node = nodes[current_node.forwarding_table[destination_node].next_node]
                print('->', current_node.number, end=' ')
        elif command == 'quit':
            break


if __name__ == '__main__':
    Main()
