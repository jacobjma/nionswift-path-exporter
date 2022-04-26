import json
import os
from dataclasses import dataclass
from typing import Tuple

import dask.array as da
import h5py
import numpy as np
from hyperspy._signals.signal2d import Signal1D
from hyperspy._signals.signal2d import Signal2D


@dataclass
class DataItem:
    data: np.ndarray
    metadata: dict

    @property
    def is_lazy(self) -> bool:
        return isinstance(self.data, da.core.Array)

    def load_from_path(self, path: str, lazy, chunks=None):
        return load_data_item(path, lazy=lazy, chunks=chunks)


def load_data_item(path: str, lazy: bool = False, chunks=None) -> DataItem:
    ext = os.path.splitext(path)[-1]

    if ext.lower() in ('.ndata', '.npz'):
        pass
    elif ext.lower() in ('.h5', '.hdf5'):
        with h5py.File(path, "r") as f:
            data = f['data']
            metadata = json.loads(data.attrs['properties'])

            if lazy:
                if chunks is None:
                    chunks = data.chunks

                data = da.from_array(data, chunks=chunks)
            else:
                data = data[:]

    else:
        raise NotImplementedError()

    return DataItem(data, metadata)


_datum_count_to_hyperspy_signal_type = {1: Signal1D, 2: Signal2D}
_calibration_key_to_axis_key = {'units': 'units', 'offset': 'offset', 'scale': 'scale'}


def _dimensional_calibration_to_hyperspy_axis(dimensional_calibration: dict, size: int) -> dict:
    axis = {'size': size}
    for calibration_key, calibration_value in dimensional_calibration.items():
        axis[_calibration_key_to_axis_key[calibration_key]] = calibration_value
    return axis


def _dimensional_calibrations_to_hyperspy_axes(dimensional_calibrations: dict, data_shape: Tuple[int, ...]):
    axes = []
    for calibration, size in zip(dimensional_calibrations, data_shape):
        axes.append(_dimensional_calibration_to_hyperspy_axis(calibration, size))
    return axes


def hyperspy_signal_from_data_item(data_item: DataItem):
    signal_type = _datum_count_to_hyperspy_signal_type[data_item.metadata['datum_dimension_count']]
    axes = _dimensional_calibrations_to_hyperspy_axes(data_item.metadata['dimensional_calibrations'],
                                                      data_item.data.shape)

    signal = signal_type(data=data_item.data, axes=axes)

    if data_item.is_lazy:
        signal = signal.as_lazy()

    return signal


#_signal_type_to_measurement_type = {'ronchigram':}


def abtem_measurement_from_data_item(data_item: DataItem):
    pass


    # signal_type = _datum_count_to_hyperspy_signal_type[data_item.metadata['datum_dimension_count']]
