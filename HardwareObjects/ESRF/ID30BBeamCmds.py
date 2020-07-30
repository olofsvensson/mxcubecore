from HardwareRepository.BaseHardwareObjects import HardwareObject
from HardwareRepository import HardwareRepository as HWR
from .BeamCmds import ControllerCommand, TestCommand, HWObjActuatorCommand


class ID30BBeamCmds(HardwareObject):
    def __init__(self, *args):
        HardwareObject.__init__(self, *args)

    def init(self):
        controller = self.getObjectByRole("controller")
        controller.detcover.set_in()
        self.centrebeam = ControllerCommand("Centre beam", controller.centrebeam)
        self.test_cmd = TestCommand("Test command")
        self.quick_realign = ControllerCommand(
           "Quick realign", controller.quick_realign
        )
        #self.hutchtrigger = HWObjActuatorCommand("Hutchtrigger", HWR.beamline.hutch_interlock)
        #self.anneal = ControllerCommand("Anneal", controller.anneal_procedure)

    def get_commands(self):
        return [self.centrebeam, self.quick_realign, self.test_cmd]
