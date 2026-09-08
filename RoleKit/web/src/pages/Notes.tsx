import type { UserMe } from "../types";
import ResourceCrud from "./ResourceCrud";

export default function Notes({ me }: { me: UserMe }) {
  return (
    <ResourceCrud
      me={me}
      heading="Notes"
      path="/notes"
      blurb="Shift memos. Separate table, separate codes. A notes:read role cannot PATCH documents."
      verbs={{
        read: "notes:read",
        write: "notes:write",
        edit: "notes:edit",
        delete: "notes:delete",
      }}
    />
  );
}
