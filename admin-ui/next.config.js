/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,

  async rewrites() {
    return [
      {
        source: "/auth/:path*",
        destination: "https://genxbabyauthbackend-production.up.railway.app/auth/:path*"
      }
    ];
  }
};

module.exports = nextConfig;
