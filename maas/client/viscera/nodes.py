"""Objects for nodes."""

__all__ = [
    "Node",
    "Nodes",
]

from collections import Sequence

from . import (
    check,
    Object,
    ObjectField,
    ObjectFieldRelated,
    ObjectFieldRelatedSet,
    ObjectSet,
    ObjectType,
    to,
)
from ..enum import NodeType


class NodesType(ObjectType):
    """Metaclass for `Nodes`."""

    async def read(cls):
        data = await cls._handler.read()
        return cls(map(cls._object, data))


class Nodes(ObjectSet, metaclass=NodesType):
    """The set of nodes stored in MAAS."""


class NodeTypeMeta(ObjectType):
    """Metaclass for `Node`."""

    async def read(cls, system_id):
        data = await cls._handler.read(system_id=system_id)
        return cls(data)


class Node(Object, metaclass=NodeTypeMeta):
    """A node stored in MAAS."""

    # domain

    fqdn = ObjectField.Checked(
        "fqdn", check(str), readonly=True)
    hostname = ObjectField.Checked(
        "hostname", check(str), check(str))
    interfaces = ObjectFieldRelatedSet("interface_set", "Interfaces")
    ip_addresses = ObjectField.Checked(  # List[str]
        "ip_addresses", check(Sequence), readonly=True)
    node_type = ObjectField.Checked(
        "node_type", to(NodeType), readonly=True)
    owner = ObjectFieldRelated("owner", "User")
    system_id = ObjectField.Checked(
        "system_id", check(str), readonly=True, pk=True)
    tags = ObjectField.Checked(  # List[str]
        "tag_names", check(Sequence), readonly=True)
    zone = ObjectFieldRelated("zone", "Zone")

    def __repr__(self):
        return super(Node, self).__repr__(
            fields={"system_id", "hostname"})

    def as_machine(self):
        """Convert to a `Machine` object.

        `node_type` must be `NodeType.MACHINE`.
        """
        from .machines import Machine
        if self.node_type != NodeType.MACHINE:
            raise ValueError(
                'Cannot convert to `Machine`, node_type is not a machine.')
        return Machine(self._data)

    def as_device(self):
        """Convert to a `Device` object.

        `node_type` must be `NodeType.DEVICE`.
        """
        from .devices import Device
        if self.node_type != NodeType.DEVICE:
            raise ValueError(
                'Cannot convert to `Device`, node_type is not a device.')
        return Device(self._data)

    def as_rack_controller(self):
        """Convert to a `RackController` object.

        `node_type` must be `NodeType.RACK_CONTROLLER` or
        `NodeType.REGION_AND_RACK_CONTROLLER`.
        """
        from .controllers import RackController
        if self.node_type not in [
                NodeType.RACK_CONTROLLER, NodeType.REGION_AND_RACK_CONTROLLER]:
            raise ValueError(
                'Cannot convert to `RackController`, node_type is not a '
                'rack controller.')
        return RackController(self._data)

    def as_region_controller(self):
        """Convert to a `RegionController` object.

        `node_type` must be `NodeType.REGION_CONTROLLER` or
        `NodeType.REGION_AND_RACK_CONTROLLER`.
        """
        from .controllers import RegionController
        if self.node_type not in [
                NodeType.REGION_CONTROLLER,
                NodeType.REGION_AND_RACK_CONTROLLER]:
            raise ValueError(
                'Cannot convert to `RegionController`, node_type is not a '
                'region controller.')
        return RegionController(self._data)
