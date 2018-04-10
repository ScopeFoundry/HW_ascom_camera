from ScopeFoundry import Measurement
from ScopeFoundry.helper_funcs import sibling_path, load_qt_ui_file
from ScopeFoundry import h5_io
import pyqtgraph as pg
import scipy.misc 
import time
#from libtiff import TIFF
#import tifffile as tiff
#import PIL.Image
import numpy as np
from .tiffile import imsave as tif_imsave
import os

class ASCOMCameraCaptureMeasure(Measurement):
    
    name = 'ascom_camera_capture'
    
    def setup(self):
        
        S = self.settings
        #S.New('bg_subtract', dtype=bool, initial=False, ro=False)
        #S.New('acquire_bg',  dtype=bool, initial=False, ro=False)
        S.New('continuous', dtype=bool, initial=True, ro=False)
        S.New('save_png', dtype=bool, initial=False, ro=False)
        S.New('save_tif', dtype=bool, initial=True, ro=False)
        S.New('save_ini', dtype=bool, initial=True, ro=False)
        S.New('save_h5', dtype=bool, initial=False, ro=False)
        
        
        self.ui_filename = sibling_path(__file__,"ascom_camera_capture.ui")
        self.ui = load_qt_ui_file(self.ui_filename)
        self.ui.setWindowTitle(self.name)
        
        # Event connections
        S.progress.connect_bidir_to_widget(self.ui.progressBar)
        self.ui.start_pushButton.clicked.connect(self.start)
        self.ui.interrupt_pushButton.clicked.connect(self.interrupt)

        S.continuous.connect_to_widget(self.ui.continuous_checkBox)
        S.save_png.connect_to_widget(self.ui.save_png_checkBox)
        S.save_tif.connect_to_widget(self.ui.save_tif_checkBox)
        S.save_ini.connect_to_widget(self.ui.save_ini_checkBox)
        S.save_h5.connect_to_widget( self.ui.save_h5_checkBox )
        
        cam_ui_connections = [
            ('exp_time', 'exp_time_doubleSpinBox'),
            ('BinX', 'binx_doubleSpinBox'),
            ('BinY', 'biny_doubleSpinBox'),
            ('NumX', 'numx_doubleSpinBox'),
            ('NumY', 'numy_doubleSpinBox'),
            ('StartX', 'startx_doubleSpinBox'),
            ('StartY', 'starty_doubleSpinBox')]
        
        cam_hw = self.app.hardware.ascom_camera
        
        for lq_name, widget_name in cam_ui_connections:                          
            cam_hw.settings.get_lq(lq_name).connect_to_widget(getattr(self.ui, widget_name))


    def run(self):
        
        cam_hw = self.app.hardware.ascom_camera
        
        print(self.name, 'interrupted', self.interrupt_measurement_called)
        
        while not self.interrupt_measurement_called:
            # Blocking version
            #self.img = cam_hw.acq_single_exposure()
            
            # non blocking version
            cam_hw.ac.StartExposure(cam_hw.settings['exp_time'])
            t0 = time.time()
            while not cam_hw.ac.is_image_ready():
                if self.interrupt_measurement_called:
                    break
                time.sleep(0.05)
                self.settings['progress'] = 100.0* (time.time() - t0)/cam_hw.settings['exp_time'] 
            self.img = cam_hw.ac.read_image_data()
            
            
            
            if not self.settings['continuous']:
                # save image
                try:
                    t0 = time.time()
                    fname = os.path.join(self.app.settings['save_dir'], "%i_%s" % (t0, self.name))
                    print( self.name,'asdf', self.img.dtype, fname)
                    if self.settings['save_ini']:
                        self.app.settings_save_ini(fname + ".ini")
                    if self.settings['save_png']:
                        scipy.misc.imsave(fname + ".png", self.img)
                    if self.settings['save_tif']:
                        #im = PIL.Image.fromarray(self.img.T)
                        #im.save("%i_%s.tif" % (t0, self.name), compression=6)
                        tif_imsave(fname + ".tif", self.img.T.astype(np.uint16), compress=0)
                    if self.settings['save_h5']:
                        with h5_io.h5_base_file(self.app,  fname = fname + ".h5") as H:
                            M = h5_io.h5_create_measurement_group(measurement=self, h5group=H)
                            M.create_dataset('img', data=self.img, compression='gzip')
                except Exception as e:
                    print('Error saving files!', e)
                    raise e
                    
                finally:
                    break # end the while loop for non-continuous scans
            else:
                pass
                # restart acq
                #ccd.start_acquisition()
        
    
    def setup_figure(self):
        #self.clear_qt_attr('graph_layout')
        #self.graph_layout=pg.GraphicsLayoutWidget(border=(100,100,100))
        #self.ui.plot_groupBox.layout().addWidget(self.graph_layout)

        self.imview = pg.ImageView()
        self.ui.plot_groupBox.layout().addWidget(self.imview)
        
    
    def update_display(self):
        if hasattr(self, "img"):
            self.imview.setImage(self.img, autoRange=False)
    
    