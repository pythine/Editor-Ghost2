import "./globals.css";

export const metadata = {
  title: "Template Video Editor",
  description: "Buat video dari pola template dengan beat dan efek.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="id">
      <body>{children}</body>
    </html>
  );
}
