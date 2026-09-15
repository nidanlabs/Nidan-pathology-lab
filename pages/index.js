import fs from 'fs';
import path from 'path';
import Head from 'next/head';

function buildAppHtml() {
  let html = fs.readFileSync(path.join(process.cwd(), 'nidan.html'), 'utf8');
  html = html.replace(/<link rel="stylesheet" href="([^"]+)">/g, (_, href) => {
    const file = href.split('?')[0];
    const css = fs.readFileSync(path.join(process.cwd(), file), 'utf8');
    return '<style>\n' + css + '\n</style>';
  });
  html = html.replace(/<script src="([^"]+)"><\/script>/g, (_, src) => {
    if (src.startsWith('http')) return '<script src="' + src + '"></script>';
    const file = src.split('?')[0];
    const js = fs.readFileSync(path.join(process.cwd(), file), 'utf8');
    return '<script>\n' + js + '\n</script>';
  });
  return html;
}

export async function getStaticProps() {
  return { props: { appHtml: buildAppHtml() } };
}

export default function Home({ appHtml }) {
  return (
    <>
      <Head>
        <title>NIDAN Pathology Lab</title>
        <meta name="viewport" content="width=device-width, initial-scale=1" />
      </Head>
      <iframe
        srcDoc={appHtml}
        title="NIDAN Pathology Lab"
        style={{ position: 'fixed', inset: 0, width: '100%', height: '100%', border: 0 }}
      />
    </>
  );
}
