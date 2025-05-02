# from IPython.display import display
import pandas as pd

def load_data(path: str, sheet_name: str) -> pd.DataFrame:
  """
  Load data from an Excel file and return it as a pandas DataFrame.
  Args:
      path (str): The path to the Excel file.
      sheet_name (str): The name of the sheet to load.
  Returns:
      pd.DataFrame: The loaded data as a pandas DataFrame.
  """
  return pd.read_excel(path, sheet_name=sheet_name)


def setCollumnAsIndex(table: pd.DataFrame, column: str) -> pd.DataFrame:
  """
  Set a specified column as the index of the DataFrame.
  Args:
      table (pd.DataFrame): The DataFrame to modify.
      column (str): The name of the column to set as the index.
  Returns:
      pd.DataFrame: The modified DataFrame with the specified column set as the index.
  """
  table.set_index(column, inplace=True)
  return table


def setFirstColumnAsIndex(table: pd.DataFrame) -> pd.DataFrame:
  """
  Set the first column as the index of the DataFrame.
  Args:
      table (pd.DataFrame): The DataFrame to modify.
  Returns:
      pd.DataFrame: The modified DataFrame with the first column set as the index.
  """
  table.set_index(table.columns[0], inplace=True)
  return table


def resetIndex(table: pd.DataFrame) -> pd.DataFrame:
  """
  Reset the index of the DataFrame, making the index a regular column again.
  Args:
      table (pd.DataFrame): The DataFrame to modify.
  Returns:
      pd.DataFrame: The modified DataFrame with the index reset.
  """
  table.reset_index(inplace=True)
  return table


def setRowAsHeader(table: pd.DataFrame, row: int) -> pd.DataFrame:
  """
  Set a specified row as the header of the DataFrame.
  Args:
      table (pd.DataFrame): The DataFrame to modify.
      row (int): The index of the row to set as the header.
  Returns:
      pd.DataFrame: The modified DataFrame with the specified row set as the header.
  """
  table.columns = table.iloc[row]
  table = table.drop(table.index[row])
  return table


def getCollumnNames(table: pd.DataFrame) -> list:
  """
  Retrieves the names of the columns in the DataFrame.
  Args:
      table (pd.DataFrame): The DataFrame to retrieve column names from.
  Returns:
      list: A list of column names.
  """
  columns = table.columns.tolist()
  return columns


def getRowNames(table: pd.DataFrame) -> list:
  """
  Retrieves the names of the rows in the DataFrame.
  Args:
      table (pd.DataFrame): The DataFrame to retrieve row names from.
  Returns:
      list: A list of row names.
  """
  rows = table.index.tolist()
  return rows


def setCellValue(table: pd.DataFrame, row: int, column: int, value) -> pd.DataFrame:
  """
  Sets a value in a specified cell of the DataFrame.
  Args:
      table (pd.DataFrame): The DataFrame to modify.
      row (int): The index of the row to modify.
      column (int): The index of the column to modify.
      value: The value to set in the specified cell.
  Returns:
      pd.DataFrame: The modified DataFrame with the specified cell updated.
  """
  table.at[row, column] = value
  return table


def getCellValue(table: pd.DataFrame, row: int, column: int):
  """
  Retrieves the value from a specified cell of the DataFrame.
  Args:
      table (pd.DataFrame): The DataFrame to retrieve the value from.
      row (int): The index of the row to retrieve the value from.
      column (int): The index of the column to retrieve the value from.
  Returns:
      The value in the specified cell.
  """
  value = table.at[row, column]
  return value


def save_data(table: pd.DataFrame, path: str, sheetName: str, resetIndex: bool = True) -> None:
  """
  Save the DataFrame to an Excel file.
  Args:
      table (pd.DataFrame): The DataFrame to save.
      path (str): The path to save the Excel file.
      sheetName (str): The name of the sheet to save the DataFrame to.
      resetIndex (bool): Whether to reset the index before saving. Default is True.
  Returns:
      None
  """
  if resetIndex:
    table.reset_index(inplace=True)
  table.to_excel(path, sheet_name=sheetName, index=False)
  print(f"Data saved to {path} in sheet {sheetName}")
  return

