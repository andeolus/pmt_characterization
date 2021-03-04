# pmt_characterization
Make measurements on PMTs, analyze them and plot results. Features: Transient time spread, uniformity, Gain over HV...

## Contingut:
* motion_controll.py: moure el braç, comprovar que funciona.  
Usage: python motion_controll.py 0 0 0  
* motion_controll_scroll.py: moure el braç agafant una xarxa de punts, comprovar que no s'encalla (passava a vegades).  
Usage: python motion_controll_scroll.py
  Warning: hard coded els punts de la xarxa, controlar que no vagi massa lluny  

## Dependencies
Per generar els plots es necessita la llibreria pandas.  
Si no es té a la distribució original es pot fer source a TTS_venv: source ~/workspace/UpgradeII/TTSvenv/bin/activate  

## Passos:
1. source /home/heplab/OOFlex/env.sh
2. sudo gpib_config
3. posar setup.ini allà on poses les dades (?)


--------------------------------------------------------
--------------------------------------------------------

## Possibles errors:

### Comunicació amb el braç:


  File "motion_controll.py", line 17, in <module>  
    ESP300 = factory.getDevice( "motionController" )  
  File "/home/heplab/OOFlex/OOFlex/interface/InterfaceFactory.py", line 81, in getDevice  
    instr = InterfaceFactory.__instrMap[ self.__setup[ instr ][ "device" ] ]  
KeyError: 'ESP300'  


		Mirar que hi hagi la carpeta: /home/heplab/OOFlex/OOFlex/instruments/Newport  
		Mirar que a setup.ini hi hagi amb l'adressa gpib correcta: [motionController] device=ESP300 address=gpib:/  /1:0  
heplab@heplab-ALDA:~/workspace/UpgradeII/FromTheOtherPC$ cat setup.ini  
[motionController]  
device=ESP300  
address=gpib://1:0  

		Mirar que la comunicació sigui correcta:  
			sudo gpib_config  
			sudo ibtest  
Do you wish to open a (d)evice or an interface (b)oard?  
	(you probably want to open a device): d  
: w      
enter a string to send to your device: *IDN?  
sending string: *IDN?  

gpib status is:  
ibsta = 0x2100  < END CMPL >  
iberr= 0  

: r  
enter maximum number of bytes to read [1024]:  
trying to read 1024 bytes from device...  
received string: 'ESP300 Version 3.08 09/09/02  
'  
Number of bytes read: 30  
gpib status is:  
ibsta = 0x2100  < END CMPL >  
iberr= 0  




### Comunicació amb l'oscil.loscopi:
correr: python ~/Control/MSO9404A_waveform.py 10 ch1  
esborrar dades brossa generades: rm data-ch1-0.bin  
