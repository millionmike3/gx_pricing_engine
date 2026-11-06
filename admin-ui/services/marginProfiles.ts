import { api } from "./api";

export const getMarginProfiles = async () => {
  const res = await api.get("/pricing/margin-profiles");
  return res.data;
};
