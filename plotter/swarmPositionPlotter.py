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
    lg_stab = LogConfig(name='twrSwarm', period_in_ms=60)
    lg_stab.add_variable('twrSwarm.xPosition', 'float')
    lg_stab.add_variable('twrSwarm.yPosition', 'float')

    lg_stab.add_variable('twrSwarm.xPosition0', 'float')
    lg_stab.add_variable('twrSwarm.yPosition0', 'float')

    lg_stab.add_variable('twrSwarm.xPosition1', 'float')
    lg_stab.add_variable('twrSwarm.yPosition1', 'float')

    # lg_stab = LogConfig(name='Stabilizer', period_in_ms=20)
    # lg_stab.add_variable('stabilizer.roll', 'float')

    c1 = plt.plot(pen='b', symbol='o', symbolPen='b', symbolBrush='b', name='blue')
    c2 = plt.plot(pen='r', symbol='o', symbolPen='r', symbolBrush='r', name='red')
    c3 = plt.plot(pen='g', symbol='o', symbolPen='g', symbolBrush='g', name='green')

    with SyncCrazyflie(URI, cf=Crazyflie(rw_cache='./cache')) as scf:
        with SyncLogger(scf, lg_stab) as logger:
            for log_entry in logger:                    
                data = log_entry[1]
                setData(c1, data['twrSwarm.xPosition'], data['twrSwarm.yPosition'])
                setData(c2, data['twrSwarm.xPosition0'], data['twrSwarm.yPosition0'])
                setData(c3, data['twrSwarm.xPosition1'], data['twrSwarm.yPosition1'])
                # setData(c1, data['stabilizer.roll'], 0)

                # timestamp = log_entry[0]
                # print('[%d]: %s' % (timestamp, data))

                if select.select([sys.stdin,],[],[],0.0)[0]:
                    termios.tcflush(sys.stdin, termios.TCIOFLUSH)
                    break

input("Press Enter to finish...")
    
