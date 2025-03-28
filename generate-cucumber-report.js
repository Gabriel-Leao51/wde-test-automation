const report = require("multiple-cucumber-html-reporter");
const path = require("path");
const fs = require("fs-extra"); // Usado para ler metadados, se necessário

const reportPath = path.resolve("cypress/reports/cucumber"); // Pasta onde o JSON e o HTML ficarão
const jsonFile = path.join(reportPath, "cucumber-report.json"); // Caminho exato do JSON

// Opcional: Ler metadados de um arquivo (ex: versão do browser, app, etc.)
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
  jsonDir: reportPath, // Diretório contendo o(s) arquivo(s) JSON do Cucumber
  reportPath: reportPath, // Diretório onde o relatório HTML será salvo
  metadata: {
    browser: {
      name: "chrome", // Você pode tornar isso dinâmico se rodar em vários browsers
      version: "Latest", // Exemplo
    },
    device: "GitHub Actions Runner",
    platform: {
      name: "ubuntu", // Exemplo
      // version: '...',
    },
  },
  customData: {
    title: "Run info",
    data: [
      { label: "Project", value: "WDE Shop E2E Tests" },
      { label: "Release", value: "1.0.0" }, // Exemplo
      { label: "Cycle", value: "CI Execution" },
      { label: "Execution Start Time", value: new Date().toLocaleString() },
    ],
  },
  reportName: "WDE Shop - Relatório de Testes BDD", // Título do Relatório HTML
  pageTitle: "WDE Shop - Relatório BDD", // Título da Aba do Navegador
  displayDuration: true, // Mostrar duração dos cenários/passos
  // durationInMS: false, // Mostrar duração em ms (padrão é formatado)
  hideMetadata: false, // Mostrar bloco de metadados
  displayReportTime: true, // Mostrar hora de geração do relatório
});

console.log(
  `Cucumber HTML report generated at: ${path.join(reportPath, "index.html")}`
);
