"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState } from "react";

const navItems = [
	{ href: "/", label: "首页" },
	{ href: "/products?tag=new", label: "新品" },
	{ href: "/products?tag=hot", label: "热销" },
	{ href: "/products", label: "分类" },
	{ href: "/cart", label: "购物车" },
	{ href: "/login", label: "登录" },
] as const;

export function Header() {
	const pathname = usePathname();
	const [open, setOpen] = useState(false);
	return (
		<header className="border-b border-neutral-200">
			<div className="container flex h-14 items-center justify-between">
				<Link href="/" className="text-lg font-semibold tracking-wide">
					CBC
				</Link>
				<nav className="hidden gap-6 md:flex">
					{navItems.map((item) => (
						<Link
							key={item.href}
							href={item.href as any}
							className={`text-sm transition-colors hover:text-neutral-900 ${pathname === item.href ? "text-neutral-900" : "text-neutral-500"}`}
						>
							{item.label}
						</Link>
					))}
				</nav>
				<button
					className="md:hidden text-sm text-neutral-600"
					onClick={() => setOpen((v) => !v)}
					aria-label="打开菜单"
				>
					菜单
				</button>
			</div>
			{open && (
				<div className="border-t border-neutral-200 md:hidden">
					<div className="container py-2">
						{navItems.map((item) => (
							<Link key={item.href} href={item.href as any} className="block py-2 text-sm text-neutral-700">
								{item.label}
							</Link>
						))}
					</div>
				</div>
			)}
		</header>
	);
}