import "./globals.css";

export const metadata = {
  title: "LogiFlow Enterprise",
  description: "Intelligent logistics and supply chain management platform",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
