import logging
import time

import cflib.crtp
from cflib.crazyflie import Crazyflie
from cflib.crazyflie.log import LogConfig
from cflib.crazyflie.syncCrazyflie import SyncCrazyflie
from cflib.crazyflie.syncLogger import SyncLogger

from pyqtgraph.Qt import QtCore, QtGui
import pyqtgraph.opengl as gl
import pyqtgraph as pg
import numpy as np
import sys

import sys, termios
import select
import time
import threading

mainQuadcopter = "mainQuadcopter"
neighbour1 = "neighbour1"
neighbour2 = "neighbour2"
neighbour3 = "neighbour3"
neighbour4 = "neighbour4"

URI = 'radio://0/100/2M'

def rotateTo3D(visualizer):
    elements = 500
    h = 0 / elements
    v = -80 / elements
    visualizer.gaxis.setSize(size=QtGui.QVector3D(10, 10, 10))
    for _ in range(elements):
        time.sleep(5/elements)
        visualizer.w.orbit(h, v)
        pg.QtGui.QApplication.processEvents()

class Visualizer(object):
    def __init__(self):
        self.traces = dict()
        self.app = QtGui.QApplication(sys.argv)
        self.w = gl.GLViewWidget()
        self.w.orbit(45 + 180, 90) # Place like 2D
        self.w.pan(1, 1, 0.5)
        self.w.opts['distance'] = 5
        self.w.setWindowTitle('pyqtgraph example: GLLinePlotItem')
        self.w.setGeometry(0, 0, 1280, 800)
        self.w.show()

        # create the background grids
        # gx = gl.GLGridItem()
        # gx.rotate(90, 0, 1, 0)
        # gx.translate(-10, 0, 0)
        # self.w.addItem(gx)
        # gy = gl.GLGridItem()
        # gy.rotate(90, 1, 0, 0)
        # gy.translate(0, -10, 0)
        # self.w.addItem(gy)
        # gz = gl.GLGridItem()
        # gz.translate(0, 0, -10)
        # self.w.addItem(gz)
        gx = gl.GLGridItem()
        gx.translate(0, 0, -1)
        self.w.addItem(gx)

        # Create the axis
        self.gaxis = gl.GLAxisItem(size=QtGui.QVector3D(10, 10, 0))
        self.w.addItem(self.gaxis)

        # self.n = 50
        # self.m = 1000
        # self.y = np.linspace(-10, 10, self.n)
        # self.x = np.linspace(-10, 10, self.m)
        # self.phase = 90

        self.traces[mainQuadcopter] = gl.GLScatterPlotItem(pos=np.empty(shape=(1,3)), color=(0, 1, 0, 1))
        self.traces[neighbour1] = gl.GLScatterPlotItem(pos=np.empty(shape=(1,3)), color=(1, 0, 0, 1))
        self.traces[neighbour2] = gl.GLScatterPlotItem(pos=np.empty(shape=(1,3)), color=(0, 0, 1, 1))
        self.traces[neighbour3] = gl.GLScatterPlotItem(pos=np.empty(shape=(1,3)), color=(1, 1, 0, 1))
        self.traces[neighbour4] = gl.GLScatterPlotItem(pos=np.empty(shape=(1,3)), color=(1, 0, 1, 1))

        for key, value in self.traces.items():
            self.w.addItem(value)

    def start(self):
        if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
            QtGui.QApplication.instance().exec_()

    def set_plotdata(self, name, points):
        self.traces[name].setData(pos=np.array(points))
        pg.QtGui.QApplication.processEvents() 
    
# Only output errors from the logging framework
logging.basicConfig(level=logging.ERROR)

if __name__ == '__main__':
    v = Visualizer()
    detected3D = False

    # Initialize the low-level drivers (don't list the debug drivers)
    cflib.crtp.init_drivers(enable_debug_driver=False)
    available = cflib.crtp.scan_interfaces()
    if len(available) > 0:

        # Configure info to log
        lg_stab = LogConfig(name='twrSwarm', period_in_ms=100)
        lg_stab.add_variable('twrSwarm.xPosition', 'float')
        lg_stab.add_variable('twrSwarm.yPosition', 'float')
        lg_stab.add_variable('twrSwarm.zPosition', 'float')

        lg_stab.add_variable('twrSwarm.iPositionN', 'uint8_t')
        lg_stab.add_variable('twrSwarm.xPositionN', 'float')
        lg_stab.add_variable('twrSwarm.yPositionN', 'float')
        lg_stab.add_variable('twrSwarm.zPositionN', 'float')

        # lg_stab = LogConfig(name='Stabilizer', period_in_ms=20)
        # lg_stab.add_variable('stabilizer.roll', 'float')

        with SyncCrazyflie(URI, cf=Crazyflie(rw_cache='./cache')) as scf:
            with SyncLogger(scf, lg_stab) as logger:
                for log_entry in logger:                    
                    data = log_entry[1]

                    v.set_plotdata(name=mainQuadcopter, points=[data['twrSwarm.xPosition'], data['twrSwarm.yPosition'], data['twrSwarm.zPosition']]) 
                    
                    neighbourIndex = data['twrSwarm.iPositionN']
                    if neighbourIndex == 0:
                        name = neighbour1
                    elif neighbourIndex == 1:
                        name = neighbour2
                    elif neighbourIndex == 2:
                        name = neighbour3
                    elif neighbourIndex == 3:
                        name = neighbour4
                        if detected3D == False:
                            detected3D = True
                            timer = threading.Timer(5.0, rotateTo3D, args=([v]))
                            timer.daemon = True # Daemonize thread
                            timer.start() 
                    else:
                        raise NameError('Drone not identified')

                    neighbourx = data['twrSwarm.xPositionN']
                    neighboury = data['twrSwarm.yPositionN']
                    neighbourz = data['twrSwarm.zPositionN']
                    v.set_plotdata(name=name, points=[neighbourx, neighboury, neighbourz]) 

                    if select.select([sys.stdin,],[],[],0.0)[0]:
                        termios.tcflush(sys.stdin, termios.TCIOFLUSH)
                        break
    else:
        print('No Crazyflies found, finishing...')

input("Press Enter to finish...")    
