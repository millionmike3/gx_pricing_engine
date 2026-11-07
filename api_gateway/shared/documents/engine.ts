import { BaseRequirements } from "./requirements";
import { DocumentChecklist, DocumentStatus } from "./types";

export function buildChecklist(receivedDocs: DocumentStatus[]): DocumentChecklist {
  const statuses: DocumentStatus[] = BaseRequirements.map(type => {
    const existing = receivedDocs.find(d => d.type === type);
    return (
      existing || {
        type,
        received: false,
        verified: false,
      }
    );
  });

  return {
    required: BaseRequirements,
    statuses,
  };
}
