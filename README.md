# LaserBiArc
Inkscape Extension for Laser Engravers/Cutters. Generates G-Codes using BiArcs. (G2/G3 G-Codes)

The heart of this extension is BiArc.py which is a translation from haskell code BiArc.hs

https://github.com/domoszlai/juicy-gcode/blob/master/src/Approx/BiArc.hs

 CodeConvert AI has been used to convert from haskell to python

The extension uses 3 files: (where numbers are year and month)
```
LaserBiArc.25.10.inx
LaserBiArc.25.10.py
BiArc.py (library-file)
```
The folder LaserBiArc containing these files can ba copied to the extensions folder.

 On my LinuxPC, Ubuntu 24.04  the files are in 
```
 /home/jan/.config/inkscape/extensions 
```

The Inkscape extensions folder is found via
Edit > Preferences > System > User extensions in the program's settings

My Inkscape v.1.4.2 (installed using PPA, not snap).  
Inkscape >= 1.0 required.

Extensions -> EM-Teknik is the submenue.

This is also the home for interpolate and OpenSCAD extensions (to be released)

Select paths, Use Extension->EM-Teknik->laserBiArc.25.10, Apply

First time used Folder and filename has to be set.

Use one filename for "production" and one for testing. (no autonumbering)

<img width="532" height="775" alt="Skärmbild från 2025-10-20 18-37-31" src="https://github.com/user-attachments/assets/d474c7a5-e9bb-4381-87ed-f88148a8c811" />

Example 

Top: Gcodetool
Middle: laserBiArc
Bottom: Original (few nodes, control points not shown)

<img width="961" height="561" alt="Skärmbild från 2025-10-20 19-06-04" src="https://github.com/user-attachments/assets/954b18ef-6427-4f38-ac49-b4f5753311f5" />

Everything has to be path. Use Object to path.

<img width="1377" height="742" alt="Skärmbild från 2025-10-20 19-18-27" src="https://github.com/user-attachments/assets/b472d366-a4fa-4519-856f-24d93b8044c9" />
<img width="1377" height="742" alt="Skärmbild från 2025-10-20 19-23-37" src="https://github.com/user-attachments/assets/11b7fc37-abfe-4a89-87f9-fa2ff6f04923" />

ref, refpath (set the origin for G-code)

Any path shape can be used to set ref. Just set ID of the path to refpath.
REMEMBER to press the Set button in the Object Properties menue to activate the change. The lower left corner of refpath is ref.
Note: The line width of refpath is used for the corresponding svg.

I use to burn the refpath "shape" on the laser-bed. Move by hand the laser to ref. 

<img width="1069" height="635" alt="Skärmbild från 2025-10-21 11-46-16" src="https://github.com/user-attachments/assets/d6d592f5-07a8-4637-ab71-8bd5318b2d6a" />

Power setting by Opacity.

<img width="1451" height="280" alt="Skärmbild från 2025-10-21 12-26-54" src="https://github.com/user-attachments/assets/90b62dce-dbd8-48d4-85c5-8325e43dd1cf" />

Burn the cat....

<img width="884" height="490" alt="Skärmbild från 2025-10-21 13-51-56" src="https://github.com/user-attachments/assets/4aee7ca5-d623-411a-9bc6-68b7888821d1" />
