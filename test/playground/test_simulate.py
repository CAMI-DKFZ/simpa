# FIXME: Include actual proper tests here!

from ippai.simulate import Tags
from ippai.simulate.simulation import simulate
from ippai.simulate.tissue_properties import get_muscle_settings
from ippai.simulate.structures import create_forearm_structures

import matplotlib.pylab as plt
import numpy as np

random_seed = 1742
np.random.seed(random_seed)
relative_shift = (np.random.random() - 0.5) * 2 * 12.5
background_oxy = (np.random.random() * 0.6) + 0.2
print(relative_shift)

settings = {
    Tags.WAVELENGTHS: [800], #np.arange(700, 951, 10),
    Tags.RANDOM_SEED: random_seed,
    Tags.VOLUME_NAME: "Forearm_"+str(random_seed).zfill(6),
    Tags.SIMULATION_PATH: "/home/janek/simulation_test/",
    Tags.RUN_OPTICAL_MODEL: True,
    Tags.OPTICAL_MODEL_NUMBER_PHOTONS: 1000000,
    Tags.OPTICAL_MODEL_BINARY_PATH: "/home/janek/mitk-superbuild/MITK-build/bin/MitkMCxyz",
    Tags.OPTICAL_MODEL_PROBE_XML_FILE: "/home/janek/CAMI_PAT_SETUP_V2.xml",
    Tags.RUN_ACOUSTIC_MODEL: False,
    'background_properties': get_muscle_settings(),
    Tags.SPACING_MM: 0.6,
    Tags.DIM_VOLUME_Z_MM: 20,
    Tags.DIM_VOLUME_X_MM: 40,
    Tags.DIM_VOLUME_Y_MM: 30,
    Tags.AIR_LAYER_HEIGHT_MM: 12,
    Tags.STRUCTURES: create_forearm_structures(relative_shift_mm=relative_shift, background_oxy=background_oxy)
}

paths = simulate(settings)
data = np.load(paths[0][0])
extent = [0, settings[Tags.DIM_VOLUME_X_MM], settings[Tags.DIM_VOLUME_Z_MM], 0]
air_height = int(settings[Tags.AIR_LAYER_HEIGHT_MM] / settings[Tags.SPACING_MM])
plt.subplot(221)
plt.imshow(np.rot90(data['mua'][10, :, air_height:], -1), extent=extent, vmin=0, vmax=.5)
plt.subplot(222)
plt.imshow(np.rot90(data['mus'][10, :, air_height:], -1), extent=extent)
plt.subplot(223)
plt.imshow(np.rot90(data['oxy'][10, :, air_height:], -1), extent=extent)
plt.subplot(224)
plt.imshow(np.rot90(data['seg'][10, :, air_height:], -1), extent=extent)
plt.show()
plt.close()

data = np.load(paths[0][1])
extent = [0, settings[Tags.DIM_VOLUME_X_MM], settings[Tags.DIM_VOLUME_Z_MM], 0]
air_height = int(settings[Tags.AIR_LAYER_HEIGHT_MM] / settings[Tags.SPACING_MM])
plt.subplot(221)
plt.imshow(np.rot90(data['mua'][10, :, air_height:], -1), extent=extent, vmin=0, vmax=.5)
plt.subplot(222)
plt.imshow(np.rot90(data['mus'][10, :, air_height:], -1), extent=extent)
plt.subplot(223)
plt.imshow(np.rot90(data['oxy'][10, :, air_height:], -1), extent=extent)
plt.subplot(224)
plt.imshow(np.rot90(data['seg'][10, :, air_height:], -1), extent=extent)
plt.show()
plt.close()