# OctoPNP
OctoPNP is an OctoPrint plugin for camera assisted pick 'n place applications in 3D-Printers.

# Introduction
OctoPNP is an extension that allows Octoprint to control printers and similar devices with additional hardware for handling of SMD-parts.
It currently requires the following hardware extensions:
* A Tray consisting of a grid of boxes to store SMD parts in a defined position
* A head camera to locate the exact part position on the tray
* A (second) bed camera to precisely align the parts during the placing operation
* A vaccum nozzle to grip parts

![octopnp_main_small](https://cloud.githubusercontent.com/assets/4190756/12094912/bf0e18b0-b30b-11e5-8111-a7cd94914f30.png)

# Installation
## Prerequirements
To achieve higher compatibility and modularity, OctoPNP doesn't acces the cameras directly. Every time an image is required, OctoPNP executes a user defined script which must be adapted for every installation according to the deployed camera setup. OctoPNP expects a set of correctly cropped and rotated images after executing the script. Filenames and path for images and script must be set in the settings dialog.

## Installing the package
The plugin itself can be installed as any regular python package:
`pip install https://github.com/platsch/OctoPPNP/archive/master.zip`

Make sure you use the same Python environment that you installed OctoPrint under, otherwise the plugin won't be able to satisfy its dependencies. Further information can be found in the Octoprint [documentation](http://docs.octoprint.org/en/devel/plugins/using.html)

## Data Format
The information for the PNP system is integrated into normal gcode files as a commented XML flavor somewhere in the gcode. OctoPNP extracts the required information automatically everytime a gcode file is loaded in Octoprint. Example files are included in the `utils` folder. The XML structure is still under development and will probably change during the next months. The comment-semicolon causes Octoprint to ignore the SMD-data.

```XML
;normal printing commands
G1 X10 F3000
G1 Y10 F3000
G1 Z5 F3000

;pick part nr 2 and place it to the destination given in the XML description
M361 P2

;description of the actual parts
;<object name="simple_lines">
;<part id="1" name="ATTINY">
;  <position box="1"/>
;  <size height="1"/>
;  <shape>
;    <point x="-2.6" y="-3.4"/>
;    <point x="-2.6" y="3.4"/>
;    <point x="2.6" y="3.4"/>
;    <point x="2.6" y="-3.4"/>
;  </shape>
;  <pads>
;    <pad x1="-2.155" y1="-4.254" x2="-1.655" y2="-2.054"/>
;    <pad x1="-0.895" y1="-4.254" x2="-0.395" y2="-2.054"/>
;    <pad x1="0.375" y1="-4.254" x2="0.875" y2="-2.054"/>
;    <pad x1="1.645" y1="-4.254" x2="2.145" y2="-2.054"/>
;    <pad x1="-2.155" y1="2.054" x2="-1.655" y2="4.254"/>
;    <pad x1="-0.885" y1="2.054" x2="-0.385" y2="4.254"/>
;    <pad x1="0.385" y1="2.054" x2="0.885" y2="4.254"/>
;    <pad x1="1.655" y1="2.054" x2="2.155" y2="4.254"/>
;  </pads>
;  <destination x="100" y="90" z="2.75" orientation="90"/>
;</part>
;
;<part id="2" name="RES_1206">
;  <position box="2"/>
;  <size height="1"/>
;  <shape>
;    <point x="-1.6891" y="-0.8763"/>
;    <point x="-1.6891" y="0.8763"/>
;    <point x="1.6891" y="0.8763"/>
;    <point x="1.6891" y="-0.8763"/>
;  </shape>
;  <pads>
;    <pad x1="0.622" y1="-0.9015" x2="2.222" y2="0.9015"/>
;    <pad x1="-2.222" y1="-0.9015" x2="-0.622" y2="0.9015"/>
;  </pads>
;  <destination x="108.304" y="90.674" z="2.75" orientation="0"/>
;</part>
;</object>
```
