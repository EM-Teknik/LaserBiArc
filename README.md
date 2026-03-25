# LaserBiArc

Inkscape Extension for Laser Engravers/Cutters. Generates G-Codes using BiArcs. (G2/G3 G-Codes)

The T (Tool) version can make tool compensated G-Code for cutters.

New improved version ..2603B.. (old for reference) The BiArc.py library file is now altered and renamed to BiArc2603B.

The heart of this extension is BiArc.py which is a translation from haskell code BiArc.hs

https://github.com/domoszlai/juicy-gcode/blob/master/src/Approx/BiArc.hs

 CodeConvert AI has been used to convert from haskell to python

The extension uses 3 files: (where numbers are year and month)
```
New:
LaserBiArc2603BT.inx
LaserBiArc2603BT.py
BiArc2603B.py
Old: (dont use)
...
BiArc.py (original library-file for reference)
```
The folder LaserBiArc containing these files can ba copied to the extensions folder.

 On my LinuxPC, Ubuntu 24.04  the files are in 
```
 /home/jan/.config/inkscape/extensions 
```

The Inkscape extensions folder is found via
Edit > Preferences > System > User extensions in the program's settings

My Inkscape v.1.4.2 and v1.2.2 OK (installed using PPA, not snap).  
Inkscape >= 1.2 required...? (v1.1.. does not work .. inkex too old)

Extensions -> EM-Teknik is the submenue.

This is also the home for interpolate and OpenSCAD extensions (to be released)

Select paths, Use Extension->EM-Teknik->laserBiArc2603, Apply

First time used Folder and filename has to be set.

New: (takes less space .. good for older laptops) 

Note: Z-axis move set to zero .. No Z-axis gcodes are generated (for my 10 W Longer Laser-engraver)

<img width="480" height="648" alt="image" src="https://github.com/user-attachments/assets/1347f815-01d6-45a5-87ab-baa1420790f4" />


Example 

Top: Gcodetool
Middle: laserBiArc
Bottom: Original (few nodes, control points not shown)

<img width="961" height="561" alt="Skärmbild från 2025-10-20 19-06-04" src="https://github.com/user-attachments/assets/954b18ef-6427-4f38-ac49-b4f5753311f5" />

Everything has to be path. Use Object to path.

<img width="1377" height="742" alt="Skärmbild från 2025-10-20 19-18-27" src="https://github.com/user-attachments/assets/b472d366-a4fa-4519-856f-24d93b8044c9" />
<img width="1377" height="742" alt="Skärmbild från 2025-10-20 19-23-37" src="https://github.com/user-attachments/assets/11b7fc37-abfe-4a89-87f9-fa2ff6f04923" />

ref, refpath (set the origin for G-code)

New: refpathr and refpathl are automatic inserted into the document. Delete the one you dont want to use. 
The ID refpath is no longer used.

Any path shape can be used to set ref. Just set ID of the path to refpathr or refpathl.
REMEMBER to press the Set button in the Object Properties menue to activate the change. The lower (new: right or left) left corner of refpath is ref.
Note: The line width and color of refpath is used for the corresponding svg.

I use to burn the refpath "shape" on the laser-bed. Move by hand the laser to ref. 

Below is refpathr selected. Note the Power test pattern.

<img width="2301" height="1296" alt="image" src="https://github.com/user-attachments/assets/de6329e2-b0f2-4afe-997e-23e14749872e" />

Power setting by Opacity.

<img width="1451" height="280" alt="Skärmbild från 2025-10-21 12-26-54" src="https://github.com/user-attachments/assets/90b62dce-dbd8-48d4-85c5-8325e43dd1cf" />

Doggo from domoszlai...

<img width="1438" height="605" alt="image" src="https://github.com/user-attachments/assets/94ceb8d4-8ca5-4ea9-978f-cb8c46030d55" />


Burn the cat....

<img width="884" height="490" alt="Skärmbild från 2025-10-21 13-51-56" src="https://github.com/user-attachments/assets/4aee7ca5-d623-411a-9bc6-68b7888821d1" />

Dedicated to my first follower.. Yumi...  https://github.com/yumiaura

<img width="980" height="622" alt="Skärmbild från 2025-10-30 09-16-58" src="https://github.com/user-attachments/assets/d5d572b5-a1d8-482a-90d5-a919197e6424" />

Model Airplane (uses exact interpolation for wing ribs .. extension to be relesed)

<img width="1302" height="845" alt="Skärmbild från 2025-11-01 14-35-30" src="https://github.com/user-attachments/assets/9772f29f-fe28-496c-a940-c7e50036620f" />

<img width="983" height="646" alt="Skärmbild från 2025-11-01 14-32-04" src="https://github.com/user-attachments/assets/892dcf13-c640-4951-9d40-2769fd909900" />

<img width="889" height="417" alt="Skärmbild från 2025-11-01 14-31-02" src="https://github.com/user-attachments/assets/0c7aa240-08f1-465c-85b3-ed217b2e6094" />

<img width="1317" height="990" alt="bild" src="https://github.com/user-attachments/assets/4dca75b5-cdb9-4892-ac2e-aaf8d0cd9477" />

Load G-code in to bCNC (needs Z-axis move .. set to number greater than 0)  and...Just press play...

<img width="1498" height="814" alt="Skärmbild från 2025-10-29 21-54-27" src="https://github.com/user-attachments/assets/cb913045-5697-430b-9545-41740f2bbe2d" />

or .. gSender (Z-axis move = 0 .. for my 10 W Longer Laser-engraver .. does not accept Z-axis gcodes)

<img width="2470" height="1297" alt="bild" src="https://github.com/user-attachments/assets/a88df071-64fb-4483-831c-21dd9344b69b" />

Longer 10W laser

![20260315_123412](https://github.com/user-attachments/assets/dd5664ea-3e47-43b4-aee2-e40c52c7a86d)


Tool:  toolpathl or toolpatr (works only when BiArc is selected)

# IMPORTANT !! The spindle control is the same as for Laser. On/Off for each path. Use manual control for the spindle !!

First: 

To enable toolpath create a path, set path ID to toolpathl or toolpatr, set color and pen width (is tool diameter)

To disable .. delete the "toolpath" or change ID. (below the "toolpath" is selected .. check the ID .. remember the Set button)

Then:

This is a 2 stage process.

1. Select path to use. Apply.
toolpathl creates a path at left side of selected path. toolpathr creates a path at right.
GCode is generated for the selected path.
 
2. Select the new created toolpath and press Apply again. This is the GCode for the cutter.


<img width="2082" height="793" alt="Skärmbild från 2026-03-24 17-10-40" src="https://github.com/user-attachments/assets/3bedbba6-4f1d-4961-bf16-ae61eeedc4b1" />

Before step 2 you can edit the toolpath. (gear example)

1. The inner corner will owercut.
2. Add nodes on the line or arc.
3. Delete some end nodes and not nessesary nodes ... done

<img width="949" height="984" alt="Skärmbild från 2026-03-24 16-53-28" src="https://github.com/user-attachments/assets/7434b864-7f84-499b-99cc-44f47914508e" />

Flipping a path shifts inner/outercut. (dots here shows the original path)

<img width="732" height="834" alt="Skärmbild från 2026-03-24 17-04-15" src="https://github.com/user-attachments/assets/3ee37305-476b-44cc-8d1c-6c00fe0b74dd" />

