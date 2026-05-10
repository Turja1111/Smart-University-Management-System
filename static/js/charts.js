export function makeLineChart(ctx, labels, data, color = "#7C3AED") {
  return new Chart(ctx, {
    type: "line",
    data: {
      labels,
      datasets: [
        {
          label: "Value",
          data,
          borderColor: color,
          backgroundColor: "rgba(124,58,237,0.1)",
          borderWidth: 2.5,
          pointBackgroundColor: color,
          pointRadius: 5,
          tension: 0.4,
          fill: true,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: {
        x: { grid: { color: "rgba(255,255,255,0.05)" }, ticks: { color: "#94A3B8" } },
        y: { grid: { color: "rgba(255,255,255,0.05)" }, ticks: { color: "#94A3B8" } },
      },
    },
  });
}

export function makeDoughnutChart(ctx, labels, data, colors) {
  return new Chart(ctx, {
    type: "doughnut",
    data: { labels, datasets: [{ data, backgroundColor: colors, borderWidth: 0, hoverOffset: 8 }] },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { position: "right", labels: { color: "#94A3B8", padding: 12, font: { size: 12 } } } },
      cutout: "65%",
    },
  });
}

export function makeBarChart(ctx, labels, data, color = "#3B82F6") {
  return new Chart(ctx, {
    type: "bar",
    data: { labels, datasets: [{ data, backgroundColor: color, borderRadius: 8 }] },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: {
        x: { grid: { display: false }, ticks: { color: "#94A3B8" } },
        y: { grid: { color: "rgba(255,255,255,0.05)" }, ticks: { color: "#94A3B8" } },
      },
    },
  });
}

