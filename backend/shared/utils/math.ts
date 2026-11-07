export function round(num: number, decimals = 2) {
  return Number(Math.round(Number(num + "e" + decimals)) + "e-" + decimals);
}
