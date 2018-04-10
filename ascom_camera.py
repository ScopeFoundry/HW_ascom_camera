import win32com.client
import time
import numpy as np

class ASCOMCamera(object):
    
    def __init__(self, com_name="ASCOM.Atik2.Camera"):
        
        if com_name is None or com_name == 'chooser':
            chooser = win32com.client.Dispatch("ASCOM.Utilities.Chooser")
            chooser.DeviceType = "Camera"
            com_name = chooser.Choose(None)
        
        self.com_name = com_name
        cam = self.cam = win32com.client.Dispatch(self.com_name)
        
        cam.Connected = True
        
        self.Name = cam.Name
        
    def StartExposure(self, Duration, Light=True):
        self.cam.StartExposure(Duration, Light)
    
    def acq_single_exposure(self, Duration, Light=True):
        self.StartExposure(Duration, Light)
        t0 = time.time()
        while not self.cam.ImageReady:
            time.sleep(0.01*Duration)
        t1 = time.time()
        print("wait til image_ready took", t1-t0)
        dat = np.array(self.cam.ImageArray)
        t2  = time.time()
        print("retrieve and convert took", t2-t1)
        return dat
    
    def is_image_ready(self):
        return self.cam.ImageReady
    
    def read_image_data(self):
        dat = np.array(self.cam.ImageArray)
        return dat
        
if __name__ == "__main__":
    
    #ac = ASCOMCamera("ASCOM.Simulator.Camera")
    ac = ASCOMCamera('chooser')
    #print "Gain:", ac.cam.Gain, list(ac.cam.Gains)
    
    #print "Readout", ac.cam.ReadoutMode, list(ac.cam.ReadoutModes)
    #print "fastreadout", ac.cam.CanFastReadout 
    #ac.cam.FastReadout = True
    
    #print "Readout", ac.cam.ReadoutMode, list(ac.cam.ReadoutModes)

    print(ac.cam.BinX, ac.cam.MaxBinX, ac.cam.NumX)
    ac.cam.BinX = 1
    ac.cam.NumX = ac.cam.CameraXSize/ac.cam.BinX
    ac.cam.BinY = 1
    ac.cam.NumY = ac.cam.CameraYSize/ac.cam.BinY

    print(ac.cam.StartX, ac.cam.StartY)
    #ac.cam.BinY = 2
    dat = ac.acq_single_exposure(0.1)
    print(dat.shape)
    
    import matplotlib.pylab as plt
    plt.imshow(dat.T, interpolation='none', vmin=np.percentile(dat, 1), vmax=np.percentile(dat,99), cmap='gray')
    plt.colorbar()
    plt.show()    
    