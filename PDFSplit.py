import PyPDF2
import subprocess
import re
import os
import argparse
import logging

#---------------------------------------------------------------------------------
# Starting from a big pdf file containng 1 certificate per page, generate
# n pdf files, one pdf per certificate
# Bonus : try to extract infos from each pdf to give it a meaningful name
# (ex : global title, people name)
#---------------------------------------------------------------------------------

class Splitter() :

  #------------------------------------------------------------------------------
  def __init__(self,args) :
    self.args=args
    self.filePrefix=".".join(self.args.infile.split("."))[:-1]
    self.pdfSplit()

  #------------------------------------------------------------------------------
  def getFileName(self,page,suffix) :
    return(self.filePrefix + '-'+  str(page) + suffix)

  #------------------------------------------------------------------------------
  def getFinalPDFFileName(self,file) :
    if self.args.name :
      return(self.args.name + "-" + file )
    txtFile=file+'.txt'
    # read text from pyPDF2 does not work :(
    subprocess.check_output(['pdftotext',file,txtFile])
    finalName=file
    with open(txtFile, "r") as f:
      regex="atteste"
      logging.info("Search to extract name from   <" + regex +">")
      for l in f :
        logging.debug(l)
        if re.search(regex,l) :
          logging.info("Got name in <" + l +">")
          finalName="".join(l.split(" ")[2:])[:-1] + ".pdf"
          break
    return(finalName)

  #------------------------------------------------------------------------------
  def getFinalPDFTitle(self,pdfReader) :
    if self.args.title :
      title = self.args.title
    else :
      rawTitle="{}".format(pdfReader.getDocumentInfo().title)
      title="".join(rawTitle.split(" ")[3:-3])
    return(title)

  #------------------------------------------------------------------------------
  def pdfSplit(self):
    pdfFileObj = open(self.args.infile, 'rb')
    pdfReader = PyPDF2.PdfFileReader(pdfFileObj)
    pdfWriter = PyPDF2.PdfFileWriter()
    pageno = 1
    for page in range(pdfReader.numPages):
      pdfWriter = PyPDF2.PdfFileWriter()
      pdfWriter.addPage(pdfReader.getPage(page))
      newPdf = self.getFileName(pageno,'.pdf')
      with open(newPdf, "wb") as f:
        pdfWriter.write(f)
      pageno += 1
      fullName= self.getFinalPDFTitle(pdfReader) + "-" + self.getFinalPDFFileName(newPdf)
      os.rename(newPdf,fullName)
    pdfFileObj.close()


#------------------------------------------------------------------------------
def fSplit(args):
  Splitter(args)

#------------------------------------------------------------------------------
if __name__ == "__main__":
  # calling the main function
  parser = argparse.ArgumentParser()
  parser.add_argument(
    '-d', '--debug',
    help="Print lots of debugging statements",
    action="store_const", dest="loglevel", const=logging.DEBUG,
    default=logging.WARNING,
  )
  parser.add_argument(
    '-v', '--verbose',
    help="Be verbose",
    action="store_const", dest="loglevel", const=logging.INFO,
  )

  subparsers = parser.add_subparsers(help='sub-command help')

  parserSplit = subparsers.add_parser('split', help='a help')
  parserSplit.set_defaults(func=fSplit)
  parserSplit.add_argument('--title','-t',help="force title")
  parserSplit.add_argument('--name','-n',help="force name")
  parserSplit.add_argument('--infile','-i',help="in",default='example.pdf')

  args=parser.parse_args()
  logging.basicConfig(format="%(asctime)s %(funcName)s %(levelname)s %(message)s", level=args.loglevel)
  args.func(args)
