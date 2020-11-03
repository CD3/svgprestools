from lxml import etree,html


NAMESPACES={'svg':'http://www.w3.org/2000/svg',
    'xml':'http://www.w3.org/XML/1998/namespace',
    'xlink':'http://www.w3.org/1999/xlink',
    'ink':'http://www.inkscape.org/namespaces/inkscape'}

XMLNS = "{"+NAMESPACES['xml']+"}"
INKNS =  "{"+NAMESPACES['ink']+"}"
XLINKNS =  "{"+NAMESPACES['xlink']+"}"
SVGNS =  "{"+NAMESPACES['svg']+"}"


def tryint(s):
  try:
    return int(s)
  except ValueError:
    return s


def split_filename_into_numerical_parts(filename):
  return [tryint(c) for c in re.split("([0-9]+)", str(filename))]


def sort_numbered_filenames(files):
  files.sort(key=split_filename_into_numerical_parts)
  return files

class AbsoluteLengthUnits:
  to_px_conversions = {'px' : 1,
      'in' : 96.,
      'cm' : 96/2.54,
      'mm' : 96/2.54/10,
      'pt' : 96/72,
      'pc' : 96/6}

  @staticmethod
  def to_px(length):
    if not isinstance(length,str):
      return length

    if len(length) == 0:
      return 0

    if length[-1] in '0123456789.':
        return float(length)

    for unit in AbsoluteLengthUnits.to_px_conversions:
      if length.endswith(unit):
        return float(length[:-len(unit)])*AbsoluteLengthUnits.to_px_conversions[unit]


