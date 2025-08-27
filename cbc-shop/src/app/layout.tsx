import type { Metadata } from "next";
import "./globals.css";
import { Header } from "@/components/Header";
import { Footer } from "@/components/Footer";
import { CartProvider } from "@/lib/cart/CartContext";

export const metadata: Metadata = {
	title: "CBC 女装电商",
	description: "面向中国消费者的女装电商网站",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
	return (
		<html lang="zh-CN">
			<body>
				<CartProvider>
					<div className="flex min-h-screen flex-col">
						<Header />
						<main className="flex-1">{children}</main>
						<Footer />
					</div>
				</CartProvider>
			</body>
		</html>
	);
}