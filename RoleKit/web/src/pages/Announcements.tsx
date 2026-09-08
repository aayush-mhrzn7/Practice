import type { UserMe } from "../types";
import ResourceCrud from "./ResourceCrud";

export default function Announcements({ me }: { me: UserMe }) {
  return (
    <ResourceCrud
      me={me}
      heading="Announcements"
      path="/announcements"
      blurb="The bulletin. Assign the desk role to get full CRUD here plus settings, still no document delete."
      verbs={{
        read: "announcements:read",
        write: "announcements:write",
        edit: "announcements:edit",
        delete: "announcements:delete",
      }}
    />
  );
}
