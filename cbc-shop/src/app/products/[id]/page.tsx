"use client";

import { useState } from "react";
import { notFound } from "next/navigation";
import { getProductById } from "@/data/products";
import { useCart } from "@/lib/cart/CartContext";

export default function ProductDetailPage({ params }: { params: { id: string } }) {
	const product = getProductById(params.id);
	const { addItem } = useCart();
	const [size, setSize] = useState<string | undefined>(undefined);
	if (!product) return notFound();

	return (
		<div className="container py-8">
			<div className="grid gap-8 md:grid-cols-2">
				<div className="aspect-[3/4] w-full bg-neutral-100" />
				<div>
					<h1 className="text-xl font-semibold">{product.name}</h1>
					<p className="mt-2 text-neutral-600">{product.description}</p>
					<p className="mt-3 text-lg font-medium">¥{product.price}</p>
					<div className="mt-4">
						<p className="mb-2 text-sm text-neutral-600">尺码</p>
						<div className="flex flex-wrap gap-2">
							{product.sizes.map((s) => (
								<button
									key={s}
									onClick={() => setSize(s)}
									className={`rounded border px-3 py-1 text-sm ${size === s ? "border-neutral-900" : "border-neutral-300"}`}
								>
									{s}
								</button>
							))}
						</div>
					</div>
					<div className="mt-6 flex gap-3">
						<button
							onClick={() => addItem({ id: product.id, name: product.name, price: product.price, size })}
							className="rounded bg-neutral-900 px-4 py-2 text-sm text-white"
						>
							加入购物车
						</button>
						<button className="rounded border border-neutral-300 px-4 py-2 text-sm">收藏（敬请期待）</button>
					</div>
					<div className="mt-8">
						<h2 className="mb-2 text-base font-semibold">用户评价（敬请期待）</h2>
						<div className="rounded border border-neutral-200 p-4 text-sm text-neutral-500">暂无评价</div>
					</div>
				</div>
			</div>
		</div>
	);
}