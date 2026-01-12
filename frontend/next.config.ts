import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  /* config options here */
  async redirects() {
    return [
      {
        source: '/tracker',
        destination: '/?tab=tracker',
        permanent: false,
      },
    ]
  },
};

export default nextConfig;
