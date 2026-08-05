import React from 'react';

export const metadata = {
  title: 'Order Supervisor Node',
  description: 'Sagepilot AI Assignment POC',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
