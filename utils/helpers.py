def format_product_data(raw_table: list[list[str]]) -> dict[str, str]:
    """Converts a Gherkin data table (with header row) into a {field: value} dict."""
    return {row[0].lower(): row[1] for row in raw_table[1:]}
