#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# *** このコードは pyusb-1.0.0b1 に依存 ***
# 以下のコマンドでインストールすること
# % sudo pip install 'pyusb==1.0.0b1'
#
import usb.core
import usb.util

class UsbDevice:
    def __init__(self, idVendor, idProduct):
        self.dev = usb.core.find(idVendor=idVendor, idProduct=idProduct)
        self.interface = 0
        if self.dev is None:
            raise ValueError('Device not found')
        return

    def __configuration(self):
        cfg = self.dev.get_active_configuration()
        intf = cfg[(0,0)]
        self.read_ep = usb.util.find_descriptor(
            intf,
            custom_match = \
                lambda e: \
                usb.util.endpoint_direction(e.bEndpointAddress) == \
                usb.util.ENDPOINT_IN)
        self.write_ep = usb.util.find_descriptor(
            intf,
            custom_match = \
                lambda e: \
                usb.util.endpoint_direction(e.bEndpointAddress) == \
                usb.util.ENDPOINT_OUT)

    def open(self):
        if self.dev.is_kernel_driver_active(self.interface):
            self.dev.detach_kernel_driver(self.interface)
        # 以下を実行すると動作が不安定になるためコメントアウト．
        # おそらく，最初にカーネルがSET_CONFIGURATIONを行っており，
        # ここでset_configuration()を行うことで上書きになるのかも．
        # デバイス側でSET_CONFIGURATIONへの応答が適当なのも原因かも．
        # self.dev.set_configuration()
        usb.util.claim_interface(self.dev, self.interface)
        self.__configuration()

    def close(self):
        if not self.dev.is_kernel_driver_active(self.interface):
            self.dev.attach_kernel_driver(self.interface)
        usb.util.release_interface(self.dev, self.interface)

    def read(self, size):
        return self.read_ep.read(size, timeout=1000)

    def write(self, data):
        return self.write_ep.write(data, timeout=1000)

if __name__ == '__main__':
    ID_VENDOR  = 0x0000
    ID_PRODUCT = 0x0000
    dev = UsbDevice(ID_VENDOR, ID_PRODUCT)
    dev.open()
    dev.write("test")
    #data = dev.read(64)
    #print data
    dev.close()
