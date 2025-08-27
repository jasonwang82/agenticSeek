import { ProductCard } from "@/components/ProductCard";
import { products } from "@/data/products";

export default function ProductsPage() {
	return (
		<div className="container py-8">
			<div className="mb-6 flex items-center justify-between">
				<h1 className="text-xl font-semibold">全部商品</h1>
				<div className="text-sm text-neutral-500">筛选与排序（敬请期待）</div>
			</div>
			<div className="grid grid-cols-2 gap-4 sm:grid-cols-3 md:grid-cols-4">
				{products.map((p) => (
					<ProductCard key={p.id} product={p} />
				))}
			</div>
		</div>
	);
}