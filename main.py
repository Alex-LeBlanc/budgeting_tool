import pandas as pd
from PyPDF2 import PdfReader
import re
import calendar
import os
import glob


CATEGORY_MAPPINGS = {
  'Food': ['RESTAURANT', 'BURGER', 'MCDONALD', 'TIMHORTON', 'CHIPOTLE', 'SHUYI', 'SUBWAY', 'CACTUSCLUB', 'RESTAURANT', 'PATISSERIE', 'PIZZA', 'AMOURDUPAIN', 'BETEAPAIN', 'MACHIMACHI', 'DUMPLINGS', 'LAYLOW', 'MEKONG','ORIGINALJOE', 'JUGOJUICE', 'OHMYGYRO', 'PORCHETTA&CO', 'PAINORTHERNTHAI', 'THEALLEY', 'SUSHI', 'IN-N-OUT'],
  'Coffee': ['Coffee', 'Cafe', 'Melk', 'Starbucks', 'ESPRESSO', 'FORNO', 'DUNKINE', 'FAROSHERBROOKE', 'ACEHOTELLOBBY', 'LEPETITDEP', 'SPEIGHTOUNCECLUBCALGARY', 'OSMOXMARUSAN'],
  'Drinks': ['LCBO', 'SAQ', 'Bar', 'CAGESPHERE', 'BRASSERIE', 'DUBLINCALLING'],
  'Transportation': ['Taxi', 'Bus', 'Metro', 'Flight', 'Ride', 'PRESTOFARE', 'OPUS', 'CHRONO-RECHARGE'],
  'Travel': ['WESTJET', 'HUDSONST', 'UBIGI'],
  'Rent & Utilities': ['BELLCANADA'],
  'Groceries': ['ADONIS', 'SABABAFINEFOOD', 'EPICERIEFINEITALIME', 'COSTCO', 'SOBEYS'],
  'Health & Wellbeing': ['PHARMA','ATHLETIC', 'DENTIST', 'SHOPPERSDRUGMART'],
  'Haircut': ['BARBIER'],
  'Sports': ['TREKBICYCLE','SPORTSEXPERT','TENNIS13','WATERPOLO'],
  'Shopping': ['Amazon','AMZN'],
  'Clothing':['LULULEMON', 'UNIQLO'],
  'Tech & Electronics': ['PAYBRIGHT'],
  'Stocks & Investments': ['NBDB'],
  'Income': [],
  'Was paid back':[],
  'Other Income':[],
  'EOM':[],
  'Food for Others':[],
  'MasterCard Payment':[],
  'Gifts':[],
  'Donations':[],
  'Big Purchases':[],
  'Car & Gas':['SHELL'],
  'Household':[],
  'Leisure':[],
  'Work & Business':[],
  'Paid someone back':[],
  'Education':[],
  'Other':[],
  '_________':[],
}

PRICE_PATTERN = r'\d+\.\d{2}$'
PRICE_AND_LOC_PATTERN = r'([A-Za-z]{2})(\d+\.\d{2})(-?)$'


def extract_price_and_loc(txt:str) -> str:
  match = re.search(PRICE_AND_LOC_PATTERN, txt)
  if match:
    loc = match.group(1)
    price = match.group(2)
    if match.group(3) == '-':
      price = f'-{price}'
    return loc, price
  return None, None


def remove_price_and_loc(txt:str) -> str:
  match = re.search(PRICE_AND_LOC_PATTERN, txt)
  if match:
    return re.sub(PRICE_AND_LOC_PATTERN, '', txt)
  return txt
  

# Function to convert MMDD to MMM-DD
def convert_mmdd_to_mmmdd(mmdd):
    mm = int(mmdd[:2])
    dd = int(mmdd[2:])
    month_abbr = calendar.month_abbr[mm]
    return f"{month_abbr}-{dd:02d}"


def extract_date(txt:str):
    match = re.match(r'^(\d{4}),', txt)
    if match:
        mmdd = match.group(1)
        # Convert MMDD to MMM-DD
        converted_date = convert_mmdd_to_mmmdd(mmdd)
        # Remove the MMDD, prefix
        new_text = re.sub(r'^\d{4},\s*', '', txt)
        return converted_date, new_text
    return None, txt


# Function to determine category based on keywords
def determine_category(item):
    for category, keywords in CATEGORY_MAPPINGS.items():
        for keyword in keywords:
            if keyword.lower() in item.lower():
                return category
    return 'Unknown'


