from ippai.simulate import Tags
from ippai.simulate.volume_creator import create_simulation_volume
from ippai.simulate.models.optical_model import run_optical_forward_model
from ippai.simulate.models.acoustic_model import run_acoustic_forward_model
import numpy as np


def simulate(settings):

    if settings[Tags.RANDOM_SEED] is not None:
        np.random.seed(settings[Tags.RANDOM_SEED])
    else:
        np.random.seed()

    volume_path = create_simulation_volume(settings)

    optical_path = None
    acoustic_path = None

    if settings[Tags.RUN_OPTICAL_MODEL]:
        optical_path = run_optical_forward_model(settings, volume_path)

    if settings[Tags.RUN_ACOUSTIC_MODEL]:
        acoustic_path = run_acoustic_forward_model(settings, optical_path)

    return [volume_path, optical_path, acoustic_path]
