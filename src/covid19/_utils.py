import tabula


def extract_pdf_tables(pdf_file):
    """Extract tables from PDF."""
    dfs = tabula.read_pdf(pdf_file, pages='all', multiple_tables=True)
    tables = []

    for df in dfs:
        row_k_to_items = {}
        for _, cell_map in df.to_dict().items():
            for row_k, cell_value in cell_map.items():

                if row_k not in row_k_to_items:
                    row_k_to_items[row_k] = []
                if not isinstance(cell_value, str):
                    cell_value = ''
                row_k_to_items[row_k].append(cell_value)

        table = list(row_k_to_items.values())
        tables.append(table)
    return tables
