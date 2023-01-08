import pandoc

file = './doc.docx'
doc = pandoc.read(file=file, format="docx")

pandoc.write(doc, "family_tree.md", format="gfm")
