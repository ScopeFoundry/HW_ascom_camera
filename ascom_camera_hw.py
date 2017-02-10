from __future__ import absolute_import
from ScopeFoundry import HardwareComponent
try:
    from .ascom_camera import ASCOMCamera
except Exception as err:
    print("could not load ascom_camera", err)
import numpy as np

class ASCOMCameraHW(HardwareComponent):
    
    name = 'ascom_camera'
    
    def setup(self):
        
        S = self.settings
        
        S.New('com_name', dtype=str, initial='chooser')
        
        S.New('exp_time', dtype=float, initial=1.0, unit='sec')
        
        S.New('BinX', dtype=int, initial=1)
        S.New('BinY', dtype=int, initial=1)
        
        S.New('StartX', dtype=int, initial=0)
        S.New('StartY', dtype=int, initial=0)

        S.New('NumX', dtype=int, initial=1)
        S.New('NumY', dtype=int, initial=1)
        
        S.New('MaxBinX', dtype=int, initial=1, ro=True)
        S.New('MaxBinY', dtype=int, initial=1, ro=True)

        S.New('CameraXSize', dtype=int, initial=1, ro=True)
        S.New('CameraYSize', dtype=int, initial=1, ro=True)
        
        S.New('PixelSizeX', dtype=int, initial=0, ro=True, unit='um')
        S.New('PixelSizeY', dtype=int, initial=0, ro=True, unit='um')

        
        S.New('CCDTemperature', dtype=float, initial=100, ro=True)
    
        S.New('CoolerOn', dtype=bool)
    
    def connect(self):
        
        S = self.settings
        
        self.ac  = ASCOMCamera(com_name=S['com_name'])
        self.cam = self.ac.cam
        S['com_name'] = self.ac.com_name
        
        for lq_name in ['BinX', 'StartX', 'NumX', 'MaxBinX', 'CameraXSize',
                        'BinY', 'StartY', 'NumY', 'MaxBinY', 'CameraYSize',
                        'PixelSizeX', 'PixelSizeY',
                        'CCDTemperature', 'CoolerOn']:
            lq = S.get_lq(lq_name)
            lq.hardware_read_func = self.read_cam_param_func(lq_name)
            #if not lq.ro:
            #    lq.hardware_set_func = self.set_cam_param_func(lq_name)
        
        S.BinX.hardware_set_func = self.write_bin_size
        S.BinY.hardware_set_func = self.write_bin_size
        
        S.StartX.hardware_set_func = self.write_start_pos
        S.StartY.hardware_set_func = self.write_start_pos
        
        S.NumX.hardware_set_func = self.write_num_px
        S.NumY.hardware_set_func = self.write_num_px

        S.CoolerOn.hardware_set_func = self.write_cam_param_func('CoolerOn')
        
        S['CoolerOn'] = True
        
        self.read_from_hardware()
                
    def disconnect(self):
        
        #disconnect logged quantities from hardware
        for lq in self.settings.as_dict().values():
            lq.hardware_read_func = None
            lq.hardware_set_func = None
        
        if hasattr(self, 'cam'):
            self.cam.Connected = False
            # clean up device object
            del self.cam
        if hasattr(self, 'ac'):
            # clean up device object
            del self.ac

                
    def read_cam_param_func(self, name):
        def param_get_func():
            return getattr(self.cam, name)
        return param_get_func
    
    def write_cam_param_func(self, name):
        def param_set_func(val):
            return setattr(self.cam, name, val)
        return param_set_func
    
    def write_start_pos(self, _=None):
        S = self.settings
        setattr(self.cam, 'StartX', S['StartX'])
        setattr(self.cam, 'StartY', S['StartY'])
        self.read_from_hardware()
        
    def write_num_px(self, _=None):
        S = self.settings
        setattr(self.cam, 'NumX', S['NumX'])
        setattr(self.cam, 'NumY', S['NumY'])
        #self.read_from_hardware()
        
    def write_bin_size(self, _=None):
        S = self.settings
        S['NumX'] = int(np.floor(S['CameraXSize']/S['BinX']))
        S['NumY'] = int(np.floor(S['CameraYSize']/S['BinY']))
        
        setattr(self.cam,'BinX', S['BinX'])
        setattr(self.cam,'BinY', S['BinY'])
        self.read_from_hardware()
        
    
    def acq_single_exposure(self):
        return self.ac.acq_single_exposure(self.settings['exp_time'])