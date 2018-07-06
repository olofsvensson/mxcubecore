from HardwareRepository.BaseHardwareObjects import HardwareObject
import types
import logging
import gevent

class BIOMAXPatches(HardwareObject):
    '''
    Hwobj for patching hwobj methods without inheriting classes.
    '''
    def before_load_sample(self):
        '''
        Ensure that the detector is in safe position and sample changer in SOAK
        '''
        if not self.sample_changer._chnPowered.getValue():
            raise RuntimeError('Cannot load sample, sample changer not powered')
        if not self.sc_in_soak():
            raise RuntimeError('Cannot load sample, sample changer not in SOAK position')
        self.curr_dtox_pos = self.dtox_hwobj.getPosition()
        if self.dtox_hwobj is not None and self.dtox_hwobj.getPosition() < self.safe_position:
            logging.getLogger("HWR").info("Moving detector to safe position before loading a sample.")
            logging.getLogger("user_level_log").info("Moving detector to safe position before loading a sample.")
            self.wait_motor_ready(self.dtox_hwobj)
            self.dtox_hwobj.syncMove(self.safe_position, timeout = 30)
            logging.getLogger("HWR").info("Detector in safe position, position: %s" %self.dtox_hwobj.getPosition())
            logging.getLogger("user_level_log").info("Detector in safe position, position: %s" %self.dtox_hwobj.getPosition())
        else:
            logging.getLogger("HWR").info("Detector already in safe position.")
            logging.getLogger("user_level_log").info("Detector already in safe position.")
        try:
            logging.getLogger("HWR").info("Waiting for Diffractometer to be ready before proceeding with the sample loading.")
            self.diffractometer.wait_device_ready(15)
        except Exception as ex:
            logging.getLogger("HWR").warning("Diffractometer not ready. Proceeding with the sample loading, good luck...")

    def after_load_sample(self):
        '''
        Move to centring after loading the sample
        '''
        if self.diffractometer is not None and self.diffractometer.get_current_phase() != 'Centring':
            logging.getLogger("HWR").info("Changing diffractometer phase to Centring")
            logging.getLogger("user_level_log").info("Changing diffractometer phase to Centring")
            try:
                self.diffractometer.wait_device_ready(15)
            except:
                pass
            self.diffractometer.set_phase('Centring')
            logging.getLogger("HWR").info("Diffractometer phase changed, current phase: %s" %self.diffractometer.get_current_phase())
        else:
            logging.getLogger("HWR").info("Diffractometer already in Centring")
            logging.getLogger("user_level_log").info("Diffractometer already in Centring")
        logging.getLogger("HWR").info("Moving detector to pre-mount position %s" %self.curr_dtox_pos)
        self.dtox_hwobj.syncMove(self.curr_dtox_pos, timeout = 30)


    def new_load(self, *args, **kwargs):
        logging.getLogger("HWR").info("Sample changer in SOAK position: %s" %self.sc_in_soak())
        self.before_load_sample()
        self.__load(args[1])
        self.after_load_sample()

    def new_unload(self, *args, **kwargs):
        logging.getLogger("HWR").info("Sample changer in SOAK position: %s" %self.sc_in_soak())
        self.before_load_sample()
        self.__unload(args[1])
        #self.after_load_sample()

    def wait_motor_ready(self, mot_hwobj, timeout=30):
        with gevent.Timeout(timeout, RuntimeError('Motor not ready')):
            while mot_hwobj.is_moving():
                gevent.sleep(0.5)

    def sc_in_soak(self):
        return self.sample_changer._chnInSoak.getValue()

    def init(self, *args):
        self.sample_changer = self.getObjectByRole('sample_changer')
        self.diffractometer = self.getObjectByRole('diffractometer')
        self.__load = self.sample_changer.load
        self.__unload = self.sample_changer.unload
        self.curr_dtox_pos = None
        self.dtox_hwobj = self.getObjectByRole('dtox')
      
        self.sample_changer.load = types.MethodType(self.new_load, self.sample_changer)
        self.sample_changer.unload = types.MethodType(self.new_unload, self.sample_changer)
