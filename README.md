meta4zenf
=========

A tool to clean the metadata of images for upload to Zenfolio.com

It tackles two issues:

(1) Zenfolio expects the metadata for title and caption without HTML.
This tool strips all HTML from the metadata keeping only the _text_ in the tags.

(2) Not all key words an image is tagged with are necessarily relevant for a public gallery on Zenfolio.com. This tool removes certain key words from
the `Keywords` tag.
