import click
from lxml import etree,html
import pathlib
import shutil
import fileinput
import sys
import subprocess
import itertools
import re
import copy
from json import loads,dumps

from svgprestools.utils import *
from svgprestools.WriteDoc import WriteDoc




@click.command(help="Create an SVG image of one or more text files.")
@click.option("--output", "-o", default="txt2svg-out.svg", help="Output filename.")
@click.argument("input", type=click.Path(exists=True), nargs=-1)
def txt2svg(output, input):

    font_size = 12
    line_hieght = 15
    leftcol = 20

    out = pathlib.Path(output)
    img = etree.Element(
        "svg",
        nsmap={
            None: "http://www.w3.org/2000/svg",
            "xlink": "http://www.w3.org/1999/xlink",
        },
    )
    img.set("version", "2")
    img.set("baseProfile", "full")

    maxcol = 0
    lino = 1
    for file in input:
        path = pathlib.Path(click.format_filename(file))
        text = path.read_text()
        grp = etree.SubElement(img, "g")
        grp.set("filename", file)
        grp.set("id", file)
        grp.set(INKNS + "groupmode", "layer")

        textelem = etree.SubElement(grp, "text")
        textelem.set("x", f"{leftcol}")
        textelem.set("y", f"{lino*line_hieght}")
        textelem.set("style", "fill:black")
        textelem.set("font-size", f"{font_size}")
        textelem.set("font-family", "monospace")
        textelem.set(XMLNS + "space", "preserve")

        tspan = etree.SubElement(textelem, "tspan")
        tspan.set("x", f"{leftcol}")
        tspan.set("dy", f"{2*line_hieght}")
        tspan.set("font-size", f"{2*font_size}")
        tspan.text = file
        tspan = etree.SubElement(textelem, "tspan")
        tspan.set("x", f"{leftcol}")
        tspan.set("dy", f"{line_hieght}")
        tspan.text = " "
        lino += 3
        for line in text.split("\n"):
            lino += 1
            print(lino)
            if line == "":
                line = " "
            if len(line) > maxcol:
                maxcol = len(line)
            tspan = etree.SubElement(textelem, "tspan")
            tspan.set("x", f"{leftcol}")
            tspan.set("dy", f"{line_hieght}")
            tspan.text = line

    out.write_bytes(
        etree.tostring(img, xml_declaration=True, pretty_print=True, encoding="utf-8")
    )


@click.command(help="Create a montage of SVG images into one SVG image.")
@click.option("--output", "-o", default=None, help="Output filename.")
@click.argument("input", type=click.Path(exists=True), nargs=1)
def svgmontage(output, input):
    if output is None:
      output = input + ".svg"
    if not output.endswith(".svg"):
      output = output + ".svg"

    input = pathlib.Path(input)
    output = pathlib.Path(output)

    oimg = etree.Element(
        "svg",
        nsmap={
            None: "http://www.w3.org/2000/svg",
            "xlink": "http://www.w3.org/1999/xlink",
        },
    )

    files = sort_numbered_filenames(
        list(itertools.chain(input.glob("*.SVG"), input.glob("*.svg")))
    )
    N = len(files)
    nrows = int(N**0.5)
    row = 0
    x = 0
    y = 0
    maxwidth = 0
    pad = 10
    i = 0
    print("Building single SVG with all images in a grid...")
    layout = []
    for file in files:
        i += 1
        row += 1

        slide_id = f"Slide-{i}"

        iimg = etree.parse(str(file))
        # prefix all tag id's with slide id
        for elem in iimg.xpath("//*[name()='clipPath']|//*[name()='image']"):
          elem.set("id", f"{slide_id}-{elem.get('id')}")

        for elem in iimg.xpath("//*[@clip-path]"):
          elem.set("clip-path", elem.get("clip-path").replace("#",f"#{slide_id}-"))
        for elem in iimg.xpath("//*[name()='use']"):
          elem.set(XLINKNS+"href", elem.get(XLINKNS+"href").replace("#",f"#{slide_id}-"))




        root = iimg.getroot()
        root.set("x", str(x))
        root.set("y", str(y))
        grp = etree.SubElement(oimg, "g")
        grp.set("filename", str(file))
        grp.set("id", slide_id)
        grp.set(INKNS + "groupmode", "layer")
        grp.append(root)

        w = int(root.get("width"))
        h = int(root.get("height"))

        layout.append({"x":x,"y":y,"w":w,"h":h})

        if w > maxwidth:
          maxwidth = w

        if row > nrows:
          row = 0
          x += maxwidth + pad
          maxwidth = 0
          y = 0
        else:
          y += int(root.get("height")) + pad


    print("done")
    print(layout)

    output.write_bytes(
        etree.tostring(oimg, xml_declaration=True, pretty_print=True, encoding="utf-8")
    )

