from __future__ import absolute_import

try:
    from .ascom_camera import ASCOMCamera
except Exception as err:
    print("could not load ascom_camera", err)

from ScopeFoundryHW.ascom_camera.ascom_camera_hw import ASCOMCameraHW
from .ascom_camera_capture import ASCOMCameraCaptureMeasure

