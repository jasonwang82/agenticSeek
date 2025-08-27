"use client";

import { useState } from "react";
import { useCart } from "@/lib/cart/CartContext";

export default function CheckoutPage() {
	const { items, subtotal, clear } = useCart();
	const [submitted, setSubmitted] = useState(false);

	if (items.length === 0) {
		return (
			<div className="container py-8">
				<h1 className="text-xl font-semibold">结算</h1>
				<p className="mt-4 text-neutral-600">购物车为空。</p>
			</div>
		);
	}

	return (
		<div className="container py-8">
			<h1 className="mb-6 text-xl font-semibold">结算</h1>
			{submitted ? (
				<div className="rounded border border-neutral-200 p-6">
					<p className="text-neutral-700">订单已创建（支付敬请期待）。</p>
				</div>
			) : (
				<form
					onSubmit={(e) => {
						e.preventDefault();
						setSubmitted(true);
						clear();
					}}
					className="grid gap-6 md:grid-cols-[1fr_320px]"
				>
					<div className="space-y-4">
						<div>
							<label className="block text-sm text-neutral-600">收货人姓名</label>
							<input required className="mt-1 w-full rounded border border-neutral-300 px-3 py-2 text-sm" />
						</div>
						<div>
							<label className="block text-sm text-neutral-600">手机号</label>
							<input required className="mt-1 w-full rounded border border-neutral-300 px-3 py-2 text-sm" />
						</div>
						<div>
							<label className="block text-sm text-neutral-600">收货地址</label>
							<input required className="mt-1 w-full rounded border border-neutral-300 px-3 py-2 text-sm" />
						</div>
					</div>
					<aside className="rounded border border-neutral-200 p-4">
						<p className="mb-2 text-sm text-neutral-600">应付金额</p>
						<p className="mb-4 text-xl font-semibold">¥{subtotal}</p>
						<button type="submit" className="w-full rounded bg-neutral-900 px-4 py-2 text-sm text-white">下单（支付敬请期待）</button>
					</aside>
				</form>
			)}
		</div>
	);
}