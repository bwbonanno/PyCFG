from typing import List, Dict
from .node import Node


class EquivalenceClasses:
    """EquivalenceClasses represents groups of basic blocks that are
    interconnected. Control flow may transition from any block to any
    block within an equivalence class through one or more jumps.
    """

    def __init__(self):
        self._roots: List[int] = []
        self._nodes: List[Node] = []
        self._identifiers: Dict[any, int] = {}
        self._sizes = []
        self._count = 0

    def __contains__(self, identifier: any):
        return identifier in self._identifiers

    @property
    def count(self) -> int:
        """Number of unique equivalence classes currently tracked"""
        return self._count

    def _find_root(self, item_idx: int) -> int:
        """Get the root representing the equivalence class of an item

        Args:
            item_idx (int): The index representing the root of the item

        Returns:
            int: The integer representing the equivalence class of the item
        """
        current_item_idx = item_idx
        while current_item_idx != self._roots[current_item_idx]:
            self._roots[current_item_idx] = self._roots[
                self._roots[current_item_idx]
            ]
            current_item_idx = self._roots[current_item_idx]
        return current_item_idx

    def add(self, identifier: any):
        """Add identifier to a new equivalence class

        Args:
            identifier (any): Identifier to use to lookup the
            equivalence class of the item

        Raises:
            ValueError: If identifier is already tracked
            within the equivalence classes
        """
        if identifier in self._identifiers:
            raise ValueError("Item already exists within EquivalenceClasses")

        new_item_index = len(self._roots)
        self._roots.append(new_item_index)
        self._nodes.append(Node(identifier))
        self._sizes.append(1)
        self._identifiers[identifier] = new_item_index
        self._count += 1

    def find(self, identifier: any) -> int:
        """Get the equivalence class of the given identifier

        Args:
            identifier (any): Identifier previously added to
            the equivalence classes

        Returns:
            int: Number corresponding to the equivalence
            class of the identifier
        """
        return self._find_root(self._identifiers[identifier])

    def union(self, identifier_one: any, identifier_two: any):
        """Union the equivalence classes containing two items

        Args:
            identifier_one (any): Any identifier tracked by equivalence classes
            identifier_two (any): Any identifier tracked by equivalence classes

        Raises:
            ValueError: If either identifier passed has not been added
        """
        if (
            identifier_one not in self._identifiers
            or identifier_two not in self._identifiers
        ):
            raise ValueError(
                "Both union identifiers must already exist within"
                " an equivalence class"
            )
        item_one_idx = self._identifiers[identifier_one]
        item_two_idx = self._identifiers[identifier_two]
        root_one = self._find_root(item_one_idx)
        root_two = self._find_root(item_two_idx)

        if root_one == root_two:
            return

        if self._sizes[root_one] < self._sizes[root_two]:
            self._roots[root_one] = root_two
            self._sizes[root_two] += self._sizes[root_one]
        else:
            self._roots[root_two] = root_one
            self._sizes[root_one] += self._sizes[root_two]
        self._count -= 1

    def connect(self, source: any, destination: any):
        """Connect two identifiers, signifying valid transition from
        source to destination

        Args:
            source (any): Source of valid transition
            destination (any): Destination of valid transition

        Raises:
            ValueError: If either identifier passed has not been added
        """
        self.union(source, destination)
        source_node = self.get_node(source)
        destination_node = self.get_node(destination)
        source_node.destinations.add(destination_node)
        destination_node.sources.add(source_node)

    def get_node(self, identifier: any) -> Node:
        """Get CFG node

        Args:
            identifier (any): Identifier of node to get

        Raises:
            ValueError: If identifier is not tracked by EquivalenceClasses

        Returns:
            Node: CFG Node corresponding to the given identifier
        """
        if identifier not in self._identifiers:
            raise ValueError("Identifier not tracked by equivalence classes")
        return self._nodes[self._identifiers[identifier]]
