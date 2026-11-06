import { api } from "./api";

export const getPropertyAdjustments = async () => {
  const res = await api.get("/pricing/property-adjustments");
  return res.data;
};