# Function to interactively assign categories to 'Unknown' rows
def reassign_unknowns(df):
    unknowns = df[df['category'] == 'Unknown']
    if unknowns.empty:
        print("No 'Unknown' categories to reassign.")
        return df
    
    available_categories = list(CATEGORY_MAPPINGS.keys())
    
    # Print the available categories with indices
    print("\nAvailable Categories:")
    for index, category in enumerate(available_categories):
        print(f"{index}: {category}")
    
    for index, row in unknowns.iterrows():
        print(f"\nDate: {row['date']}, Purchase Item: {row['purchase_item']}, Price: ${row['price']:.2f}")
        
        while True:
            user_input = input("Enter the index of the new category from the available categories (or press Enter to leave as 'Unknown'): ").strip()
            if user_input == "":
                break
            try:
                new_category_index = int(user_input)
                if 0 <= new_category_index < len(available_categories):
                    df.at[index, 'category'] = available_categories[new_category_index]
                    break
                else:
                    print("Invalid index. Please enter a number corresponding to the available categories.")
            except ValueError:
                print("Invalid input. Please enter a valid number.")
    
    return df


def convert_NBC_mc_pdf_to_df(filename:str):
  filepath = f"bank_statements/{filename}"
  print("\n\n\n\n\n\n")
  print(f"EXTRACTING {filepath}:\n")

  reader = PdfReader(filepath)
  num_pages = len(reader.pages)

  dfs = []

  for i, page in enumerate(reader.pages):
    if i >= num_pages - 1:
      break

    print(f"$$$$$$$$$$$$$$$$$$$$$ EXTRACTING PAGE #{i} ...")
    
    text = page.extract_text()

    idx = text.split("________")

    useful_part = idx[-1]

    more_useful = useful_part.split("\n")

    pattern = r'^(\d+)[UZ]\d*'
    transactions = [re.sub(pattern, r'\1,', row) for row in more_useful if re.search(pattern, row)]

    df = pd.DataFrame({'purchase_item':transactions})

    dfs.append(df)
    print(f"$$$$$$$$$$$$$$$$$$$$$ PAGE #{i} EXTRACTION COMPLETE ...")



  df = pd.concat(dfs)
  df.reset_index(inplace=True,drop=True)

  df[['date','purchase_item']] = df['purchase_item'].apply(lambda x: pd.Series(extract_date(x)))


  new_columns_tuples = df['purchase_item'].apply(extract_price_and_loc)
  df[['location','price']] = pd.DataFrame(
                                  new_columns_tuples.tolist(), 
                                  columns=['location','price']
                                )
  
  df['purchase_item'] = df['purchase_item'].apply(remove_price_and_loc)

  df['price'] = df['price'].astype(float)

  # Create the 'category' column
  df['category'] = df['purchase_item'].apply(determine_category)
  # print(df[df['category']=='Coffee'])

  df = reassign_unknowns(df)


  grouped_df = df.groupby(['category'],as_index=False)['price'].sum()

  df.to_csv(f'results/res_{filename}.csv')
  grouped_df.to_csv(f'results/summary_{filename}.csv')

  print(df.shape)
  print(grouped_df.shape)

  total_amount_due = df['price'].sum()
  print(f"-> TOTAL AMOUNT DUE FOR {filename}: ${total_amount_due:,.2f}")

  return df
  

def get_files_with_prefix(directory, prefix):
    # Construct the search pattern
    search_pattern = os.path.join(directory, f"{prefix}*")
    # Use glob to find all files that match the search pattern
    matching_files = glob.glob(search_pattern)
    filenames = [os.path.basename(file) for file in matching_files]
    return filenames


def get_amount_owing(df):
  total_amount_due = df['price'].sum()
  print(f"-> TOTAL AMOUNT DUE: ${total_amount_due:,.2f}")
  return total_amount_due


def process_all_nbc_mc():
  directory = 'bank_statements/'
  prefix = 'mc_nbc_'
  matching_files = get_files_with_prefix(directory, prefix)

  dfs = []
  amounts_due = []
  for file in matching_files:
    temp_df = convert_NBC_mc_pdf_to_df(file)
    dfs.append(temp_df)
    amounts_due.append(get_amount_owing(temp_df))

  due_df = pd.DataFrame({'statement':matching_files, 'amount_due':amounts_due})
  
  df = pd.concat(dfs)
  df.reset_index(inplace=True,drop=True)
  grouped_df = df.groupby(['category'],as_index=False)['price'].sum()

  df = df[['date','purchase_item','location','category','price']]

  df.to_csv(f'results/AGG_results.csv', index=False)
  grouped_df.to_csv(f'results/AGG_summary.csv', index=False)
  due_df.to_csv(f'results/amounts_due.csv', index=False)

  print(df)
  print(grouped_df)
  print(due_df)

  print(df.shape)
  print(grouped_df.shape)



if __name__ == "__main__":
  # convert_pdf_to_df("bank_statements/mc_nbc_2024-04-28_Statement.pdf")
  # convert_NBC_mc_pdf_to_df("mc_nbc_2024-03-31_Statement.pdf")
  process_all_nbc_mc()

