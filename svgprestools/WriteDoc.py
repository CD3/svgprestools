from .utils import *



class WriteDoc:
  def __init__(self,filename):
    self.doc = etree.parse(str(filename))
    self.root = self.doc.getroot()

  def get_pages(self):
    for page in self.root.xpath("//svg:svg[@class='write-page']",namespaces=NAMESPACES):
      yield page

  def get_rulings(self):
    for ruling in self.root.xpath("//svg:g[contains(@class,'ruleline')]",namespaces=NAMESPACES):
      yield ruling


  def get_document_width(self):
    W = 0
    for page in self.get_pages():
      x = AbsoluteLengthUnits.to_px(page.get("x", 0))
      w = AbsoluteLengthUnits.to_px(page.get("width", 0))
      W = max(W,x+w)

    return W

  def get_document_height(self):
    H = 0
    for page in self.get_pages():
      y = AbsoluteLengthUnits.to_px(page.get("y", 0))
      h = AbsoluteLengthUnits.to_px(page.get("height", 0))
      H = max(H,y+h)

    return H

  def shift_vertical(self, shift):
    for page in self.get_pages():
      y = AbsoluteLengthUnits.to_px(page.get("y",0)) + AbsoluteLengthUnits.to_px(shift)
      page.set("y",f"{y}px")

  def shift_horizontal(self, shift):
    for page in self.get_pages():
      x = AbsoluteLengthUnits.to_px(page.get("x",0)) + AbsoluteLengthUnits.to_px(shift)
      page.set("x",f"{x}px")

