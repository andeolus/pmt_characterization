# pmt_characterization
Make measurements on PMTs, analyze them and plot results. Features: Transient time spread, uniformity, Gain over HV...

## Contingut:
### measure
* **motion_controll.py**: moure el braç, comprovar que funciona.  
_Usage_: python motion_controll.py 0 0 0  
* **motion_controll_scroll.py**: moure el braç agafant una xarxa de punts, comprovar que no s'encalla  
_Usage_: python motion_controll_scroll.py xmin xmax xN ymin ymax yN --bool_wait  
* **mesura_PMT_scan.py**: fer mesures en una xarxa de punts, guardant dades a la carpeta "name" amb "num_waveforms" per punt  
_Usage_: python mesura_PMT_scan.py name num_waveforms xmin xmax xN ymin ymax yN  
### analyze
### plotters
* plotWaveform_P3.py
* HV_plotter.py

## Dependències
Per generar els plots es necessita la llibreria pandas.  
Si no es té a la distribució original es pot fer source a TTS_venv:  
source ~/workspace/UpgradeII/TTSvenv/bin/activate  

## Passos:
### Mesura
1. Connecta amb el braç Newport ESP300 Motion Controller  
    1. **source /home/heplab/OOFlex/env.sh**  
    2. Comprovar que funciona amb ***python motion_controll.py 0 0 0*** ;  
    si no funciona comprova "Possible errors": [Troubleshooting](#troubleshooting)  
    3. Comprovar que tampoc s'encalla entre punts amb python **motion_controll_scroll.py**  
2. Connecta amb l'oscil·loscopi, preferiblement PMT a ch1 i LASER a ch4  
    1. correr: **python ~/Control/MSO9404A_waveform.py 10 ch1** (també a utils/)  
    2. esborrar dades brossa generades: rm data-ch1-0.bin  
3. Busca la finestra de punts on s'han de fer les mesures  
    - amb motion_controll.py 0 0 0 troba un punt on vegis senyal  
    - amb **motion_controll_scroll.py*** troba els límits de la finestra  
    - pot ser convenient resetejar les coordenades del braç perquè tinguin un rang 0-max  
4. Executa **mesura_PMT_scan.py** als punts de la finestra  
    - python  mesura_PMT_scan.py name num_waveforms xmin xmax xN ymin ymax yN  



---

## Troubleshooting
### Comunicació amb el braç:
- posar setup.ini allà on s'executa motion_controll.py [o a utils/; pendent d'implementar]  
- sudo gpib_config  
- sudo ibtest  

```python
    File "motion_controll.py", line 17, in <module>  
        ESP300 = factory.getDevice( "motionController" )  
    File "/home/heplab/OOFlex/OOFlex/interface/InterfaceFactory.py", line 81, in getDevice  
        instr = InterfaceFactory.__instrMap[ self.__setup[ instr ][ "device" ] ]  
KeyError: 'ESP300'  
```

* Mirar que hi hagi la carpeta: /home/heplab/OOFlex/OOFlex/instruments/Newport  
* Mirar que a setup.ini hi hagi amb l'adressa gpib correcta:
```bash
heplab@heplab-ALDA:~/workspace/UpgradeII/$ cat setup.ini
```
```
[motionController]  
device=ESP300  
address=gpib://1:0  
```

* Mirar que la comunicació sigui correcta:

```bash
sudo gpib_config  
sudo ibtest  
```

```
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
received string: 'ESP300 Version 3.08 09/09/02'
Number of bytes read: 30  
gpib status is:  
ibsta = 0x2100  < END CMPL >  
iberr= 0  
```
