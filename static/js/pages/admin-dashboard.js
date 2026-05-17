import { api, ensureMeLoaded } from "../api.js";
import { getRole } from "../auth.js";
import { toast } from "../toast.js";
import { countUp } from "../utils.js";

async function main() {
  try {
    // Always load fresh user data FIRST before checking role
    await ensureMeLoaded();

    const role = getRole();
    if (role === "student") {
      window.location.href = "/student/dashboard/";
      return;
    }
    if (role === "teacher") {
      window.location.href = "/teacher/dashboard/";
      return;
    }
    if (role !== "admin") {
      window.location.href = "/login/";
      return;
    }

    // Load stats concurrently — wrap each so one failure doesn't block others
    const [users, anomalies, audits] = await Promise.allSettled([
      api.admin.users(),
      api.admin.anomalies(),
      api.admin.auditLogs(),
    ]);

    const userList   = users.value?.results   ?? users.value   ?? [];
    const anomList   = anomalies.value?.results ?? anomalies.value ?? [];
    const auditList  = audits.value?.results   ?? audits.value  ?? [];

    const statEl = (id) => document.getElementById(id);
    if (statEl("a-total-users"))  countUp(statEl("a-total-users"),  userList.length,  1000);
    if (statEl("a-anomalies"))    countUp(statEl("a-anomalies"),    anomList.length,  1000);
    if (statEl("a-audits"))       countUp(statEl("a-audits"),       auditList.length, 1000);
    if (statEl("a-reports"))      countUp(statEl("a-reports"),      anomList.filter(a => !a.resolved).length, 1000);

  } catch (e) {
    toast.error("Dashboard error", e.message || "Failed to load system stats");
  }
}

main();
