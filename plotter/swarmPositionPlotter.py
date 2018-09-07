import logging
import time

import cflib.crtp
from cflib.crazyflie import Crazyflie
from cflib.crazyflie.log import LogConfig
from cflib.crazyflie.syncCrazyflie import SyncCrazyflie
from cflib.crazyflie.syncLogger import SyncLogger

import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui
import sys, termios
import select

URI = 'radio://0/100/2M'

def createPlot():
    # create plot
    plt = pg.plot()
    plt.showGrid(x=True, y=True)
    # plt.addLegend()

    # set properties
    # plt.setLabel('left', 'Value', units='V')
    # plt.setLabel('bottom', 'Time', units='s')
    plt.setXRange(-2, 2)
    plt.setYRange(-2, 2)
    plt.setWindowTitle('Swarm relative positioning')

    screen = QtGui.QDesktopWidget().screenGeometry()
    windowWidth = screen.width() / 2
    plt.resize(windowWidth, windowWidth)
    plt.win.move(0, 0)
    return plt

def setData(dataItem, x, y):
    dataItem.setData([x], [y])
    pg.QtGui.QApplication.processEvents()
    
# Only output errors from the logging framework
logging.basicConfig(level=logging.ERROR)

if __name__ == '__main__':
    plt = createPlot()

    # Initialize the low-level drivers (don't list the debug drivers)
    cflib.crtp.init_drivers(enable_debug_driver=False)

    # Configure info to log
    lg_stab = LogConfig(name='twrSwarm', period_in_ms=40)
    lg_stab.add_variable('twrSwarm.xPosition', 'float')
    lg_stab.add_variable('twrSwarm.yPosition', 'float')

    lg_stab.add_variable('twrSwarm.iPositionN', 'uint8_t')
    lg_stab.add_variable('twrSwarm.xPositionN', 'float')
    lg_stab.add_variable('twrSwarm.yPositionN', 'float')

    # lg_stab = LogConfig(name='Stabilizer', period_in_ms=20)
    # lg_stab.add_variable('stabilizer.roll', 'float')

    mainQ = plt.plot(symbol='o', symbolPen='g', symbolBrush='g', name='MainQuadcopter')
    n0 = plt.plot(symbol='o', symbolPen='r', symbolBrush='r', name='Neighbour1')
    n1 = plt.plot(symbol='o', symbolPen='b', symbolBrush='b', name='Neighbour2')
    n2 = plt.plot(symbol='o', symbolPen='y', symbolBrush='y', name='Neighbour3')
    # plt.plot(pen='y', symbol='o', symbolPen='y', symbolBrush='y', name='Neighbour3')

    with SyncCrazyflie(URI, cf=Crazyflie(rw_cache='./cache')) as scf:
        with SyncLogger(scf, lg_stab) as logger:
            for log_entry in logger:                    
                data = log_entry[1]

                setData(mainQ, data['twrSwarm.xPosition'], data['twrSwarm.yPosition'])
                
                neighbourIndex = data['twrSwarm.iPositionN']
                neighbourx = data['twrSwarm.xPositionN']
                neighboury = data['twrSwarm.yPositionN']
                # neighbourz = data['twrSwarm.zPositionN']
                if neighbourIndex == 0:
                    setData(n0, neighbourx, neighboury)
                elif neighbourIndex == 1:
                    setData(n1, neighbourx, neighboury)
                elif neighbourIndex == 2:
                    setData(n2, neighbourx, neighboury)
                else:
                    raise NameError('Drone not identified')

                if select.select([sys.stdin,],[],[],0.0)[0]:
                    termios.tcflush(sys.stdin, termios.TCIOFLUSH)
                    break

input("Press Enter to finish...")
    
