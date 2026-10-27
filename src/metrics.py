"""
Segmentation metrics. Pixels labelled -1 (no data) are always ignored.

Use `Counts` to add up results over a whole dataset, then read the metrics
once at the end. This gives dataset-level IoU, which is what Sen1Floods11
papers report.
"""

import numpy as np

from .config import LABEL_IGNORE


class Counts:
    """Running totals of true positives, false positives and false negatives."""

    def __init__(self):
        self.tp = 0
        self.fp = 0
        self.fn = 0
        self.tn = 0

    def update(self, pred, label):
        """pred: 0/1 array. label: -1/0/1 array of the same shape."""
        pred = np.asarray(pred).astype(bool)
        label = np.asarray(label)
        valid = label != LABEL_IGNORE
        truth = label == 1
        self.tp += int(np.sum(pred & truth & valid))
        self.fp += int(np.sum(pred & ~truth & valid))
        self.fn += int(np.sum(~pred & truth & valid))
        self.tn += int(np.sum(~pred & ~truth & valid))

    def iou(self):
        d = self.tp + self.fp + self.fn
        return self.tp / d if d else float("nan")

    def dice(self):
        d = 2 * self.tp + self.fp + self.fn
        return 2 * self.tp / d if d else float("nan")

    def precision(self):
        d = self.tp + self.fp
        return self.tp / d if d else float("nan")

    def recall(self):
        d = self.tp + self.fn
        return self.tp / d if d else float("nan")

    def summary(self):
        return {
            "IoU": round(self.iou(), 4),
            "Dice": round(self.dice(), 4),
            "Precision": round(self.precision(), 4),
            "Recall": round(self.recall(), 4),
        }


class Reliability:
    """
    Calibration check: when the model says "70% water", is it water about 70%
    of the time? Pixels are grouped into bins by predicted probability.

    ece() = expected calibration error (0 = perfectly honest probabilities).
    curve() = points for a reliability diagram.
    """

    def __init__(self, n_bins=15):
        self.n = n_bins
        self.count = np.zeros(n_bins)
        self.sum_prob = np.zeros(n_bins)
        self.sum_water = np.zeros(n_bins)

    def update(self, prob, label):
        """prob: water probability array. label: -1/0/1 array of the same shape."""
        prob = np.asarray(prob, dtype=np.float64)
        label = np.asarray(label)
        valid = label != LABEL_IGNORE
        p = prob[valid].ravel()
        y = (label[valid] == 1).ravel().astype(np.float64)
        idx = np.minimum((p * self.n).astype(int), self.n - 1)
        self.count += np.bincount(idx, minlength=self.n)
        self.sum_prob += np.bincount(idx, weights=p, minlength=self.n)
        self.sum_water += np.bincount(idx, weights=y, minlength=self.n)

    def ece(self):
        total = self.count.sum()
        if total == 0:
            return float("nan")
        m = self.count > 0
        gap = np.abs(self.sum_water[m] / self.count[m] - self.sum_prob[m] / self.count[m])
        return float(np.sum(self.count[m] / total * gap))

    def curve(self):
        """Returns (mean predicted probability, observed water fraction, pixel count) per bin."""
        m = self.count > 0
        return (self.sum_prob[m] / self.count[m], self.sum_water[m] / self.count[m], self.count[m])
