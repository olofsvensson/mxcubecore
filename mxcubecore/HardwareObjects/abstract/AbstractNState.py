#
#  Project: MXCuBE
#  https://github.com/mxcube.
#
#  This file is part of MXCuBE software.
#
#  MXCuBE is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Lesser General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  MXCuBE is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public License
#  along with MXCuBE.  If not, see <http://www.gnu.org/licenses/>.

"""
Defines the interface for N state devices
"""

import abc
from enum import Enum, unique
from HardwareRepository.HardwareObjects.abstract.AbstractActuator import (
    AbstractActuator,
)


__copyright__ = """ Copyright © 2020 by the MXCuBE collaboration """
__license__ = "LGPLv3+"


@unique
class InOutEnum(Enum):
    IN = "IN"
    OUT = "OUT"


@unique
class OpenCloseEnum(Enum):
    OPEN = "OPEN"
    CLOSE = "CLOSED"


@unique
class OnOffEnum(Enum):
    ON = "ON"
    OFF = "OFF"


class AbstractNState(AbstractActuator):
    """
    Abstract base class for N state objects.
    """

    __metaclass__ = abc.ABCMeta

    def __init__(self, name):
        AbstractActuator.__init__(self, name)
        self.predefined_values = {}
        self.username = None
        self.state_definition = None
        self._valid = False

    def init(self):
        """Initialise some parametrs."""
        self.predefined_values = self.get_predefined_values()
        self.username = self.getProperty("username")
        _valid = []
        try:
            self.state_definition = globals(self.getProperty("state_definition", None))
            _stl = len(self.state_definition.__members__)
            for value in self["predefined_value"]:
                if (
                    value.getProperty("name").upper()
                    in self.state_definition.__members__
                ):
                    _valid.append(True)
            if all(_valid) and len(_valid) == len(self.state_definition.__members__):
                self._valid = True

        except KeyError:
            pass

    def get_predefined_values(self):
        """Get the predefined values
        Returns:
            (dict): Dictionary of predefined {name: value}
        """
        predefined_values = {}
        for value in self["predefined_value"]:
            try:
                predefined_values.update(
                    {value.getProperty("name"): value.getProperty("value")}
                )
            except AttributeError:
                pass

        return predefined_values
