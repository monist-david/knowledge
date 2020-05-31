# import matplotlib.pyplot as plt
# from mpl_toolkits.mplot3d import Axes3D
# import numpy as np
# import math
#
#
# def onclick(event):
#     print('%s click: button=%d, x=%d, y=%d, xdata=%f, ydata=%f' %
#           ('double' if event.dblclick else 'single', event.button,
#            event.x, event.y, event.xdata, event.ydata))
#     print(ax.format_coord(event.xdata, event.y))
#
#
# fig = plt.figure()
# ax = plt.axes(projection='3d')
# zdata = (0, 0, 0, 0, 1)
# xdata = (1, 1, -1, -1, 0)
# ydata = (1, -1, 1, -1, 0)
# ax.set_xlim([-10, 10])
# ax.set_ylim([-10, 10])
# ax.set_zlim([-10, 10])
# ax.scatter3D(xdata, ydata, zdata, c="r")
#
# plt.
# cid = fig.canvas.mpl_connect('button_press_event', onclick)
#
# plt.show()
#
