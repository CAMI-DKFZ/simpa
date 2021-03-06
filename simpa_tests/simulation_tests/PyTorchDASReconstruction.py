# The MIT License (MIT)
#
# Copyright (c) 2021 Computer Assisted Medical Interventions Group, DKFZ
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated simpa_documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from simpa.utils import Tags, TISSUE_LIBRARY
import numpy as np
import matplotlib.pyplot as plt
from simpa.utils.settings_generator import Settings
from simpa.utils.dict_path_manager import generate_dict_path
from simpa.io_handling import load_data_field, load_hdf5
from simpa.core.simulation import simulate


class PyTorchDASReconstruction():

    def setUp(self):
        """
        This is not a completely autonomous simpa_tests case yet.
        If run on another pc, please adjust the SAVE_PATH, MCX_BINARY_PATH, ACOUSTIC_MODEL_BINARY_PATH, ACOUSTIC_MODEL_SCRIPT_LOCATION
        :return:
        """
        print("setUp")

        SAVE_PATH = "D:/save/"
        MCX_BINARY_PATH = "D:/bin/Release/mcx.exe"  # On Linux systems, the .exe at the end must be omitted.
        MATLAB_PATH = "C:/Program Files/MATLAB/R2020b/bin/matlab.exe"
        ACOUSTIC_MODEL_SCRIPT = "C:/simpa/simpa/core/acoustic_simulation"

        self.VOLUME_TRANSDUCER_DIM_IN_MM = 75
        self.VOLUME_PLANAR_DIM_IN_MM = 20
        self.VOLUME_HEIGHT_IN_MM = 25
        self.SPACING = 0.3 #15
        self.RANDOM_SEED = 4711
        np.random.seed(self.RANDOM_SEED)

        self.settings = {
            # These parameters set the general properties of the simulated volume
            Tags.RANDOM_SEED: self.RANDOM_SEED,
            Tags.VOLUME_NAME: "CompletePipelineTestMSOT_" + str(self.RANDOM_SEED),
            Tags.SIMULATION_PATH: SAVE_PATH,
            Tags.SPACING_MM: self.SPACING,
            Tags.DIM_VOLUME_Z_MM: self.VOLUME_HEIGHT_IN_MM,
            Tags.DIM_VOLUME_X_MM: self.VOLUME_TRANSDUCER_DIM_IN_MM,
            Tags.DIM_VOLUME_Y_MM: self.VOLUME_PLANAR_DIM_IN_MM,
            Tags.VOLUME_CREATOR: Tags.VOLUME_CREATOR_VERSATILE,
            Tags.SIMULATE_DEFORMED_LAYERS: True,

            # Simulation Device
            Tags.DIGITAL_DEVICE: Tags.DIGITAL_DEVICE_MSOT,

            # The following parameters set the optical forward model
            Tags.RUN_OPTICAL_MODEL: True,
            Tags.WAVELENGTHS: [700],
            Tags.OPTICAL_MODEL_NUMBER_PHOTONS: 1e7,
            Tags.OPTICAL_MODEL_BINARY_PATH: MCX_BINARY_PATH,
            Tags.OPTICAL_MODEL: Tags.OPTICAL_MODEL_MCX,
            Tags.ILLUMINATION_TYPE: Tags.ILLUMINATION_TYPE_MSOT_ACUITY_ECHO,
            Tags.LASER_PULSE_ENERGY_IN_MILLIJOULE: 50,

            # The following parameters tell the script that we do not want any extra
            # modelling steps
            Tags.RUN_ACOUSTIC_MODEL: True,
            Tags.ACOUSTIC_SIMULATION_3D: False,
            Tags.ACOUSTIC_MODEL: Tags.ACOUSTIC_MODEL_K_WAVE,
            Tags.ACOUSTIC_MODEL_BINARY_PATH: MATLAB_PATH,
            Tags.ACOUSTIC_MODEL_SCRIPT_LOCATION: ACOUSTIC_MODEL_SCRIPT,
            Tags.GPU: True,

            Tags.PROPERTY_ALPHA_POWER: 1.05,

            Tags.SENSOR_RECORD: "p",
            Tags.PMLInside: False,
            Tags.PMLSize: [31, 32],
            Tags.PMLAlpha: 1.5,
            Tags.PlotPML: False,
            Tags.RECORDMOVIE: False,
            Tags.MOVIENAME: "visualization_log",
            Tags.ACOUSTIC_LOG_SCALE: True,

            Tags.APPLY_NOISE_MODEL: False,
            Tags.SIMULATION_EXTRACT_FIELD_OF_VIEW: True,

            Tags.PERFORM_IMAGE_RECONSTRUCTION: True,
            Tags.RECONSTRUCTION_ALGORITHM: Tags.RECONSTRUCTION_ALGORITHM_PYTORCH_DAS,
            #Tags.TIME_REVEARSAL_SCRIPT_LOCATION: "C:/simpa/simpa/core/image_reconstruction/time_reversal_3D.m",
            Tags.RECONSTRUCTION_PERFORM_BANDPASS_FILTERING: False,
            Tags.TUKEY_WINDOW_ALPHA: 0.5,
            Tags.BANDPASS_CUTOFF_LOWPASS: int(8e6),
            Tags.BANDPASS_CUTOFF_HIGHPASS: int(0.1e6),
            #Tags.RECONSTRUCTION_BMODE_METHOD: Tags.RECONSTRUCTION_BMODE_METHOD_HILBERT_TRANSFORM,
            Tags.RECONSTRUCTION_APODIZATION_METHOD: Tags.RECONSTRUCTION_APODIZATION_BOX,
            Tags.RECONSTRUCTION_MODE: Tags.RECONSTRUCTION_MODE_DIFFERENTIAL
        }
        self.settings = Settings(self.settings)
        np.random.seed(self.RANDOM_SEED)

        self.settings[Tags.STRUCTURES] = self.create_example_tissue()

    def tearDown(self):
        print("tearDown")

    def test_reconstruction_of_simulation(self):
        print("Simulating ", self.RANDOM_SEED)
        import time
        timer = time.time()
        simulate(self.settings)
        print("Needed", time.time() - timer, "seconds")
        print("Simulating ", self.RANDOM_SEED, "[Done]")

        reconstructed_image_path = generate_dict_path(
            Tags.RECONSTRUCTED_DATA,
            wavelength=self.settings[Tags.WAVELENGTH])

        reconstructed_image = load_hdf5(
            self.settings[Tags.SIMPA_OUTPUT_PATH],
            reconstructed_image_path)[Tags.RECONSTRUCTED_DATA]

        initial_pressure = load_data_field(self.settings[Tags.SIMPA_OUTPUT_PATH], Tags.OPTICAL_MODEL_INITIAL_PRESSURE, wavelength=self.settings[Tags.WAVELENGTH])

        plt.subplot(1, 2, 1)
        plt.title("Reconstructed image")
        plt.imshow(np.log10(np.abs(reconstructed_image)))
        plt.subplot(1, 2, 2)
        plt.title("Initial pressure")
        plt.imshow(np.log10(initial_pressure))
        plt.show()

    def create_example_tissue(self):
        """
        This is a very simple example script of how to create a tissue definition.
        It contains a muscular background, an epidermis layer on top of the muscles
        and a blood vessel.
        """
        background_dictionary = Settings()
        background_dictionary[Tags.MOLECULE_COMPOSITION] = TISSUE_LIBRARY.muscle()
        background_dictionary[Tags.STRUCTURE_TYPE] = Tags.BACKGROUND

        muscle_dictionary = Settings()
        muscle_dictionary[Tags.PRIORITY] = 1
        muscle_dictionary[Tags.STRUCTURE_START_MM] = [0, 0, 0]
        muscle_dictionary[Tags.STRUCTURE_END_MM] = [0, 0, 100]
        muscle_dictionary[Tags.MOLECULE_COMPOSITION] = TISSUE_LIBRARY.muscle()
        muscle_dictionary[Tags.CONSIDER_PARTIAL_VOLUME] = True
        muscle_dictionary[Tags.ADHERE_TO_DEFORMATION] = True
        muscle_dictionary[Tags.STRUCTURE_TYPE] = Tags.HORIZONTAL_LAYER_STRUCTURE

        vessel_1_dictionary = Settings()
        vessel_1_dictionary[Tags.PRIORITY] = 3
        vessel_1_dictionary[Tags.STRUCTURE_START_MM] = [self.VOLUME_TRANSDUCER_DIM_IN_MM / 2,
                                                        0, 10]
        vessel_1_dictionary[Tags.STRUCTURE_END_MM] = [self.VOLUME_TRANSDUCER_DIM_IN_MM / 2,
                                                      self.VOLUME_PLANAR_DIM_IN_MM, 10]
        vessel_1_dictionary[Tags.STRUCTURE_RADIUS_MM] = 3
        vessel_1_dictionary[Tags.MOLECULE_COMPOSITION] = TISSUE_LIBRARY.blood_generic()
        vessel_1_dictionary[Tags.CONSIDER_PARTIAL_VOLUME] = True
        vessel_1_dictionary[Tags.STRUCTURE_TYPE] = Tags.CIRCULAR_TUBULAR_STRUCTURE

        vessel_2_dictionary = Settings()
        vessel_2_dictionary[Tags.PRIORITY] = 3
        vessel_2_dictionary[Tags.STRUCTURE_START_MM] = [self.VOLUME_TRANSDUCER_DIM_IN_MM / 2 + 12,
                                                        0, 7]
        vessel_2_dictionary[Tags.STRUCTURE_END_MM] = [self.VOLUME_TRANSDUCER_DIM_IN_MM / 2 + 10,
                                                      self.VOLUME_PLANAR_DIM_IN_MM, 5]
        vessel_2_dictionary[Tags.STRUCTURE_RADIUS_MM] = 3
        vessel_2_dictionary[Tags.STRUCTURE_ECCENTRICITY] = 0.9
        vessel_2_dictionary[Tags.MOLECULE_COMPOSITION] = TISSUE_LIBRARY.blood_generic()
        vessel_2_dictionary[Tags.CONSIDER_PARTIAL_VOLUME] = True
        vessel_2_dictionary[Tags.STRUCTURE_TYPE] = Tags.ELLIPTICAL_TUBULAR_STRUCTURE

        vessel_3_dictionary = Settings()
        vessel_3_dictionary[Tags.PRIORITY] = 3
        vessel_3_dictionary[Tags.STRUCTURE_START_MM] = [self.VOLUME_TRANSDUCER_DIM_IN_MM / 2 - 12,
                                                        0, 3]
        vessel_3_dictionary[Tags.STRUCTURE_X_EXTENT_MM] = 8
        vessel_3_dictionary[Tags.STRUCTURE_Y_EXTENT_MM] = 10
        vessel_3_dictionary[Tags.STRUCTURE_Z_EXTENT_MM] = 16
        vessel_3_dictionary[Tags.MOLECULE_COMPOSITION] = TISSUE_LIBRARY.blood_generic()
        vessel_3_dictionary[Tags.CONSIDER_PARTIAL_VOLUME] = True
        vessel_3_dictionary[Tags.STRUCTURE_TYPE] = Tags.RECTANGULAR_CUBOID_STRUCTURE

        tissue_dict = Settings()
        tissue_dict[Tags.BACKGROUND] = background_dictionary
        tissue_dict["muscle"] = muscle_dictionary
        tissue_dict["vessel_1"] = vessel_1_dictionary
        tissue_dict["vessel_2"] = vessel_2_dictionary
        tissue_dict["vessel_3"] = vessel_3_dictionary
        return tissue_dict


if __name__ == '__main__':
    test = PyTorchDASReconstruction()
    test.setUp()
    test.test_reconstruction_of_simulation()
