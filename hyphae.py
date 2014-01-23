#!/usr/bin/python
# -*- coding: utf-8 -*-

from numpy import cos, sin, pi, arctan2, sqrt, square, int, linspace
from numpy.random import random as rand
import numpy as np
import cairo,Image
from time import time as time
from operator import itemgetter

any = np.any
all = np.all

PI = pi
PII = 2*pi
N = 4000
ONE = 1./N
BACK = 1.
FRONT = 0.
MID = 0.5
ALPHA = 0.2

filename = './img'

RAD = 3./N;

ZONES = 400

print
print 'filename',filename
print 'N', N
print 'one', ONE

def stroke(x,y): 
  ctx.rectangle(x,y,ONE,ONE) 
  ctx.fill() 
vstroke = np.vectorize(stroke) 

def ctx_init():
  sur = cairo.ImageSurface(cairo.FORMAT_ARGB32,N,N)
  ctx = cairo.Context(sur)
  ctx.scale(N,N)
  ctx.set_source_rgb(BACK,BACK,BACK)
  ctx.rectangle(0,0,1,1)
  ctx.fill()
  return sur,ctx
sur,ctx = ctx_init()

def get_colors(f):
  from random import shuffle
  scale = 1./255.
  im = Image.open(f)
  w,h = im.size
  rgbim = im.convert('RGB')
  res = []
  for i in xrange(0,w):
    for j in xrange(0,h):
      r,g,b = rgbim.getpixel((i,j))
      res.append((r*scale,g*scale,b*scale))

  shuffle(res)

  return res
colors = get_colors('color/dark_cyan_white_black.gif')
ncolors = len(colors)
print 'colors',  ncolors
print

def near_zone_inds(x,y,Z):
  
  i = 1+int(x*ZONES) 
  j = 1+int(y*ZONES) 
  ij = np.array([i-1,i,i+1,i-1,i,i+1,i-1,i,i+1])*ZONES+\
       np.array([j+1,j+1,j+1,j,j,j,j-1,j-1,j-1])

  it = itemgetter(*ij)
  its = it(Z)
  inds = np.array([b for a in its for b in a ])

  return inds

def main():


  Z = [[] for i in xrange((ZONES+2)**2)]

  nmax = 2*1e7
  R = np.zeros(nmax,dtype=np.float)
  X = np.zeros(nmax,dtype=np.float)
  Y = np.zeros(nmax,dtype=np.float)
  THE = np.zeros(nmax,dtype=np.float)


  X[0] = 0.5
  Y[0] = 0.5
  THE[0] = RAD

  i = 1+int(0.5*ZONES) 
  j = 1+int(0.5*ZONES) 
  ij = i*ZONES+j
  Z[ij].append(0)

  num = 1
  itt = 0
  ti = time()
  drawn = -1


  while True:
    try:
      itt += 1

      k = int(sqrt(rand())*num)
      the = ( PI * (0.5-rand()) )+THE[k]
      r = RAD  + rand()*ONE*10.
      x = X[k] + sin(the)*r
      y = Y[k] + cos(the)*r
      
      inds = near_zone_inds(x,y,Z)

      good = True
      if len(inds)>0:
        dd = square(X[inds]-x) + \
             square(Y[inds]-y)

        sqrt(dd,dd)
        mask = dd*2 >= R[inds] + r
        good = mask.all()
        
      if good: 
        X[num] = x
        Y[num] = y
        R[num] = r
        THE[num] = the

        i = 1+int(x*ZONES) 
        j = 1+int(y*ZONES) 
        Z[i*ZONES+j].append(num)
        
        ## lines
        ctx.set_source_rgba(FRONT,FRONT,FRONT)
        ctx.set_line_width(2./N)
        ctx.move_to(X[k],Y[k])
        ctx.line_to(x,y)
        ctx.stroke()
       
        ## sandpaint
        #dx = X[k]-x
        #dy = Y[k]-y
        #a = arctan2(dy,dx)
        #dots = 2*int(r*N)
        #scales = linspace(0,r,dots)
        #xp = X[k] - scales*cos(a) + rand(dots)*ONE*2.
        #yp = Y[k] - scales*sin(a) + rand(dots)*ONE*2.

        #ctx.set_source_rgba(FRONT,FRONT,FRONT)
        #vstroke(xp,yp)

        num+=1
      #else:


        #dx = X[k] - x
        #dy = Y[k] - y
        #a = arctan2(dy,dx)
        #scales = rand(GRAINS)*r
        #xp = X[k] - scales*cos(a)
        #yp = Y[k] - scales*sin(a)

        #r,g,b = colors[k%ncolors]
        #ctx.set_source_rgba(r,g,b,ALPHA)
        #vstroke(xp,yp)
        
      if not num % 1000 and not num==drawn:
        sur.write_to_png('{:s}.{:d}.png'.format(filename,num))
        print itt, num, time()-ti
        ti = time()
        drawn = num
    except KeyboardInterrupt:
      break

  return

if __name__ == '__main__':
  if True:
    import pstats, cProfile
    OUT = 'profile'
    pfilename = 'profile.profile'
    cProfile.run('main()',pfilename)
    p = pstats.Stats(pfilename)
    p.strip_dirs().sort_stats('cumulative').print_stats()
  else:
    main()