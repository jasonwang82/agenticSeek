import Link from "next/link";
import type { Product } from "@/data/products";

export function ProductCard({ product }: { product: Product }) {
	return (
		<Link href={`/products/${product.id}`} className="group block">
			<div className="aspect-[3/4] w-full overflow-hidden bg-neutral-100">
				{/* 图片占位 */}
				<div className="flex h-full items-center justify-center text-neutral-400">
					商品图片
				</div>
			</div>
			<div className="mt-3 flex items-center justify-between">
				<p className="text-sm text-neutral-700">{product.name}</p>
				<p className="text-sm font-medium text-neutral-900">¥{product.price}</p>
			</div>
		</Link>
	);
}