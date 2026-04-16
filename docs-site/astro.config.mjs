import { defineConfig } from 'astro/config';
import starlight from '@astrojs/starlight';
import starlightThemeGalaxy from 'starlight-theme-galaxy';

export default defineConfig({
  site: 'https://crowdstrike.github.io',
  base: '/falcon-mcp',
  integrations: [
    starlight({
      plugins: [starlightThemeGalaxy()],
      components: {
        Hero: './src/components/Hero.astro',
      },
      logo: {
        src: './src/assets/hunting.png',
        replacesTitle: false
      },
      title: 'Falcon MCP',
      favicon: '/icons/faviconV2.png',
      social: [
        { label: 'GitHub', icon: 'github', href: 'https://github.com/CrowdStrike/falcon-mcp' },
      ],
      customCss: ['./src/styles/custom.css'],
      sidebar: [
        {
          label: 'Getting Started',
          items: [
            { label: 'Installation', slug: 'getting-started/installation' },
            { label: 'API Credentials', slug: 'getting-started/credentials' },
            { label: 'Configuration', slug: 'getting-started/configuration' },
            { label: 'Quick Start', slug: 'getting-started/quickstart' },
          ],
        },
        {
          label: 'Usage',
          items: [
            { label: 'CLI Commands', slug: 'usage/cli' },
            { label: 'Transport Methods', slug: 'usage/transports' },
            { label: 'Editor Integration', slug: 'usage/editor-integration' },
            { label: 'Flight Control (MSSP)', slug: 'usage/flight-control' },
          ],
        },
        {
          label: 'Modules',
          autogenerate: { directory: 'modules' },
        },
        {
          label: 'Deployment',
          items: [
            { label: 'Docker', slug: 'deployment/docker' },
            { label: 'Amazon Bedrock', slug: 'deployment/amazon-bedrock' },
            { label: 'Google Cloud', slug: 'deployment/google-cloud' },
          ],
        },
        {
          label: 'Development',
          items: [
            { label: 'Contributing', slug: 'development/contributing' },
            { label: 'Module Development', slug: 'development/module-development' },
            { label: 'Resource Development', slug: 'development/resource-development' },
            { label: 'Integration Testing', slug: 'development/integration-testing' },
            { label: 'E2E Testing', slug: 'development/e2e-testing' },
            { label: 'Docs Site Guide', slug: 'development/docs-site' },
          ],
        },
        {
          label: 'Examples',
          items: [
            { label: 'Basic Usage', slug: 'examples/basic-usage' },
            { label: 'MCP Config', slug: 'examples/mcp-config' },
          ],
        },
        { label: 'Changelog', slug: 'changelog' },
      ],
    }),
  ],
});
