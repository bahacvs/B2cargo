"""Adapter hata tipleri.

Pipeline bu hataları yakalayıp izole eder (1 depo/kaynak çökerse diğerleri devam).
"""

from __future__ import annotations


class AdapterError(RuntimeError):
    """Bir veri kaynağına (Devambar/Sensor/Arvento) erişilemediğinde fırlatılır."""
