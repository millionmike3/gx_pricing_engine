import { api } from "./api";

export const getCreditTiers = async () => {
  const res = await api.get("/pricing/credit-tiers");
  return res.data;
};
