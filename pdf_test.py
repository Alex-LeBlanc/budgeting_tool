from PyPDF2 import PdfReader
import re

print("\n\n\n\n\n\n")

reader = PdfReader("bank_statements/2024-03-31_Statement.pdf")
num_pages = len(reader.pages)

for i, page in enumerate(reader.pages):
  text = page.extract_text()

  print(f"#################### PAGE #{i}: #######################")
  # print(page)
  # print()

  idx = text.split("________")

  useful_part = idx[-1]
  # print(useful_part)

  # print(len(useful_part))

  # # for i in useful_part:
  # #   print(i)
  # print("\n" in useful_part)
  # print(useful_part.count("\n"))

  more_useful = useful_part.split("\n")

  pattern = r'\d+U\d*'

  transactions = [re.sub(pattern, '', row.replace(" ", "    ")) for row in more_useful if len(row)>3 and row[-3]=='.']

  pattern = r'\d+U\d*'
  
  for j in transactions:
    print("-> ", j)




  print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$\n")

  if i >= num_pages - 2:
    break

# pdf_path = "bank_statements/2024-03-31_Statement.pdf"
# dfs = tabula.read_pdf(pdf_path, stream=True)
# print(dfs[0])