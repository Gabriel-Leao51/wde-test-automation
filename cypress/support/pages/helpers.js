export function formatProductData(rawTable) {
  const productData = {};
  for (let i = 1; i < rawTable.length; i++) {
    const row = rawTable[i];
    const fieldName = row[0].toLowerCase();
    const fieldValue = row[1];
    productData[fieldName] = fieldValue;
  }
  return productData;
}
