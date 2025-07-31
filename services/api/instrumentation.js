/*instrumentation.js*/
// Require dependencies
const { diag, DiagConsoleLogger, DiagLogLevel } = require('@opentelemetry/api');
const { NodeSDK } = require('@opentelemetry/sdk-node');
const { OTLPTraceExporter } = require('@opentelemetry/exporter-trace-otlp-http');
const { PrometheusExporter } = require('@opentelemetry/exporter-prometheus');
const { Resource } = require('@opentelemetry/resources');
const {
  SemanticResourceAttributes,
} = require('@opentelemetry/semantic-conventions');
const {
  getNodeAutoInstrumentations,
} = require('@opentelemetry/auto-instrumentations-node');

diag.setLogger(new DiagConsoleLogger(), DiagLogLevel.DEBUG);

const sdk = new NodeSDK({
  resource: new Resource({
    [SemanticResourceAttributes.SERVICE_NAME]: 'dice-server',
    [SemanticResourceAttributes.SERVICE_VERSION]: '0.1.0',
  }),
  traceExporter: new OTLPTraceExporter({
    url:
      process.env.OTEL_EXPORTER_OTLP_ENDPOINT || 'http://localhost:4318/v1/traces',
    headers: {}, // Add any headers if needed
  }),
  metricReader: new PrometheusExporter({
    startServer: true,
    port: 9464,
  }),
  instrumentations: [getNodeAutoInstrumentations()],
});

sdk.start();
