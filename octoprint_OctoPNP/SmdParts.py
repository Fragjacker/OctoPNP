# coding=utf-8
from __future__ import absolute_import

__author__ = "Florens Wasserfall <wasserfall@kalanka.de>"
__license__ = 'GNU Affero General Public License http://www.gnu.org/licenses/agpl.html'


import xml.etree.ElementTree as ET

class SmdParts():

    def __init__(self):
        self._et = None
        pass

    def load(self, xmlstring):
        self._et = ET.fromstring(xmlstring)
        sane, msg = self._sanitize()
        if not sane:
            self.unload()
        return sane, msg

    def unload(self):
        self._et = None

    def isFileLoaded(self):
        if self._et is not None:
            return True
        else:
            return False

    def getPartCount(self):
        count = 0
        for elem in self._et.findall("./part"):
            count += 1
        return count


    # returns a list of all available parts
    def getPartIds(self):
        result = []
        for elem in self._et.findall("./part"):
            result.append(int(elem.get("id")))
        return result

    #return the nr of the box this part is supposed to be in
    def getPartPosition(self, partnr):
        return int(self._et.find("./part[@id='" + str(partnr) + "']/position").get("box"))

    def getPartName(self, partnr):
        return self._et.find("./part[@id='" + str(partnr) + "']").get("name")

    def getPartHeight(self, partnr):
        return float(self._et.find("./part[@id='" + str(partnr) + "']/size").get("height"))

    def getPartShape(self, partnr):
        result = []
        if(self._et.find("./part[@id='" + str(partnr) + "']/shape") is not None):
            for elem in self._et.find("./part[@id='" + str(partnr) + "']/shape"):
                result.append([float(elem.get("x")), float(elem.get("y"))])
        return result

    def getPartPads(self, partnr):
        result = []
        if( self._et.find("./part[@id='" + str(partnr) + "']/pads") is not None):
            for elem in self._et.find("./part[@id='" + str(partnr) + "']/pads"):
                result.append([float(elem.get("x1")), float(elem.get("y1")), float(elem.get("x2")), float(elem.get("y2"))])
        return result


    def getPartDestination(self, partnr):
        x = float(self._et.find("./part[@id='" + str(partnr) + "']/destination").get("x"))
        y = float(self._et.find("./part[@id='" + str(partnr) + "']/destination").get("y"))
        z = float(self._et.find("./part[@id='" + str(partnr) + "']/destination").get("z"))
        orientation = float(self._et.find("./part[@id='" + str(partnr) + "']/destination").get("orientation"))
        return [x, y, z, orientation]

    def _sanitize(self):
        result = True
        msg = ""

        # valid object?
        if self._et.tag != "object":
            result = False
            msg = "file contains XML data, but no valid <object>"
        # object name
        if not self._et.attrib.get("name"):
            self._et.set("name", "Object 1")

        count = 0

        # Iterate over parts
        for part in self._et.iter("part"):
            if result:
                count += 1
                # id
                try:
                    int(part.get("id"))
                except:
                    result = False
                    msg = "Invalid or no id in part " + str(count)

                # sanitize part name
                if not part.get("name"):
                    part.set("name", "part " + str(count))

                # box position
                if result:
                    result, msg = self._sanitizeTag(part, "position", ["box"], int)
                # height
                if result:
                    result, msg = self._sanitizeTag(part, "size", ["height"], float)
                # shape
                if result:
                    if(part.find("shape") is not None):
                        for elem in part.find("shape"):
                            result, msg = self._sanitizeAttribute(part, elem, ["x", "y"], float)
                # pads
                if result:
                    if(part.find("pads") is not None):
                        for elem in part.find("pads"):
                            result, msg = self._sanitizeAttribute(part, elem, ["x1", "y1", "x2", "y2"], float)
                # destination
                if result:
                    result, msg = self._sanitizeTag(part, "destination", ["x", "y", "z", "orientation"], float)

        return result, msg


    def _sanitizeTag(self, part, tag, attributes, validate):
        result = True
        msg = ""

        elem = part.find(tag)
        if(elem is not None):
            result, msg = self._sanitizeAttribute(part, elem, attributes, validate)
        else:
            result = False
            msg = "No tag " + tag + " in part " + part.get("id") + " - " + part.get("name")

        return result, msg


    def _sanitizeAttribute(self, part, elem, attributes, validate):
        result = True
        msg = ""

        for attribute in attributes:
            if result:
                try:
                    validate(elem.get(attribute))
                except:
                    result = False
                    msg = "Invalid or no attribute " + attribute + " in part " + part.get("id") + " - " + part.get("name")

        return result, msg
