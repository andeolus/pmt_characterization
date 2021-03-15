# pmt_characterization
Make measurements on PMTs, analyze them and plot results. Features: Transient time spread, uniformity, Gain over HV...

## Contingut

### measure
* **motion_controll.py**: moure el braç, comprovar que funciona.  
_Usage_: python motion_controll.py 0 0 0  
* **motion_controll_scroll.py**: moure el braç agafant una xarxa de punts, comprovar que no s'encalla  
_Usage_: python motion_controll_scroll.py xmin xmax xN ymin ymax yN --bool_wait  
* **mesura_PMT_scan.py**: fer mesures en una xarxa de punts, guardant dades a la carpeta "name" amb "num_waveforms" per punt  
_Usage_: python mesura_PMT_scan.py name num_waveforms xmin xmax xN ymin ymax yN  

### analyze
* **pmt_uniformity_analyze.py**  
Analyzes a list of files for different coordinates or settings and prints analyzed data to the output file TTS.txt  
It needs the directory containing the data files or the list of files.  
If a directory is given, data files in it must start with P (ensured by measure/mesura_PMT_scan.py).
Data files should contain \_X\*mm and \_Y\*mm with \* being the coordinates.  
Creates a TTS.txt file with the relevant info which can be used latter by plotters/TTS_plotter  
_Usage_: python3 pmt_uniformity_analyze.py [-h] [pedestal range] [signal init] [signal end] data_files  
```
usage: pmt_uniformity_analyze.py [-h]
                                 [pedRange] [cut_ini] [cut_end] ficheros
                                 [ficheros ...]

Analyzes measurements of a PMT in a grid of points Provide the name of the
folder containing data.

positional arguments:
  pedRange    range from 0 to calculate pedestal mean (in samples, usually of
              0.2 ns)
  cut_ini     starting point of signal (in samples)
  cut_end     ending point of signal (in samples)
  ficheros    directory were data is stored or list of data files. Files
              should start with P

optional arguments:
  -h, --help  show this help message and exit
```

Defaults
  - pedRange = 200 ;  description: pedestal range (in samples)  
  - cut_ini = 250  ;  description: signal init (in samples)  
  - cut_end = 1024 ;  description: signal end (in samples)  
  - ficheros = []  ;  description: directory containing the data files or the list of files  

* old: **TTS.py**  
analyze uniformity using all the files for different points.  
The direcory of the files can be given alternatively to a list of all files. files must start with P (ensured by measure/mesura_PMT_scan.py).  
creates a TTS.txt file with the relevant info which can be used latter by plotters/TTS_plotter  
_Usage_: python3 analyze_PMT_uniformity.py <-r [pedestal range]> <-i [signal init]> <-e [signal end]> <-n [number of points]> <-h [help]> data_files  
Defaults
  - pedRange = 200 ;  description: [pedestal range]  
  - cut_ini = 250  ;  description: [signal init]  
  - cut_end = 1024 ;  description: [signal end]  
  - ficheros = []  ;  description: description: directory containing the data files or the list of files  
  - numPoints= 0   ;  description: not used, inherited from previous scripts that applyied filters [number of points]  

### plotters
* **TTS_plotter.py**  
Plot trasient time, transit time spread and mean signal amplitude of a given PMT.  
Needs the name of the input file containing the information, typically TTS.txt or TTS_wma.txt  
Needs the pandas module  
_Usage_: python3 pmt_uniformity_plotter.py [-h] [--cfd_frac [CFD_FRAC]] [--cfd_cut]  [-w [xmin] [xmax] [ymin] [ymax]] [-n [WINDOW_NAME]] [input_file]
```
positional arguments  
  input_file            path [/name] of the file containing the analyzed data  
optional arguments  
  -h, --help            show this help message and exit  
  --cfd_frac [CFD_FRAC]  
                        CFD threshold, default: 0.5  
  --cfd_cut [CFD_CUT]   apply cut to plot only the given CFD threshold (input  
                        file could contain more than one)  
  -w [WINDOW [WINDOW ...]], --window [WINDOW [WINDOW ...]]  
                        restrict plot to a particular window of xmin xmax ymin  
                        ymax  
  -n [WINDOW_NAME], --window_name [WINDOW_NAME]  
                        name of the window you are plotting, eg: whole or  
                        region15x15  
```
* old: **TTS_plotter.py**  
generates plots directly in running directory  
needs pandas module
_Usage_: python3 TTS_plotter.py  
Hard coded parameters:  
  - datadir='TS0340_09sep/'  
  - input file TTS_wma.txt -> needs to be changed tot TTS.txt eventually  

* **plotWaveform_P3.py**:  
* **HV_plotter.py**:

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
