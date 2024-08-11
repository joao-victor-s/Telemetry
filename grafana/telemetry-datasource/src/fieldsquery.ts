const TOKEN_REGEX = /([a-zA-Z0-9_]+)(\[(\d+)\])?/;

function extractObjectValueFromQueryToken(
  obj: any,
  token: string,
  safe: boolean
): unknown {
  if ((obj === undefined || obj === null) && safe) {
    return obj;
  }

  const match = TOKEN_REGEX.exec(token);
  if (!match || match.length === 0) {
    throw new Error(`Invalid object path token '${token}'`);
  }

  const identifier = match[1];

  let index;
  if (match[2]) {
    if (match[3]) {
      index = parseInt(match[3], 10);
    } else {
      throw new Error("Invalid usage of [] operator");
    }
  }

  let extractedValue = obj[identifier];
  if (typeof index === "number" && extractedValue) {
    extractedValue = extractedValue[index];
  }

  return extractedValue;
}

/** Queries an object, extracting a value given a path. Returns undefined if path is invalid. */
export function extractObjectValueFromQuery(
  obj: any,
  query: string,
  safe = true
): unknown {
  if (!query) {
    return obj;
  }

  const tokens = query.split(".");
  let currentValue = obj;
  for (const token of tokens) {
    currentValue = extractObjectValueFromQueryToken(currentValue, token, safe);
  }

  return currentValue;
}
