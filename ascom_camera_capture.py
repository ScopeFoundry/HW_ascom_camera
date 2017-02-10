from ScopeFoundry import Measurement
from ScopeFoundry.helper_funcs import sibling_path, load_qt_ui_file
import pyqtgraph as pg
import scipy.misc 
import time
#from libtiff import TIFF
#import tifffile as tiff
import PIL.Image
import numpy as np

class ASCOMCameraCaptureMeasure(Measurement):
    
    name = 'ascom_camera_capture'
    
    def setup(self):
        
        S = self.settings
        #S.New('bg_subtract', dtype=bool, initial=False, ro=False)
        #S.New('acquire_bg',  dtype=bool, initial=False, ro=False)
        S.New('continuous', dtype=bool, initial=True, ro=False)
        S.New('save_png', dtype=bool, initial=True, ro=False)
        S.New('save_tif', dtype=bool, initial=True, ro=False)
        
        self.ui_filename = sibling_path(__file__,"ascom_camera_capture.ui")
        self.ui = load_qt_ui_file(self.ui_filename)
        self.ui.setWindowTitle(self.name)
        
        # Event connections
        S.progress.connect_bidir_to_widget(self.ui.progressBar)
        self.ui.start_pushButton.clicked.connect(self.start)
        self.ui.interrupt_pushButton.clicked.connect(self.interrupt)

        S.continuous.connect_bidir_to_widget(self.ui.continuous_checkBox)
        S.save_png.connect_bidir_to_widget(self.ui.save_png_checkBox)
        S.save_tif.connect_bidir_to_widget(self.ui.save_tif_checkBox)
        
        cam_ui_connections = [
            ('exp_time', 'exp_time_doubleSpinBox'),
            ('BinX', 'binx_doubleSpinBox'),
            ('BinY', 'biny_doubleSpinBox'),
            ('NumX', 'numx_doubleSpinBox'),
            ('NumY', 'numy_doubleSpinBox'),
            ('StartX', 'startx_doubleSpinBox'),
            ('StartY', 'starty_doubleSpinBox')]
        
        cam_hc = self.app.hardware.ascom_camera
        
        for lq_name, widget_name in cam_ui_connections:                          
            cam_hc.settings.get_lq(lq_name).connect_bidir_to_widget(getattr(self.ui, widget_name))


    def run(self):
        
        cam_hc = self.app.hardware.ascom_camera
        
        print(self.name, 'interrupted', self.interrupt_measurement_called)
        
        while not self.interrupt_measurement_called:
            self.img = cam_hc.acq_single_exposure()
            
            if not self.settings['continuous']:
                # save image
                try:
                    t0 = time.time()
                    print( self.name,'asdf', self.img.dtype)
                    if self.settings['save_png']:
                        scipy.misc.imsave("%i_%s.png" % (t0, self.name), self.img)
                    if self.settings['save_tif']:
                        im = PIL.Image.fromarray(self.img.T)
                        im.save("%i_%s.tif" % (t0, self.name))
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
        self.imview.setImage(self.img, autoRange=False)
    
    