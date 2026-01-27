
__all__ = [
    "Simulator",
    "SimulationSaver"
]


from typing import Callable
import h5py
import os
import numpy as np
import jaxlib
from typing import Union

from .node import Node
from .variable import Variable
from .system import System
from .agenda import Agenda


class Simulator:

    """A simulator.

    Arguments
    system -- A system.
    agenda -- An agenda for handling events.
    """

    def __init__(self, system : System, agenda : Agenda = Agenda()):
        assert (hasattr(system, "clock") and
                hasattr(system.clock, "t")), \
                "I need a clock to run a simulation with events."
        self._system = system
        self._agenda = agenda

    @property
    def system(self) -> System:
        return self._system

    @property
    def agenda(self) -> Agenda:
        return self._agenda

    def add_event(self, time : float, event : Callable):
        self.agenda.add(time, event)

    def forward(self):
        """Simulate one timestep."""
        while (not self.agenda.empty() and
            self.system.clock.t.value >= self.agenda.current_time):
            self.agenda.forward()
        self.system.forward()

    def transition(self):
        self.system.transition()


class SimulationSaver(object):
    """A class that offers data saving functionality for a single
    simulation.

    Arguments:
    file_or_group   -- The file or group to use. If this is a string, we
                       are assuming that it is referring to a file to be
                       created. If the file exists already an exception
                       will be thrown. If the file does not exist
                       already, it will be created and the data will be
                       written in the root ("/") group. Otherwise, this
                       must be a group of an already opened HDF5 file.
                       Then the data will be written on that group.
                       The group can contain other datasets and
                       attributes. However, it cannot contain attributes
                       and datasets that are to be tracked by system.
    system          -- The system to keep track of. To track a node
                       set its `track` flag to `True`.
    max_steps       -- The maximum number of simulation steps. Default
                       is 1000.

    """

    def __init__(
        self,
        file_or_group : Union[str, h5py.Group],
        system : System,
        max_steps : int = 10000,
        overwrite: bool=False,
    ):
        if isinstance(file_or_group, str):
            file = os.path.abspath(file_or_group)
            if os.path.exists(file) and overwrite:
                os.remove(file)
            else:
                assert not os.path.exists(file), f"File '{file}' already exists!"

            file_handler = h5py.File(file, "w")
            group = file_handler["/"]
        else:
            group = file_or_group
            assert isinstance(group, h5py.Group), \
                f"{group} is not an h5py.Group of an already openned file!"
            file_handler = None
        self._file_handler = file_handler
        self._group = group
        self._max_steps = max_steps
        self._tracked_nodes = []
        self._count = 0
        self._create_h5_structure(group, system)

    def _create_h5_structure(
        self,
        group : h5py.Group,
        system_or_node : Union[System, Node]
    ):
        """Creates the necessary tables to save the system or the node."""
        if isinstance(system_or_node, System):
            system = system_or_node
            sg = group.create_group(system.name)
            sg.attrs["description"] = system.description
            for n in system.direct_nodes:
                self._create_h5_structure(sg, n)
        else:
            node = system_or_node
            if (not isinstance(node, Variable)) or (not node.track):
                return
            node_type = type(node.value)
            if node_type == int:
                dtype = "i"
                shape = ()
            elif node_type == float:
                dtype = "f"
                shape = ()
            elif node_type == np.ndarray:
                dtype = node.value.dtype
                shape = node.value.shape
            elif isinstance(node.value, (np.integer, np.inexact)):
                dtype = node.value.dtype
                shape = node.value.shape
            elif node_type == jaxlib.xla_extension.DeviceArray:
                dtype = node.value.dtype
                shape = node.value.shape
            else:
                raise ValueError(f"Node {node.name} has an uninitialized value."
                    + " Please specify a value so that I can figure out"
                    + " the type of the variable I need to store.")
            maxshape = (self.max_steps,) + shape
            # Create the dataset
            dst = group.create_dataset(
                node.name,
                shape=maxshape,
                dtype=dtype
            )
            # Add some metadata to the dataset
            dst.attrs["units"] = node.units if node.units is not None else ""
            dst.attrs["description"] = (
                node.description if node.description is not None else ""
            )
            self.tracked_nodes.append(node)

    @property
    def max_steps(self):
        """Get the maximu number of steps that can be saved."""
        return self._max_steps
    
    @property
    def tracked_nodes(self):
        """Get the tracked nodes."""
        return self._tracked_nodes

    @property
    def file_handler(self):
        """Get the HDF5 filehandler (if there is one)."""
        return self._file_handler

    @property
    def group(self):
        """Get the HDF5 group on which we are writing the data."""
        return self._group

    def _save_node(self, node : Variable):
        """Save the current state of the system to the file.

        This a recursive function. The data are saved at index `count`.
        """
        if self.file_handler is None:
            dset = self.group[node.absname]
            dset[self._count] = node.value
        else:
            dset = self.file_handler[node.absname]
            dset[self._count] = node.value

    def save(self):
        """Save the current state of the system to the file."""
        for n in self.tracked_nodes:
            self._save_node(n)
        self._count += 1
