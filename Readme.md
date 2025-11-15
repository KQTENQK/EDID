# EDID binaries

A set of binaries were originally got from https://github.com/linuxhw/EDID.


```/Analog/``` and ```/Digital/``` contains binaries correspondingly.





# EDID editor (EdidEditor.py)



Program to edit EDID serials and manufacture dates.



``` py EdidEditor.py input.bin output.bin [options] ```



### Options:



```--serial``` - manufacturer serial number (8 HEX symbols)



```--week``` - production week (1-53)



```--year``` - production year (1990-2249)



```--product``` - product serial number (max 13 ASCII symbols)



## Example:



``` py EdidEditor.py monitor.bin new\_monitor.bin --serial A1B2C3D4 --week 25 --year 2023 --product "MONITOR123" ```



# ToHex.py



A script to parse text data from https://github.com/linuxhw/EDID to binaries.



