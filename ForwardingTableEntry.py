class ForwardingTableEntry:
    def __init__(self, distance, next_node):
        self.distance = distance
        self.next_node = next_node

    def __str__(self):
        return 'distance: ' + str(self.distance) + ', next_node: ' + str(self.next_node)
