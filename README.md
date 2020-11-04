# Description

svgpresutils is a collection of small tools for working with SVG files and SVG-based presentations created with [sozi](https://sozi.baierouge.fr/).
It started as a script for creating an SVG image from multiple plain text files (`txt2svg`) so that I could generate simple Prezi-like
presentations for code review, and has expanded to include tools for modifying and including
Stylus Lab [Write](http://www.styluslabs.com/) documents (an application for taking handwritten notes) in sozi presentations.

The packages provides a small module with some utility functions, but most of the functionality is contained in console scripts.

## Install

```
$ pip install svgpresutils
```

## Tools

### `txt2svg`

Create an SVG image from plain text files.

```
# txt2svg -o image-of-files.svg file1.txt file2.txt main.cpp
```

### `svgmontage`

Combine multiple SVG images into a single, montage, image. Similar to imagemagick's montage command, but the
images are included as SVGs instead of converted to bitmaps.

### `write2sozi`

Reformat an SVG document created by Stylus Lab's Write application for taking handwritten notes so that it
can be used in a sozi presentation. This is useful for creating a presentation from handwritten notes/figures.

### `extract-write-ink`

Extract ink from a write document into a standalone SVG image.

### `update-sozi-presentation`

Update the SVG image or JSON data in a sozi HTML presentation file. This is useful for quickly rebuilding a sozi
presentation after modifying the SVG image.

### `write-cat`

Concatenate multiple Write documents into a single document.

### `write-change-background`

Replace the background (ruling) in a write document.
