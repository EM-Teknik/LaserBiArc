#LaserBiArc.25.12.py
#
# License: GPL3
# Copyright (c) Jan Knuts EM-Teknik (jan.knuts@gmail.com)
# https://github.com/EM-Teknik/LaserBiArc
#

#import sys
#sys.path.insert(0, '/usr/share/inkscape/extensions')

import inkex

from inkex import bezier, Transform

from inkex.paths import CubicSuperPath, Path

from inkex.elements import PathElement, Group, Line     #, ElementList

from typing import List, Tuple

from BiArc2602 import CubicBezier, BiArc, bezier2biarcs, LineTo, ArcTo, distance, BiArc_par    #, isClockwise3 not used now

import math


class gcode(inkex.EffectExtension):
    def add_arguments (self, pars):

        pars.add_argument ("--laser_on_command", type=str, default="M03", help="Laser on command")
        pars.add_argument ("--laser_off_command", type=str, default="M05", help="Laser off command")
        pars.add_argument ("--laser_speed", type=int, default=750, help="Laser speed (mm/min)")
        pars.add_argument ("--travel_speed", type=int, default=3000, help="Travelr speed (mm/min)")
        pars.add_argument ("--laser_power", type=int, default=255, help="255 or 10000 for full power")
        pars.add_argument ("--laser_power_scaled", type=inkex.Boolean, help="power scaled by opacity")      
        pars.add_argument ("--zmove", type=int, default=1, help="0 to 10")      
        #pars.add_argument ("--sel_refpath_right", type=inkex.Boolean, help="refpath corner")      
        pars.add_argument ("--biarc", type=inkex.Boolean, help="gcode flawor")
        pars.add_argument ("--use_inflP", type=inkex.Boolean, help="use inflection points")    
        pars.add_argument ("--flatness", type=float, default=1, help="flatness(0-10)")
        pars.add_argument ("--passes", type=int, default=1, help="1 to 10")      
        pars.add_argument ("--save1", type=inkex.Boolean, default="true" , help="save1")        
        pars.add_argument ("--folder1", type=str, help="Path")
        pars.add_argument ("--filename1", type=str, help="Filename")
        #pars.add_argument ("--save2", type=inkex.Boolean, help="save1")        
        #pars.add_argument ("--folder2", type=str, help="Path")
        #pars.add_argument ("--filename2", type=str, help="Filename")
        pars.add_argument ("--dn", type=int, default=0, help="0 to 5 debug info")

    def debug(self,dn,no,msg):
        if no==dn:
            self.msg(msg)

# start of code based on ...
# License: GPL2
# Copyright Mark "Klowner" Riedesel
# https://github.com/Klowner/inkscape-applytransforms
#

    NULL_TRANSFORM = Transform([[1.0, 0.0, 0.0], [0.0, 1.0, 0.0]])

    @staticmethod
    def objectToPath(node):
        if node.tag == inkex.addNS('g', 'svg'):
            return node

        if node.tag == inkex.addNS('path', 'svg') or node.tag == 'path':
            for attName in node.attrib.keys():
                if ("sodipodi" in attName) or ("inkscape" in attName):
                     del node.attrib[attName]
            return node

        return node

    def recursiveFuseTransform(self, node, transf=[[1.0, 0.0, 0.0], [0.0, 1.0, 0.0]]):
        transf = Transform(transf) @ Transform(node.get("transform", None))
        #transf = Transform(transf) * Transform(node.get("transform", None))   #depreciated

        node = self.objectToPath(node)

        if 'transform' in node.attrib:
            del node.attrib['transform']

        if transf == self.NULL_TRANSFORM:
            # Don't do anything if there is effectively no transform applied
            # reduces alerts for unsupported nodes
            pass
        elif 'd' in node.attrib:
            d = node.get('d')
            p = CubicSuperPath(d)
            p = Path(p).to_absolute().transform(transf, True)
            node.set('d', str(Path(CubicSuperPath(p).to_path())))
        '''
        if isinstance(node, inkex.PathElement):
            self.rec_sel.extend(node)
            self.msg("rec_sel: %s" % (self.rec_sel))
        '''
        for child in node.getchildren():
            self.recursiveFuseTransform(child, transf)
