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
