/*instrumentation.js*/
// Require dependencies
const { NodeSDK } = require('@opentelemetry/sdk-node');
const { OTLPTraceExporter } = require('@opentelemetry/exporter-trace-otlp-http');
const { PrometheusExporter } = require('@opentelemetry/exporter-prometheus');
const {
  getNodeAutoInstrumentations,
} = require('@opentelemetry/auto-instrumentations-node');
const {
  PeriodicExportingMetricReader,
} = require('@opentelemetry/sdk-metrics');

const sdk = new NodeSDK({
  traceExporter: new OTLPTraceExporter({
    url: process.env.OTEL_EXPORTER_OTLP_ENDPOINT,
    headers: {
      'x-otlp-project-name': 'nodejs-api-service',
      'x-otlp-project-type': 'test_metrics_labels',
    },
  }),
  metricReader: new PrometheusExporter({
    startServer: true,
    port: 9464,
  }),
  instrumentations: [getNodeAutoInstrumentations()],
});

sdk.start();
