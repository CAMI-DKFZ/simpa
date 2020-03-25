import numpy as np
import subprocess
from ippai.simulate import Tags
from utils.serialization import IPPAISerializer
import json
import os
import scipy.io as sio


def simulate(settings, optical_path):

    data_dict = dict()
    tmp_opt_data = np.load(optical_path)
    for key in tmp_opt_data.keys():
        data_dict[key] = tmp_opt_data[key]

    if Tags.PERFORM_UPSAMPLING in settings:
        if settings[Tags.PERFORM_UPSAMPLING]:
            tmp_ac_data = np.load(os.path.join(settings[Tags.SIMULATION_PATH], settings[Tags.VOLUME_NAME],
                                               "upsampled_properties_" + str(settings[Tags.WAVELENGTH]) + "nm.npz"))
        else:
            tmp_ac_data = np.load(os.path.join(settings[Tags.SIMULATION_PATH], settings[Tags.VOLUME_NAME],
                                               "properties_" + str(settings[Tags.WAVELENGTH]) + "nm.npz"))
    else:
        tmp_ac_data = np.load(os.path.join(settings[Tags.SIMULATION_PATH], settings[Tags.VOLUME_NAME],
                                           "properties_" + str(settings[Tags.WAVELENGTH]) + "nm.npz"))

    data_dict["sos"] = np.rot90(tmp_ac_data["sos"], 3)
    data_dict["density"] = np.rot90(tmp_ac_data["density"], 3)
    data_dict["alpha_coeff"] = np.rot90(tmp_ac_data["alpha_coeff"], 3)
    data_dict["sensor_mask"] = np.rot90(tmp_ac_data["sensor_mask"], 3)
    try:
        data_dict["directivity_angle"] = np.rot90(tmp_ac_data["directivity_angle"], 3)
    except ValueError:
        print("No directivity_angle specified")
    except KeyError:
        print("No directivity_angle specified")

    # plt.imshow(data_dict["sos"])
    # plt.show()

    pre, ext = os.path.splitext(optical_path)
    optical_path = pre + ".mat"
    sio.savemat(optical_path, data_dict)

    tmp_output_file = settings[Tags.SIMULATION_PATH] + "/" + settings[Tags.VOLUME_NAME] + "_output.npy"
    settings["output_file"] = tmp_output_file

    tmp_json_filename = settings[Tags.SIMULATION_PATH] + "/" + settings[Tags.VOLUME_NAME] + "/test_settings.json"
    with open(tmp_json_filename, "w") as json_file:
        serializer = IPPAISerializer()
        json.dump(settings, json_file, indent="\t", default=serializer.default)

    cmd = list()
    cmd.append(settings[Tags.ACOUSTIC_MODEL_BINARY_PATH])
    cmd.append("-nodisplay")
    cmd.append("-nosplash")
    cmd.append("-r")
    cmd.append("addpath('"+settings[Tags.ACOUSTIC_MODEL_SCRIPT_LOCATION]+"');" +
               settings[Tags.ACOUSTIC_MODEL_SCRIPT] + "('" + tmp_json_filename +
               "', '" + optical_path + "');exit;")
    cur_dir = os.getcwd()
    os.chdir(settings[Tags.SIMULATION_PATH])

    subprocess.run(cmd)

    raw_time_series_data = np.load(tmp_output_file)
    settings["dt_acoustic_sim"] = float(sio.loadmat(tmp_output_file + ".mat", variable_names="time_step")["time_step"])

    os.remove(optical_path)
    os.remove(tmp_output_file)
    os.remove(tmp_output_file + ".mat")
    os.chdir(cur_dir)

    return raw_time_series_data


