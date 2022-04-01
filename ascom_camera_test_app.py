from ScopeFoundry import BaseMicroscopeApp

class AscomCameraTestApp(BaseMicroscopeApp):

    name = "AscomCameraTestApp"

    def setup(self):
        
        
        from ScopeFoundryHW.ascom_camera import ASCOMCameraHW, ASCOMCameraCaptureMeasure
        
        
        self.add_hardware(ASCOMCameraHW(self))
        self.add_measurement(ASCOMCameraCaptureMeasure(self))
        
        

if __name__ == '__main__':
    import sys
    app = AscomCameraTestApp(sys.argv)
    app.exec_()