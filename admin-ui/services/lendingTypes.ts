import { api } from "./api";

export const getLendingTypes = async () => {
  const res = await api.get("/pricing/lending-types");
  return res.data;
};
