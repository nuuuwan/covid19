import re

import tabula
from utils import dt


def extract_pdf_tables(pdf_file):
    """Extract tables from PDF."""
    dfs = tabula.read_pdf(pdf_file, pages='all', multiple_tables=True)
    tables = []

    for df in dfs:
        row_k_to_items = {}
        for _, row_str_map in df.to_dict().items():
            for row_k, row_str_value in row_str_map.items():

                if row_k not in row_k_to_items:
                    row_k_to_items[row_k] = []
                if isinstance(row_str_value, str):
                    row_str_value = row_str_value.replace('-', '0')
                    row_str_value = re.sub(r'[^0-9\s]', '', row_str_value)
                    row_str_value = re.sub(r'\s+', ' ', row_str_value).strip()
                    if row_str_value:
                        row_k_to_items[row_k].append(row_str_value)
                elif isinstance(row_str_value, int):
                    row_k_to_items[row_k].append(row_str_value)

        table = list(row_k_to_items.values())
        tables.append(table)
    return tables


def _row_to_ints(row):
    row_str = ' '.join(row)
    row_str = row_str.replace('-', '0')
    row_str = re.sub(r'[^0-9\s]', '', row_str)
    row_str = re.sub(r'\s+', ' ', row_str).strip()
    return list(
        filter(
            lambda x: x is not None,
            list(map(dt.parse_int, row_str.split(' '))),
        )
    )