@click.command(help="Modify a Write (StylusLabs) SVG image so that it can be used by Sozi.")
@click.option("--output", "-o", default=None, help="Output filename.")
@click.argument("input", type=click.Path(exists=True), nargs=1)
def write2sozi(output, input):
    input = pathlib.Path(input)

    if output is None:
      output = input.stem + "-sozi.svg"
    if not output.endswith(".svg"):
      output = output + ".svg"

    output = pathlib.Path(output)


    doc = WriteDoc(str(input))
    # replace nested svg tags with g tags
    width = 0
    height = 0
    for page in doc.get_pages():
      page.tag = "g"
      x = page.get("x",0)
      y = page.get("y",0)
      page.set("transform",f"translate({x},{y})")

      height += int(page.get("height").strip("px"))
      width = max( int(page.get("width").strip("px")), width )

    for d in doc.root.xpath("/svg:svg[@id='write-document']",namespaces=NAMESPACES):
      d.set("width",str(width))
      d.set("height",str(height))


    output.write_bytes(
        etree.tostring(doc.root, xml_declaration=True, pretty_print=True, encoding="utf-8")
    )


@click.command(help="Extract the ink and images from a Write document.")
@click.option("--output", "-o", default=None, help="Output filename.")
@click.argument("input", type=click.Path(exists=True), nargs=1)
def extractWriteInk(output, input):
    input = pathlib.Path(input)

    if output is None:
      output = input.stem + "-ink.svg"

    if not output.endswith(".svg"):
      output = output + ".svg"

    output = pathlib.Path(output)


    iimg = etree.parse(str(input))
    svg = iimg.getroot()

    oimg = etree.Element(
        "svg",
        nsmap={
            None: NAMESPACES['svg'],
            "xlink": NAMESPACES['xlink']
        },
    )

    width = 0
    height = 0
    for page in svg.xpath("//svg:svg[@class='write-page']",namespaces=NAMESPACES):
      group = etree.SubElement(oimg,"g")
      group.set("transform",f"translate(0,{height})")
      # extract inkstrokes and images
      for elem in page.xpath(".//svg:path[@class='write-flat-pen']|.//svg:image",namespaces=NAMESPACES):
        group.append(elem)

      height += int(page.get("height").strip("px"))
      height += 100
      width = max( int(page.get("width").strip("px")), width )


    oimg.set("width",str(width))
    oimg.set("height",str(height))








    output.write_bytes(
        etree.tostring(oimg, xml_declaration=True, pretty_print=True, encoding="utf-8")
    )



