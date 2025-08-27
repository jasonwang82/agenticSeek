"use client";

import { useCart } from "@/lib/cart/CartContext";

export default function CartPage() {
	const { items, subtotal, updateQty, removeItem, clear } = useCart();
	return (
		<div className="container py-8">
			<h1 className="mb-6 text-xl font-semibold">购物车</h1>
			{items.length === 0 ? (
				<div className="rounded border border-neutral-200 p-6 text-neutral-600">购物车为空</div>
			) : (
				<div className="grid gap-6 md:grid-cols-[1fr_320px]">
					<ul className="space-y-4">
						{items.map((i) => (
							<li key={`${i.id}-${i.size ?? "_"}`} className="flex items-center justify-between rounded border border-neutral-200 p-4">
								<div>
									<p className="text-sm text-neutral-700">{i.name}</p>
									<p className="text-xs text-neutral-500">尺码：{i.size ?? "-"}</p>
								</div>
								<div className="flex items-center gap-3">
									<input
										type="number"
										min={1}
										value={i.qty}
										onChange={(e) => updateQty(i.id, i.size, Math.max(1, Number(e.target.value)))}
										className="w-16 rounded border border-neutral-300 px-2 py-1 text-sm"
									/>
									<button onClick={() => removeItem(i.id, i.size)} className="text-sm text-red-600">移除</button>
								</div>
							</li>
						))}
					</ul>
					<aside className="rounded border border-neutral-200 p-4">
						<p className="mb-2 text-sm text-neutral-600">小计</p>
						<p className="mb-4 text-xl font-semibold">¥{subtotal}</p>
						<a href="/checkout" className="block rounded bg-neutral-900 px-4 py-2 text-center text-sm text-white">去结算</a>
						<button onClick={clear} className="mt-3 block w-full rounded border border-neutral-300 px-4 py-2 text-sm">清空</button>
					</aside>
				</div>
			)}
		</div>
	);
}