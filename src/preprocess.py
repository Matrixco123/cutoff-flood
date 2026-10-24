"""
The ONE radar preprocessing function for the whole project.

Training images (Sen1Floods11) and Assam images (Earth Engine) must both pass
through `preprocess_sar` before reaching the model. If the two are processed
differently, the model fails silently on Assam. Do not write a second version
of this anywhere else.
"""

import numpy as np

from .config import VV_RANGE, VH_RANGE, LABEL_IGNORE


def preprocess_sar(img):
    """
    Prepare a Sentinel-1 image for the model.

    Parameters
    ----------
    img : array of shape (2, H, W)
        Band 0 = VV, band 1 = VH, both in decibels (dB).

    Returns
    -------
    float32 array of shape (2, H, W) with values in [0, 1].
    Missing values (NaN) are set to the low end of the range.
    """
    img = np.asarray(img, dtype=np.float32)
    if img.ndim != 3 or img.shape[0] != 2:
        raise ValueError(f"Expected shape (2, H, W) with VV, VH; got {img.shape}")

    out = np.empty_like(img)
    for i, (lo, hi) in enumerate((VV_RANGE, VH_RANGE)):
        band = np.nan_to_num(img[i], nan=lo, posinf=hi, neginf=lo)
        band = np.clip(band, lo, hi)
        out[i] = (band - lo) / (hi - lo)
    return out


def clean_label(label):
    """
    Prepare a Sen1Floods11 label.

    Input values: -1 = no data, 0 = not water, 1 = water.
    Returns an int64 array of shape (H, W) where -1 is kept so the loss
    and the metrics can ignore those pixels.
    """
    label = np.asarray(label)
    if label.ndim == 3:
        label = label[0]
    label = np.nan_to_num(label, nan=LABEL_IGNORE).astype(np.int64)
    label[(label != 0) & (label != 1)] = LABEL_IGNORE
    return label
