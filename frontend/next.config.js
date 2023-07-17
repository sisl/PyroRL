// next.config.js
const { createProxyMiddleware } = require('http-proxy-middleware');

module.exports = {
  async rewrites() {
    return [
      // Forward all requests with /api to the Flask backend running on http://localhost:5000
      {
        source: '/api/:path*',
        destination: 'http://127.0.0.1:5000/api/:path*',
      },
    ];
  },
};
