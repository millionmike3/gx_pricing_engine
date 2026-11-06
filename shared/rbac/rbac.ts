import { Roles } from "./roles";
import { Permissions } from "./permissions";

const RolePermissions = {
  [Roles.ADMIN]: [
    Permissions.VIEW_PRICING,
    Permissions.RUN_SCENARIO,
    Permissions.UPLOAD_MATRIX,
  ],
  [Roles.INVESTOR]: [Permissions.VIEW_PORTFOLIO],
  [Roles.BORROWER]: [Permissions.VIEW_PRICING],
};

export function can(role: string, permission: string) {
  return RolePermissions[role]?.includes(permission) || false;
}
