#!/usr/bin/env python
"""
Created by Milan B. (C) 2017 www.bastl.sk

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
"""

import inkex
import re

defaults = {
'exc_header': """M48
VER,1
FMAT,2
ICI,OFF
""",
'exc_footer': """M30
"""
}


class C(inkex.Effect):
  def __init__(self):
    inkex.Effect.__init__(self)
    self.OptionParser.add_option("-m", "--mode",   action="store", type="string", dest="output_mode",   default="gcd",   help="Format of output file")
    self.OptionParser.add_option("-f", "--file",   action="store", type="string", dest="output_file",   default="output.gcode",   help="Name of output file")
    self.OptionParser.add_option("-u", "--unit",   action="store", type="string", dest="unit",   default="mm",   help="Unit")
    self.OptionParser.add_option("-x", "--maxsize",   action="store", type="float", dest="maxsize",   default=5.0,   help="Maximum drill diameter")
    self.OptionParser.add_option("", "--tab",   action="store", type="string", dest="dummy_tab",   default="",   help="")
    self.OptionParser.add_option("", "--header",   action="store", type="string", dest="gheader",   default="G92 X0 Y0 Z0|G90",   help="Program header")
    self.OptionParser.add_option("", "--footer",   action="store", type="string", dest="gfooter",   default="G28 X|M84",   help="Program Footer")
    self.OptionParser.add_option("", "--init-cmd",   action="store", type="string", dest="init_cmd",   default="",   help="Additional initialization")
    self.OptionParser.add_option("", "--spindle-on",   action="store", type="string", dest="spindle_on",   default="M03 S255",   help="Spindle ON Command")
    self.OptionParser.add_option("", "--spindle-off",   action="store", type="string", dest="spindle_off",   default="M05",   help="Spindle OFF Command")
    self.OptionParser.add_option("", "--tool-cmd",   action="store", type="string", dest="tool_cmd",   default="",   help="Tool Change Command")
    self.OptionParser.add_option("", "--msg-cmd",   action="store", type="string", dest="msg_cmd",   default="M117",   help="Display Message Command")
    self.OptionParser.add_option("", "--drill-height",   action="store", type="float", dest="drill_height",   default=0.0,   help="Drill Height")
    self.OptionParser.add_option("", "--safe-height",   action="store", type="float", dest="safe_height",   default=5.0,   help="Safe Height")
    self.OptionParser.add_option("", "--tool-change-height",   action="store", type="float", dest="tool_height",   default=35.0,   help="Tool Change Height")
    self.OptionParser.add_option("", "--drill-speed",   action="store", type="int", dest="drill_speed",   default=50,   help="Drill speed")
    self.OptionParser.add_option("", "--retract-speed",   action="store", type="int", dest="retract_speed",   default=700,   help="Retract speed")
    self.OptionParser.add_option("", "--move-speed",   action="store", type="int", dest="move_speed",   default=5000,   help="Move speed")


  def effect(self):

    def drill(l, dia):
      def excfmt(x):
        if self.options.unit == "mm":
	  return "%06d" % (int(x*1000))
	else:
	  return "%06d" % (int(x*10000))
        
      for t in l:
        cx,cy,d = t
	if d == dia:
          if self.options.output_mode == "gcd":
            # experimental - add wait begore move
            f.write("G04 P0\n")
            f.write("G00 X%.3f Y%.3f F%d\n" % (cx, cy, self.options.move_speed))
            f.write("G01 Z%.3f F%d\n" % (self.options.drill_height, self.options.drill_speed))
            f.write("G01 Z%.3f F%d\n" % (self.options.safe_height, self.options.retract_speed))
	  else:
            f.write("X%sY%s\n" % (excfmt(cx),excfmt(cy)))

    def tool_list(drills):
      i = 0
      if self.options.output_mode == "gcd":
        f.write("\n")
      for d in drills:
        if self.options.output_mode == "gcd":
	  f.write("; Tool %02d diameter: %f\n" % (40+i, d))
	else:
	  f.write("T%02dC%.3f\n" % (40+i, d))
	i = i+1

    def tool_change(drill_dia, index):
      if self.options.output_mode == "gcd":
        f.write("\n")
        f.write(self.options.spindle_off.replace("|","\n")+"\n")
        f.write("G00 Z%.3f F%d\n" % (self.options.tool_height, self.options.retract_speed))
        f.write("%s Change Drill: %.2f%s\n" % (self.options.msg_cmd.replace("|","\n"), drill_dia, self.options.unit))
        if self.options.tool_cmd != "":
	  f.write(self.options.tool_cmd.replace("|","\n")+"\n")
        f.write(self.options.spindle_on.replace("|","\n")+"\n")
        f.write("G00 Z%.3f F%d\n" % (self.options.safe_height, self.options.retract_speed))
#        if self.options.spindle_delay != 0:
#          f.write("G04 P%d\n" % (self.options.spindle_delay,))
        f.write("\n")
	
      else:
        f.write("T%02d\n" % (index+40))
        

    f = open(self.options.output_file, "w")

    # Create list of circles
    scale = self.uutounit(1, self.options.unit)
    l = []
    if len(self.selected) == 0:
      svg = self.document.xpath('//svg:circle',namespaces=inkex.NSS)
      for g in svg:
        cx=scale*float(g.get("cx"))
	cy=scale*float(g.get("cy"))
	d=2*scale*float(g.get("r"))
	if d <= self.options.maxsize:
	  l.append((cx, cy, d))
    else:
      for id, node in self.selected.iteritems():
        if node.tag == inkex.addNS('circle','svg'):
          cx=scale*float(node.get("cx"))
	  cy=scale*float(node.get("cy"))
	  d=2*scale*float(node.get("r"))
	  if d <= self.options.maxsize:
	    l.append((cx, cy, d))

    drills = []
    for t in l:
      x,y,r = t
      if not r in drills:
        drills.append(r)
	
    drills.sort()
    if self.options.output_mode == "gcd":
      f.write(self.options.gheader.replace("|","\n")+"\n")
      if self.options.unit == "mm":
        f.write("G21\n")
      else:
        f.write("G20\n")
      if self.options.init_cmd != "":
        f.write(self.options.init_cmd.replace("|","\n")+"\n")
    else:
      f.write(defaults['exc_header'])
      if self.options.unit == "mm":
        f.write("METRIC,000.000\n")
      else:
        f.write("INCH,LZ\n")

    tool_list(drills)

    if self.options.output_mode == "exc":
      f.write("%\n")

    ix = 0
    for d in drills:
      tool_change(d, ix)
      drill(l,d)
      ix = ix+1

    if self.options.output_mode == "gcd":
      f.write(self.options.spindle_off.replace("|","\n")+"\n")

    if self.options.output_mode == "gcd":
      f.write(self.options.gfooter.replace("|","\n")+"\n")
    else:
      f.write(defaults['exc_footer'])

    f.close()


c = C()
c.affect()
