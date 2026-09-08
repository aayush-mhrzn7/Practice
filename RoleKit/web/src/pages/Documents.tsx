import type { UserMe } from "../types";
import ResourceCrud from "./ResourceCrud";

export default function Documents({ me }: { me: UserMe }) {
  return (
    <ResourceCrud
      me={me}
      heading="Documents"
      path="/documents"
      blurb="Long-form records. Gates: documents:read, write, edit, delete. Hiding a button is not auth."
      verbs={{
        read: "documents:read",
        write: "documents:write",
        edit: "documents:edit",
        delete: "documents:delete",
      }}
    />
  );
}
