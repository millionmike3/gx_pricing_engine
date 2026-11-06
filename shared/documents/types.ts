export type DocumentType =
  | "id"
  | "income"
  | "assets"
  | "property"
  | "tax_returns";

export type DocumentStatus = {
  type: DocumentType;
  received: boolean;
  verified: boolean;
};

export type DocumentChecklist = {
  required: DocumentType[];
  statuses: DocumentStatus[];
};
