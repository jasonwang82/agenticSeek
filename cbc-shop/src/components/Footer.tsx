import Link from "next/link";

export function Footer() {
	return (
		<footer className="border-t border-neutral-200">
			<div className="container flex flex-col gap-4 py-8 md:flex-row md:items-center md:justify-between">
				<p className="text-sm text-neutral-500">© {new Date().getFullYear()} CBC</p>
				<nav className="flex gap-6 text-sm text-neutral-600">
					<Link href="/contact">联系官方</Link>
					<Link href="/policy/terms">服务条款</Link>
					<Link href="/policy/privacy">隐私政策</Link>
				</nav>
			</div>
		</footer>
	);
}