@click.command(help="Update the SVG image or JSON settings in a Sozi HTML presentation.")
@click.argument("input", type=click.Path(exists=True), nargs=1)
@click.option("--output", "-o", default=None, help="Output filename.")
@click.option("--image", "-i", default=None, type=click.Path(exists=True))
@click.option("--json", "-j", default=None, type=click.Path(exists=True))
def updateSoziPresentation(input, output, image, json):
    input = pathlib.Path(input)
    if output is None:
      shutil.copy(input,input.with_suffix(input.suffix+".bak"))
      output = input
    else:
      output = pathlib.Path(output)
    
    doc = html.parse(str(input)).getroot()
    if image is not None:
      img = etree.parse(str(image)).getroot()

      images = doc.xpath("/html/body/svg",namespaces=NAMESPACES)
      if len(images) > 1:
        print("Found more than one image! Exiting.")
        sys.exit()

      if len(images) < 1:
        print("Did not find an image in the presentation. The new image will be added to the <body> element")
        body = doc.xpath("/html/body",namespaces=NAMESPACES)[0]
        body.append(img)
      else:
        image[0].getparent().replace(images[i],img)

    if json is not None:
      text = pathlib.Path(json).read_text()
      data = loads(text)
      text = "var soziPresentationData = " + dumps(data,separators=(',',':'))
      found = False
      for script in doc.xpath("/html/body/script",namespaces=NAMESPACES):
        if script.text.startswith("var soziPresentationData"):
          found = True
          script.text = text
      if not found:
        print("Did not find an sozi data in the presentation. The data will be added in a <script> element of the <body> element")
        body = doc.xpath("/html/body",namespaces=NAMESPACES)[0]
        script = etree.Element('script')
        script.text = text
        body.append(script)



    
    output.write_bytes(html.tostring(doc,encoding="utf-8"))


    







@click.command(help="Concatenate multiple Write SVG images into a single SVG image.")
@click.argument("input", type=click.Path(exists=True), nargs=-1)
@click.option("--output", "-o", type=click.Path(), help="Output filename.")
@click.option("--overwrite/--no-overwrite", "-x/-n", help="Overwrite output file if it exists.")
@click.option("--horizontal/--vertical", "-h/-v", help="Concatinate documents horizontally or vertically.")
def writeCat(input, output,overwrite,horizontal):

  if len(input) < 1:
    return 0

  doc = WriteDoc(input[0])
  H = doc.get_document_height()
  W = doc.get_document_width()
  for file in input[1:]: 
    doc2 = WriteDoc(str(file))
    if horizontal:
      doc2.shift_horizontal(W)
    else:
      doc2.shift_vertical(H)
    for page in doc2.get_pages():
      doc.root.append(page)
    H = doc.get_document_height()
    W = doc.get_document_width()

  H = doc.get_document_height()
  W = doc.get_document_width()

  for style in doc.root.xpath("/svg:svg/svg:defs/svg:style",namespaces=NAMESPACES):
    style.text = "#write-document, #write-doc-background { width: "+str(W)+"px;  height: "+str(H)+"px; }"



  if output:
    output = pathlib.Path(output)
    if overwrite or not output.exists():
      output.write_bytes(etree.tostring(doc.root,encoding="utf-8"))
    else:
      print(f"Error: output file {str(output)} exists. Use -x to overwrite.")
  else:
    print(etree.tostring(doc.root).decode("utf-8"))


    







@click.command(help="Change the background used in a Write SVG image.")
@click.argument("input", type=click.Path(exists=True), nargs=1)
@click.option("--output", "-o", type=click.Path(), help="Output filename.")
@click.option("--template", "-t", type=click.Path(exists=True), help="Write template that contains the background to use.")
@click.option("--overwrite/--no-overwrite", "-x/-n", help="Overwrite output file if it exists.")
def writeChangeBackground(input, output, template, overwrite):

  if len(input) < 1:
    return 0

  rulings = []
  if template:
    tmpl = WriteDoc(template)
    rulings = list( tmpl.get_rulings() )

  file = input
  # for file in input:
  doc = WriteDoc(file)
  i = 0
  for ruling in doc.get_rulings():
    if len(rulings) > 0:
      ruling.getparent().replace(ruling,copy.deepcopy(rulings[i]))
      i += 1
      i = i % len(rulings)
    else:
      ruling.getparent().remove(ruling)





  if output:
    output = pathlib.Path(output)
    if overwrite or not output.exists():
      output.write_bytes(etree.tostring(doc.root,encoding="utf-8"))
    else:
      print(f"Error: output file {str(output)} exists. Use -x to overwrite.")
  else:
    print(etree.tostring(doc.root).decode("utf-8"))


    









