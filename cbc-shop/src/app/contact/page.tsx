"use client";

import { useState } from "react";

export default function ContactPage() {
	const [loading, setLoading] = useState(false);
	const [status, setStatus] = useState<string | null>(null);
	return (
		<div className="container py-8">
			<h1 className="mb-6 text-xl font-semibold">联系官方</h1>
			<form
				onSubmit={async (e) => {
					e.preventDefault();
					const form = e.currentTarget as HTMLFormElement;
					const formData = new FormData(form);
					setLoading(true);
					setStatus(null);
					try {
						const res = await fetch("/api/contact", {
							method: "POST",
							headers: { "Content-Type": "application/json" },
							body: JSON.stringify({
								name: formData.get("name"),
								email: formData.get("email"),
								message: formData.get("message"),
							}),
						});
						const data = await res.json();
						setStatus(data?.ok ? "发送成功" : "发送失败");
					} catch {
						setStatus("发送失败");
					} finally {
						setLoading(false);
					}
				}}
				className="max-w-xl space-y-4"
			>
				<div>
					<label className="block text-sm text-neutral-600">姓名</label>
					<input name="name" required className="mt-1 w-full rounded border border-neutral-300 px-3 py-2 text-sm" />
				</div>
				<div>
					<label className="block text-sm text-neutral-600">邮箱</label>
					<input name="email" type="email" required className="mt-1 w-full rounded border border-neutral-300 px-3 py-2 text-sm" />
				</div>
				<div>
					<label className="block text-sm text-neutral-600">留言</label>
					<textarea name="message" required className="mt-1 w-full rounded border border-neutral-300 px-3 py-2 text-sm" rows={5} />
				</div>
				<button disabled={loading} className="rounded bg-neutral-900 px-4 py-2 text-sm text-white disabled:opacity-60">{loading ? "发送中" : "发送"}</button>
				{status && <p className="text-sm text-neutral-600">{status}</p>}
			</form>
		</div>
	);
}