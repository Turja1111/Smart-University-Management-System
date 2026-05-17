import { api, ensureMeLoaded } from "../api.js";
import { getRole, getUser } from "../auth.js";
import { toast } from "../toast.js";
import { countUp } from "../utils.js";

async function main() {
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

  try {
    await ensureMeLoaded();
    const [users, anomalies, audits] = await Promise.all([
      api.admin.users(),
      api.admin.anomalies(),
      api.admin.auditLogs()
    ]);

    // Animate stats
    const totalUsers = users?.results?.length || users?.length || 0;
    const totalAnomalies = anomalies?.results?.length || anomalies?.length || 0;
    const totalAudits = audits?.results?.length || audits?.length || 0;

    countUp(document.getElementById("a-total-users"), totalUsers, 1000);
    countUp(document.getElementById("a-anomalies"), totalAnomalies, 1000);
    countUp(document.getElementById("a-audits"), totalAudits, 1000);

  } catch (e) {
    toast.error("Dashboard error", e.message || "Failed to load system stats");
  }
}

main();
