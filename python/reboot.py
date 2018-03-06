from cflib.drivers.crazyradio import Crazyradio

cr = Crazyradio()

cr.set_channel(90)
cr.set_data_rate(cr.DR_2MPS)

print(cr.send_packet((0xff, 0xfe, 0xff)).data) # Init the reboot
#print(cr.send_packet((0xff, 0xfe, 0xf0, 0)).ack)  # Reboot to Bootloader
print(cr.send_packet((0xff, 0xfe, 0xf0, 1)).data)  # Reboot to Firmware
