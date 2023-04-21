const { createProxyMiddleware } = require('http-proxy-middleware');

//SetupProxy to define what paths are used
module.exports = function(app) {
  app.use(
    '/video',
    createProxyMiddleware({
      target: 'http://localhost:5000',
      changeOrigin: true,
    })
  );
  app.use(
    '/script',
    createProxyMiddleware({
      target: 'http://localhost:5000',
      changeOrigin: true,
    })
  );
};
