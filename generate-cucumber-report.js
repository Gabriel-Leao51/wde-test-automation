const report = require("multiple-cucumber-html-reporter");
const path = require("path");
const fs = require("fs-extra");

const reportPath = path.resolve("cypress/reports/cucumber");
const jsonFile = path.join(reportPath, "cucumber-report.json");

const metadataPath = path.join(reportPath, "metadata.json");
let metadata = {};
try {
  if (fs.existsSync(metadataPath)) {
    metadata = fs.readJsonSync(metadataPath);
  }
} catch (err) {
  console.warn("Could not read metadata file:", err);
}

report.generate({
  jsonDir: reportPath,
  reportPath: reportPath,
  metadata: {
    browser: {
      name: "chrome",
      version: "Latest",
    },
    device: "GitHub Actions Runner",
    platform: {
      name: "ubuntu",
    },
  },
  customData: {
    title: "Run info",
    data: [
      { label: "Project", value: "WDE Shop E2E Tests" },
      { label: "Release", value: "1.0.0" },
      { label: "Cycle", value: "CI Execution" },
      { label: "Execution Start Time", value: new Date().toLocaleString() },
    ],
  },
  reportName: "WDE Shop - Relatório de Testes BDD",
  pageTitle: "WDE Shop - Relatório BDD",
  displayDuration: true,
  hideMetadata: false,
  displayReportTime: true,
});

console.log(
  `Cucumber HTML report generated at: ${path.join(reportPath, "index.html")}`
);
