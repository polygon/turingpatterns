from pylab import *
import scipy.signal
import pdb
import matplotlib.cm as cm
import scipy.misc
import gtk
from multiprocessing import Pool
import time

def convolve_kernel(data):
  s = time.time()
  Field, prod, inh = data

  kernel_producer = zeros(Field.shape[0])
  kernel_producer[0:prod] = 1.0 / prod
  Kernel_producer = fft(kernel_producer)
  kernel_inhibitor = zeros(Field.shape[0])
  kernel_inhibitor[0:inh] = 1.0 / inh
  Kernel_inhibitor = fft(kernel_inhibitor)
  res_prod = real(ifft(Field * Kernel_producer[:, newaxis], axis=0))
  res_inh = real(ifft(Field * Kernel_inhibitor[:, newaxis], axis=0))
  res_prod = real(ifft(fft(res_prod,axis=1) * Kernel_producer[newaxis, :], axis=1))
  res_inh = real(ifft(fft(res_inh,axis=1) * Kernel_inhibitor[newaxis, :], axis=1))
  f = time.time()
  print f - s
  return (res_prod, res_inh)

def evolve_fft2(field, pool):
#  PROD = array([100, 50, 10, 5, 2])
#  INH = array([200, 100, 20, 10, 4])
#  AMOUNT = array([0.05, 0.04, 0.03, 0.02, 0.01])
  PROD = array([170, 90, 60, 10, 4])
  INH = array([230, 120, 80, 20, 6])
  AMOUNT = array([0.05, 0.04, 0.03, 0.02, 0.01])
#  PROD = array([4])
#  INH = array([8])
#  AMOUNT = array([0.01])
  prod = zeros((field.shape[0],field.shape[1],PROD.size))
  inh = zeros((field.shape[0],field.shape[1],PROD.size))
  Field = fft(field, axis=0)
  args = zip([Field]*PROD.size, PROD, INH)
  results = pool.map(convolve_kernel, args)
  for i in range(PROD.size):
    prod[:, :, i] = results[i][0]
    inh[:, :, i] = results[i][1]
#  for i in range(PROD.size):
#		prod[:, :, i], inh[:, :, i] = convolve_kernel((Field, PROD[i], INH[i]))
  fields = prod - inh
  mins = abs(fields).argmin(2)
  diff = sign(fields[indices((fields.shape[0],fields.shape[1]))[0],indices((field.shape[0],fields.shape[1]))[1],mins])
  field = field + AMOUNT[mins]*diff
  return field

def normalize(field):
  return field / abs(field).max()

def clip(field):
  return maximum(minimum(field, 1.0), -1.0)

ion()

#field = rand(1024, 1024) * 2.0 - 1.0
field = rand(512, 512) * 2.0 - 1.0
#field[200:300, :] = rand(100, 512) * 2.0 - 1.0
pic = imshow(field, cmap=cm.bone)

img = cm.bone(field)
pool = Pool(5)

#image = gtk.Image()
#pb = gtk.gdk.pixbuf_new_from_array((img * 128 + 128).astype(uint8), gtk.gdk.COLORSPACE_RGB, 8)
#image.set_from_pixbuf(pb)

#window = gtk.Window(type=gtk.WINDOW_TOPLEVEL)
#window.set_size_request(512, 512)
#window.add(image)
#image.show()
#window.show()

for i in range(1000):
#  for j in range(10):
#  field = evolve_fft(field)
#  field = evolve(field)
#  field = evolve_cool(field)
  s = time.time()
  field = evolve_fft2(field, pool)
  field = normalize(field)
  f = time.time()
  print f - s
  fout = (field + 1.0) / 2.0
  imgpink = cm.pink(fout, 1.0)
#  imgbone = cm.bone(fout, 1.0)
#  imghot = cm.hot(field, 1.0)
#  scipy.misc.imsave('symm_%s.png' % (str(i).zfill(4)), imgpink)
#  scipy.misc.imsave('hot_%s.png' % (str(i).zfill(4)), imghot)
#  scipy.misc.imsave('bone_%s.png' % (str(i).zfill(4)), imgbone)

  print "%i / 1000" % (i)
#  field = clip(field)
  pic.set_data(imgpink)
  draw()
