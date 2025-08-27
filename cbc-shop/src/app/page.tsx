import Link from "next/link";
import { products } from "@/data/products";
import { ProductCard } from "@/components/ProductCard";

export default function HomePage() {
	const newItems = products.slice(0, 4);
	const hotItems = products.filter((p) => p.tags.includes("hot")).slice(0, 4);
	return (
		<div className="container py-8">
			<section className="mb-10">
				<div className="mb-4 flex items-center justify-between">
					<h2 className="text-lg font-semibold">新品推荐</h2>
					<Link href="/products?tag=new" className="text-sm text-neutral-600">查看更多</Link>
				</div>
				<div className="grid grid-cols-2 gap-4 sm:grid-cols-3 md:grid-cols-4">
					{newItems.map((p) => (
						<ProductCard key={p.id} product={p} />
					))}
				</div>
			</section>
			<section>
				<div className="mb-4 flex items-center justify-between">
					<h2 className="text-lg font-semibold">热销商品</h2>
					<Link href="/products?tag=hot" className="text-sm text-neutral-600">查看更多</Link>
				</div>
				<div className="grid grid-cols-2 gap-4 sm:grid-cols-3 md:grid-cols-4">
					{hotItems.map((p) => (
						<ProductCard key={p.id} product={p} />
					))}
				</div>
			</section>
		</div>
	);
}