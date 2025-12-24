/** @type {import('next').NextConfig} */
const nextConfig = {
    output: 'standalone',
    eslint: {
        ignoreDuringBuilds: true, // We lint in CI, not build time to save time
    },
};

export default nextConfig;