#
# License: GPL2
# Copyright Mark "Klowner" Riedesel
# https://github.com/Klowner/inkscape-applytransforms
# end of code based on ..

    
    def effect(self):
   
        laser_on_command=self.options.laser_on_command
        laser_off_command=self.options.laser_off_command
        travel_speed=self.options.travel_speed
        laser_speed=self.options.laser_speed
        laser_power=self.options.laser_power
        laser_power_scaled=self.options.laser_power_scaled
        zmove=self.options.zmove
        #sel_refpath_right=self.options.sel_refpath_right

        biarc=self.options.biarc 
  
        #use_inflP=self.options.use_inflP
        use_inflP=True
        BiArc_par.use_inflP=use_inflP
        
        passes=self.options.passes
        save1=self.options.save1 
        folder1=self.options.folder1
        file1=self.options.filename1
        #save2=self.options.save2 
        #folder2=self.options.folder2
        #file2=self.options.filename2
        
        dn=self.options.dn              #debug number       
        BiArc_par.dn=dn
 
        layer = self.svg.get_current_layer()

               
        #get the refpath used
        refpathl = self.svg.getElementById('refpathl')
        refpathr = self.svg.getElementById('refpathr')
        self.debug(dn,5,"refpathl %s refpathr %s" % (refpathl,refpathr))
        if refpathr is not None:          
            self.debug(dn,5,"refpathr %s" % refpathr.get("d"))
            self.debug(dn,5,"refpathr transform: %s" % (refpathr.get("transform")))
            stroke_width=refpathr.style['stroke-width']
            stroke_color=refpathr.style['stroke']
            refx = refpathr.bounding_box().right
            refy = refpathr.bounding_box().bottom 
        elif refpathl is not None:
            self.debug(dn,5,"refpathl %s" % refpathl.get("d"))
            self.debug(dn,5,"refpathl transform: %s" % (refpathl.get("transform")))
            stroke_width=refpathl.style['stroke-width']
            stroke_color=refpathl.style['stroke']
            refx = refpathl.bounding_box().left
            refy = refpathl.bounding_box().bottom 
        else:
            #refpath is "document"
            stroke_width=0.2     #default if no refpath
            stroke_color='red' #default if no refpath
            vb=self.svg.get_viewbox()
            self.debug(dn,5,"svg.get_viewbox() %s" % (vb))         
            refx, refy = vb[0], vb[3]  #viewbox size ex A4 [0.0, 0.0, 210.0, 297.0]
            self.debug(dn,5,"viewbox lower left corner x=%s y=%s " % (refx,refy))

            #add refpathr refpathl
            pel1 = PathElement()
            pel1.set('d','m {:.1f},{:.1f} h  -5 l 3,-1 -8,-9 9,8 1,-3 z'.format(refx,refy))
            pel1.set('id', 'refpathr')
            pel1.set("label", "refpathr")   #inkscape:label
            pel1.style['stroke'] = stroke_color
            pel1.style['stroke-width'] = stroke_width 
            pel1.style['fill'] = 'orange'  
            layer.add(pel1)

            pel2 = PathElement()
            pel2.set('d','m {:.1f},{:.1f} h 5 l -3,-1 8,-9 -9,8 -1,-3 z'.format(refx,refy)) 
            pel2.set('id', 'refpathl')
            pel2.set("label", "refpathl")
            pel2.style['stroke'] = stroke_color
            pel2.style['stroke-width'] = stroke_width 
            pel2.style['fill'] = 'lightgreen'  
            layer.add(pel2)

            self.msg('adding refpaths .. keep the one to use!')
            self.msg('refpathr .. points down, right !')
            self.msg('refpathl .. points down, left !')
            self.msg('if two refpaths exist .. refpathr is used! ')

        self.debug(dn,5,"refpath stroke_width: %s color %s" % (stroke_width,stroke_color))               
        self.debug(dn,5,"refx {:.2f} refy {:.2f}".format(refx,refy))
        #self.debug(dn,5,"refpath transform: %s" % (refpath.get("transform")))
                           
        gcode_svg=PathElement() 
        #gcode_svg.style='stroke:stroke_color; stroke-width:stroke_width;fill:none'
        gcode_svg.style['stroke'] = stroke_color
        gcode_svg.style['stroke-width'] = stroke_width    
        gcode_svg.style['fill'] = 'none'
       
        my_svgl="" 
        my_svgc=""

        gl=""
        gc=""
        
        if zmove > 0:
            gc_begin="M05 S0\nG90\nG21\nG1 F%s\nG1 Z%s\n" % (travel_speed,zmove)  #init for circular gcode
            gl_begin="M05 S0\nG90\nG21\nG1 F%s\nG1 Z%s\n" % (travel_speed,zmove)  #init for linear gcode
        else:
            gc_begin="M05 S0\nG90\nG21\nG1 F%s\n" % (travel_speed)  #init for circular gcode
            gl_begin="M05 S0\nG90\nG21\nG1 F%s\n" % (travel_speed)  #init for linear gcode

        # before path depends on calculated values "on the fly"

        if zmove > 0:
            gc_after_path="G4 P0\n%s S0\nG1 F%s\nG1 Z%s\n" % (laser_off_command,travel_speed,zmove)     # "gcode after path"
            gl_after_path="G4 P0\n%s S0\nG1 F%s\nG1 Z%s\n" % (laser_off_command,travel_speed,zmove)     # "gcode after path"
        else:
            gc_after_path="G4 P0\n%s S0\nG1 F%s\n" % (laser_off_command,travel_speed)     # "gcode after path"
            gl_after_path="G4 P0\n%s S0\nG1 F%s\n" % (laser_off_command,travel_speed)     # "gcode after path"

        gl_home ="G1 X0 Y0\n"            # home        
        gc_home ="G1 X0 Y0\n"            # home
      
        path_list=[]       
       
        select_elems = self.svg.selection.filter(PathElement)
        self.debug(dn,1,"select_elems: %s" % (select_elems))

        if self.svg.selection:
            #for (_, shape) in self.svg.selection.items():
            for (key, shape) in self.svg.selection.items():
                self.debug(dn,1,"key: %s .. shape: %s transform %s" % (key,shape,shape.get("transform", None)))
                self.recursiveFuseTransform(shape)
        
        selection = self.svg.selection.get(PathElement)	#fungerar på grupperade path  ... recursive search !!
        
        self.debug(dn,1,"selection %s " % (selection))

        for element in selection:

            #self.msg("el_key %s el_val %s" % (el_key,el_val))
            self.debug(dn,1,"element: %s len() %s " % (element,len(element)))
            self.debug(dn,1,"element transform: %s" % (element.get("transform")))          

        path_list = selection

        p1=[0,0]     #used in biarc section
        
        if len(path_list) < 1:
            self.msg('No Path found !')
            self.msg('Remember to use Path->Object to Path for non Path objects!')
            return
        self.debug(dn,1,"\nlen(path_list)=%s\n" % (len(path_list)))
        
        self.debug(dn,1,"biarc= %s" % (biarc))

        if not biarc:   #linear
            for np,path in enumerate(path_list):
                #control laser_power using opacity
                opacity=path.style("opacity")                   #style="opacity:0.5;fill:#000000;fill-opacity:1;stroke:none"
                self.debug(dn,3,"opacity %s" % (opacity))

                if laser_power_scaled:
                    laser_power_adjusted=laser_power*opacity
                else:
                    laser_power_adjusted=laser_power
                
                csp_list = path.path.to_superpath()             #cubic super path=list of  [[control, node, control]....
                self.debug(dn,1,"np= %s csp_list= %s" % (np,csp_list))

                bezier.cspsubdiv(csp_list, self.options.flatness)   #use flatness..adds nodes in superpath
                
                for nc,csp in enumerate(csp_list): 

                    self.debug(dn,1,"nc %s csp =%s" % (nc,csp))
                  
                    first=True
                    for npt,pt in enumerate(csp):                            #cp (control point) or pt (point) instead of pt ??
                    
                        self.debug(dn,1,"npt %s pt %s" % (npt,pt))

                        p1x, p1y=pt[1][0], pt[1][1]             # pt[0="left" control, 1=node, 2="right" control] [ 0=x ,1=y ]

                        if first:
                            first=False
                            if zmove > 0:
                                gl +="G0 X{:.3f} Y{:.3f}\nG1 Z0\n".format(p1x-refx, refy-p1y)                                                   
                            else:
                                gl +="G0 X{:.3f} Y{:.3f}\n".format(p1x-refx, refy-p1y)                                                   
 
                            gl +="G4 P0\n{} S{:.1f}\nG4 P0\n".format(laser_on_command,laser_power_adjusted)  #std laser_on_command (M03) laser_power(Sxxx)

                            gl +="G1 F750.00\n"                     

                            my_svgl+="M %s %s" % ( p1x, p1y )

                        gl +="G1 X{:.3f} Y{:.3f}\n".format(p1x-refx, refy-p1y)  

                        my_svgl+="L %s %s" % ( p1x, p1y )
                                                               
                    #gl +="G4 P0\nM05 S0\nG1 F3000\nG1 Z5\n"      # "gcode after path"
                    gl +=gl_after_path
                    my_svgl+="\n"

        else:   #BiArc
            for np,path in enumerate(path_list):
                #control laser_power using opacity
                opacity=path.style("opacity")                   #style="opacity:0.5;fill:#000000;fill-opacity:1;stroke:none"
                self.debug(dn,3,"opacity %s" % (opacity))

                if laser_power_scaled:
                    laser_power_adjusted=laser_power*opacity
                else:
                    laser_power_adjusted=laser_power
                
                csp_list = path.path.to_superpath()             #cubic super path=list of  [[control, node, control]....
                self.debug(dn,4,"\nnp= %s csp_list= %s\n" % (np,csp_list))

                # BiArc
                first=True
               
                for npc,csp in enumerate(csp_list):                            #cp (control point) or pt (point) instead of pt ??
                    self.debug(dn,2,"\nnpc= %s len(csp_list)= %s\n" % (npc,len(csp_list)))
                    first=True
                    firstp1=True
                    for nc in range(0,len(csp)-1):      # nc and nc+1 is used as index (n) in csp (cubic superpath)  (ncsp !! bättre)                       
                        self.debug(dn,2,"BiArc..npc=%s nc=%s" % (npc,nc) )
                        if firstp1:
                            p1=csp_list[npc][nc][1]
                            firstp1=False
                    
                        p1x, p1y = p1[0], p1[1]                   
                        c1=csp_list[npc][nc][2]
                        c2=csp_list[npc][nc+1][0]
                        p2=csp_list[npc][nc+1][1]

                        #self.msg("p1 %s c1 %s c2 %s p2 %s" % (p1,c1,c2,p2) )                     
                        bez=CubicBezier(p1,c1,c2,p2)        #this is the notation from  https://github.com/domoszlai/juicy-gcode
                        #self.msg(bez)
                        cmds = bezier2biarcs(bez, 0.1)      # 0.1 hard coded ..
                        #self.msg(cmds)

                        for cmd in cmds:
                            if first:
                                first=False                                               
                                #gc +="G1 X{:.4f} Y{:.4f}\nG1 Z0\n".format(p1x-refx,refy-p1y )                                                   
                                gc +="G1 X{:.4f} Y{:.4f}\n".format(p1x-refx,refy-p1y )                                                   
                                gc +="G4 P0\n{} S{:.1f}\nG4 P0\n".format(laser_on_command,laser_power_adjusted)  #std laser_on_command (M03) laser_power(Sxxx)
                                if zmove > 0:
                                    gc +="G1 F%s\nG1 Z0\n" % (laser_speed)                          #std laser_speed (Fxxx)
                                else:
                                    gc +="G1 F%s\n" % (laser_speed)                          #std laser_speed (Fxxx)
                                gc +="G0 X{:.4f} Y{:.4f}\n".format(p1x-refx,refy-p1y)
                            
                                my_svgc+="M %s %s" % (p1x,p1y)

                            if isinstance(cmd, LineTo):
                                #helper..reference using x,y etc for G01
                                px, py=cmd.point[0], cmd.point[1]
                                p=[px,py]

                                gc +="G1 X{:.4f} Y{:.4f}\n".format(px-refx,refy-py)
                            
                                p1=p    #current pos after g-command
                            
                                my_svgc+="L %s %s" % ( px, py )
                                self.debug(dn,1,"LineTo {:.5f} {:.5f}".format(px, py) )
                        
                            elif isinstance(cmd, ArcTo):
                                #helper..reference using x,y etc for G02 and G03
                                (cx,cy)=(cmd.center[0],cmd.center[1])           # [ 0=x ,1=y ]
                                c=[cx,cy]
                                (p1x,p1y)=p1
                                (p2x,p2y)=(cmd.endpoint[0],cmd.endpoint[1])
                                p2=[p2x,p2y]
                                dcx=(cx-p1x)
                                dcy=(cy-p1y)
                                                                                   
                                #r1=distance([p1[0],p1[1]],cmd.endpoint)
                                r2=distance(cmd.center,cmd.endpoint)
                            
                                #iscw=isClockwise3(p1, c, p2)        #from BiArc.py 
                                ##iscw= not isClockwise3(p1, p2, c)  #from BiArc.py 
                                iscw=cmd.isClockwise                 #JK now corrected in BiArc2602.py
 
                                self.debug(dn,1,"ArcTo {:.4f} {:.4f} {:.4f} {:.4f} cmd.isClockwise={} iscw={}".format(cx,cy,p2x,p2y,cmd.isClockwise,iscw ) )

                                cw=0
                                gcmd="G3"
                                if iscw:
                                     cw=1
                                     gcmd="G2"

                                if not (math.isnan(p2x) or math.isnan(p2y) or math.isnan(cx) or math.isnan(cy)) :
                                    gc+="{} X{:.4f} Y{:.4f} I{:.4f} J{:.4f}\n".format(gcmd, (p2x-refx),(refy-p2y),dcx,-dcy )
                                else:
                                    self.msg("Warning..isnone occured..skipping Arc in G-code at p1={:.4f},{:.4f} p2={:.4f},{:.4f}".format(p1x,p1y,p2x,p2y))

                                p1=p2                           #current pos after g-command

                                if not (math.isnan(p2x) or math.isnan(p2y) or math.isnan(r2)) :                                           
                                    my_svgc+="A %s %s %s %s %s %s %s\n" % (r2, r2, 0, 0, cw, p2x, p2y)
                                    #my_svgc+="A {:.4f} {:.4f} {} {} {} {:.4f} {:.4f}".format(r2, r2, 0, 0, cw, p2x, p2y)
                                else:
                                    self.msg("Warning..isnone occured..skipping Arc in SVG at p2={:.4f},{:.4f} r2={:.4f}".format(p2x,p2y,r2))
                                    #my_svgc+="L %s %s" % ( p2x, p2y )
 
                    gc +=gc_after_path

                #self.msg(my_svgc)               
        
        if biarc:
            gcode_svg.path = my_svgc # circular (biarc)
        else:
            gcode_svg.path = my_svgl # linear
        
        layer.append(gcode_svg) 

        #self.msg(gcode_svg.path)

        '''
        # this is OK in ubuntu but not windows.. skip it
        if "/" in folder1:           # linux (ubuntu)  
            if folder1[-1] != '/':
                folder1+="/"
        elif "\\" in folder1:        # windows
            if folder1[-1] != '\\':
                folder1+="\\"
        if "/" in folder2:           # linux (ubuntu)  
            if folder2[-1] != '/':
                folder2+="/"
        elif "\\" in folder2:        # windows
            if folder2[-1] != '\\':
                folder2+="\\"
        '''
        if biarc:
             g=gc_begin
             for np in range(passes):
                 g+=gc
             g+=gc_home
        else:
             g=gl_begin
             for np in range(passes):
                 g+=gl             
             g+=gl_home

        with open(folder1+file1, "w") as f:
            f.write(g)

        '''
        if save1:
            with open(folder1+file1, "w") as f:
                f.write(g)

        if save2:
            with open(folder2+file2, "w") as f:
                f.write(g)
        '''
		
if __name__ == '__main__':
    gcode().run()
    
'''    

'''   
    
    
