from mxcubecore.BaseHardwareObjects import HardwareObject
from mxcubecore.HardwareObjects.abstract.AbstractMultiCollect import (
    AbstractMultiCollect,
)
from mxcubecore.HardwareObjects.ESRF.ESRFMultiCollect import ESRFMultiCollect

from mxcubecore import HardwareRepository as HWR

from mxcubecore.TaskUtils import task
import logging
import time
import os
import gevent
import shutil
import pprint
import jsonpickle

from functools import reduce

class MultiCollectMockup(ESRFMultiCollect, HardwareObject):
    def __init__(self, name):
        ESRFMultiCollect.__init__(self, name)
        HardwareObject.__init__(self, name)
        self._centring_status = None
        self.ready_event = None
        self.actual_frame_num = 0
        self.template = "/scisoft/pxsoft/data/WORKFLOW_TEST_DATA/id30a1/20141114/RAW_DATA/6-1-2/opid30a1_1_%04d.cbf"
        self._max_number_of_frames = 10000
        self._last_image_saved = 1


    def get_reference_image(self, image_path, template, run_number, image_no):
        reference_image = None
        if "insu_3_11" in image_path:
            referenceDirectory = "/scisoft/pxsoft/data/WORKFLOW_TEST_DATA/id23eh2/20181208/RAW_DATA/Sample-1-1-03"
            if  template.startswith("mesh-"):
                reference_image = os.path.join(referenceDirectory, "MeshScan_02/mesh-insu_3_0_%04d.cbf" % image_no)
            else:
                batchNo = template[10:12]
                reference_image = os.path.join(referenceDirectory, "insu_3_%s_1_%04d.cbf" % (batchNo, image_no))
        elif "insu_5_20" in image_path:
            referenceDirectory = "/data/id23eh2/inhouse/opid232/20181208/RAW_DATA/Sample-1-1-05"
            if  template.startswith("mesh-"):
                referenceDirectory = "/scisoft/pxsoft/data/WORKFLOW_TEST_DATA/id23eh2/20181208/RAW_DATA/Sample-1-1-03"
                reference_image = os.path.join(referenceDirectory, "MeshScan_02/mesh-insu_3_0_%04d.cbf" % image_no)
            else:
                batchNo = template[10:12]
                reference_image = os.path.join(referenceDirectory, "insu_5_%s_1_%04d.cbf" % (batchNo, image_no))
        elif "BurnStrategy" in image_path:
            time.sleep(0.5)
            if  template.startswith("ref-"):
                #                reference_image = "/data/id23eh1/inhouse/mxihr6/20150121/RAW_DATA/Guillaume/Cer/BurnStrategy_01/ref-x_1_%04d.cbf" % image_no
                reference_image = "/scisoft/pxsoft/data/AUTO_PROCESSING/id30a3/20151123/RAW_DATA/test6/BurnStrategy_02/ref-test_1_%04d.cbf" % image_no
            #                reference_image = "/data/id23eh1/inhouse/opid231/20170530/RAW_DATA/wftest2/BurnStrategy_01/ref-opid231_1_%04d.cbf" % image_no
            elif  template.startswith("burn-"):
                wedgeNumber = int(template.split("_")[-3].split("w")[-1])
                #                reference_image = "/data/id23eh1/inhouse/mxihr6/20150121/RAW_DATA/Guillaume/Cer/BurnStrategy_01/burn-xw%d_1_%04d.cbf" % (wedgeNumber, image_no)
                reference_image = "/scisoft/pxsoft/data/AUTO_PROCESSING/id30a3/20151123/RAW_DATA/test6/BurnStrategy_02/burn-testw%d_1_%04d.cbf" % (wedgeNumber, image_no)
            #                reference_image = "/data/id23eh1/inhouse/opid231/20170530/RAW_DATA/wftest2/BurnStrategy_01/burn-opid231w%d_1_%04d.cbf" % (wedgeNumber, image_no)
        # elif template.startswith("line-"):
        #     new_run_number = 2 + ((run_number-1) % 3)
        #     reference_image = "/scisoft/pxsoft/data/WORKFLOW_TEST_DATA/id30a1/20141114/RAW_DATA/6-1-2/MXPressE_02/line-opid30a1_%d_%04d.cbf" % (new_run_number, image_no)
        elif template.startswith("line-") or template.startswith("mesh-"):
            #                    reference_image = "/scisoft/pxsoft/data/WORKFLOW_TEST_DATA/id30a1/20141003/RAW_DATA/MXPressE_01/mesh-MARK2-m1010713a_1_%04d.cbf" % image_no
            line_image_no = (image_no - 1) % 72 + 1
            reference_image = "/scisoft/pxsoft/data/WORKFLOW_TEST_DATA/id30a1/20141114/RAW_DATA/6-1-2/MXPressE_02/mesh-opid30a1_1_%04d.cbf" % line_image_no
        elif  template.startswith("ref-"):
            #reference_image = "/data/id30a1/inhouse/opid30a1/20141114/RAW_DATA/opid30a1/6-1-2/MXPressE_02/ref-opid30a1_4_%04d.cbf" % image_no
            reference_image = "/scisoft/pxsoft/data/WORKFLOW_TEST_DATA/id30a1/20141114/RAW_DATA/6-1-2/MXPressE_02/ref-opid30a1_4_%04d.cbf" % image_no
        else:
            #reference_image = "/data/id30a1/inhouse/opid30a1/20141114/RAW_DATA/opid30a1/6-1-2/opid30a1_1_%04d.cbf" % image_no
            #reference_image = "/scisoft/pxsoft/data/AUTO_PROCESSING/id29/20150501/RAW_DATA/max/cz/CN082A/vial6/peak1/vial6_peak1_w1_1_%04d.cbf" % image_no
            #reference_image = "/scisoft/pxsoft/data/AUTO_PROCESSING/TEST-C2-P321/1/RAW_DATA/2nd_2nd_w1_1_%04d.cbf" % image_no
            #reference_image = "/data/id29/inhouse/opid291/20160331/RAW_DATA/P1_HP/xtal7_puck5/xtal7_puck5_w1_1_%04d.cbf" % image_no
            #reference_image = "/scisoft/pxsoft/data/AUTO_PROCESSING/id30a1/20160829/ins/ins-samp16/ins-samp16_1_%04d.cbf" % image_no
            #reference_image = "/scisoft/pxsoft/data/AUTO_PROCESSING/id23eh2/20180903/sapask_14/sapaSK_hel_2_%04d.cbf" % image_no
            #reference_image = "/data/id23eh2/inhouse/opid232/20181017/RAW_DATA/Sample-8-1-05/local-user_w1_1_%04d.cbf" % image_no
            reference_image = self.template % image_no
        return reference_image


    def execute_command(self, command_name, *args, **kwargs):
        return

    # def init(self):
    #     self.setControlObjects(
    #         diffractometer=self.get_object_by_role("diffractometer"),
    #         sample_changer=self.get_object_by_role("sample_changer"),
    #         lims=self.get_object_by_role("dbserver"),
    #         safety_shutter=self.get_object_by_role("safety_shutter"),
    #         machine_current=self.get_object_by_role("machine_current"),
    #         cryo_stream=self.get_object_by_role("cryo_stream"),
    #         energy=self.get_object_by_role("energy"),
    #         resolution=self.get_object_by_role("resolution"),
    #         detector_distance=self.get_object_by_role("detector_distance"),
    #         transmission=self.get_object_by_role("transmission"),
    #         undulators=self.get_object_by_role("undulators"),
    #         flux=self.get_object_by_role("flux"),
    #         detector=self.get_object_by_role("detector"),
    #         beam_info=self.get_object_by_role("beam_info"),
    #     )
    #     self.emit("collectConnected", (True,))
    #     self.emit("collectReady", (True,))

    # @task
    # def loop(self, owner, data_collect_parameters_list):
    #     self.collection_id = "12345"
    #     failed_msg = "Data collection failed!"
    #     failed = True
    #     collections_analyse_params = []
    #     self.emit("collectReady", (False,))
    #     self.emit("collectStarted", (owner, 1))
    #
    #     for data_collect_parameters in data_collect_parameters_list:
    #
    #         # database filling
    #         if HWR.beamline.lims:
    #             data_collect_parameters["collection_start_time"] = time.strftime(
    #                 "%Y-%m-%d %H:%M:%S"
    #             )
    #             # if HWR.beamline.machine_info is not None:
    #             #     logging.getLogger("user_level_log").info(
    #             #         "Getting synchrotron filling mode"
    #             #     )
    #             #     data_collect_parameters[
    #             #         "synchrotronMode"
    #             #     ] = self.get_machine_fill_mode()
    #             data_collect_parameters["status"] = "failed"
    #
    #             logging.getLogger("user_level_log").info("Storing data collection in LIMS")
    #             (self.collection_id, detector_id) = HWR.beamline.lims.store_data_collection(
    #                 data_collect_parameters, self.bl_config
    #             )
    #
    #             data_collect_parameters["collection_id"] = self.collection_id
    #             logging.getLogger("user_level_log").info("collection_id: {0}".format(self.collection_id))
    #             logging.getLogger("user_level_log").info("detector_id: {0}".format(detector_id))
    #
    #             if detector_id:
    #                 data_collect_parameters["detector_id"] = detector_id
    #
    #         data_collect_parameters["status"] = "Running"
    #         logging.debug("collect parameters = %r", data_collect_parameters)
    #         fileinfo = data_collect_parameters["fileinfo"]
    #         fileinfo["suffix"] = "cbf"
    #         template = (
    #                 "%(prefix)s_%(run_number)s_%%04d.%(suffix)s" % fileinfo
    #         )
    #         logging.getLogger("HWR").info("*"*80)
    #         logging.getLogger("HWR").info("template: {0}".format(template))
    #         logging.getLogger("HWR").info("*"*80)
    #         directory = fileinfo["directory"]
    #         if not os.path.exists(directory):
    #             os.makedirs(directory, 0o755)
    #         run_number = int(fileinfo["run_number"])
    #         for oscillation_parameters in data_collect_parameters["oscillation_sequence"]:
    #             number_of_images = oscillation_parameters["number_of_images"]
    #             start_image_number = oscillation_parameters["start_image_number"]
    #             failed = False
    #             (
    #                 osc_id,
    #                 sample_id,
    #                 sample_code,
    #                 sample_location,
    #             ) = self.update_oscillations_history(data_collect_parameters)
    #             self.emit(
    #                 "collectOscillationStarted",
    #                 (
    #                     owner,
    #                     sample_id,
    #                     sample_code,
    #                     sample_location,
    #                     data_collect_parameters,
    #                     osc_id,
    #                 ),
    #             )
    #
    #             for image in range(number_of_images):
    #                 time.sleep(
    #                     data_collect_parameters["oscillation_sequence"][0]["exposure_time"]
    #                 )
    #                 image_no = image + start_image_number
    #                 image_path = os.path.join(directory, template % image_no)
    #                 reference_image = self.get_reference_image(image_path, template, run_number, image_no)
    #                 shutil.copyfile(reference_image, image_path)
    #                 self.emit("collectImageTaken", image)
    #
    #             frame = 1
    #             filename = template % frame
    #             file_location = directory
    #             file_path = os.path.join(file_location, filename)
    #             jpeg_filename = "%s.jpeg" % os.path.splitext(template)[0]
    #             thumb_filename = "%s.thumb.jpeg" % os.path.splitext(template)[0]
    #             archive_directory = self.get_archive_directory(directory)
    #             jpeg_file_template = os.path.join(archive_directory, jpeg_filename)
    #             jpeg_thumbnail_file_template = os.path.join(
    #                 archive_directory, thumb_filename
    #             )
    #             try:
    #                 jpeg_full_path = jpeg_file_template % frame
    #                 jpeg_thumbnail_full_path = (
    #                         jpeg_thumbnail_file_template % frame
    #                 )
    #             except Exception:
    #                 jpeg_full_path = None
    #                 jpeg_thumbnail_full_path = None
    #             logging.getLogger("HWR").info("file_path: {0}".format(file_path))
    #             logging.getLogger("HWR").info("jpeg_full_path: {0}".format(jpeg_full_path))
    #             logging.getLogger("HWR").info("jpeg_thumbnail_full_path: {0}".format(jpeg_thumbnail_full_path))
    #
    #             self.generate_image_jpeg(
    #                 str(file_path),
    #                 str(jpeg_full_path),
    #                 str(jpeg_thumbnail_full_path),
    #                 wait=False,
    #             )
    #
    #         data_collect_parameters["status"] = "Data collection successful"
    #         self.emit(
    #             "collectOscillationFinished",
    #             (
    #                 owner,
    #                 True,
    #                 data_collect_parameters["status"],
    #                 self.collection_id,
    #                 osc_id,
    #                 data_collect_parameters,
    #             ),
    #         )
    #         if HWR.beamline.lims:
    #             try:
    #                 logging.getLogger("user_level_log").info(
    #                     "Updating data collection in LIMS"
    #                 )
    #                 # if "kappa" in data_collect_parameters["actualCenteringPosition"]:
    #                 #     data_collect_parameters["oscillation_sequence"][0][
    #                 #         "kappaStart"
    #                 #     ] = current_diffractometer_position["kappa"]
    #                 #     data_collect_parameters["oscillation_sequence"][0][
    #                 #         "phiStart"
    #                 #     ] = current_diffractometer_position["kappa_phi"]
    #                 HWR.beamline.lims.update_data_collection(data_collect_parameters)
    #             except Exception:
    #                 logging.getLogger("HWR").exception(
    #                     "Could not update data collection in LIMS"
    #                 )
    #
    #     self.emit(
    #         "collectEnded",
    #         owner,
    #         not failed,
    #         failed_msg if failed else "Data collection successful",
    #     )
    #     logging.getLogger("HWR").info("data collection successful in loop")
    #     self.emit("collectReady", (True,))

    @task
    def take_crystal_snapshots(self, number_of_snapshots):
        self.bl_control.diffractometer.take_snapshots(number_of_snapshots, wait=True)

    @task
    def data_collection_hook(self, data_collect_parameters):
        data_collect_parameters["shutterless"] = True
        oscillation_parameters = data_collect_parameters["oscillation_sequence"][0]
        if oscillation_parameters["number_of_images"] > self._max_number_of_frames:
            oscillation_parameters["number_of_images"] = self._max_number_of_frames
        ESRFMultiCollect.data_collection_hook(self, data_collect_parameters)
        self._data_collect_parameters = data_collect_parameters
        return

    def do_prepare_oscillation(self, frame_start, osc_range, exptime, wedge_size,
                               shutterless, npass, j):
        return frame_start, frame_start + osc_range

    @task
    def oscil(self, start, end, exptime, npass):
        return

    @task
    def data_collection_cleanup(self):
        return

    @task
    def close_fast_shutter(self):
        return

    @task
    def open_fast_shutter(self):
        return

    @task
    def move_motors(self, motor_position_dict):
        return

    @task
    def open_safety_shutter(self):
        return

    def safety_shutter_opened(self):
        return

    @task
    def close_safety_shutter(self):
        return

    @task
    def prepare_intensity_monitors(self):
        return

    def prepare_acquisition(
        self, take_dark, start, osc_range, exptime, npass, number_of_images, comment=""
    ):
        return

    def set_detector_filenames(
        self, frame_number, start, filename, jpeg_full_path, jpeg_thumbnail_full_path
    ):
        return

    def prepare_oscillation(
            self,
            start,
            osc_range,
            exptime,
            number_of_images,
            shutterless,
            npass,
            first_frame,
        ):
        return (start, start + osc_range)

    def do_oscillation(self, start, end, exptime, shutterless, npass, first_frame, is_wedgesize):
        pass

    def last_image_saved(self):
        return self._last_image_saved

    def update_data_collection_in_lims(self):
        """
        Descript. :
        """
        self._data_collect_parameters["flux"] = self._flux
        self._data_collect_parameters["flux_end"] = self._flux
        # self._data_collect_parameters["totalAbsorbedDose"] = self.get_total_absorbed_dose()
        self._data_collect_parameters["wavelength"] = self._wavelength
        self._data_collect_parameters[
            "detectorDistance"
        ] = self._detector_distance
        # self._data_collect_parameters["resolution"] = self.get_resolution()
        self._data_collect_parameters["transmission"] = self.beamline_setup_read("/beamline/transmission")
        self._data_collect_parameters["xBeam"] = self._beam_centre_x
        self._data_collect_parameters["yBeam"] = self._beam_centre_y
        # self._data_collect_parameters[
        #     "resolutionAtCorner"
        # ] = self.get_resolution_at_corner()
        beam_size_x, beam_size_y = self.get_beam_size()
        aperture = HWR.beamline.beam.get_value()[-1]
        self._data_collect_parameters["beamSizeAtSampleX"] = int(aperture) / 1000.0
        self._data_collect_parameters["beamSizeAtSampleY"] = int(aperture) / 1000.0
        # self._data_collect_parameters["beamShape"] = self.get_beam_shape()
        # hor_gap, vert_gap = self.get_slit_gaps()
        # self._data_collect_parameters["slitGapHorizontal"] = hor_gap
        # self._data_collect_parameters["slitGapVertical"] = vert_gap
        try:
            HWR.beamline.lims.update_data_collection(
                self._data_collect_parameters
            )
        except BaseException:
            logging.getLogger("HWR").exception(
                "Could not update data collection in LIMS"
            )

    def _getattr_from_path(self, obj, attr, delim="/"):
        """Recurses through an attribute chain to get the attribute."""
        return reduce(getattr, attr.split(delim), obj)

    def beamline_setup_read(self, path):
        value = None

        if path.strip("/").endswith("default-acquisition-parameters"):
            value = jsonpickle.encode(self.get_default_acquisition_parameters())
        elif path.strip("/").endswith("default-path-template"):
            value = jsonpickle.encode(self.get_default_path_template())
        else:
            try:
                path = path[1:] if path[0] == "/" else path
                ho = self._getattr_from_path(HWR, path)
                value = ho.get_value()
            except:
                logging.getLogger("HWR").exception("Could no get %s " % str(path))

        return value

    def start_acquisition(self, exptime, npass, first_frame, shutterless):
        logging.getLogger("user_level_log").info("Simulated acquisition started")
        self.emit("collectReady", (False,))
        self.emit("collectStarted", (None, 1))
        fileinfo = self._data_collect_parameters["fileinfo"]
        template = fileinfo["template"]
        directory = fileinfo["directory"]
        run_number = int(fileinfo["run_number"])
        first_frame = True
        image_no = None
        for oscillation_parameters in self._data_collect_parameters["oscillation_sequence"]:
            number_of_images = oscillation_parameters["number_of_images"]
            start_image_number = oscillation_parameters["start_image_number"]
            logging.getLogger("user_level_log").info("number_of_images : {0}".format(number_of_images))
            for index in range(number_of_images):
                image_no = index + start_image_number
                image_path = os.path.join(directory, template % image_no)
                reference_image = self.get_reference_image(image_path, template, run_number, image_no)
                if first_frame:
                    dictHeader = self.readHeaderPilatus(reference_image)
                    self.update_beamline_config(dictHeader)
                    first_frame = False
                if not "noimage" in template:
                    if not os.path.exists(directory):
                        os.makedirs(directory, 0o755)
                    shutil.copyfile(reference_image, image_path)
                    # time.sleep(0.2)
                if image_no % 10:
                    self.emit("collectImageTaken", image_no)
                    logging.getLogger("user_level_log").info("Simulating collection of image: %s", image_path)
            self.emit("collectImageTaken", image_no)
            self._last_image_saved = image_no
            self.write_image(True)
        self.update_data_collection_in_lims()


    def readHeaderPilatus(self, _strImageFileName):
        """
        Returns an dictionary with the contents of a Pilatus CBF image header.
        """
        dictPilatus = None
        imageFile = open(_strImageFileName, "rb")
        imageFile.seek(0, 0)
        bContinue = True
        iMax = 60
        iIndex = 0
        while bContinue:
            strLine = imageFile.readline().decode('utf-8')
            iIndex += 1
            if (strLine.find("_array_data.header_contents") != -1):
                dictPilatus = {}
            if (strLine.find("_array_data.data") != -1) or iIndex > iMax:
                bContinue = False
            if (dictPilatus != None) and (strLine[0] == "#"):
                # Check for date
                strTmp = strLine[2:].replace("\r\n", "")
                if strLine[6] == "/" and strLine[10] == "/":
                    dictPilatus["DateTime"] = strTmp
                else:
                    strKey = strTmp.split(" ")[0]
                    strValue = strTmp.replace(strKey, "")[1:]
                    dictPilatus[strKey] = strValue
        imageFile.close()
        return dictPilatus

    def update_beamline_config(self, dictHeader):
        # Beam centre
        listBeamXY = dictHeader["Beam_xy"].replace("(", "").replace(")",",").split(",")
        self._beam_centre_x = float(listBeamXY[0])*0.172
        self._beam_centre_y = float(listBeamXY[1])*0.172
        # Angle_increment (125833144)    str: 0.1500 deg.
        self._osc_range = float(dictHeader["Angle_increment"].split(" ")[0])
        # Flux
        self._flux = float(dictHeader["Flux"].split(" ")[0])
        # Wavelength
        self._wavelength = float(dictHeader["Wavelength"].split(" ")[0])
        # Detector distance
        self._detector_distance = float(dictHeader["Detector_distance"].split(" ")[0])*1000.0
        # Detector
        detector_fileext = "cbf"
        detector_manufacturer = "DECTRIS"
        detector_type = "pilatus"
        if dictHeader["Detector:"] == "PILATUS 6M, S/N 60-0116-F, ESRF ID23":
            detector_model = "Pilatus_6M_F"
            self._detector_px = 2463
            self._detector_py = 2527
        elif dictHeader["Detector:"] == "PILATUS 6M, S/N 60-0104, ESRF ID29":
            detector_model = "Pilatus_6M_F"
            self._detector_px = 2463
            self._detector_py = 2527
        elif dictHeader["Detector:"] == "PILATUS3 6M, S/N 60-0128, ESRF ID29":
            detector_model = "Pilatus3_6M"
            self._detector_px = 2463
            self._detector_py = 2527
        elif dictHeader["Detector:"] == "PILATUS3 2M, S/N 24-0118, ESRF ID30" or \
                dictHeader["Detector:"] == "PILATUS3 2M, S/N 24-0118, ESRF ID23":
            detector_model = "Pilatus3_2M"
            self._detector_px = 1475
            self._detector_py = 1679
        else:
            # Unknown detector...
            raise
            return


        # self.setBeamlineConfiguration(
        #     synchrotron_name="ESRF",
        #     directory_prefix = self.getProperty("directory_prefix"),
        #     default_exposure_time = self.getProperty("default_exposure_time"),
        #     minimum_exposure_time = self.getProperty("minimum_exposure_time"),
        #     detector_fileext = detector_fileext,
        #     detector_type = detector_type,
        #     detector_manufacturer = detector_manufacturer,
        #     detector_model = detector_model,
        #     detector_px = self._detector_px,
        #     detector_py = self._detector_py,
        #     undulators = None,
        #     focusing_optic = self.getProperty('focusing_optic'),
        #     monochromator_type = self.getProperty('monochromator'),
        #     beam_divergence_vertical = self.getProperty('beam_divergence_vertical'),
        #     beam_divergence_horizontal = self.getProperty('beam_divergence_horizontal'),
        #     polarisation = self.getProperty('polarisation'),
        #     #maximum_phi_speed=self.getProperty('maximum_phi_speed'),
        #     #minimum_phi_oscillation=self.getProperty('minimum_phi_oscillation'),
        #     input_files_server = self.getProperty("input_files_server")
        # )

    def write_image(self, last_frame):
        self.actual_frame_num += 1
        return

    def stop_acquisition(self):
        return

    def reset_detector(self):
        return

    # def prepare_input_files(
    #     self, files_directory, prefix, run_number, process_directory
    # ):
    #     self.actual_frame_num = 0
    #     i = 1
    #     while True:
    #         xds_input_file_dirname = "xds_%s_run%s_%d" % (prefix, run_number, i)
    #         xds_directory = os.path.join(process_directory, xds_input_file_dirname)
    #
    #         if not os.path.exists(xds_directory):
    #             break
    #
    #         i += 1
    #
    #     mosflm_input_file_dirname = "mosflm_%s_run%s_%d" % (prefix, run_number, i)
    #     mosflm_directory = os.path.join(process_directory, mosflm_input_file_dirname)
    #
    #     hkl2000_dirname = "hkl2000_%s_run%s_%d" % (prefix, run_number, i)
    #     hkl2000_directory = os.path.join(process_directory, hkl2000_dirname)
    #
    #     self.raw_data_input_file_dir = os.path.join(
    #         files_directory, "process", xds_input_file_dirname
    #     )
    #     self.mosflm_raw_data_input_file_dir = os.path.join(
    #         files_directory, "process", mosflm_input_file_dirname
    #     )
    #     self.raw_hkl2000_dir = os.path.join(files_directory, "process", hkl2000_dirname)
    #
    #     return xds_directory, mosflm_directory, hkl2000_directory

    # @task
    # def write_input_files(self, collection_id):
    #     return

    # def get_wavelength(self):
    #     return

    def get_undulators_gaps(self):
        return []

    def get_resolution_at_corner(self):
        return

    def get_beam_size(self):
        return None, None

    def get_slit_gaps(self):
        return None, None

    def get_beam_shape(self):
        return

    def get_machine_current(self):
        if self.bl_control.machine_current is not None:
            return self.bl_control.machine_current.getCurrent()
        else:
            return 0

    def get_machine_message(self):
        if self.bl_control.machine_current is not None:
            return self.bl_control.machine_current.getMessage()
        else:
            return ""

    def get_machine_fill_mode(self):
        if self.bl_control.machine_current is not None:
            return self.bl_control.machine_current.getFillMode()
        else:
            ""

    def get_cryo_temperature(self):
        if self.bl_control.cryo_stream is not None:
            return self.bl_control.cryo_stream.getTemperature()

    def get_current_energy(self):
        return

    def get_beam_centre(self):
        return None, None

    def get_beamline_configuration(self, *args):
        return self.bl_config._asdict()

    def is_connected(self):
        return True

    def is_ready(self):
        return True

    def sample_changer_HO(self):
        return self.bl_control.sample_changer

    def diffractometer(self):
        return self.bl_control.diffractometer

    def sanity_check(self, collect_params):
        return

    def set_brick(self, brick):
        return

    def directory_prefix(self):
        return self.bl_config.directory_prefix

    # def store_image_in_lims(self, frame, first_frame, last_frame):
    #     return True

    def get_oscillation(self, oscillation_id):
        return self.oscillations_history[oscillation_id - 1]

    def sample_accept_centring(self, accepted, centring_status):
        self.sample_centring_done(accepted, centring_status)

    def set_centring_status(self, centring_status):
        self._centring_status = centring_status

    def get_oscillations(self, session_id):
        return []

    def set_helical(self, helical_on):
        return

    def set_helical_pos(self, helical_oscil_pos):
        return

    # def get_archive_directory(self, directory):
    #     archive_dir = os.path.join(directory, "archive")
    #     return archive_dir

    # @task
    # def generate_image_jpeg(self, filename, jpeg_path, jpeg_thumbnail_path):
    #     pass
