import { api } from "./api";

export const getMacroWeights = async () => {
  const res = await api.get("/pricing/macro-weights");
  return res.data;
};
