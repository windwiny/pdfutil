#!/usr/bin/env python
# coding: utf-8

# combine 2 inventory pdf to one A4 page

from __future__ import print_function
import os, sys, time
import re
import fitz

rno=re.compile('^\d{8,11}$')
ryuan=re.compile('^￥\d+|^¥\d+')

fs = sys.argv[1:]
fs = [f for f in fs if f.endswith('.pdf') or f.endswith('.PDF') ]
print(fs)



class PdfDoc:
    def __init__(self):
        self.ipg = 0
        self.doc = fitz.open()  # empty output PDF
        
        # A4 portrait output page format
        self.a4width, self.a4height = fitz.paper_size("a4")

        r = fitz.Rect(0, 0, self.a4width, self.a4height)
        r1 = r * 0.5
        r5 = r1 + (0+10,0+10,r1.width-10,0-10)
        r6 = r1 + (0+10, r1.height+10, r1.width-10, r1.height-10)

        self.r_tab = [r5, r6]
        
    
    def addpage(self, spage, rotate=0):
        """now copy input pages to output"""
        if self.ipg % len(self.r_tab) == 0:           # create new output page
            self.page = self.doc.new_page(-1, width=self.a4width, height=self.a4height)

        # insert input page into the correct rectangle
        self.page.show_pdf_page(
                self.r_tab[self.ipg % len(self.r_tab)],    # select output rect
                src,                # input document
                spage.number,       # input page number
                rotate=rotate)

        self.ipg += 1
    
    
    def save(self, outfile='', append=''):
        """ save to pdf file"""
        if outfile == '':
            outfile = "merged-" + time.strftime('%Y%m%d%H%M%S') + append + '.pdf'
        # by all means, save new file using garbage collection and compression
        if self.doc.page_count > 0:
            self.doc.save(outfile, garbage = len(self.r_tab), deflate = True)

        print("output file %s has %d pages" % (outfile, self.doc.page_count) )
        self.doc.close()
        
    pass


def print_invt_amount(spage, infile):
    lines=spage.get_text().splitlines()
    res1 = set()
    res2 = set()
    for line in lines:
        if rno.match(line):
            res1.add(line)
        if ryuan.match(line):
            res2.add(line)

    res1=list(res1)
    res1.sort()
    res2=list(res2)
    res2.sort(key=lambda x: -float(x[1:]))
    oo = res1 + res2
    oo = [ "%s" % i for i in oo ]
    result = [ 'inventno', "\t".join(oo), 'on %s:%d' % (infile, spage.number) ]
    print("\t".join(result))



odoc1 = PdfDoc()    # inventory
odoc2 = PdfDoc()    # list

for infile in fs:
    src = fitz.open(infile)
    print('--open: ', infile)
    for spage in src:
        print_invt_amount(spage, infile)
        if spage.rect.width < spage.rect.height:
            rotate = -90
            odoc1.addpage(spage, rotate)
        else:
            rotate = 0
            odoc2.addpage(spage)
    src.close()

odoc1.save(append='-list')
odoc2.save()

