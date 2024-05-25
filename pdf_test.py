from PyPDF2 import PdfReader
import tabula

reader = PdfReader("bank_statements/2024-03-31_Statement.pdf")
num_pages = len(reader.pages)

for i, page in enumerate(reader.pages):
  text = page.extract_text()

  print(f"\n\n#################### PAGE #{i}: #######################")
  # print(page)
  # print()

  idx = text.split("________")

  useful_part = idx[-1]
  print(useful_part)

  print(len(useful_part))

  # for i in useful_part:
  #   print(i)
  print("\n" in useful_part)
  print(useful_part.count("\n"))

  more_useful = useful_part.split("\n")

  for i in more_useful:
    print("-> ", i)

  print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$\n\n\n\n")
  break



# pdf_path = "bank_statements/2024-03-31_Statement.pdf"
# dfs = tabula.read_pdf(pdf_path, stream=True)
# print(dfs[0])