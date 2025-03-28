const { defineConfig } = require("cypress");
const createBundler = require("@bahmutov/cypress-esbuild-preprocessor");
const {
  addCucumberPreprocessorPlugin,
} = require("@badeball/cypress-cucumber-preprocessor");
const {
  createEsbuildPlugin,
} = require("@badeball/cypress-cucumber-preprocessor/esbuild");

module.exports = defineConfig({
  reporter: "cypress-mochawesome-reporter", // Define o reporter a ser usado
  reporterOptions: {
    charts: true, // Exibe gráficos no relatório
    reportPageTitle: "WDE Shop - Relatório de Testes Automatizados", // Título customizado da página HTML
    embeddedScreenshots: true, // Embutir screenshots diretamente no relatório (se houver falhas)
    inlineAssets: true, // Inclui CSS/JS no HTML (arquivo único, mais fácil de arquivar)
    saveAllAttempts: false, // Se usar retries, salva apenas a última tentativa no relatório
    reportDir: "cypress/reports/mochawesome", // Diretório onde os JSONs serão salvos (IMPORTANTE)
    overwrite: false, // NÃO sobrescrever relatórios JSON antigos (necessário para merge)
    html: false, // NÃO gerar HTML automaticamente por arquivo (faremos isso após merge)
    json: true, // GERAR os arquivos JSON individuais por arquivo de teste
  },
  video: true,
  e2e: {
    specPattern: "**/*.feature",
    baseUrl: "https://wde-5p3f.onrender.com/",
    pageLoadTimeout: 90000,
    retries: {
      runMode: 1,
      openMode: 0,
    },
    async setupNodeEvents(on, config) {
      await addCucumberPreprocessorPlugin(on, config);

      on(
        "file:preprocessor",
        createBundler({
          plugins: [createEsbuildPlugin(config)],
        })
      );

      return config;
    },
  },
});
